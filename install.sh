#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
WHEEL_DIR="${SCRIPT_DIR}/wheels"
VENV_DIR="${SCRIPT_DIR}/.venv"
BIN_DIR="${SCRIPT_DIR}/bin"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required" >&2
  exit 1
fi

WHEEL=$(find "$WHEEL_DIR" -maxdepth 1 -name 'spira_trust-*.whl' -type f | sort | tail -n 1)
if [ -z "${WHEEL}" ]; then
  echo "No spira_trust wheel found under ${WHEEL_DIR}" >&2
  exit 1
fi

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --no-index "$WHEEL"
mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/spira-trust" <<'EOF'
#!/usr/bin/env sh
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "$SCRIPT_DIR/../.venv/bin/spira-trust" "$@"
EOF

cat > "$BIN_DIR/spira" <<'EOF'
#!/usr/bin/env sh
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "$SCRIPT_DIR/../.venv/bin/spira" "$@"
EOF

chmod +x "$BIN_DIR/spira-trust" "$BIN_DIR/spira"
echo "SPIRA Trust installed."
echo "Run: ${BIN_DIR}/spira-trust --help"
