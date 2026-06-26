import argparse
from pathlib import Path

import joblib
import pandas as pd


def predict(input_path: str, model_path: str = "models/model.joblib"):
    input_file = Path(input_path)
    model_file = Path(model_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found: {model_file}")

    model = joblib.load(model_file)
    df = pd.read_csv(input_file)

    predictions = model.predict(df)
    output = df.copy()
    output["prediction"] = predictions

    output_path = input_file.parent / "predictions.csv"
    output.to_csv(output_path, index=False)

    print(f"Predictions saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--model", default="models/model.joblib", help="Path to trained model")
    args = parser.parse_args()

    predict(args.input, args.model)
