#!/usr/bin/env bash
# Render Mermaid .mmd files to PNG.
# Requires: npm install -g @mermaid-js/mermaid-cli
#
# Diagrams are organized by module under scripts/diagrams/<module>/.
# Each subdirectory name must match a module in modules/<module>/.
# The rendered PNG is placed in modules/<module>/images/.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIAGRAMS_DIR="$SCRIPT_DIR/diagrams"

if ! command -v mmdc &>/dev/null; then
  echo "mmdc not found. Install it with: npm install -g @mermaid-js/mermaid-cli" >&2
  exit 1
fi

count=0
for module_dir in "$DIAGRAMS_DIR"/*/; do
  [ -d "$module_dir" ] || continue
  module=$(basename "$module_dir")
  images_dir="$REPO_ROOT/modules/$module/images"

  if [ ! -d "$REPO_ROOT/modules/$module" ]; then
    echo "WARNING: No module 'modules/$module/' found, skipping $module_dir" >&2
    continue
  fi

  mkdir -p "$images_dir"

  for mmd in "$module_dir"*.mmd; do
    [ -f "$mmd" ] || continue
    name=$(basename "$mmd" .mmd)
    echo "Rendering $module/$name.mmd -> modules/$module/images/$name.png"
    mmdc -i "$mmd" -o "$images_dir/$name.png" -e png
    count=$((count + 1))
  done
done

if [ "$count" -eq 0 ]; then
  echo "No .mmd files found. Add diagrams under scripts/diagrams/<module>/."
else
  echo "Done. Rendered $count diagram(s)."
fi
