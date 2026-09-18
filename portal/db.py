from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    player_name TEXT NOT NULL,
    character_name TEXT,
    role TEXT NOT NULL CHECK(role IN ('player','dm')),
    pin_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS private_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    prompt_key TEXT NOT NULL,
    body TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'draft',
    dm_notes TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL,
    UNIQUE(user_id, prompt_key),
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS voyage_npcs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    ship_role TEXT NOT NULL DEFAULT '',
    memorable_detail TEXT NOT NULL DEFAULT '',
    why_remembered TEXT NOT NULL DEFAULT '',
    relationship TEXT NOT NULL DEFAULT '',
    party_permission INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'draft',
    dm_notes TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS private_items (
    user_id TEXT PRIMARY KEY,
    title TEXT NOT NULL DEFAULT '',
    mechanics TEXT NOT NULL DEFAULT '',
    dm_notes TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS public_party_cards (
    user_id TEXT PRIMARY KEY,
    public_text TEXT NOT NULL DEFAULT 'This player has not yet chosen what their character reveals to the party.',
    portrait_path TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    attachment_type TEXT,
    attachment_id TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS published_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL DEFAULT '',
    meta_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    published INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS dnc_state (
    singleton_id INTEGER PRIMARY KEY CHECK(singleton_id = 1),
    state_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def init_schema(self) -> None:
        with self.connect() as con:
            con.executescript(SCHEMA)
            row = con.execute("SELECT singleton_id FROM dnc_state WHERE singleton_id=1").fetchone()
            if not row:
                initial = {
                    "last_roll": None,
                    "calls": [],
                    "main_pot": 0,
                    "side_pots": [],
                    "available_bets": [],
                    "climb": 0,
                    "climb_note": "",
                }
                con.execute(
                    "INSERT INTO dnc_state(singleton_id,state_json,updated_at) VALUES(1,?,?)",
                    (json.dumps(initial), utc_now()),
                )
