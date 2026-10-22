#!/bin/bash
# Start Minutes on macOS or Linux (double-click Start.command on a Mac).
cd "$(dirname "$0")"
UV=$(command -v uv || true)
for candidate in "$HOME/.local/bin/uv" "$HOME/.cargo/bin/uv" /opt/homebrew/bin/uv /usr/local/bin/uv; do
  if [ -z "$UV" ] && [ -x "$candidate" ]; then UV="$candidate"; fi
done
if [ -z "$UV" ]; then
  echo "Minutes needs uv. Install it with:  curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi
exec "$UV" run --quiet python -m minutes "$@"
