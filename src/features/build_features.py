import pandas as pd


def split_features_target(df: pd.DataFrame, target_column: str):
    if target_column not in df.columns:
        raise ValueError(f"Target column not found: {target_column}")

    X = df.drop(columns=[target_column])
    y = df[target_column]

    return X, y
