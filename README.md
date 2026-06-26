# ML Project Template

A clean, production-ready machine learning project structure.

## Project Structure

```text
ml_project_template/
├── data/
│   ├── raw/              # Original untouched data
│   ├── interim/          # Temporary transformed data
│   ├── processed/        # Final training-ready data
│   └── external/         # Third-party data
├── notebooks/            # EDA and experiments
├── src/
│   ├── config/           # Config loading
│   ├── data/             # Data loading and preprocessing
│   ├── features/         # Feature engineering
│   ├── models/           # Model definitions
│   ├── training/         # Training pipeline
│   ├── evaluation/       # Metrics and evaluation
│   ├── inference/        # Prediction code
│   └── utils/            # Helper functions
├── configs/              # YAML config files
├── models/               # Saved model artifacts
├── reports/              # Reports and visualizations
├── tests/                # Unit tests
├── logs/                 # Runtime logs
├── requirements.txt
├── pyproject.toml
├── Dockerfile
└── Makefile
```

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

## Run Training

```bash
python -m src.training.train --config configs/config.yaml
```

## Run Inference

```bash
python -m src.inference.predict --input data/processed/sample.csv
```

## Run Tests

```bash
pytest
```

## Notes

- Keep raw data unchanged.
- Put reusable code inside `src/`.
- Use notebooks only for exploration, not production logic.
- Save trained models inside `models/`.
