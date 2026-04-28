from __future__ import annotations

import io
import os
import re
import subprocess
import sys
import trace
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_ROOT = PROJECT_ROOT / "server"
TESTS_ROOT = SERVER_ROOT / "tests"
TARGET_DIRS = (SERVER_ROOT / "models", SERVER_ROOT / "routes")
TEST_PATTERN = "test_*.py"


def ensure_server_on_path() -> None:
    server_path = str(SERVER_ROOT)
    if server_path not in sys.path:
        sys.path.insert(0, server_path)


def discover_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    return loader.discover(
        start_dir=str(TESTS_ROOT),
        pattern=TEST_PATTERN,
        top_level_dir=str(SERVER_ROOT),
    )


def collect_executable_lines(code: types.CodeType) -> set[int]:
    lines = {line_number for _, _, line_number in code.co_lines() if line_number is not None}
    for constant in code.co_consts:
        if isinstance(constant, types.CodeType):
            lines.update(collect_executable_lines(constant))
    return lines


def iter_target_files() -> Iterable[Path]:
    for target_dir in TARGET_DIRS:
        for path in sorted(target_dir.rglob("*.py")):
            if path.name != "__init__.py":
                yield path


def run_coverage_suite() -> tuple[bool, float]:
    ensure_server_on_path()

    tracer = trace.Trace(count=True, trace=False)
    suite = discover_suite()
    output_buffer = io.StringIO()

    with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
        result = tracer.runfunc(unittest.TextTestRunner(stream=output_buffer, verbosity=1).run, suite)

    counts = tracer.results().counts
    executed_lines_by_file: dict[str, set[int]] = {}

    for (filename, line_number), hit_count in counts.items():
        if hit_count <= 0:
            continue
        executed_lines_by_file.setdefault(os.path.realpath(filename), set()).add(line_number)

    executable_lines_total = 0
    executed_lines_total = 0
    for path in iter_target_files():
        compiled = compile(path.read_text(encoding="utf-8"), str(path), "exec")
        executable_lines = collect_executable_lines(compiled)
        executed_lines = executed_lines_by_file.get(os.path.realpath(str(path)), set())

        executable_lines_total += len(executable_lines)
        executed_lines_total += len(executable_lines & executed_lines)

    coverage_percent = 0.0
    if executable_lines_total:
        coverage_percent = (executed_lines_total / executable_lines_total) * 100

    return result.wasSuccessful(), round(coverage_percent, 1)


def run_suite_once() -> tuple[bool, str]:
    environment = os.environ.copy()
    python_path = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = str(SERVER_ROOT) if not python_path else f"{SERVER_ROOT}:{python_path}"

    command = [sys.executable, "-m", "unittest", "discover", "-s", str(TESTS_ROOT), "-p", TEST_PATTERN]
    completed = subprocess.run(
        command,
        cwd=str(SERVER_ROOT),
        capture_output=True,
        text=True,
        env=environment,
    )
    return completed.returncode == 0, (completed.stdout + completed.stderr).strip()


def run_flakiness_check() -> tuple[int, int]:
    test_runs = int(os.environ.get("TEST_RUNS", "3"))
    passing_runs = 0
    failing_runs = 0

    for _ in range(test_runs):
        success, _ = run_suite_once()
        if success:
            passing_runs += 1
        else:
            failing_runs += 1

    flaky_runs = 1 if passing_runs and failing_runs else 0
    return flaky_runs, failing_runs


def run_mutation_check() -> float | None:
    mutation_command = os.environ.get("MUTATION_COMMAND", "").strip()
    if not mutation_command:
        return None

    completed = subprocess.run(
        mutation_command,
        cwd=str(PROJECT_ROOT),
        shell=True,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    mutation_output = f"{completed.stdout}\n{completed.stderr}"
    match = re.search(r"(\d+(?:\.\d+)?)", mutation_output)
    if not match or completed.returncode != 0:
        return None

    return round(float(match.group(1)), 1)


def calculate_score(coverage_percent: float, mutation_score: float | None, flaky_runs: int, failing_runs: int) -> float:
    score = coverage_percent + (mutation_score or 0.0)
    if flaky_runs:
        score -= 100.0
    if failing_runs:
        score -= 100.0
    return round(max(score, 0.0), 1)


def main() -> int:
    coverage_success, coverage_percent = run_coverage_suite()
    flaky_runs, failing_runs = run_flakiness_check()
    mutation_score = run_mutation_check()
    score = calculate_score(coverage_percent, mutation_score, flaky_runs, failing_runs)
    status = "PASS" if coverage_success and failing_runs == 0 and flaky_runs == 0 else "FAIL"
    mutation_display = f"{mutation_score:.1f}" if mutation_score is not None else "NA"

    print(
        f"STATUS={status} TEST_RUNS={os.environ.get('TEST_RUNS', '3')} "
        f"TEST_FAILURES={failing_runs} COVERAGE={coverage_percent:.1f} "
        f"MUTATION={mutation_display} FLAKY={flaky_runs} SCORE={score:.1f}"
    )
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())