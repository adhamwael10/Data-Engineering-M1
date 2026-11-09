
from dash import dcc, html


def create_filter_panel(boroughs, years):

    default_borough = (
        "BROOKLYN"
        if "BROOKLYN" in boroughs
        else boroughs[0]
    )

    return html.Div([

        html.H3(
            "Explore the Data",
            className="section-title"
        ),

        html.Div([

            # BOROUGH FILTER
            html.Div([

                html.Label(
                    "Select Borough",
                    className="filter-label"
                ),

                dcc.Dropdown(
                    id="borough-dropdown",
                    options=[
                        {
                            "label": borough.title(),
                            "value": borough
                        }
                        for borough in boroughs
                    ],
                    value=default_borough,
                    clearable=False
                )

            ], className="filter-group"),

            # YEAR FILTER
            html.Div([

                html.Label(
                    "Select Year",
                    className="filter-label"
                ),

                dcc.Dropdown(
                    id="year-dropdown",
                    options=[
                        {
                            "label": str(int(year)),
                            "value": int(year)
                        }
                        for year in years
                    ],
                    value=None,
                    placeholder="All years",
                    clearable=True
                )

            ], className="filter-group"),

            # SEARCH
            html.Div([

                html.Label(
                    "Search",
                    className="filter-label"
                ),

                dcc.Input(
                    id="search-input",
                    type="text",
                    placeholder="Brooklyn 2023 or 10001",
                    className="search-input"
                )

            ], className="filter-group")

        ], className="filter-grid"),

        html.Button(
            "Generate Report",
            id="generate-button",
            n_clicks=0,
            className="generate-button"
        )

    ], className="filter-panel")
