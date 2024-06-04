import sys
import os
import re
from libzim.reader import Archive
from trafilatura import extract

# Parse arguments and get the zim file(s).
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

# Main processing loop.
# For each zim file...
for zim_file in zim_files:
    print(f"Processing {zim_file}...")
    arc = Archive(zim_file)
    
    # and each entry in that file...
    for entry_id in range(arc.all_entry_count):
        try:
            entry = arc._get_entry_by_id(entry_id)
            item = entry.get_item()

            if item.mimetype != "text/html":
                print(f"Skipping {item.title} ({item.mimetype})")
                continue
            
            content = bytes(item.content).decode("UTF-8")
            
            # Extract the contents.
            result = extract(content, favor_precision=True)
            
            # Split by sentence
            sentences = re.split(r'(?<=[.?!])\s+', result)
            print(f"Found {len(sentences)} sentences for {item.title}")
        except KeyError:
            print(f"Entry {entry_id} could not be found or accessed.")
            sys.exit(1)
        except Exception as e:
            print(f"A {type(e).__name__} occurred while processing entry {entry_id}: {e}")
            continue
