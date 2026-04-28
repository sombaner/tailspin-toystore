---
applyTo: 'server/routes/*.py'
---

# Flask Endpoint Instructions

> For full coding standards (type hints, error responses, docstrings), see `.github/copilot-instructions.md`.

## Blueprint Pattern

- Each resource gets its own blueprint in `server/routes/`
- Register blueprint in `server/app.py`
- URL prefix: `/api/<resource>` (e.g., `/api/games`, `/api/reviews`)

## Centralized Queries

- Create a reusable base query function (see `get_games_base_query()` in `server/routes/games.py`)
- Use `db.session.query(Model).join(...)` with explicit joins
- Use `isouter=True` for optional relationships

## Response Conventions

- Success: return `jsonify(data)` or `jsonify([item.to_dict() for item in items])`
- Error: return `jsonify({"error": "<message>"}), <status_code>`
- All JSON keys use camelCase

## Companion Files

When creating a new endpoint, also update:
- `server/models/` — new model if needed (extend `BaseModel`)
- `server/models/__init__.py` — import new model
- `server/app.py` — register new blueprint
- `server/tests/test_<resource>.py` — tests (see [test instructions](./python-tests.instructions.md))

## Prototype Files

- [Endpoint prototype](../../server/routes/games.py)
- [Tests prototype](../../server/tests/test_games.py)

## Validation

Run `./scripts/run-server-tests.sh` — all tests must pass before completion.
