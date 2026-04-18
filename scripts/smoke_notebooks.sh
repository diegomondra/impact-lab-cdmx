#!/usr/bin/env bash
# Cold-run every Marimo notebook headless, verify HTTP 200, stop it, report.
# Owned by Agent 2 (integration watch). Re-run on every ~20-min tick.
#
# Usage:  bash scripts/smoke_notebooks.sh
#
# Exit code: 0 if every notebook boots AND serves HTTP 200; 1 otherwise.

set -uo pipefail
cd "$(dirname "$0")/.."

# Find uv even when the shell PATH doesn't carry it (common right after
# `curl | sh` install — installer drops uv in ~/.local/bin but the current
# shell won't see it until rc is re-sourced).
if ! command -v uv >/dev/null 2>&1; then
  for _p in "$HOME/.local/bin" /opt/homebrew/bin /usr/local/bin "$HOME/.cargo/bin"; do
    if [[ -x "$_p/uv" ]]; then
      export PATH="$_p:$PATH"
      break
    fi
  done
fi
if ! command -v uv >/dev/null 2>&1; then
  echo "FATAL: uv not found on PATH or in ~/.local/bin, /opt/homebrew/bin,"
  echo "       /usr/local/bin, ~/.cargo/bin. Install with:"
  echo "           curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 2
fi

PORT_BASE=27100
LOGDIR=$(mktemp -d -t marimo-smoke)
BOOT_TIMEOUT=25  # seconds to wait per notebook before declaring dead
OVERALL=0

notebooks=(
  notebooks/tus_100_pesos.py
  notebooks/budget_dashboard.py
  notebooks/obra_map.py
  # notebooks/explore.py  — parked 2026-04-18: pre-existing marimo ≥0.8
  # reactivity violation (duplicate `fig` var across cells). Not part of
  # the pitch surface. See HANDOFFS.md "explore.py parked".
)

echo "=== marimo smoke @ $(date +%H:%M:%S) ==="
echo "uv:     $(uv --version 2>/dev/null || echo 'MISSING')"
echo "marimo: $(uv run --quiet marimo --version 2>/dev/null || echo 'MISSING')"
echo "logs:   $LOGDIR"
echo ""

cleanup() {
  # kill anything we left behind
  [[ -n "${PID:-}" ]] && kill "$PID" 2>/dev/null
  wait 2>/dev/null || true
}
trap cleanup EXIT

for i in "${!notebooks[@]}"; do
  nb="${notebooks[$i]}"
  port=$((PORT_BASE + i))
  log="$LOGDIR/$(basename "$nb" .py).log"
  status="FAIL"
  http_ok=0

  if [[ ! -f "$nb" ]]; then
    printf "  [%2d/%d] SKIP   %-32s (not yet created)\n" "$((i+1))" "${#notebooks[@]}" "$nb"
    continue
  fi

  printf "  [%2d/%d] boot   %-32s :%d " "$((i+1))" "${#notebooks[@]}" "$nb" "$port"
  uv run --quiet marimo run "$nb" --headless --host 127.0.0.1 --port "$port" --no-token \
    > "$log" 2>&1 &
  PID=$!

  # poll for HTTP 200
  for _ in $(seq 1 "$BOOT_TIMEOUT"); do
    if ! kill -0 "$PID" 2>/dev/null; then
      break  # process died
    fi
    if curl -sf -o /dev/null --max-time 2 "http://127.0.0.1:$port/"; then
      http_ok=1
      status="OK"
      break
    fi
    sleep 1
  done

  # final HTTP verdict
  if [[ $http_ok -eq 1 ]]; then
    printf "→ HTTP 200 "
  else
    printf "→ NO RESPONSE "
    OVERALL=1
  fi

  # check logs for python-side errors (ignore the loader's intentional fixture warning)
  if grep -viE 'WARNING: load_(budget|income|source).*fixture' "$log" 2>/dev/null \
     | grep -qiE 'traceback|importerror|modulenotfounderror|syntaxerror|attributeerror|nameerror|typeerror|keyerror|valueerror'; then
    printf "[errors] "
    status="FAIL"
    OVERALL=1
  fi

  # fixture usage detection — expected until Agent 1 emits parquets, but worth surfacing
  if grep -q 'falling back to inline fixture' "$log" 2>/dev/null; then
    fixtures_used=$(grep -c 'falling back to inline fixture' "$log")
    printf "[fixtures×%d] " "$fixtures_used"
  fi

  echo "$status"

  # if anything went wrong, dump the relevant bits
  if [[ "$status" != "OK" ]]; then
    echo "    ---- $log (tail 30) ----"
    tail -30 "$log" 2>/dev/null | sed 's/^/    /'
    echo "    ---- errors ----"
    grep -iE 'traceback|error|exception' "$log" 2>/dev/null | head -10 | sed 's/^/    /'
    echo ""
  fi

  kill "$PID" 2>/dev/null
  wait "$PID" 2>/dev/null
  PID=
done

echo ""
if [[ $OVERALL -eq 0 ]]; then
  echo "SMOKE: all green"
  echo "  logs kept at: $LOGDIR"
else
  echo "SMOKE: FAIL"
  echo "  logs kept at: $LOGDIR"
  exit 1
fi
