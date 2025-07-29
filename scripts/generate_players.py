#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path
import shutil

# Define paths
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIO_DIR = BASE_DIR / "docs" / "assets" / "audio"
PLAYERS_DIR = BASE_DIR / "docs" / "_players"

def get_date_from_dirname(dirname):
    """Extract date from directory name format YYYYMMDD_..."""
    match = re.match(r"^(\d{8})_", dirname)
    if match:
        return match.group(1)
    return "00000000"  # Default for sorting if pattern doesn't match

def main():
    # Create players directory if it doesn't exist
    PLAYERS_DIR.mkdir(exist_ok=True)
    
    # Get all subdirectories in the audio directory
    audio_dirs = [d for d in os.listdir(AUDIO_DIR) if os.path.isdir(AUDIO_DIR / d) and re.match(r"^\d{8}_", d)]
    
    # Sort directories by date (oldest first)
    audio_dirs.sort(key=get_date_from_dirname)
    
    print(f"Found {len(audio_dirs)} audio directories to process")
    
    for dir_name in audio_dirs:
        dir_path = AUDIO_DIR / dir_name
        metadata_path = dir_path / "metadata.json"
        
        # Skip if metadata.json doesn't exist
        if not metadata_path.exists():
            print(f"Warning: No metadata.json found in {dir_name}, skipping...")
            continue
        
        try:
            # Read metadata.json
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Extract required fields
            name_of_show = metadata.get("name_of_show", "Unknown Show")
            date_of_show = metadata.get("date_of_show", "Unknown Date")
            
            # Construct title
            title = f"{name_of_show} {date_of_show}"
            
            # Create markdown content
            markdown_content = f"""---
layout: player
title: {title}
transcript_path: {dir_name}
---
"""
            
            # Write to markdown file
            output_path = PLAYERS_DIR / f"{dir_name}.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"Generated player file: {output_path}")
            
        except Exception as e:
            print(f"Error processing {dir_name}: {e}")
    
    print("Player generation complete!")

if __name__ == "__main__":
    main()
