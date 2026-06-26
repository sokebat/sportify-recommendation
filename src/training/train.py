import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from src.config.config_loader import load_config
from src.data.load_data import load_csv
from src.data.preprocess import basic_preprocess
from src.features.build_features import split_features_target
from src.models.model_factory import create_model
from src.evaluation.metrics import classification_metrics
from src.utils.logger import get_logger


def train(config_path: str):
    config = load_config(config_path)
    logger = get_logger(__name__, config["logging"]["log_file"])

    logger.info("Loading data...")
    df = load_csv(config["data"]["raw_path"])

    logger.info("Preprocessing data...")
    df = basic_preprocess(df)

    target_column = config["data"]["target_column"]
    X, y = split_features_target(df, target_column)

    categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric_cols = X.select_dtypes(exclude=["object", "category"]).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("num", "passthrough", numeric_cols),
        ]
    )

    model = create_model(
        model_type=config["model"]["type"],
        params=config["model"]["params"],
        task="classification",
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config["data"]["test_size"],
        random_state=config["project"]["random_state"],
    )

    logger.info("Training model...")
    pipeline.fit(X_train, y_train)

    logger.info("Evaluating model...")
    predictions = pipeline.predict(X_test)
    metrics = classification_metrics(y_test, predictions)

    logger.info(f"Metrics: {metrics}")

    model_output_path = Path(config["training"]["model_output_path"])
    model_output_path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(pipeline, model_output_path)
    logger.info(f"Model saved to {model_output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to config YAML file")
    args = parser.parse_args()

    train(args.config)
