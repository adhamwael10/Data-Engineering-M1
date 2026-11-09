
import pandas as pd
from pathlib import Path


# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Dataset location
DATA_PATH = BASE_DIR / "Data" / "integrated_data.csv"


def load_data():

    """
    Load and prepare the integrated housing
    and transportation dataset.
    """

    # Check whether the CSV exists
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    # Load dataset
    df = pd.read_csv(DATA_PATH)

    # Required columns
    required_columns = [
        "zip_code",
        "year",
        "permit_count",
        "crash_count",
        "borough"
    ]

    # Validate columns
    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Prepare year
    df["year"] = pd.to_datetime(
        df["year"],
        errors="coerce"
    ).dt.year

    # Prepare ZIP codes
    df["zip_code"] = (
        df["zip_code"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(5)
    )

    # Standardize borough names
    df["borough"] = (
        df["borough"]
        .astype(str)
        .str.upper()
    )

    # Convert numerical columns
    df["permit_count"] = pd.to_numeric(
        df["permit_count"],
        errors="coerce"
    )

    df["crash_count"] = pd.to_numeric(
        df["crash_count"],
        errors="coerce"
    )

    # Remove rows with invalid required values
    df = df.dropna(
        subset=required_columns
    ).copy()

    print("Dataset loaded successfully!")
    print("Dataset shape:", df.shape)

    return df
