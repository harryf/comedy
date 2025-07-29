#!/usr/bin/env python3
"""
deploy_audio.py

This script copies specific files from ./archive/out subdirectories to ./docs/assets/audio.
It copies all JSON files and segment_XXX.m4a audio files, but skips other audio files.
"""

import os
import shutil
import re
import sys
from pathlib import Path


def create_directory_if_not_exists(directory):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")


def is_segment_audio_file(filename):
    """Check if the file is a segment audio file (segment_XXX.m4a)."""
    return bool(re.match(r"segment_\d+\.m4a", filename))


def is_json_file(filename):
    """Check if the file is a JSON file."""
    return filename.lower().endswith('.json')


def should_copy_file(filename):
    """Determine if a file should be copied based on our criteria."""
    return is_json_file(filename) or is_segment_audio_file(filename)


def copy_files(source_dir, dest_dir):
    """
    Copy files from source_dir to dest_dir based on our criteria.
    Returns the count of copied files.
    """
    count = 0
    
    # Create the destination directory if it doesn't exist
    create_directory_if_not_exists(dest_dir)
    
    # Get all files in the source directory
    for item in os.listdir(source_dir):
        source_path = os.path.join(source_dir, item)
        
        # Skip directories
        if os.path.isdir(source_path):
            continue
        
        # Check if we should copy this file
        if should_copy_file(item):
            dest_path = os.path.join(dest_dir, item)
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            count += 1
            print(f"Copied: {item}")
    
    return count


def main():
    # Define paths
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    
    source_base_dir = project_root / "archive" / "out"
    dest_base_dir = project_root / "docs" / "assets" / "audio"
    
    # Check if source directory exists
    if not os.path.exists(source_base_dir):
        print(f"Error: Source directory does not exist: {source_base_dir}")
        sys.exit(1)
    
    # Create the destination base directory if it doesn't exist
    create_directory_if_not_exists(dest_base_dir)
    
    # Process each subdirectory in the source directory
    total_dirs = 0
    total_files = 0
    
    for item in os.listdir(source_base_dir):
        source_subdir = os.path.join(source_base_dir, item)
        
        # Skip if not a directory
        if not os.path.isdir(source_subdir):
            continue
        
        # Create corresponding destination subdirectory
        dest_subdir = os.path.join(dest_base_dir, item)
        
        # Copy files from this subdirectory
        print(f"\nProcessing directory: {item}")
        files_copied = copy_files(source_subdir, dest_subdir)
        
        if files_copied > 0:
            total_dirs += 1
            total_files += files_copied
    
    # Print summary
    print(f"\nSummary:")
    print(f"Processed {total_dirs} directories")
    print(f"Copied {total_files} files")
    print(f"Files were copied to: {dest_base_dir}")


if __name__ == "__main__":
    main()
