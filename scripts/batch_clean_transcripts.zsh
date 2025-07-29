#!/usr/bin/env zsh
set -euo pipefail

ROOT="/Users/harry/Code/comedy/archive/out"
TOOL_DIR="/Users/harry/Code/comedybot/comedy_set_analysis/transcriber/tools"
PYTHON="$HOME/Code/comedybot/.venv/bin/python"
SCRIPT="$TOOL_DIR/transcript_analyser_tool_2.py"

for dir in "$ROOT"/*; do
  [[ -d "$dir" ]] || continue

  raw="$dir/transcript_raw_v2.json"
  [[ -f "$raw" ]] || { echo "No transcript_raw_v2.json in $dir, skipping"; continue }

  # Run the tool, outputs to transcript_clean.json in the same dir
  echo "Cleaning transcript in $dir"
  "$PYTHON" "$SCRIPT" -i "$raw" -o "$dir/"
done

