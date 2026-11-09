
import pandas as pd

from dash import Input, Output, State

from utils.data_processing import (
    filter_dataset,
    calculate_kpis,
    get_yearly_data
)

from components.charts import (
    create_empty_chart,
    create_permits_chart,
    create_scatter_chart,
    create_yearly_trends_chart,
    create_permits_heatmap
)

from components.insights import create_insights_cards

from components.map import (
    create_zip_map,
    load_zip_geojson,
    normalize_zip
)


def calculate_geographic_stats(filtered_df):
    """
    Calculate geographic statistics using the same ZIP code
    matching logic as the NYC geographic map.
    """

    if filtered_df.empty:
        return "0", "0", "0", "0.0%"

    df = filtered_df.copy()

    df["zip_code"] = df["zip_code"].apply(normalize_zip)
    df = df.dropna(subset=["zip_code"])

    if df.empty:
        return "0", "0", "0", "0.0%"

    # Load geographic boundaries
    geojson = load_zip_geojson()

    geojson_zips = {
        normalize_zip(feature["properties"].get("zcta5"))
        for feature in geojson["features"]
    }

    geojson_zips.discard(None)

    # Find ZIP codes available in the filtered dataset
    csv_zips = set(df["zip_code"].unique())

    # Identify ZIP codes matched with GeoJSON
    matched_zips = csv_zips.intersection(geojson_zips)

    # Calculate geographic match rate
    match_rate = (
        (len(matched_zips) / len(csv_zips)) * 100
        if csv_zips else 0
    )

    # Aggregate data by ZIP code
    df["permit_count"] = pd.to_numeric(
        df["permit_count"],
        errors="coerce"
    ).fillna(0)

    df["crash_count"] = pd.to_numeric(
        df["crash_count"],
        errors="coerce"
    ).fillna(0)

    # Keep only geographically matched ZIP codes
    matched_df = df[
        df["zip_code"].isin(matched_zips)
    ]

    total_permits = int(matched_df["permit_count"].sum())
    total_collisions = int(matched_df["crash_count"].sum())

    return (
        f"{len(matched_zips):,}",
        f"{total_permits:,}",
        f"{total_collisions:,}",
        f"{match_rate:.1f}%"
    )


def register_dashboard_callbacks(app, df, colors):

    """
    Register callbacks for:

    - Dashboard charts
    - KPI cards
    - Geographic map
    - Geographic statistics
    - Report status
    - Integrated dataset table
    - Automated analytical insights
    """

    @app.callback(
        [

            Output("bar-chart-permits", "figure"),
            Output("cross-domain-scatter", "figure"),
            Output("yearly-trends-chart", "figure"),
            Output("zip-year-heatmap", "figure"),

            Output("nyc-zip-map", "figure"),

            Output("geo-zips-value", "children"),
            Output("geo-permits-value", "children"),
            Output("geo-collisions-value", "children"),
            Output("geo-match-value", "children"),

            Output("report-status", "children"),

            Output("kpi-permits-value", "children"),
            Output("kpi-collisions-value", "children"),
            Output("kpi-zips-value", "children"),
            Output("kpi-years-value", "children"),

            Output("integrated-data-table", "data"),
            Output("table-record-count", "children"),

            Output("insights-cards", "children")

        ],

        Input("generate-button", "n_clicks"),

        [

            State("borough-dropdown", "value"),
            State("year-dropdown", "value"),
            State("search-input", "value"),
            State("map-metric-dropdown", "value")

        ]
    )

    def update_dashboard(
        n_clicks,
        selected_borough,
        selected_year,
        search_term,
        map_metric
    ):

        # =====================================
        # 1. FILTER DATA
        # =====================================

        (
            filtered_df,
            active_borough,
            active_year,
            search_error

        ) = filter_dataset(
            df,
            selected_borough,
            selected_year,
            search_term
        )

        # =====================================
        # 2. HANDLE EMPTY RESULTS
        # =====================================

        if filtered_df.empty:

            empty_fig = create_empty_chart(
                "No matching data found",
                colors
            )

            empty_map = create_zip_map(
                filtered_df,
                map_metric
            )

            status = search_error or (
                "No records match the selected filters. "
                "Try another borough, year, or ZIP code."
            )

            return (

                empty_fig,
                empty_fig,
                empty_fig,
                empty_fig,

                empty_map,

                "0",
                "0",
                "0",
                "0.0%",

                status,

                "0",
                "0",
                "0",
                "0",

                [],
                "Showing 0 records",

                create_insights_cards(filtered_df)

            )

        # =====================================
        # 3. CALCULATE KPIs
        # =====================================

        kpis = calculate_kpis(filtered_df)

        # =====================================
        # 4. CALCULATE GEOGRAPHIC STATISTICS
        # =====================================

        (
            geo_zips,
            geo_permits,
            geo_collisions,
            geo_match_rate

        ) = calculate_geographic_stats(filtered_df)

        # =====================================
        # 5. AGGREGATE YEARLY DATA
        # =====================================

        yearly_data = get_yearly_data(filtered_df)

        # =====================================
        # 6. CREATE EXISTING CHARTS
        # =====================================

        display_borough = (

            active_borough.title()
            if active_borough
            else "All Boroughs"

        )

        fig1 = create_permits_chart(
            yearly_data,
            display_borough,
            colors
        )

        fig2 = create_scatter_chart(
            filtered_df,
            colors
        )

        fig3 = create_yearly_trends_chart(
            yearly_data,
            colors
        )

        fig4 = create_permits_heatmap(
            filtered_df,
            colors
        )

        # =====================================
        # 7. CREATE NYC GEOGRAPHIC MAP
        # =====================================

        map_fig = create_zip_map(
            filtered_df,
            map_metric
        )

        # =====================================
        # 8. GENERATE ANALYTICAL INSIGHTS
        # =====================================

        insights = create_insights_cards(
            filtered_df
        )

        # =====================================
        # 9. PREPARE TABLE DATA
        # =====================================

        table_df = filtered_df.copy()

        table_df["zip_code"] = (
            table_df["zip_code"].astype(str)
        )

        table_df = table_df[[
            "zip_code",
            "borough",
            "year",
            "permit_count",
            "crash_count"
        ]]

        table_df = table_df.astype(object).where(
            pd.notna(table_df),
            None
        )

        table_records = table_df.to_dict(
            orient="records"
        )

        table_count = (
            f"Showing {len(table_records):,} records"
        )

        # =====================================
        # 10. REPORT STATUS
        # =====================================

        display_year = (

            active_year
            if active_year is not None
            else "All years"

        )

        status = (

            f"Showing {len(filtered_df):,} records | "
            f"Borough: {display_borough} | "
            f"Year: {display_year}"

        )

        # =====================================
        # 11. RETURN RESULTS
        # =====================================

        return (

            fig1,
            fig2,
            fig3,
            fig4,

            map_fig,

            geo_zips,
            geo_permits,
            geo_collisions,
            geo_match_rate,

            status,

            f"{kpis['total_permits']:,}",
            f"{kpis['total_collisions']:,}",
            f"{kpis['total_zips']:,}",
            f"{kpis['total_years']:,}",

            table_records,
            table_count,

            insights

        )

    return update_dashboard
