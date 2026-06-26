from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


def create_model(model_type: str, params: dict | None = None, task: str = "classification"):
    params = params or {}

    if model_type == "random_forest" and task == "classification":
        return RandomForestClassifier(**params)

    if model_type == "random_forest" and task == "regression":
        return RandomForestRegressor(**params)

    raise ValueError(f"Unsupported model type/task: {model_type}/{task}")
