# Test Improvement Plan

## Objective

Improve backend test quality for the Tailspin Toys Flask API with higher line coverage, stronger branch protection, zero flakiness, and more meaningful assertions.

## AutoResearch Mapping

- Human layer: this file defines goals, constraints, and priorities.
- Agent layer: the coding agent may edit only files under `server/tests/` during an improvement loop.
- Infrastructure layer: `run_and_score.sh` and `scripts/run_and_score.py` are immutable during an improvement loop and define how tests are measured.

## Mutable Scope

- `server/tests/test_*.py`

## Immutable Scope

- `server/models/`
- `server/routes/`
- `client/`
- `run_and_score.sh`
- `scripts/run_and_score.py`
- test runner or framework configuration

## Constraints

- No production code changes.
- No new dependencies.
- No edits to the scoring harness or metric definitions during a test-improvement run.
- Prefer additions or refinements that strengthen behavioral guarantees instead of snapshot-style assertions.
- Avoid duplicate coverage where an existing test already proves the same behavior.

## Quality Rules

- Assert outcomes that would fail if the implementation regressed.
- Cover edge cases and branch behavior before adding happy-path duplicates.
- Keep tests deterministic: no time-based waits, random inputs, or order-sensitive assertions without an explicit contract.
- When a failure reveals a product bug, stop and record it instead of weakening the test.

## Current Pilot Area

- Primary target: `server/routes/games.py`
- Secondary target: `server/models/game.py`, `server/models/publisher.py`, `server/models/category.py`
- Initial gaps already addressed: whitespace-trimmed query parameters and model serialization/count behavior.

## Baseline

- Run `./run_and_score.sh` before and after each batch.
- Current baseline: `STATUS=PASS TEST_RUNS=3 TEST_FAILURES=0 COVERAGE=40.6 MUTATION=NA FLAKY=0 SCORE=40.6`

## Priorities

1. Fix any flaky tests before chasing additional coverage.
2. Expand route-level edge cases for filtering, sorting, empty states, and not-found behavior.
3. Expand model serialization and validation edge cases that protect API contracts.
4. Only pursue mutation scoring after a stable coverage baseline exists and a supported mutation command is available through `MUTATION_COMMAND`.

## Loop

1. Read this file and the target tests in full.
2. Make one small test-only change.
3. Run `./run_and_score.sh`.
4. Keep the change only if metrics improve without introducing flakiness.
5. Record useful guidance updates here before starting the next iteration.