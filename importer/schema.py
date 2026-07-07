import sqlite3
from pathlib import Path

class DatabaseClient(sqlite3.Connection):
    def __init__(self, db_path: Path):
        super().__init__(database=db_path)

        self.row_factory = sqlite3.Row
        self.execute("PRAGMA foreign_keys = ON;")

    def create_title_table(self):
        self.execute("""
            CREATE TABLE title (
                id          INTEGER NOT NULL UNIQUE,
                name        TEXT NOT NULL,
                synopsis    TEXT NOT NULL
            );
        """)

    def create_artist_table(self):
        self.execute("""
            CREATE TABLE artist (
                id          INTEGER NOT NULL UNIQUE,
                name        TEXT NOT NULL,
                profile     TEXT
            );
        """)

    def create_title_artist_table(self):
        self.execute("""
            CREATE TABLE title_artist (
                title_id    INTEGER NOT NULL,
                artist_id   INTEGER NOT NULL,
                role        TEXT NOT NULL,
                PRIMARY KEY (title_id, artist_id),
                FOREIGN KEY (title_id) REFERENCES title (id) ON DELETE CASCADE,
                FOREIGN KEY (artist_id) REFERENCES artist (id) ON DELETE CASCADE
            );
        """)

    def create_subtitle_table(self):
        self.execute("""
            CREATE TABLE subtitle (
                title_id    INTEGER NOT NULL,
                id          INTEGER NOT NULL,   -- dense
                date        INTEGER NOT NULL,
                image_cnt   INTEGER NOT NULL,
                name        TEXT NOT NULL,
                comment     TEXT,
                PRIMARY KEY (title_id, id),
                FOREIGN KEY (title_id) REFERENCES title (id) ON DELETE CASCADE
            );
        """)