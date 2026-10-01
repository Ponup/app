# Contributing to Ponup

Thanks for contributing to Ponup. This guide covers the local development
workflow and the checks expected before opening a pull request.

## Getting started

Prerequisites:

- Docker and Docker Compose
- Git

Clone the repository, then start the full development stack:

```bash
make dev
```

The web app is available at <http://localhost:3000>, and the API documentation
is at <http://localhost:8000/docs>. See the [README](README.md) for optional
environment configuration and MCP connection details.

The backend is Python 3.12 with FastAPI, SQLAlchemy, and `uv`. The frontend is
React, TypeScript, Vite, and `pnpm`. Compose installs and runs the required
dependencies, so local Python and Node installations are not required for the
standard workflow.

## Development workflow

Use the Makefile targets for common tasks:

```bash
make dev       # start the Docker Compose stack
make down      # stop the stack
make migrate   # apply database migrations
make seed      # create demo data
make test      # run backend and frontend tests
make lint      # run Ruff and ESLint
```

When changing the database schema, include the required Alembic migration and
verify it with `make migrate` against a local development database.

## Tests and style

Add or update tests for changed behavior. Backend tests live in
`backend/tests`, and frontend tests live in `frontend/tests`.

Before submitting a pull request, run:

```bash
make lint
make test
```

Keep backend Python compatible with Python 3.12. Ruff enforces a 100-character
line length. Follow the existing TypeScript, React, and ESLint patterns in the
frontend.

## Pull requests

Keep pull requests focused and describe:

- What changed and why.
- How the change was tested.
- Any migration, configuration, or deployment considerations.

Do not include secrets, local `.env` files, or generated build artifacts.

## Changelog

Update [CHANGELOG.md](CHANGELOG.md) for every user-visible change. Add an entry
under the `Unreleased` heading using a Keep a Changelog category: `Added`,
`Changed`, `Deprecated`, `Removed`, `Fixed`, or `Security`.

For releases, move unreleased entries into a dated semantic-version heading and
update the comparison links.
