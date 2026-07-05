install:
	pip install -r requirements.txt

api:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
