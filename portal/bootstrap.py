from __future__ import annotations

from pathlib import Path
from typing import Mapping

import yaml

from .auth import hash_pin
from .repository import PortalRepository
from .db import utc_now


def load_players(config_path: str | Path) -> list[dict]:
    return yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))["players"]


def seed_users(repo: PortalRepository, players: list[dict], pins: Mapping[str, str]) -> None:
    missing = [p["user_id"] for p in players if not pins.get(p["user_id"])]
    if missing:
        raise ValueError(f"Missing PINs for: {', '.join(missing)}")
    for p in players:
        repo.create_user(
            p["user_id"], p["player_name"], p.get("character_name"), p["role"], hash_pin(str(pins[p["user_id"]]))
        )


def seed_known_private_answers(repo: PortalRepository) -> None:
    # These two answers are explicitly identified by the Player Portal seed as known private answers.
    # Seed them directly in storage without publishing them anywhere.
    now = utc_now()
    with repo.db.connect() as con:
        con.execute(
            """INSERT OR IGNORE INTO private_prompts(user_id,prompt_key,body,status,updated_at)
               VALUES('greg','why_cross_sea',?, 'draft', ?)""",
            ("Melvin is fleeing wizard-school student-loan debt.", now),
        )
        con.execute(
            """INSERT OR IGNORE INTO private_prompts(user_id,prompt_key,body,status,updated_at)
               VALUES('nick','why_cross_sea',?, 'draft', ?)""",
            ("Wiccan was ordered to travel by the First Court.", now),
        )
