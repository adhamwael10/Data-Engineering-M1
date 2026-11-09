
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


# ==========================================
# GEOGRAPHIC STATISTICS
# ==========================================

def calculate_geographic_stats(filtered_df):

    if filtered_df.empty:
        return "0", "0", "0", "0.0%"

    df = filtered_df.copy()

    df["zip_code"] = df["zip_code"].apply(normalize_zip)
    df = df.dropna(subset=["zip_code"])

    if df.empty:
        return "0", "0", "0", "0.0%"

    geojson = load_zip_geojson()

    geojson_zips = {
        normalize_zip(feature["properties"].get("zcta5"))
        for feature in geojson["features"]
    }

    geojson_zips.discard(None)

    csv_zips = set(df["zip_code"].unique())

    matched_zips = csv_zips.intersection(geojson_zips)

    match_rate = (
        len(matched_zips) / len(csv_zips) * 100
        if csv_zips else 0
    )

    df["permit_count"] = pd.to_numeric(
        df["permit_count"],
        errors="coerce"
    ).fillna(0)

    df["crash_count"] = pd.to_numeric(
        df["crash_count"],
        errors="coerce"
    ).fillna(0)

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


# ==========================================
# CATEGORY MATCHING
# ==========================================

def get_category_keys(
    category_df,
    category_column,
    selected_category
):

    if not selected_category:
        return None

    subset = category_df[
        category_df[category_column] == selected_category
    ].copy()

    if subset.empty:
        return set()

    return set(
        zip(
            subset["zip_code"].astype(str).str.zfill(5),
            subset["year"].astype(int),
            subset["borough"].astype(str).str.upper()
        )
    )


def apply_category_filters(
    filtered_df,
    housing_category_df,
    transport_category_df,
    selected_housing_category,
    selected_transport_category
):

    result = filtered_df.copy()

    housing_keys = get_category_keys(
        housing_category_df,
        "work_type",
        selected_housing_category
    )

    transport_keys = get_category_keys(
        transport_category_df,
        "contributing_factor_vehicle_1",
        selected_transport_category
    )

    # Housing category filter
    if housing_keys is not None:

        result = result[
            [
                (
                    str(row.zip_code).zfill(5),
                    int(row.year),
                    str(row.borough).upper()
                ) in housing_keys
                for row in result.itertuples()
            ]
        ]

    # Transportation category filter
    if transport_keys is not None:

        result = result[
            [
                (
                    str(row.zip_code).zfill(5),
                    int(row.year),
                    str(row.borough).upper()
                ) in transport_keys
                for row in result.itertuples()
            ]
        ]

    return result


# ==========================================
# REGISTER DASHBOARD CALLBACKS
# ==========================================

def register_dashboard_callbacks(
    app,
    df,
    colors,
    housing_category_df,
    transport_category_df
):

    """
    Register callbacks for:

    - Category dropdown options
    - Dashboard charts
    - KPI cards
    - Geographic map
    - Geographic statistics
    - Report status
    - Integrated dataset table
    - Automated analytical insights
    """

    # ======================================
    # 1. POPULATE CATEGORY DROPDOWNS
    # ======================================

    @app.callback(
        Output("housing-category-dropdown", "options"),
        Output("transport-category-dropdown", "options"),
        Input("generate-button", "n_clicks")
    )
    def populate_category_options(n_clicks):

        housing_categories = sorted(
            housing_category_df["work_type"]
            .dropna()
            .astype(str)
            .unique()
        )

        transport_categories = sorted(
            transport_category_df[
                "contributing_factor_vehicle_1"
            ]
            .dropna()
            .astype(str)
            .unique()
        )

        housing_options = [
            {"label": category, "value": category}
            for category in housing_categories
        ]

        transport_options = [
            {"label": category, "value": category}
            for category in transport_categories
        ]

        return housing_options, transport_options

    # ======================================
    # 2. MAIN DASHBOARD CALLBACK
    # ======================================

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

        # CHANGED: Both controls now trigger the callback
        [
            Input("generate-button", "n_clicks"),
            Input("map-metric-dropdown", "value")
        ],

        # Other filters remain State
        [

            State("borough-dropdown", "value"),
            State("year-dropdown", "value"),
            State("search-input", "value"),
            State("housing-category-dropdown", "value"),
            State("transport-category-dropdown", "value")

        ]
    )

    def update_dashboard(
        n_clicks,
        map_metric,
        selected_borough,
        selected_year,
        search_term,
        selected_housing_category,
        selected_transport_category
    ):

        # ==================================
        # 1. APPLY BASIC FILTERS
        # ==================================

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

        # ==================================
        # 2. APPLY CATEGORY FILTERS
        # ==================================

        filtered_df = apply_category_filters(
            filtered_df,
            housing_category_df,
            transport_category_df,
            selected_housing_category,
            selected_transport_category
        )

        # ==================================
        # 3. HANDLE EMPTY RESULTS
        # ==================================

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
                "Try different filter combinations."
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

        # ==================================
        # 4. CALCULATE KPIs
        # ==================================

        kpis = calculate_kpis(filtered_df)

        # ==================================
        # 5. GEOGRAPHIC STATISTICS
        # ==================================

        (
            geo_zips,
            geo_permits,
            geo_collisions,
            geo_match_rate
        ) = calculate_geographic_stats(filtered_df)

        # ==================================
        # 6. YEARLY AGGREGATION
        # ==================================

        yearly_data = get_yearly_data(filtered_df)

        display_borough = (
            active_borough.title()
            if active_borough
            else "All Boroughs"
        )

        # ==================================
        # 7. CREATE CHARTS
        # ==================================

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

        # ==================================
        # 8. CREATE MAP
        # ==================================

        map_fig = create_zip_map(
            filtered_df,
            map_metric
        )

        # ==================================
        # 9. ANALYTICAL INSIGHTS
        # ==================================

        insights = create_insights_cards(
            filtered_df
        )

        # ==================================
        # 10. PREPARE DATA TABLE
        # ==================================

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

        # ==================================
        # 11. REPORT STATUS
        # ==================================

        display_year = (
            active_year
            if active_year is not None
            else "All years"
        )

        selected_filters = []

        if selected_housing_category:
            selected_filters.append(
                f"Housing: {selected_housing_category}"
            )

        if selected_transport_category:
            selected_filters.append(
                f"Transportation: {selected_transport_category}"
            )

        category_status = (
            " | ".join(selected_filters)
            if selected_filters
            else "All categories"
        )

        status = (
            f"Showing {len(filtered_df):,} records | "
            f"Borough: {display_borough} | "
            f"Year: {display_year} | "
            f"{category_status}"
        )

        # ==================================
        # 12. RETURN DASHBOARD RESULTS
        # ==================================

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
