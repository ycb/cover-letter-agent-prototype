test:
	pytest

coverage:
	pytest --cov=agents --cov=core

lint:
	black --check .
	isort --check-only .
	flake8 .
	mypy agents/ core/ --ignore-missing-imports

format:
	black .
	isort . 