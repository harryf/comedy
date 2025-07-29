#!/usr/bin/env python3
import os
import json
import argparse
from pathlib import Path


def find_transcript_files(directory):
    """Recursively find all transcript_raw_v2.json files in the given directory."""
    directory = Path(directory)
    transcript_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file == "transcript_raw_v2.json":
                transcript_files.append(Path(root) / file)
    
    return transcript_files


def detect_hallucinations(transcript_file):
    """
    Detect hallucinations in a transcript file.
    Hallucinations are defined as the same two lines of text repeating consecutively.
    """
    try:
        with open(transcript_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "transcription" not in data:
            return False
        
        transcription = data["transcription"]
        
        # Need at least 4 entries to detect a repeating pattern of 2 lines
        if len(transcription) < 4:
            return False
        
        # Check for repeating patterns of 2 consecutive lines
        for i in range(0, len(transcription) - 3):
            text1 = transcription[i]["text"].strip()
            text2 = transcription[i+1]["text"].strip()
            text3 = transcription[i+2]["text"].strip()
            text4 = transcription[i+3]["text"].strip()
            
            # Check if we have a repeating pattern of 2 lines
            if text1 == text3 and text2 == text4:
                return True
        
        return False
    
    except Exception as e:
        print(f"Error processing {transcript_file}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Detect hallucinations in Whisper transcripts")
    parser.add_argument("directory", help="Directory to search for transcript_raw_v2.json files")
    args = parser.parse_args()
    
    # Find all transcript files
    transcript_files = find_transcript_files(args.directory)
    print(f"Found {len(transcript_files)} transcript files to analyze")
    
    # Check each file for hallucinations
    hallucination_count = 0
    for file_path in transcript_files:
        if detect_hallucinations(file_path):
            print(f"{file_path}")
            hallucination_count += 1
    
    print(f"\nAnalysis complete. Found {hallucination_count} files with potential hallucinations.")


if __name__ == "__main__":
    main()
