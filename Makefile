.PHONY: dev down migrate seed test lint

dev:
	docker compose up --build

down:
	docker compose down

migrate:
	docker compose run --rm api uv run alembic upgrade head

seed:
	docker compose run --rm api uv run python -m app.seed

test:
	docker compose run --rm api uv run pytest
	docker compose run --rm frontend pnpm test -- --run

lint:
	docker compose run --rm api uv run ruff check .
	docker compose run --rm frontend pnpm lint
