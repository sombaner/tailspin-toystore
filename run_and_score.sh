#!/bin/bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

if [[ ! -d "$PROJECT_ROOT/venv" ]]; then
    bash "$PROJECT_ROOT/scripts/setup-env.sh"
fi

if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source "$PROJECT_ROOT/venv/Scripts/activate" || . "$PROJECT_ROOT/venv/Scripts/activate"
else
    source "$PROJECT_ROOT/venv/bin/activate" || . "$PROJECT_ROOT/venv/bin/activate"
fi

export PYTHONPATH="$PROJECT_ROOT/server${PYTHONPATH:+:$PYTHONPATH}"

python3 "$PROJECT_ROOT/scripts/run_and_score.py"