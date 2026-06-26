import pandas as pd

from src.data.preprocess import basic_preprocess


def test_basic_preprocess_removes_duplicates_and_fills_missing_values():
    df = pd.DataFrame({
        "age": [20, 20, None],
        "city": ["Kathmandu", "Kathmandu", None],
        "target": [1, 1, 0],
    })

    result = basic_preprocess(df)

    assert result.duplicated().sum() == 0
    assert result.isnull().sum().sum() == 0
