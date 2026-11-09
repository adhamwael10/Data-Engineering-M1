
from dash import dcc, html, dash_table

from components.kpi_cards import create_kpi_section
from components.filters import create_filter_panel


def create_layout(boroughs, years):

    return html.Div([

        # =========================================
        # HEADER
        # =========================================

        html.Div([

            html.P(
                "NYC DATA INTELLIGENCE",
                className="header-label"
            ),

            html.H1(
                "Housing & Transportation Explorer",
                className="header-title"
            ),

            html.P(
                "Understanding the relationship between urban "
                "development and traffic safety in New York City.",
                className="header-description"
            )

        ], className="dashboard-header"),

        # =========================================
        # KPI SECTION
        # =========================================

        create_kpi_section(),

        # =========================================
        # FILTER SECTION
        # =========================================

        create_filter_panel(boroughs, years),

        # =========================================
        # REPORT STATUS
        # =========================================

        html.Div(
            id="report-status",
            className="report-status"
        ),

        # =========================================
        # CHARTS
        # =========================================

        html.Div([

            html.Div([
                dcc.Graph(
                    id="bar-chart-permits",
                    config={"displayModeBar": True}
                )
            ], className="chart-card"),

            html.Div([
                dcc.Graph(
                    id="cross-domain-scatter",
                    config={"displayModeBar": True}
                )
            ], className="chart-card"),

            html.Div([
                dcc.Graph(
                    id="yearly-trends-chart",
                    config={"displayModeBar": True}
                )
            ], className="chart-card"),

            html.Div([
                dcc.Graph(
                    id="zip-year-heatmap",
                    config={"displayModeBar": True}
                )
            ], className="chart-card")

        ], className="charts-container"),

        # =========================================
        # NYC GEOGRAPHIC MAP
        # =========================================

        html.Div([

            html.Div([

                html.P(
                    "GEOGRAPHIC INTELLIGENCE",
                    className="insights-label"
                ),

                html.H2(
                    "NYC Geographic Distribution",
                    className="insights-title"
                ),

                html.P(
                    "Explore the geographical distribution of "
                    "building permits and traffic collisions "
                    "across NYC ZIP code areas.",
                    className="insights-description"
                )

            ], className="map-header"),

            html.Div([

                html.Div([

                    html.Label(
                        "Select Map Metric",
                        className="map-control-label"
                    ),

                    dcc.Dropdown(

                        id="map-metric-dropdown",

                        options=[
                            {
                                "label": "Approved Building Permits",
                                "value": "permit_count"
                            },
                            {
                                "label": "Traffic Collisions",
                                "value": "crash_count"
                            }
                        ],

                        value="permit_count",
                        clearable=False,
                        searchable=False,
                        className="map-metric-dropdown"

                    )

                ], className="map-controls"),

                dcc.Graph(
                    id="nyc-zip-map",
                    config={
                        "displayModeBar": True,
                        "scrollZoom": True,
                        "responsive": True
                    }
                )

            ], className="map-card"),

            # =====================================
            # GEOGRAPHIC STATISTICS
            # =====================================

            html.Div([

                html.Div([

                    html.P(
                        "ZIP CODES MAPPED",
                        className="geo-stat-label"
                    ),

                    html.H3(
                        "0",
                        id="geo-zips-value",
                        className="geo-stat-value"
                    ),

                    html.P(
                        "Successfully matched geographic areas",
                        className="geo-stat-description"
                    )

                ], className="geo-stat-card geo-stat-blue"),

                html.Div([

                    html.P(
                        "TOTAL APPROVED PERMITS",
                        className="geo-stat-label"
                    ),

                    html.H3(
                        "0",
                        id="geo-permits-value",
                        className="geo-stat-value"
                    ),

                    html.P(
                        "Across mapped ZIP code areas",
                        className="geo-stat-description"
                    )

                ], className="geo-stat-card geo-stat-cyan"),

                html.Div([

                    html.P(
                        "TOTAL TRAFFIC COLLISIONS",
                        className="geo-stat-label"
                    ),

                    html.H3(
                        "0",
                        id="geo-collisions-value",
                        className="geo-stat-value"
                    ),

                    html.P(
                        "Across mapped ZIP code areas",
                        className="geo-stat-description"
                    )

                ], className="geo-stat-card geo-stat-purple"),

                html.Div([

                    html.P(
                        "GEOGRAPHIC MATCH RATE",
                        className="geo-stat-label"
                    ),

                    html.H3(
                        "0%",
                        id="geo-match-value",
                        className="geo-stat-value"
                    ),

                    html.P(
                        "CSV ZIP codes matched with GeoJSON",
                        className="geo-stat-description"
                    )

                ], className="geo-stat-card geo-stat-orange")

            ], className="geo-stats-grid")

        ], className="map-section"),

        # =========================================
        # AUTOMATED ANALYTICAL INSIGHTS
        # =========================================

        html.Div([

            html.Div([

                html.P(
                    "DATA INTELLIGENCE",
                    className="insights-label"
                ),

                html.H2(
                    "Key Analytical Insights",
                    className="insights-title"
                ),

                html.P(
                    "Automatically generated findings based on "
                    "your selected dataset and filters.",
                    className="insights-description"
                )

            ], className="insights-header"),

            html.Div(
                id="insights-cards",
                className="insights-grid"
            )

        ], className="insights-section"),

        # =========================================
        # INTEGRATED DATA TABLE
        # =========================================

        html.Div([

            html.Div([

                html.Div([

                    html.H3(
                        "Integrated Dataset Explorer",
                        className="section-title"
                    ),

                    html.P(
                        "Explore, sort, filter and export the "
                        "integrated housing and transportation records.",
                        className="table-description"
                    )

                ]),

                html.Div(
                    id="table-record-count",
                    className="table-record-count"
                )

            ], className="table-header"),

            dash_table.DataTable(

                id="integrated-data-table",

                columns=[

                    {
                        "name": "ZIP Code",
                        "id": "zip_code",
                        "type": "text"
                    },

                    {
                        "name": "Borough",
                        "id": "borough",
                        "type": "text"
                    },

                    {
                        "name": "Year",
                        "id": "year",
                        "type": "numeric"
                    },

                    {
                        "name": "Approved Permits",
                        "id": "permit_count",
                        "type": "numeric",
                        "format": {
                            "specifier": ",.0f"
                        }
                    },

                    {
                        "name": "Traffic Collisions",
                        "id": "crash_count",
                        "type": "numeric",
                        "format": {
                            "specifier": ",.0f"
                        }
                    }

                ],

                data=[],

                page_action="native",
                page_current=0,
                page_size=10,

                sort_action="native",
                sort_mode="multi",

                filter_action="native",

                export_format="csv",
                export_headers="display",

                fixed_rows={
                    "headers": True
                },

                style_table={
                    "overflowX": "auto",
                    "minWidth": "100%"
                },

                style_cell={
                    "backgroundColor": "#151F32",
                    "color": "#F8FAFC",
                    "border": "1px solid #273449",
                    "padding": "14px",
                    "textAlign": "left",
                    "fontFamily": "Arial",
                    "fontSize": "13px",
                    "minWidth": "110px",
                    "maxWidth": "220px",
                    "whiteSpace": "normal"
                },

                style_header={
                    "backgroundColor": "#1C2940",
                    "color": "#22D3EE",
                    "fontWeight": "bold",
                    "border": "1px solid #273449",
                    "padding": "15px",
                    "textAlign": "left"
                },

                style_data={
                    "backgroundColor": "#151F32",
                    "color": "#F8FAFC"
                },

                style_filter={
                    "backgroundColor": "#0F192B",
                    "color": "#F8FAFC",
                    "border": "1px solid #273449"
                },

                style_data_conditional=[

                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#19253A"
                    },

                    {
                        "if": {"state": "active"},
                        "backgroundColor": "#263B59",
                        "border": "1px solid #3B82F6"
                    },

                    {
                        "if": {"state": "selected"},
                        "backgroundColor": "#263B59",
                        "border": "1px solid #3B82F6"
                    }

                ],

                style_as_list_view=True

            )

        ], className="data-table-card"),

        # =========================================
        # DATA STORY
        # =========================================

        html.Div([

            html.P(
                "ABOUT THE PROJECT",
                className="story-label"
            ),

            html.H3(
                "Our Data Story",
                className="story-title"
            ),

            html.P(
                "This project investigates how housing development "
                "and motor vehicle collisions vary across NYC ZIP codes "
                "and over time. By integrating building permit data "
                "with transportation data, we explore potential "
                "relationships between urban development and traffic safety.",
                className="story-description"
            ),

            html.H4(
                "Limitations",
                className="story-heading"
            ),

            html.P(
                "The analysis identifies associations, not causation. "
                "Transportation data coverage starts in 2020, while 2026 "
                "is an incomplete year. Dataset sampling and cleaning "
                "decisions may also affect representativeness.",
                className="story-description"
            )

        ], className="story-card")

    ], className="dashboard-container")
