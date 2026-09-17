"""Reproducible analysis for the Saudi high-school resource-allocation manuscript.

Place this script beside
`Supplementary_Data_General_Education_Statistics_2024.xlsx` and run:

    python Supplementary_Code_High_School_Analysis_v3.py

The script creates report-ready CSV tables and four figures in `analysis_outputs/`.
All descriptive and inferential comparisons are aligned to the 13 Saudi
administrative regions. The public-versus-fee-paying inferential analysis first
aggregates the 192 high-school administrative cells by region and funding group,
then compares the paired regional ratios. It does not treat administrative cells
as independent school-level observations.
"""

from __future__ import annotations

from pathlib import Path
import math
import os
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "Supplementary_Data_General_Education_Statistics_2024.xlsx"
OUTPUT_DIR = BASE_DIR / "analysis_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

EXPECTED_COLUMNS = {
    "Administrators",
    "Teachers",
    "Students",
    "Number of Schools",
    "Gender",
    "Education Type",
    "Stage",
    "Education Administration",
    "Region",
}

REGION_ORDER = [
    "Riyadh",
    "Makkah",
    "Eastern",
    "Asir",
    "Al Madinah",
    "Jazan",
    "Al-Qassim",
    "Tabuk",
    "Ha'il",
    "Al Jouf",
    "Najran",
    "Northern Borders",
    "Al Bahah",
]

SECTOR_ORDER = ["Government", "Private", "International"]
FUNDING_ORDER = [
    "Publicly funded (Government)",
    "Fee-paying (Private + International)",
]
COUNT_COLUMNS = ["Number of Schools", "Students", "Teachers", "Administrators"]
RATIO_COLUMNS = [
    "Students per School",
    "Students per Teacher",
    "Students per Administrator",
]


def clean_stale_outputs() -> None:
    """Remove obsolete cell-level inferential outputs from earlier versions."""
    stale = [
        "table6_welch_tests_high_school_cells.csv",
        "table6_paired_regional_comparison.csv",
        "supplementary_regional_funding_ratios.csv",
    ]
    for filename in stale:
        path = OUTPUT_DIR / filename
        if path.exists():
            path.unlink()


def safe_divide(numerator: pd.Series | float, denominator: pd.Series | float):
    """Divide while replacing zero denominators with NaN."""
    if isinstance(denominator, pd.Series):
        return numerator / denominator.replace(0, np.nan)
    if denominator == 0:
        return np.nan
    return numerator / denominator


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Data file not found: {DATA_PATH}. Place the workbook beside this script."
        )

    source = pd.read_excel(DATA_PATH)
    missing = EXPECTED_COLUMNS.difference(source.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    for column in COUNT_COLUMNS:
        source[column] = pd.to_numeric(source[column], errors="raise")

    non_royal = source[source["Education Type"] != "Royal Commission"].copy()
    high_school = non_royal[non_royal["Stage"] == "High school"].copy()

    if high_school.empty:
        raise ValueError("No records were found with Stage == 'High school'.")

    high_school["Funding Group"] = np.where(
        high_school["Education Type"].eq("Government"),
        FUNDING_ORDER[0],
        FUNDING_ORDER[1],
    )
    return source, non_royal, high_school


def validate_totals(high_school: pd.DataFrame) -> None:
    totals = high_school[COUNT_COLUMNS].sum()
    expected = {
        "Number of Schools": 5356,
        "Students": 1451903,
        "Teachers": 120330,
        "Administrators": 14175,
    }
    for column, expected_value in expected.items():
        actual = int(totals[column])
        if actual != expected_value:
            warnings.warn(
                f"Unexpected total for {column}: {actual:,}; expected {expected_value:,}."
            )

    observed_regions = set(high_school["Region"].dropna().unique())
    missing_regions = set(REGION_ORDER).difference(observed_regions)
    if missing_regions:
        raise ValueError(f"Missing expected regions: {sorted(missing_regions)}")


def build_table1_regional_descriptives(high_school: pd.DataFrame) -> pd.DataFrame:
    regional = high_school.groupby("Region", as_index=True)[COUNT_COLUMNS].sum()
    regional = regional.reindex(REGION_ORDER)

    labels = {
        "Administrators": "Administrators",
        "Teachers": "Teachers",
        "Students": "Students",
        "Number of Schools": "No. of Schools",
    }
    rows: list[dict[str, object]] = []
    for column in ["Administrators", "Teachers", "Students", "Number of Schools"]:
        values = regional[column].dropna()
        rows.append(
            {
                "Metric": labels[column],
                "Total": int(values.sum()),
                "Mean": values.mean(),
                "Median": values.median(),
                "SD": values.std(ddof=1),
                "Minimum": int(values.min()),
                "Maximum": int(values.max()),
                "Q1": values.quantile(0.25),
                "Q3": values.quantile(0.75),
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(OUTPUT_DIR / "table1_regional_descriptive_statistics.csv", index=False)
    return table


def add_derived_ratios(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["Students per School"] = safe_divide(
        result["Students"], result["Number of Schools"]
    )
    result["Students per Teacher"] = safe_divide(
        result["Students"], result["Teachers"]
    )
    result["Students per Administrator"] = safe_divide(
        result["Students"], result["Administrators"]
    )
    return result


def build_table2_sector_summary(high_school: pd.DataFrame) -> pd.DataFrame:
    sector = high_school.groupby("Education Type")[COUNT_COLUMNS].sum()
    sector = sector.reindex(SECTOR_ORDER)
    sector = add_derived_ratios(sector)
    sector.to_csv(OUTPUT_DIR / "table2_school_type_summary.csv")
    return sector


def build_table3_funding_summary(high_school: pd.DataFrame) -> pd.DataFrame:
    funding = (
        high_school.groupby("Funding Group")[COUNT_COLUMNS]
        .sum()
        .reindex(FUNDING_ORDER)
    )
    funding = add_derived_ratios(funding)

    totals = high_school[COUNT_COLUMNS].sum()
    funding["School share (%)"] = (
        funding["Number of Schools"] / totals["Number of Schools"] * 100
    )
    funding["Student share (%)"] = funding["Students"] / totals["Students"] * 100
    funding["Teacher share (%)"] = funding["Teachers"] / totals["Teachers"] * 100
    funding["Administrator share (%)"] = (
        funding["Administrators"] / totals["Administrators"] * 100
    )

    gender = (
        high_school.groupby(["Funding Group", "Gender"])["Students"]
        .sum()
        .unstack(fill_value=0)
        .reindex(FUNDING_ORDER)
    )
    for gender_name in ["Boys", "Girls"]:
        if gender_name not in gender.columns:
            gender[gender_name] = 0
    funding["Boys"] = gender["Boys"]
    funding["Girls"] = gender["Girls"]
    funding["Boys within group (%)"] = funding["Boys"] / funding["Students"] * 100
    funding["Girls within group (%)"] = funding["Girls"] / funding["Students"] * 100

    funding = funding[
        [
            "Number of Schools",
            "School share (%)",
            "Students",
            "Student share (%)",
            "Boys",
            "Boys within group (%)",
            "Girls",
            "Girls within group (%)",
            "Teachers",
            "Teacher share (%)",
            "Administrators",
            "Administrator share (%)",
            "Students per School",
            "Students per Teacher",
            "Students per Administrator",
        ]
    ]
    funding.to_csv(OUTPUT_DIR / "table3_public_vs_fee_paying_summary.csv")
    return funding


def build_table4_school_load(high_school: pd.DataFrame) -> pd.DataFrame:
    regional = high_school.groupby("Region")[COUNT_COLUMNS].sum()
    regional = add_derived_ratios(regional)
    national_mean = high_school["Students"].sum() / high_school["Number of Schools"].sum()
    table = regional[["Students per School"]].sort_values(
        "Students per School", ascending=False
    )
    table["Rank"] = table["Students per School"].rank(
        method="min", ascending=False
    ).astype(int)
    table["Difference from National Mean"] = (
        table["Students per School"] - national_mean
    )
    table = table[["Rank", "Students per School", "Difference from National Mean"]]
    table.to_csv(OUTPUT_DIR / "table4_regional_school_load.csv")
    return table


def build_table5_regional_summary(high_school: pd.DataFrame) -> pd.DataFrame:
    regional = high_school.groupby("Region")[COUNT_COLUMNS].sum()
    regional = add_derived_ratios(regional)
    regional["Load Rank"] = regional["Students per School"].rank(
        method="min", ascending=False
    ).astype(int)
    regional = regional.reindex(REGION_ORDER)
    regional.to_csv(OUTPUT_DIR / "table5_regional_summary.csv")
    return regional


def build_regional_funding_ratios(high_school: pd.DataFrame) -> pd.DataFrame:
    """Aggregate across gender and education administrations within region/funding group."""
    regional_funding = (
        high_school.groupby(["Region", "Funding Group"])[COUNT_COLUMNS]
        .sum()
        .reindex(
            pd.MultiIndex.from_product(
                [REGION_ORDER, FUNDING_ORDER], names=["Region", "Funding Group"]
            )
        )
    )
    if regional_funding["Students"].isna().any():
        missing = regional_funding[regional_funding["Students"].isna()].index.tolist()
        raise ValueError(f"Missing region/funding combinations: {missing}")

    regional_funding = add_derived_ratios(regional_funding).reset_index()
    regional_funding.to_csv(
        OUTPUT_DIR / "supplementary_regional_funding_ratios.csv", index=False
    )
    return regional_funding


def paired_effect_size_dz(differences: pd.Series) -> float:
    """Cohen's dz for paired observations."""
    return differences.mean() / differences.std(ddof=1)


def build_table6_paired_regional_comparison(
    high_school: pd.DataFrame,
) -> pd.DataFrame:
    regional_funding = build_regional_funding_ratios(high_school)
    wide = regional_funding.pivot(
        index="Region", columns="Funding Group", values=RATIO_COLUMNS
    ).reindex(REGION_ORDER)

    rows: list[dict[str, object]] = []
    for indicator in RATIO_COLUMNS:
        public = wide[(indicator, FUNDING_ORDER[0])]
        fee = wide[(indicator, FUNDING_ORDER[1])]
        paired = pd.concat([public, fee], axis=1).dropna()
        paired.columns = ["Publicly funded", "Fee-paying"]
        differences = paired["Publicly funded"] - paired["Fee-paying"]
        n = len(differences)

        paired_t = stats.ttest_rel(
            paired["Publicly funded"], paired["Fee-paying"], nan_policy="omit"
        )
        se = differences.std(ddof=1) / math.sqrt(n)
        critical_t = stats.t.ppf(0.975, df=n - 1)
        ci_low = differences.mean() - critical_t * se
        ci_high = differences.mean() + critical_t * se

        # Exact/automatic two-sided signed-rank sensitivity test.
        wilcoxon = stats.wilcoxon(
            paired["Publicly funded"],
            paired["Fee-paying"],
            alternative="two-sided",
            method="auto",
        )
        shapiro = stats.shapiro(differences)

        rows.append(
            {
                "Indicator": indicator,
                "Paired regions (n)": n,
                "Public mean": paired["Publicly funded"].mean(),
                "Public median": paired["Publicly funded"].median(),
                "Fee-paying mean": paired["Fee-paying"].mean(),
                "Fee-paying median": paired["Fee-paying"].median(),
                "Mean paired difference (Public - Fee-paying)": differences.mean(),
                "95% CI lower": ci_low,
                "95% CI upper": ci_high,
                "Paired t": paired_t.statistic,
                "Paired t p-value": paired_t.pvalue,
                "Wilcoxon W": wilcoxon.statistic,
                "Wilcoxon p-value": wilcoxon.pvalue,
                "Cohen dz": paired_effect_size_dz(differences),
                "Shapiro-Wilk p (paired differences)": shapiro.pvalue,
                "Regions Public > Fee-paying": int((differences > 0).sum()),
                "Regions Public < Fee-paying": int((differences < 0).sum()),
            }
        )

    table = pd.DataFrame(rows)
    table.to_csv(
        OUTPUT_DIR / "table6_paired_regional_comparison.csv", index=False
    )
    return table


def make_figure1(high_school: pd.DataFrame) -> None:
    regional = high_school.groupby("Region")[COUNT_COLUMNS].sum()
    sorted_regions = regional.sort_values("Students", ascending=False).index
    sorted_data = regional.loc[sorted_regions]

    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    metrics = ["Students", "Teachers", "Administrators", "Number of Schools"]
    for metric, ax in zip(metrics, axes.flat):
        bars = ax.bar(sorted_data.index, sorted_data[metric])
        ax.set_title(metric)
        ax.set_ylabel("Count")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:,.0f}",
                (bar.get_x() + bar.get_width() / 2, height),
                ha="center",
                va="bottom",
                fontsize=8,
                xytext=(0, 3),
                textcoords="offset points",
            )
    fig.suptitle(
        "Regional Distribution of High-School Resources in Saudi Arabia",
        fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "figure1_regional_resources.png", dpi=300, bbox_inches="tight"
    )
    plt.close(fig)


def make_figure2(high_school: pd.DataFrame) -> None:
    gender = high_school.groupby(["Region", "Gender"])["Students"].sum().unstack(fill_value=0)
    for column in ["Boys", "Girls"]:
        if column not in gender.columns:
            gender[column] = 0
    gender["Total"] = gender["Boys"] + gender["Girls"]
    gender = gender.sort_values("Total", ascending=False)

    x = np.arange(len(gender))
    width = 0.38
    fig, ax = plt.subplots(figsize=(16, 7))
    ax.bar(x - width / 2, gender["Boys"], width, label="Boys")
    ax.bar(x + width / 2, gender["Girls"], width, label="Girls")
    ax.set_xticks(x)
    ax.set_xticklabels(gender.index, rotation=45, ha="right")
    ax.set_ylabel("Students")
    ax.set_title("High-School Student Enrolment by Gender and Region")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "figure2_gender_by_region.png", dpi=300, bbox_inches="tight"
    )
    plt.close(fig)


def make_figure3(high_school: pd.DataFrame) -> None:
    composition = high_school.pivot_table(
        index=["Region", "Gender"],
        columns="Education Type",
        values="Students",
        aggfunc="sum",
        fill_value=0,
    ).reindex(columns=SECTOR_ORDER, fill_value=0)
    percent = composition.div(composition.sum(axis=1), axis=0).fillna(0) * 100
    percent = percent.reset_index()
    percent["Region-Gender"] = percent["Region"] + " - " + percent["Gender"]
    percent = percent.set_index("Region-Gender")

    fig, ax = plt.subplots(figsize=(18, 8))
    bottom = np.zeros(len(percent))
    for sector in SECTOR_ORDER:
        values = percent[sector].to_numpy()
        ax.bar(percent.index, values, bottom=bottom, label=sector)
        bottom += values
    ax.set_ylim(0, 100)
    ax.set_ylabel("Share of students (%)")
    ax.set_title("High-School Student Distribution by School Type, Gender, and Region")
    ax.tick_params(axis="x", rotation=60)
    ax.legend(title="School type")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "figure3_sector_gender_composition.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def make_figure4(high_school: pd.DataFrame) -> None:
    grouped = high_school.groupby(["Region", "Education Type"])[COUNT_COLUMNS].sum()
    grouped = add_derived_ratios(grouped).reset_index()
    long = grouped.melt(
        id_vars=["Region", "Education Type"],
        value_vars=RATIO_COLUMNS,
        var_name="Metric",
        value_name="Value",
    )

    g = sns.catplot(
        data=long,
        x="Region",
        y="Value",
        hue="Education Type",
        col="Metric",
        kind="bar",
        col_wrap=3,
        sharey=False,
        height=5.5,
        aspect=1.1,
        order=REGION_ORDER,
        hue_order=SECTOR_ORDER,
    )
    g.set_titles("{col_name}")
    g.set_axis_labels("", "Ratio / average")
    for ax in g.axes.flat:
        ax.tick_params(axis="x", rotation=55)
        ax.grid(axis="y", linestyle="--", alpha=0.3)
    g.fig.suptitle(
        "High-School Resource Ratios by Region and School Type",
        y=1.03,
        fontweight="bold",
    )
    g.fig.savefig(
        OUTPUT_DIR / "figure4_resource_ratios.png", dpi=300, bbox_inches="tight"
    )
    plt.close(g.fig)


def print_report(
    table1: pd.DataFrame,
    table2: pd.DataFrame,
    table3: pd.DataFrame,
    table4: pd.DataFrame,
    table5: pd.DataFrame,
    table6: pd.DataFrame,
) -> None:
    pd.set_option("display.max_columns", None)
    print("\nTABLE 1 — REGIONAL DESCRIPTIVE STATISTICS\n", table1.round(2).to_string(index=False))
    print("\nTABLE 2 — SCHOOL-TYPE SUMMARY\n", table2.round(2).to_string())
    print("\nTABLE 3 — PUBLICLY FUNDED VS FEE-PAYING\n", table3.round(2).to_string())
    print("\nTABLE 4 — REGIONAL SCHOOL LOAD\n", table4.round(2).to_string())
    print("\nTABLE 5 — REGIONAL SUMMARY\n", table5.round(2).to_string())
    print("\nTABLE 6 — PAIRED REGIONAL COMPARISON\n", table6.round(4).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


def main() -> None:
    clean_stale_outputs()
    _, _, high_school = load_data()
    validate_totals(high_school)

    table1 = build_table1_regional_descriptives(high_school)
    table2 = build_table2_sector_summary(high_school)
    table3 = build_table3_funding_summary(high_school)
    table4 = build_table4_school_load(high_school)
    table5 = build_table5_regional_summary(high_school)
    table6 = build_table6_paired_regional_comparison(high_school)

    make_figure1(high_school)
    make_figure2(high_school)
    make_figure3(high_school)
    make_figure4(high_school)

    print_report(table1, table2, table3, table4, table5, table6)


if __name__ == "__main__":
    main()
