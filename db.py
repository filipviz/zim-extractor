import sqlite3

db_path = "zim-extractor.db"

def setup_db() -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS archives (
            title TEXT NOT NULL DEFAULT "",
            filepath TEXT NOT NULL DEFAULT "",
        )
    """)
    
    # TODO: vss embeddings table?
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            archive_id TEXT NOT NULL DEFAULT "",
            chunk_text TEXT NOT NULL,
            FOREIGN KEY (archive_id) REFERENCES archives(rowid)
        )
    """)

    return con

