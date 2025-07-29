#!/usr/bin/env zsh
set -euo pipefail

ROOT="/Users/harry/Code/comedy/archive/out"

for dir in "$ROOT"/*; do
  [[ -d "$dir" ]] || continue

  # Find .mp3 or .m4a not matching 'segment_???.m4a'
  audio_file=""
  for ext in mp3 m4a; do
    found=("${dir}"/*.$ext(Nom))
    for f in $found; do
      [[ "$f" =~ segment_[0-9][0-9][0-9]\.m4a ]] && continue
      audio_file="$f"
      break
    done
    [[ -n "$audio_file" ]] && break
  done

  # No audio file found, skip
  [[ -n "$audio_file" ]] || { echo "No suitable audio file found in $dir"; continue; }

  transcript_file="$dir/transcript_raw_v2.json"
  echo "Transcribing $audio_file → $transcript_file"
  retranscribe "$audio_file" "$transcript_file"
done

