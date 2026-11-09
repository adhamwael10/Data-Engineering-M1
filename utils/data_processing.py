
import re
import pandas as pd


def filter_dataset(
    df,
    selected_borough=None,
    selected_year=None,
    search_term=None
):
    """
    Filter the dataset using borough, year and ZIP code.

    Supported search terms:
    - Borough names
    - Years
    - Five-digit ZIP codes

    Returns:
    filtered_df, active_borough, active_year, search_error
    """

    filtered_df = df.copy()
    search_text = (search_term or "").strip().upper()

    active_borough = selected_borough
    active_year = selected_year
    search_error = None

    if search_text:

        remaining_text = search_text

        # -----------------------------------------
        # 1. DETECT BOROUGH
        # -----------------------------------------

        available_boroughs = sorted(
            df["borough"].dropna().unique(),
            key=len,
            reverse=True
        )

        for borough in available_boroughs:
            if borough in remaining_text:
                active_borough = borough

                remaining_text = remaining_text.replace(
                    borough, "", 1
                )
                break

        # -----------------------------------------
        # 2. DETECT YEAR
        # -----------------------------------------

        year_match = re.search(
            r"\b(20\d{2})\b",
            remaining_text
        )

        if year_match:
            active_year = int(year_match.group(1))

            remaining_text = re.sub(
                r"\b20\d{2}\b",
                "",
                remaining_text,
                count=1
            )

        # -----------------------------------------
        # 3. DETECT ZIP CODE
        # -----------------------------------------

        zip_match = re.search(
            r"\b\d{5}\b",
            remaining_text
        )

        searched_zip = None

        if zip_match:
            searched_zip = zip_match.group(0)

            remaining_text = re.sub(
                r"\b\d{5}\b",
                "",
                remaining_text,
                count=1
            )

        # -----------------------------------------
        # 4. VALIDATE REMAINING SEARCH TEXT
        # -----------------------------------------

        remaining_text = re.sub(
            r"[\s,;:/\-]+",
            "",
            remaining_text
        )

        if remaining_text:
            search_error = (
                "Unsupported search. Please enter a borough, "
                "year, or five-digit ZIP code."
            )

            return (
                filtered_df.iloc[0:0].copy(),
                active_borough,
                active_year,
                search_error
            )

        # -----------------------------------------
        # 5. VALIDATE YEAR
        # -----------------------------------------

        if (
            active_year is not None
            and active_year not in df["year"].values
        ):
            search_error = (
                f"No records are available for the year "
                f"{active_year}."
            )

            return (
                filtered_df.iloc[0:0].copy(),
                active_borough,
                active_year,
                search_error
            )

        # -----------------------------------------
        # 6. VALIDATE ZIP CODE
        # -----------------------------------------

        if searched_zip:
            if searched_zip not in df["zip_code"].values:
                search_error = (
                    f"No records found for ZIP code {searched_zip}."
                )

                return (
                    filtered_df.iloc[0:0].copy(),
                    active_borough,
                    active_year,
                    search_error
                )

            filtered_df = filtered_df[
                filtered_df["zip_code"] == searched_zip
            ]

    # -----------------------------------------
    # 7. APPLY BOROUGH FILTER
    # -----------------------------------------

    if active_borough:
        filtered_df = filtered_df[
            filtered_df["borough"] == active_borough
        ]

    # -----------------------------------------
    # 8. APPLY YEAR FILTER
    # -----------------------------------------

    if active_year is not None:
        filtered_df = filtered_df[
            filtered_df["year"] == int(active_year)
        ]

    return (
        filtered_df,
        active_borough,
        active_year,
        search_error
    )


def calculate_kpis(df):
    """Calculate dashboard KPI values."""

    if df.empty:
        return {
            "total_permits": 0,
            "total_collisions": 0,
            "total_zips": 0,
            "total_years": 0
        }

    return {
        "total_permits": int(df["permit_count"].sum()),
        "total_collisions": int(df["crash_count"].sum()),
        "total_zips": int(df["zip_code"].nunique()),
        "total_years": int(df["year"].nunique())
    }


def get_yearly_data(df):
    """Aggregate permits and collisions by year."""

    if df.empty:
        return pd.DataFrame(
            columns=[
                "year",
                "permit_count",
                "crash_count"
            ]
        )

    return (
        df.groupby("year", as_index=False)
        [["permit_count", "crash_count"]]
        .sum()
        .sort_values("year")
    )
