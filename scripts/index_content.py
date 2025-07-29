#!/usr/bin/env python3
import os
from pathlib import Path
import sys
import glob
import yaml
import json
import markdown
from dotenv import load_dotenv
load_dotenv()

from algoliasearch.search.client import SearchClientSync

ALGOLIA_APP_ID = os.getenv("ALGOLIA_APPLICATION_ID")
ALGOLIA_ADMIN_API_KEY = os.getenv("ALGOLIA_API_KEY")
ALGOLIA_INDEX_NAME = os.getenv("ALGOLIA_INDEX_NAME")

def parse_markdown_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Separate YAML front matter if present
    if content.startswith('---'):
        _, fm, rest = content.split('---', 2)
        meta = yaml.safe_load(fm)
        body = rest.strip()
    else:
        meta = {}
        body = content
    
    # Only include lines that start with > character
    blockquote_lines = []
    for line in body.split('\n'):
        if line.startswith('> '):
            # Remove the '> ' prefix
            blockquote_lines.append(line[2:])
    
    # Join only the blockquote lines
    processed_body = '\n'.join(blockquote_lines)
    
    # Convert Markdown to HTML for the full content
    html = markdown.markdown(body)
    # Only use blockquote text for the content field
    text = processed_body
    return meta, text, html

MAX_BYTES = 10000

def truncate_to_bytes(s, max_bytes=MAX_BYTES, encoding='utf-8', ellipsis='…'):
    encoded = s.encode(encoding)
    if len(encoded) <= max_bytes:
        return s
    # Reserve space for the ellipsis
    ellipsis_bytes = ellipsis.encode(encoding)
    max_content_bytes = max_bytes - len(ellipsis_bytes)
    # Truncate and decode safely
    truncated = encoded[:max_content_bytes]
    safe_str = truncated.decode(encoding, errors='ignore')
    return safe_str + ellipsis

def fit_record_to_bytes(record, html, max_bytes=MAX_BYTES):
    # Copy record except for content_html
    temp = dict(record)
    min_bytes = 500  # Don't let content_html get too small (tune as needed)
    encoding = 'utf-8'
    # Calculate size of the record with content_html empty
    temp['content'] = ''
    base_size = len(json.dumps(temp).encode(encoding))
    allowed = max_bytes - base_size
    # Start with allowed size and decrement until fits
    for b in range(allowed, min_bytes, -250):  # try in steps of 250 bytes
        candidate = truncate_to_bytes(html, max_bytes=b)
        record['content'] = candidate
        total_size = len(json.dumps(record).encode(encoding))
        if total_size <= max_bytes:
            return record
    # As last resort, brutally truncate
    record['content'] = truncate_to_bytes(html, max_bytes=min_bytes)
    if len(json.dumps(record).encode(encoding)) <= max_bytes:
        return record
    raise ValueError('Record cannot fit size limit even after heavy truncation')

def record_exists(client, index_name, object_id):
    try:
        client.get_object(index_name, object_id)
        return True
    except Exception as e:
        # Algolia raises an exception if not found
        return False

def index_markdown_files(directory):
    client = SearchClientSync(ALGOLIA_APP_ID, ALGOLIA_ADMIN_API_KEY)

    for filepath in glob.glob(os.path.join(directory, '*.md')):
        object_id = Path(os.path.basename(filepath)).stem
        if record_exists(client, ALGOLIA_INDEX_NAME, object_id):
            print(f"Skipping (already exists): {filepath}")
            continue
        
        meta, text, html = parse_markdown_file(filepath)
        record = dict(meta) if meta else {}
        record['objectID'] = object_id
        record['filepath'] = filepath
        record = fit_record_to_bytes(record, text, max_bytes=MAX_BYTES)
        client.save_object(ALGOLIA_INDEX_NAME,
            body=record
        )
        print(f"Prepared: {filepath}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: index_content.py <directory>")
        sys.exit(1)
    index_markdown_files(sys.argv[1])

