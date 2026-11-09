
from dash import html


def create_kpi_card(
    title,
    subtitle,
    value_id,
    accent_class
):
    """
    Create a reusable KPI card using CSS classes.
    """

    return html.Div([

        html.P(
            title,
            className="kpi-title"
        ),

        html.H2(
            "—",
            id=value_id,
            className="kpi-value"
        ),

        html.P(
            subtitle,
            className="kpi-subtitle"
        )

    ], className=f"kpi-card {accent_class}")


def create_kpi_section():
    """
    Create the complete KPI cards section.
    """

    return html.Div([

        create_kpi_card(
            "APPROVED PERMITS",
            "Across selected areas",
            "kpi-permits-value",
            "kpi-card-primary"
        ),

        create_kpi_card(
            "TRAFFIC COLLISIONS",
            "Recorded motor vehicle collisions",
            "kpi-collisions-value",
            "kpi-card-cyan"
        ),

        create_kpi_card(
            "ZIP CODES ANALYZED",
            "Geographic coverage",
            "kpi-zips-value",
            "kpi-card-purple"
        ),

        create_kpi_card(
            "YEARS ANALYZED",
            "Selected time period",
            "kpi-years-value",
            "kpi-card-orange"
        )

    ], className="kpi-container")
