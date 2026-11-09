
import json
from functools import lru_cache
from pathlib import Path
from copy import deepcopy

import pandas as pd
import plotly.graph_objects as go


# =====================================================
# COLORS
# =====================================================

BACKGROUND = "#151F32"
BORDER_COLOR = "#273449"
TEXT_COLOR = "#F8FAFC"
MUTED_COLOR = "#94A3B8"

MAP_COLORS = [
    [0.0, "#123B73"],
    [0.35, "#2563EB"],
    [0.7, "#0EA5E9"],
    [1.0, "#22D3EE"]
]


# =====================================================
# LOAD NYC ZIP CODE GEOGRAPHIC DATA
# =====================================================

@lru_cache(maxsize=1)
def load_zip_geojson():

    project_root = Path(__file__).resolve().parents[1]

    geojson_path = (
        project_root / "Data" / "nyc_zip_codes.geojson"
    )

    if not geojson_path.exists():
        raise FileNotFoundError(
            f"NYC ZIP GeoJSON file not found: {geojson_path}"
        )

    with open(geojson_path, "r", encoding="utf-8") as file:
        geojson = json.load(file)

    if geojson.get("type") != "FeatureCollection":
        raise ValueError("Invalid NYC ZIP code GeoJSON file.")

    if not geojson.get("features"):
        raise ValueError("GeoJSON contains no geographic features.")

    return geojson


# =====================================================
# NORMALIZE ZIP CODES
# =====================================================

def normalize_zip(value):

    if pd.isna(value):
        return None

    value = str(value).strip()

    if value.endswith(".0"):
        value = value[:-2]

    if not value:
        return None

    return value.zfill(5)


# =====================================================
# PREPARE GEOJSON IDENTIFIERS
# =====================================================

def prepare_geojson():

    geojson = deepcopy(load_zip_geojson())

    valid_features = []

    for feature in geojson["features"]:

        properties = feature.get("properties", {})

        zip_code = normalize_zip(
            properties.get("zcta5")
        )

        if zip_code is None:
            continue

        # Ensure GeoJSON IDs match normalized CSV ZIP codes
        properties["zcta5"] = zip_code

        valid_features.append(feature)

    geojson["features"] = valid_features

    return geojson


# =====================================================
# EMPTY MAP
# =====================================================

def create_empty_map(
    message="No matching geographic data"
):

    fig = go.Figure()

    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(
            color=MUTED_COLOR,
            size=17
        )
    )

    fig.update_layout(

        geo=dict(
            bgcolor=BACKGROUND,
            showland=True,
            landcolor="#19253A",
            showocean=True,
            oceancolor=BACKGROUND,
            showlakes=True,
            lakecolor=BACKGROUND,
            showcoastlines=True,
            coastlinecolor=BORDER_COLOR,
            showcountries=False,
            showsubunits=False,
            projection=dict(type="mercator")
        ),

        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,

        font=dict(
            color=TEXT_COLOR,
            family="Arial"
        ),

        margin=dict(l=0, r=0, t=10, b=0),

        height=620
    )

    return fig


# =====================================================
# CREATE INTERACTIVE NYC ZIP CODE MAP
# =====================================================

def create_zip_map(
    filtered_df,
    selected_metric="permit_count"
):

    # ---------------------------------------------
    # Metric configuration
    # ---------------------------------------------

    metric_labels = {
        "permit_count": "Approved Building Permits",
        "crash_count": "Traffic Collisions"
    }

    if selected_metric not in metric_labels:
        selected_metric = "permit_count"

    metric_label = metric_labels[selected_metric]

    # ---------------------------------------------
    # Check dataset
    # ---------------------------------------------

    if filtered_df is None or filtered_df.empty:

        return create_empty_map(
            "No data available for the selected filters"
        )

    required_columns = [
        "zip_code",
        "permit_count",
        "crash_count",
        "borough"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in filtered_df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # ---------------------------------------------
    # 1. Load geographic boundaries
    # ---------------------------------------------

    geojson = prepare_geojson()

    features = geojson["features"]

    geojson_zips = {
        feature["properties"]["zcta5"]
        for feature in features
    }

    # ---------------------------------------------
    # 2. Prepare filtered dataset
    # ---------------------------------------------

    df = filtered_df.copy()

    df["zip_code"] = df["zip_code"].apply(
        normalize_zip
    )

    df = df.dropna(subset=["zip_code"])

    df["permit_count"] = pd.to_numeric(
        df["permit_count"],
        errors="coerce"
    ).fillna(0)

    df["crash_count"] = pd.to_numeric(
        df["crash_count"],
        errors="coerce"
    ).fillna(0)

    df["borough"] = (
        df["borough"]
        .fillna("Unknown")
        .astype(str)
    )

    # ---------------------------------------------
    # 3. Aggregate data by ZIP code
    # ---------------------------------------------

    aggregation = {
        "permit_count": ("permit_count", "sum"),
        "crash_count": ("crash_count", "sum"),
        "borough": ("borough", "first")
    }

    if "year" in df.columns:

        # Support both integer years (2023)
        # and date-formatted years (2023-01-01).
        year_values = pd.to_numeric(
            df["year"],
            errors="coerce"
        )

        date_mask = year_values.isna()

        year_values.loc[date_mask] = (
            pd.to_datetime(
                df.loc[date_mask, "year"],
                errors="coerce"
            ).dt.year
        )

        df["_year_label"] = year_values

        aggregation["years"] = (
            "_year_label",
            lambda values: ", ".join(
                map(
                    str,
                    sorted(values.dropna().unique())
                )
            )
        )

    aggregated = (
        df.groupby("zip_code", as_index=False)
        .agg(**aggregation)
    )

    if "years" not in aggregated.columns:
        aggregated["years"] = "Not available"

    # ---------------------------------------------
    # 4. Match CSV ZIP codes with GeoJSON
    # ---------------------------------------------

    matched_df = aggregated[
        aggregated["zip_code"].isin(geojson_zips)
    ].copy()

    if matched_df.empty:

        return create_empty_map(
            "No matching ZIP codes in the selected data"
        )

    matched_zips = set(matched_df["zip_code"])

    unmatched_zips = (
        geojson_zips - matched_zips
    )

    # ---------------------------------------------
    # 5. Create map
    # ---------------------------------------------

    fig = go.Figure()

    # ---------------------------------------------
    # Unmatched ZIP areas - neutral grey
    # ---------------------------------------------

    if unmatched_zips:

        fig.add_trace(

            go.Choropleth(

                geojson=geojson,

                locations=sorted(unmatched_zips),

                z=[0] * len(unmatched_zips),

                featureidkey="properties.zcta5",

                colorscale=[
                    [0, "#273449"],
                    [1, "#273449"]
                ],

                zmin=0,
                zmax=1,

                showscale=False,

                marker_line_color="#0B1220",
                marker_line_width=0.6,

                hovertemplate=(
                    "<b>ZIP Code: %{location}</b><br>"
                    "No matching integrated data"
                    "<extra></extra>"
                )

            )

        )

    # ---------------------------------------------
    # Matched ZIP areas - actual dataset values
    # ---------------------------------------------

    matched_df["years"] = (
        matched_df["years"].fillna("Not available")
    )

    custom_data = matched_df[
        [
            "borough",
            "permit_count",
            "crash_count",
            "years"
        ]
    ].to_numpy()

    map_values = matched_df[selected_metric]

    maximum_value = max(
        float(map_values.max()),
        1
    )

    fig.add_trace(

        go.Choropleth(

            geojson=geojson,

            locations=matched_df["zip_code"],

            z=map_values,

            featureidkey="properties.zcta5",

            colorscale=MAP_COLORS,

            zmin=0,
            zmax=maximum_value,

            customdata=custom_data,

            marker_line_color="#0B1220",
            marker_line_width=0.8,

            colorbar=dict(

                title=dict(
                    text=metric_label,
                    font=dict(
                        color=TEXT_COLOR,
                        size=12
                    )
                ),

                tickfont=dict(
                    color="#CBD5E1"
                ),

                bgcolor=BACKGROUND,

                thickness=14,

                outlinewidth=0

            ),

            hovertemplate=(

                "<b>ZIP Code: %{location}</b><br>"

                "Borough: %{customdata[0]}<br>"

                "Years: %{customdata[3]}<br>"

                "Approved Permits: "
                "%{customdata[1]:,.0f}<br>"

                "Traffic Collisions: "
                "%{customdata[2]:,.0f}<br>"

                f"{metric_label}: "
                "%{z:,.0f}"

                "<extra></extra>"

            )

        )

    )

    # ---------------------------------------------
    # 6. Map layout and appearance
    # ---------------------------------------------

    fig.update_geos(

        projection_type="mercator",

        fitbounds="locations",

        visible=False,

        bgcolor=BACKGROUND,

        showland=True,

        landcolor="#19253A",

        showocean=True,

        oceancolor=BACKGROUND,

        showlakes=True,

        lakecolor=BACKGROUND,

        showcoastlines=True,

        coastlinecolor=BORDER_COLOR,

        showcountries=False,

        showsubunits=False

    )

    fig.update_layout(

        paper_bgcolor=BACKGROUND,

        plot_bgcolor=BACKGROUND,

        font=dict(
            color=TEXT_COLOR,
            family="Arial"
        ),

        margin=dict(
            l=0,
            r=0,
            t=10,
            b=0
        ),

        height=620,

        showlegend=False,

        uirevision="nyc-zip-map"

    )

    return fig
