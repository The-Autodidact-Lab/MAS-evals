#!/usr/bin/env bash
set -euo pipefail

# Configurable via env vars; these defaults match what you've been using
MODEL="${MODEL:-openai/gpt-5-mini}"
PROVIDER="${PROVIDER:-llama-api}"
AGENT="${AGENT:-default}"

# All ss* scenarios you want to run
SCENARIOS=(ss1 ss2 ss3 ss4 ss5 ss6 ss7 ss8 ss9 ss10 ss11 ss12)

echo "Running scenarios: ${SCENARIOS[*]}"
echo "Model: $MODEL  Provider: $PROVIDER  Agent: $AGENT"

# Temporary output directory for ARE traces/results
OUT_DIR="$(mktemp -d -t are_ss_run_XXXX)"
echo "Output dir: $OUT_DIR"

# Run all scenarios in one MultiScenario run and export results
python3 -m are.simulation.main \
  -m "$MODEL" \
  --provider "$PROVIDER" \
  -a "$AGENT" \
  --export \
  --output_dir "$OUT_DIR" \
  $(printf ' -s %s' "${SCENARIOS[@]}")

RESULT_FILE="$OUT_DIR/output.jsonl"

if [[ ! -f "$RESULT_FILE" ]]; then
  echo "ERROR: Expected results file '$RESULT_FILE' not found."
  exit 1
fi

echo
echo "=== ScenarioValidationResult Summary ==="
python3 - "$RESULT_FILE" << 'PY'
import json, sys, os

path = sys.argv[1]
print(f"Results file: {os.path.abspath(path)}\n")
print(f"{'Scenario':<10} {'Success':<7} {'Exception':<40}")
print("-" * 60)

with open(path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        rec = json.loads(line)

        # Benchmark JSONL schema: task_id + metadata
        md = rec.get("metadata", {}) or {}
        scenario_id = md.get("scenario_id") or rec.get("task_id") or "?"

        status = md.get("status")
        has_exc = md.get("has_exception")
        # Treat status == "success" and has_exception == False as success
        success = (status == "success") and not has_exc

        exc = md.get("exception_message") or md.get("exception_type") or ""
        print(f"{scenario_id:<10} {str(success):<7} {str(exc)[:40]:<40}")
PY

echo
echo "Done."