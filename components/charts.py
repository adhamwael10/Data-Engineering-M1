
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def apply_chart_theme(fig, colors):
    """
    Apply the shared dark theme to a Plotly chart.
    """

    fig.update_layout(
        paper_bgcolor=colors["surface"],
        plot_bgcolor=colors["surface"],
        font_color=colors["text"],
        title_font_size=17,
        margin=dict(l=40, r=30, t=65, b=40),
        legend_title_text=""
    )

    fig.update_xaxes(
        gridcolor=colors["border"],
        zerolinecolor=colors["border"]
    )

    fig.update_yaxes(
        gridcolor=colors["border"],
        zerolinecolor=colors["border"]
    )

    return fig


def create_empty_chart(message, colors):
    """
    Create an empty chart with an explanatory message.
    """

    fig = px.scatter(
        title=message,
        template="plotly_dark"
    )

    return apply_chart_theme(fig, colors)


def create_permits_chart(yearly_data, borough, colors):
    """
    Create a bar chart showing approved permits by year.
    """

    fig = px.bar(
        yearly_data,
        x="year",
        y="permit_count",
        title=f"Approved Building Permits - {borough}",
        labels={
            "year": "Year",
            "permit_count": "Number of Approved Permits"
        },
        text_auto=True,
        color_discrete_sequence=[colors["primary"]],
        template="plotly_dark"
    )

    fig.update_traces(
        marker_line_width=0,
        textposition="outside"
    )

    return apply_chart_theme(fig, colors)


def create_scatter_chart(filtered_df, colors):
    """
    Compare approved permits and traffic collisions.
    """

    comparison_df = filtered_df[
        filtered_df["year"] >= 2020
    ].copy()

    if comparison_df.empty:
        return create_empty_chart(
            "No comparable transportation data for this period",
            colors
        )

    fig = px.scatter(
        comparison_df,
        x="permit_count",
        y="crash_count",
        color="year",
        hover_data=["zip_code", "borough"],
        title="Housing Permits vs. Traffic Collisions",
        labels={
            "permit_count": "Approved Permits",
            "crash_count": "Motor Vehicle Collisions",
            "year": "Year"
        },
        template="plotly_dark",
        color_continuous_scale="Turbo"
    )

    return apply_chart_theme(fig, colors)


def create_yearly_trends_chart(yearly_data, colors):
    """
    Compare yearly permits and collisions.
    """

    if yearly_data.empty:
        return create_empty_chart(
            "No yearly data available",
            colors
        )

    trends_data = yearly_data.copy()

    # Transportation observations before 2020
    # are treated as unavailable, not zero.
    trends_data.loc[
        trends_data["year"] < 2020,
        "crash_count"
    ] = float("nan")

    trends_data = trends_data.melt(
        id_vars="year",
        value_vars=["permit_count", "crash_count"],
        var_name="metric",
        value_name="count"
    )

    trends_data = trends_data.dropna(
        subset=["count"]
    )

    trends_data["metric"] = trends_data["metric"].map({
        "permit_count": "Approved Permits",
        "crash_count": "Traffic Collisions"
    })

    fig = px.line(
        trends_data,
        x="year",
        y="count",
        color="metric",
        markers=True,
        title="Yearly Housing & Transportation Trends",
        labels={
            "year": "Year",
            "count": "Total Count",
            "metric": "Category"
        },
        color_discrete_map={
            "Approved Permits": colors["primary"],
            "Traffic Collisions": colors["cyan"]
        },
        template="plotly_dark"
    )

    fig.update_layout(
        hovermode="x unified"
    )

    return apply_chart_theme(fig, colors)


def create_permits_heatmap(filtered_df, colors):
    """
    Create a ZIP code vs. year heatmap.

    Each cell represents the total approved building
    permits for one ZIP code in one year.
    """

    if filtered_df.empty:
        return create_empty_chart(
            "No data available for the heatmap",
            colors
        )

    heatmap_data = filtered_df.copy()

    heatmap_data["year"] = pd.to_numeric(
        heatmap_data["year"],
        errors="coerce"
    )

    heatmap_data["permit_count"] = pd.to_numeric(
        heatmap_data["permit_count"],
        errors="coerce"
    )

    heatmap_data = heatmap_data.dropna(
        subset=["zip_code", "year", "permit_count"]
    )

    if heatmap_data.empty:
        return create_empty_chart(
            "No valid permit data available",
            colors
        )

    # Aggregate duplicate ZIP/year observations.
    pivot_data = heatmap_data.pivot_table(
        index="zip_code",
        columns="year",
        values="permit_count",
        aggfunc="sum"
    )

    pivot_data = pivot_data.sort_index().sort_index(axis=1)

    if pivot_data.empty:
        return create_empty_chart(
            "No ZIP code and year combinations found",
            colors
        )

    fig = go.Figure(

        data=go.Heatmap(

            z=pivot_data.values,

            x=[
                str(int(year))
                for year in pivot_data.columns
            ],

            y=pivot_data.index.astype(str),

            colorscale=[
                [0, "#111827"],
                [0.25, "#1D4ED8"],
                [0.55, "#0891B2"],
                [0.8, "#22D3EE"],
                [1, "#A78BFA"]
            ],

            colorbar={
                "title": {
                    "text": "Permits",
                    "font": {"color": colors["text"]}
                },
                "tickfont": {
                    "color": colors["muted"]
                }
            },

            hovertemplate=(
                "ZIP Code: %{y}<br>"
                "Year: %{x}<br>"
                "Approved Permits: %{z:,.0f}"
                "<extra></extra>"
            ),

            connectgaps=False
        )

    )

    fig.update_layout(
        title="Building Permit Activity by ZIP Code & Year",
        xaxis_title="Year",
        yaxis_title="ZIP Code",
        yaxis={
            "type": "category",
            "autorange": "reversed"
        }
    )

    return apply_chart_theme(fig, colors)
