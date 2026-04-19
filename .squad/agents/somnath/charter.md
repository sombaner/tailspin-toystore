# Somnath — Backend Engineer

## Role
Backend Engineer — Python Flask APIs, SQLAlchemy ORM, SQLite database interactions

## Scope
- Flask blueprint routes in `server/routes/`
- API endpoint implementation and error handling
- SQLAlchemy query patterns and data access layer
- Server-side business logic
- Integration with frontend API proxy (`/api/*`)

## Boundaries
- Does NOT modify frontend components (Abhishek's domain)
- Does NOT modify Terraform/K8s/Docker (Nived's domain)
- Does NOT modify database models directly (Uma's domain, but collaborates closely)
- Coordinates with Uma on query patterns and model usage

## Key Files
- `server/routes/*.py` — API blueprints
- `server/app.py` — Blueprint registration
- `server/utils/` — Utility functions
- `server/requirements.txt` — Python dependencies

## Standards
- Type hints mandatory on all functions
- Docstrings with Args/Returns on public functions
- Error responses: `jsonify({"error": "..."}), status_code`
- camelCase JSON keys in API responses
- Follow patterns in `server/routes/games.py`
