#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path
from datetime import datetime
import time

# Define paths
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BITS_DIR = BASE_DIR / "docs" / "_bits"
COMEDYBOT_DIR = Path.home() / ".comedybot"
BIT_REGISTRY_PATH = COMEDYBOT_DIR / "bit_registry.json"
CANONICAL_BITS_PATH = COMEDYBOT_DIR / "canonical_bits.json"
BITS_SOURCE_DIR = COMEDYBOT_DIR / "bits"

def format_date(date_str):
    """Format date as '%-d %B, %Y'"""
    # Expected format: "14 Jun 2018, 20:00"
    try:
        # Parse the date string
        date_obj = datetime.strptime(date_str.split(',')[0], "%d %b %Y")
        # Format as required
        return date_obj.strftime("%-d %B, %Y")
    except Exception as e:
        print(f"Error formatting date '{date_str}': {e}")
        return date_str

def format_duration(start, end):
    """Format duration as 'Xm Ys'"""
    duration_seconds = end - start
    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)
    return f"{minutes}m {seconds}s"

def yaml_safe_string(value):
    """Format a string to be safely used in YAML front matter"""
    if not isinstance(value, str):
        return value
        
    # Check if the string contains any special characters that would need quoting
    if any(c in value for c in ":\"'{}[]!@#$%^&*()\n\t") or 'ü' in value or 'ö' in value or 'ä' in value:
        # Escape single quotes by doubling them
        escaped_value = value.replace("'", "''")
        # Wrap in single quotes
        return f"'{escaped_value}'"
    return value

def get_canonical_name(bit_id, canonical_bits):
    """Find the canonical name for a bit_id"""
    for canonical_name, bit_ids in canonical_bits.items():
        if bit_id in bit_ids:
            return canonical_name
    return "Uncategorized"  # Fallback if not found

def main():
    # Create bits directory if it doesn't exist
    BITS_DIR.mkdir(exist_ok=True)
    
    # Read bit registry
    try:
        with open(BIT_REGISTRY_PATH, 'r', encoding='utf-8') as f:
            bit_registry = json.load(f)
        print(f"Loaded {len(bit_registry)} bits from registry")
    except Exception as e:
        print(f"Error reading bit registry: {e}")
        return
    
    # Read canonical bits mapping
    try:
        with open(CANONICAL_BITS_PATH, 'r', encoding='utf-8') as f:
            canonical_bits = json.load(f)
        print(f"Loaded {len(canonical_bits)} canonical bit categories")
    except Exception as e:
        print(f"Error reading canonical bits: {e}")
        return
    
    # Process each bit
    for bit_id, timestamp in bit_registry.items():
        bit_file_path = BITS_SOURCE_DIR / f"{bit_id}.json"
        
        # Skip if bit file doesn't exist
        if not bit_file_path.exists():
            print(f"Warning: Bit file not found for {bit_id}, skipping...")
            continue
        
        try:
            # Read bit data
            with open(bit_file_path, 'r', encoding='utf-8') as f:
                bit_data = json.load(f)
            
            # Get canonical name for this bit
            canonical_name = get_canonical_name(bit_id, canonical_bits)
            
            # Extract required fields
            bit_info = bit_data.get("bit_info", {})
            show_info = bit_data.get("show_info", {})
            transcript = bit_data.get("transcript", {})

            show_id = show_info.get("show_identifier", "Unknown Show")
            
            # Calculate duration
            start = bit_info.get("start", 0)
            end = bit_info.get("end", 0)
            duration = format_duration(start, end)
            
            # Format date
            date_of_show = format_date(show_info.get("date_of_show", "Unknown Date"))
            
            # Get joke types and themes
            joke_types = bit_info.get("joke_types", [])
            themes = bit_info.get("themes", [])
            
            # Collect all bits with the same canonical name
            related_bits = []
            if canonical_name in canonical_bits:
                for related_bit_id in canonical_bits[canonical_name]:
                    related_bit_path = BITS_SOURCE_DIR / f"{related_bit_id}.json"
                    if related_bit_path.exists():
                        with open(related_bit_path, 'r', encoding='utf-8') as f:
                            related_bit_data = json.load(f)
                            related_show_info = related_bit_data.get("show_info", {})
                            related_bits.append({
                                "bit_id": related_bit_id,
                                "date": related_show_info.get("date_of_show", "Unknown"),
                                "venue": related_show_info.get("name_of_venue", "Unknown Venue")
                            })
            
            # Format transcript lines for front matter
            transcript_lines = transcript.get("lines", [])
            
            # Create markdown content
            markdown_content = f"""---
layout: bit
bit_id: {bit_id}
show_id: {show_id}
canonical_name: {yaml_safe_string(canonical_name)}
bit_name: {yaml_safe_string(bit_info.get("title", "Untitled"))}
comedian: {yaml_safe_string(show_info.get("comedian", "Unknown"))}
date_of_show: {yaml_safe_string(date_of_show)}
name_of_venue: {yaml_safe_string(show_info.get("name_of_venue", "Unknown Venue"))}
link_to_venue_on_google_maps: {yaml_safe_string(show_info.get("link_to_venue_on_google_maps", ""))}
notes: {yaml_safe_string(show_info.get("notes", ""))}
duration: {duration}
lpm: {bit_info.get("lpm", 0)}
start_seconds: {bit_info.get("start", 0)}
joke_types:
"""
            
            # Add joke types
            for joke_type in joke_types:
                markdown_content += f"  - {joke_type}\n"
            
            # Add themes
            markdown_content += "themes:\n"
            for theme in themes:
                markdown_content += f"  - {theme}\n"
            
            # Add related bits
            markdown_content += "bits:\n"
            for related_bit in related_bits:
                related_date = format_date(related_bit["date"])
                markdown_content += f"  - bit_id: {related_bit['bit_id']}\n"
                markdown_content += f"    date_of_show: {yaml_safe_string(related_date)}\n"
                markdown_content += f"    name_of_venue: {yaml_safe_string(related_bit['venue'])}\n"
            
            # Add transcript data in the format expected by the layout
            markdown_content += "\nlines:\n"
            for line in transcript_lines:
                text = line.get('text', '').replace("'", "''")
                markdown_content += f"  - text: '{text}'\n"
            
            # Close the front matter
            markdown_content += "\n---\n"
            
            # Add some content after the front matter
            markdown_content += f"\n# {canonical_name}\n\n"
            markdown_content += f"Performance at {show_info.get('name_of_venue', 'Unknown Venue')} on {date_of_show}\n"
            
            # Write to markdown file
            output_path = BITS_DIR / f"{bit_id}.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"Generated bit file: {output_path}")
            
        except Exception as e:
            print(f"Error processing bit {bit_id}: {e}")
    
    print("Bit generation complete!")

if __name__ == "__main__":
    main()
