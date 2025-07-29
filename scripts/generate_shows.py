#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path

# Define paths
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIO_DIR = BASE_DIR / "docs" / "assets" / "audio"
SHOWS_DIR = BASE_DIR / "docs" / "_shows"

def get_date_from_dirname(dirname):
    """Extract date from directory name format YYYYMMDD_..."""
    match = re.match(r"^(\d{8})_", dirname)
    if match:
        return match.group(1)
    return "00000000"  # Default for sorting if pattern doesn't match

def main():
    # Create shows directory if it doesn't exist
    SHOWS_DIR.mkdir(exist_ok=True)
    
    # Get all subdirectories in the audio directory
    audio_dirs = [d for d in os.listdir(AUDIO_DIR) if os.path.isdir(AUDIO_DIR / d) and re.match(r"^\d{8}_", d)]
    
    # Sort directories by date (oldest first)
    audio_dirs.sort(key=get_date_from_dirname)
    
    print(f"Found {len(audio_dirs)} audio directories to process")
    
    for dir_name in audio_dirs:
        dir_path = AUDIO_DIR / dir_name
        metadata_path = dir_path / "metadata.json"
        transcript_path = dir_path / "transcript_clean.json"
        
        # Skip if metadata.json doesn't exist
        if not metadata_path.exists():
            print(f"Warning: No metadata.json found in {dir_name}, skipping...")
            continue
            
        # Skip if transcript_clean.json doesn't exist
        if not transcript_path.exists():
            print(f"Warning: No transcript_clean.json found in {dir_name}, skipping...")
            continue
        
        try:
            # Read metadata.json
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Read transcript_clean.json
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript = json.load(f)
            
            # Extract required fields with fallbacks
            audio_file = metadata.get("audio_file", "Unknown")
            comedian = metadata.get("comedian", "Unknown")
            name_of_show = metadata.get("name_of_show", "Unknown Show")
            date_of_show = metadata.get("date_of_show", "Unknown Date")
            name_of_venue = metadata.get("name_of_venue", "Unknown Venue")
            link_to_venue = metadata.get("link_to_venue_on_google_maps", "")
            notes = metadata.get("notes", "")
            length_of_set = metadata.get("length_of_set", 0)
            laughs_per_minute = metadata.get("laughs_per_minute", 0)
            
            # Escape notes for YAML header using literal block style
            if notes and notes.strip():
                # Format as a YAML literal block with proper indentation
                escaped_notes = '|\n  ' + notes.replace('\n', '\n  ')
            else:
                escaped_notes = '""'
                
            # Create markdown content - header
            markdown_content = f"""---
layout: show
type: show
player_id: {dir_name}
audio_file: {audio_file}
comedian: {comedian}
name_of_show: {name_of_show}
date_of_show: {date_of_show}
name_of_venue: {name_of_venue}
link_to_venue_on_google_maps: {link_to_venue}
length_of_set: {length_of_set}
laughs_per_minute: {laughs_per_minute}
notes: {escaped_notes}
---

"""
            
            # Skip adding Notes section in the body since we're now including it in the header
            # The show.html layout will handle displaying it
            
            # Add Transcript section
            # markdown_content += "\n## Transcript\n\n"
            markdown_content += "\n<h2><i class=\"fas fa-file-alt\"></i> Transcript</h2>\n\n"
            
            
            # Add transcript as blockquotes
            for segment in transcript:
                if segment.get("type") == "text" and "text" in segment:
                    markdown_content += f"> {segment['text']}\n>\n"
            
            # Remove the last empty blockquote line
            if markdown_content.endswith(">\n"):
                markdown_content = markdown_content[:-2]
            
            # Write to markdown file
            output_path = SHOWS_DIR / f"{dir_name}.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"Generated show file: {output_path}")
            
        except Exception as e:
            print(f"Error processing {dir_name}: {e}")
    
    print("Show generation complete!")

if __name__ == "__main__":
    main()
