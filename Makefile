.PHONY: run migrate test lint

run:
	python -m hypergriot.app

migrate:
	alembic upgrade head

test:
	pytest -q

lint:
	ruff .
	black --check .
