
import pandas as pd
from dash import html


def format_number(value):
    """Format numeric values for dashboard display."""
    return f"{value:,.0f}"


def create_insight_card(label, value, description, accent):
    """Create a reusable analytical insight card."""

    return html.Div([

        html.Div(
            label,
            className="insight-label"
        ),

        html.H2(
            value,
            className="insight-value"
        ),

        html.P(
            description,
            className="insight-description"
        )

    ], className=f"insight-card {accent}")


def create_insights_cards(filtered_df):
    """
    Generate analytical insights from the currently
    filtered integrated dataset.
    """

    if filtered_df.empty:

        return [
            html.Div(
                "No insights available for the selected filters.",
                className="insight-empty"
            )
        ]

    data = filtered_df.copy()

    data["year"] = pd.to_numeric(
        data["year"], errors="coerce"
    )

    data["permit_count"] = pd.to_numeric(
        data["permit_count"], errors="coerce"
    )

    data["crash_count"] = pd.to_numeric(
        data["crash_count"], errors="coerce"
    )

    data = data.dropna(
        subset=["year", "permit_count"]
    )

    if data.empty:
        return [
            html.Div(
                "No valid analytical records available.",
                className="insight-empty"
            )
        ]

    # =========================================
    # 1. TOP ZIP CODE BY PERMIT ACTIVITY
    # =========================================

    zip_activity = (
        data.groupby("zip_code")["permit_count"]
        .sum()
        .sort_values(ascending=False)
    )

    top_zip = str(zip_activity.index[0])

    top_zip_permits = zip_activity.iloc[0]

    zip_insight = create_insight_card(
        "TOP ZIP CODE",
        top_zip,
        f"{format_number(top_zip_permits)} approved permits "
        "across the selected period.",
        "insight-blue"
    )

    # =========================================
    # 2. YEAR WITH HIGHEST PERMIT ACTIVITY
    # =========================================

    yearly_activity = (
        data.groupby("year")["permit_count"]
        .sum()
        .sort_index()
    )

    peak_year = int(yearly_activity.idxmax())

    peak_permits = yearly_activity.max()

    peak_insight = create_insight_card(
        "PEAK PERMIT YEAR",
        str(peak_year),
        f"{format_number(peak_permits)} approved permits "
        "recorded in this year.",
        "insight-purple"
    )

    # =========================================
    # 3. YEAR-OVER-YEAR PERMIT TREND
    # =========================================

    # Exclude 2026 because it is an incomplete year
    # in this project's dataset.

    completed_yearly = yearly_activity[
        yearly_activity.index < 2026
    ]

    if len(completed_yearly) >= 2:

        latest_year = int(completed_yearly.index[-1])

        previous_year = int(completed_yearly.index[-2])

        latest_value = completed_yearly.iloc[-1]

        previous_value = completed_yearly.iloc[-2]

        if previous_value > 0:

            percentage_change = (
                (latest_value - previous_value)
                / previous_value
            ) * 100

            if percentage_change > 0:

                trend_value = f"+{percentage_change:.1f}%"

                trend_description = (
                    f"Permit activity increased from "
                    f"{previous_year} to {latest_year}."
                )

                trend_class = "insight-green"

            elif percentage_change < 0:

                trend_value = f"{percentage_change:.1f}%"

                trend_description = (
                    f"Permit activity decreased from "
                    f"{previous_year} to {latest_year}."
                )

                trend_class = "insight-orange"

            else:

                trend_value = "0.0%"

                trend_description = (
                    f"Permit activity remained unchanged "
                    f"from {previous_year} to {latest_year}."
                )

                trend_class = "insight-cyan"

        else:

            trend_value = "N/A"

            trend_description = (
                "Previous-year permit activity was zero."
            )

            trend_class = "insight-cyan"

    else:

        trend_value = "N/A"

        trend_description = (
            "At least two complete years are needed "
            "to calculate the yearly change."
        )

        trend_class = "insight-cyan"

    trend_insight = create_insight_card(
        "YEARLY PERMIT CHANGE",
        trend_value,
        trend_description,
        trend_class
    )

    # =========================================
    # 4. PERMITS VS COLLISIONS CORRELATION
    # =========================================

    comparable_data = data[
        data["year"] >= 2020
    ][["permit_count", "crash_count"]].dropna()

    if (
        len(comparable_data) >= 3
        and comparable_data["permit_count"].nunique() > 1
        and comparable_data["crash_count"].nunique() > 1
    ):

        correlation = comparable_data[
            "permit_count"
        ].corr(
            comparable_data["crash_count"]
        )

        if correlation >= 0.7:
            correlation_label = "Strong positive"

        elif correlation >= 0.3:
            correlation_label = "Moderate positive"

        elif correlation > 0:
            correlation_label = "Weak positive"

        elif correlation <= -0.7:
            correlation_label = "Strong negative"

        elif correlation <= -0.3:
            correlation_label = "Moderate negative"

        elif correlation < 0:
            correlation_label = "Weak negative"

        else:
            correlation_label = "No linear correlation"

        correlation_value = f"{correlation:+.2f}"

        correlation_description = (
            f"{correlation_label} association across "
            f"{len(comparable_data):,} comparable records "
            f"from 2020 onward."
        )

    else:

        correlation_value = "N/A"

        correlation_description = (
            "Insufficient variation or comparable records "
            "to calculate correlation."
        )

    correlation_insight = create_insight_card(
        "PERMITS VS COLLISIONS",
        correlation_value,
        correlation_description,
        "insight-orange"
    )

    return [
        zip_insight,
        peak_insight,
        trend_insight,
        correlation_insight
    ]
