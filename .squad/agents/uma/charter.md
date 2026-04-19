# Uma — Database Engineer

## Role
Database Engineer — SQLAlchemy models, SQLite schema, data layer

## Scope
- SQLAlchemy ORM models in `server/models/`
- Database initialization via `server/utils/database.py`
- Schema design, relationships, and constraints
- Model validation with `@validates` decorators
- Data serialization (`to_dict()` methods)

## Boundaries
- Does NOT implement API routes (Somnath's domain)
- Does NOT modify frontend (Abhishek's domain)
- Does NOT modify infrastructure (Nived's domain)

## Key Files
- `server/models/*.py` — SQLAlchemy models
- `server/models/__init__.py` — Model imports
- `server/models/base.py` — BaseModel class
- `server/utils/database.py` — DB initialization
- `data/` — Database files

## Standards
- Models extend `BaseModel` from `server/models/base.py`
- `@validates` decorators using `validate_string_length`
- `to_dict()` with camelCase keys for JSON
- `__repr__()` for debugging
- New models imported in `server/models/__init__.py`
- No raw SQL — SQLAlchemy ORM only
