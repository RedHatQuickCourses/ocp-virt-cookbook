#!/usr/bin/env bash
# Render Mermaid .mmd files to PNG.
# Requires: npm install -g @mermaid-js/mermaid-cli

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIAGRAMS_DIR="$SCRIPT_DIR/diagrams"
IMAGES_DIR="$REPO_ROOT/modules/getting-started/images"

if ! command -v mmdc &>/dev/null; then
  echo "mmdc not found. Install it with: npm install -g @mermaid-js/mermaid-cli" >&2
  exit 1
fi

for mmd in "$DIAGRAMS_DIR"/*.mmd; do
  [ -f "$mmd" ] || continue
  name=$(basename "$mmd" .mmd)
  echo "Rendering $name.mmd -> $IMAGES_DIR/$name.png"
  mmdc -i "$mmd" -o "$IMAGES_DIR/$name.png" -e png
done

echo "Done."
