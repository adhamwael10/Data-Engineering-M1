
import dash

from utils.data_loader import (
    load_data,
    load_category_data
)

from components.layout import create_layout

from callbacks.dashboard_callbacks import (
    register_dashboard_callbacks
)


# ==========================================
# 1. INITIALIZE APPLICATION
# ==========================================

app = dash.Dash(__name__)
server = app.server


# ==========================================
# 2. LOAD DATASETS
# ==========================================

df = load_data()

housing_category_df, transport_category_df = (
    load_category_data()
)

boroughs = sorted(df["borough"].unique())
years = sorted(df["year"].unique())


# ==========================================
# 3. PLOTLY CHART COLORS
# ==========================================

COLORS = {
    "background": "#0B1220",
    "surface": "#151F32",
    "surface_light": "#1C2940",
    "primary": "#3B82F6",
    "cyan": "#22D3EE",
    "purple": "#A78BFA",
    "orange": "#F59E0B",
    "text": "#F8FAFC",
    "muted": "#94A3B8",
    "border": "#273449"
}


# ==========================================
# 4. CREATE DASHBOARD LAYOUT
# ==========================================

app.layout = create_layout(
    boroughs,
    years
)


# ==========================================
# 5. REGISTER CALLBACKS
# ==========================================

register_dashboard_callbacks(
    app,
    df,
    COLORS,
    housing_category_df,
    transport_category_df
)


# ==========================================
# 6. RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
