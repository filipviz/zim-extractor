import sys
import os

import torch
import faiss
from libzim.reader import Archive
from trafilatura import extract
from trafilatura.deduplication import Simhash

from xmlproc import process_xml_content
from embedding import embed_chunks
from db import setup_db

"""
TODO:
- Add sqlite-vss (or another vector store - faiss has drawbacks).
- Figure out huggingface dataset format for text/embedding dataset.
- (Eventually) bloom filter dedup?
"""

# Parse arguments and get the zim file(s) to be processed.
if len(sys.argv) != 2:
    print("Usage: python3 main.py <zim-folder-or-file>")
    sys.exit(1)

zim_path = sys.argv[1]
zim_files = []

if os.path.isfile(zim_path):
    if zim_path.endswith(".zim"):
        zim_files.append(zim_path)
else:
    for root, dirs, files in os.walk(zim_path):
        for file in files:
            if file.endswith(".zim"):
                zim_files.append(os.path.join(root, file))

if not zim_files:
    print("No .zim files found.")
    sys.exit(1)
    
# Set up the sqlite3 connection
con = setup_db()

# Main processing loop. For each zim file...
for zim_file in zim_files:
    print(f"Processing {zim_file}...")
    archive = Archive(zim_file)
    
    # Get the title
    try:
        archive_title = archive.get_metadata('Title').decode('utf-8')
    except KeyError:
        pass
    
    cur = con.cursor()
    cur.execute(
        "INSERT INTO archives (title, filepath) VALUES (?, ?)",
        [archive_title, zim_file]
    )
    archive_id = cur.lastrowid
    
    # and for each entry in that file...
    for entry_id in range(archive.all_entry_count):
        try:
            entry = archive._get_entry_by_id(entry_id)
            item = entry.get_item()

            # Skip non-HTML content.
            if item.mimetype != "text/html":
                # print(f"Skipping {item.title} ({item.mimetype})")
                continue
            
            # Decode the content.
            try:
                content = bytes(item.content).decode("UTF-8")
            except UnicodeDecodeError as e:
                print(f"Failed to decode {archive.filename} - {item.title}: {e}")
                continue
            
            # Extract the contents.
            result = extract(
                content,
                favor_precision=True,
                output_format="xml",
                deduplicate=True,
            )
            chunks = process_xml_content(result, archive_title)
            embeddings = embed_chunks(chunks)
            
            cur.executemany(
                "INSERT INTO chunks (archive_id, chunk_text) VALUES (?, ?)",
                [(cur.lastrowid, chunk) for chunk, embedding in zip(chunks, embeddings)]
            )
            con.commit()
            
        except KeyError:
            print(f"Entry {entry_id} could not be found or accessed.")
            sys.exit(1)
        except Exception as e:
            print(f"A {type(e).__name__} occurred while processing entry {entry_id}: {e}")
            con.rollback()
            continue
