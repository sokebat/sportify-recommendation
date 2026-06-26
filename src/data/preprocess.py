import pandas as pd


def basic_preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Simple numeric missing value handling
    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    # Simple categorical missing value handling
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in categorical_cols:
        df[col] = df[col].fillna("Unknown")

    return df
