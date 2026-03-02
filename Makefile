.PHONY: test lint format type

test:
	pytest -q

lint:
	ruff check .

format:
	ruff format .

type:
	mypy src
