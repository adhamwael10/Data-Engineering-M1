
import pandas as pd
from pathlib import Path


# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"

# Dataset paths
DATA_PATH = DATA_DIR / "integrated_data.csv"
HOUSING_CATEGORY_PATH = DATA_DIR / "housing_category_data.csv"
TRANSPORT_CATEGORY_PATH = DATA_DIR / "transport_category_data.csv"


def load_csv(path):
    """Load a CSV file after checking that it exists."""

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    return pd.read_csv(path, low_memory=False)


def load_data():
    """Load and prepare the integrated dataset."""

    df = load_csv(DATA_PATH)

    required_columns = [
        "zip_code",
        "year",
        "permit_count",
        "crash_count",
        "borough"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    df["year"] = pd.to_datetime(
        df["year"],
        errors="coerce"
    ).dt.year

    df["zip_code"] = (
        df["zip_code"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(5)
    )

    df["borough"] = (
        df["borough"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    for col in ["permit_count", "crash_count"]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(
        subset=required_columns
    ).copy()

    print("Integrated dataset loaded:", df.shape)

    return df


def load_category_data():
    """Load and prepare the two category datasets."""

    housing_df = load_csv(HOUSING_CATEGORY_PATH)
    transport_df = load_csv(TRANSPORT_CATEGORY_PATH)

    housing_required = [
        "zip_code",
        "year",
        "borough",
        "work_type",
        "permit_count"
    ]

    transport_required = [
        "zip_code",
        "year",
        "borough",
        "contributing_factor_vehicle_1",
        "collision_count"
    ]

    for name, dataset, required in [
        ("Housing", housing_df, housing_required),
        ("Transportation", transport_df, transport_required)
    ]:

        missing = [
            col for col in required
            if col not in dataset.columns
        ]

        if missing:
            raise ValueError(
                f"{name} category dataset is missing columns: {missing}"
            )

    for dataset in [housing_df, transport_df]:

        dataset["zip_code"] = (
            dataset["zip_code"]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.zfill(5)
        )

        dataset["year"] = pd.to_numeric(
            dataset["year"],
            errors="coerce"
        )

        dataset["borough"] = (
            dataset["borough"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    housing_df = housing_df.dropna(
        subset=["year", "work_type"]
    ).copy()

    transport_df = transport_df.dropna(
        subset=["year", "contributing_factor_vehicle_1"]
    ).copy()

    housing_df["year"] = housing_df["year"].astype(int)
    transport_df["year"] = transport_df["year"].astype(int)

    housing_df["work_type"] = (
        housing_df["work_type"].astype(str).str.strip()
    )

    transport_df["contributing_factor_vehicle_1"] = (
        transport_df["contributing_factor_vehicle_1"]
        .astype(str)
        .str.strip()
    )

    print("Housing category dataset:", housing_df.shape)
    print("Transportation category dataset:", transport_df.shape)

    return housing_df, transport_df
