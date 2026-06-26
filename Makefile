install:
	pip install -r requirements.txt

train:
	python -m src.training.train --config configs/config.yaml

predict:
	python -m src.inference.predict --input data/processed/sample.csv

test:
	pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
