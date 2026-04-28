---
applyTo: 'server/tests/test_*.py'
---

# Python Test Instructions

> For full test conventions, see `.github/copilot-instructions.md` § Testing.

## Test Structure

- Use `unittest.TestCase` subclass per resource
- Type annotate all test methods with `-> None`
- Naming: `test_<functionality>_<scenario>` (e.g., `test_get_game_not_found`)

## setUp / tearDown Pattern

```python
def setUp(self) -> None:
    self.app = create_app()
    self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    init_db(self.app, testing=True)
    self.client = self.app.test_client()
    with self.app.app_context():
        # seed TEST_DATA here

def tearDown(self) -> None:
    with self.app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
```

## Shared Test Data

- Define `TEST_DATA` as class-level constants
- Seed data in `setUp`, never rely on test ordering

## Required Coverage

- Success path (200 response, correct data shape)
- Not found (404 with error JSON)
- Invalid input (400 with error JSON)
- Empty results (200 with empty list)

## Prototype

Follow patterns in [server/tests/test_games.py](../../server/tests/test_games.py).

## Validation

Run `./scripts/run-server-tests.sh` — all tests must pass.
