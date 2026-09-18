from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from .auth import Viewer, verify_pin
from .db import Database, utc_now


class AccessDenied(PermissionError):
    pass


class PortalRepository:
    def __init__(self, db: Database):
        self.db = db

    def user_count(self) -> int:
        with self.db.connect() as con:
            return int(con.execute("SELECT COUNT(*) FROM users").fetchone()[0])

    def create_user(self, user_id: str, player_name: str, character_name: str | None, role: str, pin_hash: str) -> None:
        with self.db.connect() as con:
            con.execute(
                "INSERT OR REPLACE INTO users(user_id,player_name,character_name,role,pin_hash) VALUES(?,?,?,?,?)",
                (user_id, player_name, character_name, role, pin_hash),
            )
            con.execute(
                "INSERT OR IGNORE INTO public_party_cards(user_id,updated_at) VALUES(?,?)",
                (user_id, utc_now()),
            )

    def authenticate(self, user_id: str, pin: str) -> Viewer | None:
        with self.db.connect() as con:
            row = con.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not row or not verify_pin(pin, row["pin_hash"]):
            return None
        return Viewer(row["user_id"], row["player_name"], row["character_name"], row["role"])

    def list_identities(self) -> list[dict[str, Any]]:
        with self.db.connect() as con:
            rows = con.execute(
                "SELECT user_id,player_name,character_name,role FROM users ORDER BY CASE role WHEN 'player' THEN 0 ELSE 1 END, player_name"
            ).fetchall()
        return [dict(r) for r in rows]

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        with self.db.connect() as con:
            row = con.execute("SELECT user_id,player_name,character_name,role FROM users WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else None

    def list_players(self) -> list[dict[str, Any]]:
        with self.db.connect() as con:
            rows = con.execute(
                "SELECT user_id,player_name,character_name,role FROM users WHERE role='player' ORDER BY player_name"
            ).fetchall()
        return [dict(r) for r in rows]

    def _require_self_or_dm(self, viewer: Viewer, target_user_id: str) -> None:
        if not viewer.is_dm and viewer.user_id != target_user_id:
            raise AccessDenied("Private player data is restricted to that player and the DM.")

    def save_prompt(self, viewer: Viewer, prompt_key: str, body: str, *, submit: bool = False) -> None:
        if viewer.is_dm:
            raise AccessDenied("DM should review prompts rather than submit player answers.")
        status = "submitted" if submit else "draft"
        with self.db.connect() as con:
            con.execute(
                """INSERT INTO private_prompts(user_id,prompt_key,body,status,updated_at)
                   VALUES(?,?,?,?,?)
                   ON CONFLICT(user_id,prompt_key) DO UPDATE SET body=excluded.body,status=excluded.status,updated_at=excluded.updated_at""",
                (viewer.user_id, prompt_key, body, status, utc_now()),
            )

    def get_prompt(self, viewer: Viewer, target_user_id: str, prompt_key: str) -> dict[str, Any] | None:
        self._require_self_or_dm(viewer, target_user_id)
        with self.db.connect() as con:
            row = con.execute(
                "SELECT * FROM private_prompts WHERE user_id=? AND prompt_key=?", (target_user_id, prompt_key)
            ).fetchone()
        return dict(row) if row else None

    def list_prompt_reviews(self, viewer: Viewer) -> list[dict[str, Any]]:
        if not viewer.is_dm:
            raise AccessDenied("DM only")
        with self.db.connect() as con:
            rows = con.execute(
                """SELECT p.*,u.player_name,u.character_name FROM private_prompts p
                   JOIN users u ON u.user_id=p.user_id ORDER BY p.updated_at DESC"""
            ).fetchall()
        return [dict(r) for r in rows]

    def dm_review_prompt(self, viewer: Viewer, record_id: int, status: str, dm_notes: str, body: str | None = None) -> None:
        if not viewer.is_dm:
            raise AccessDenied("DM only")
        with self.db.connect() as con:
            if body is None:
                con.execute(
                    "UPDATE private_prompts SET status=?,dm_notes=?,updated_at=? WHERE id=?",
                    (status, dm_notes, utc_now(), record_id),
                )
            else:
                con.execute(
                    "UPDATE private_prompts SET body=?,status=?,dm_notes=?,updated_at=? WHERE id=?",
                    (body, status, dm_notes, utc_now(), record_id),
                )

    def save_voyage_npc(self, viewer: Viewer, data: dict[str, Any], npc_id: int | None = None, *, submit: bool = False) -> int:
        if viewer.is_dm:
            raise AccessDenied("DM should review voyage NPCs rather than create player submissions here.")
        status = "submitted" if submit else "draft"
        values = (
            data.get("name", ""), data.get("ship_role", ""), data.get("memorable_detail", ""),
            data.get("why_remembered", ""), data.get("relationship", ""), int(bool(data.get("party_permission"))),
            status, utc_now()
        )
        with self.db.connect() as con:
            if npc_id:
                row = con.execute("SELECT user_id FROM voyage_npcs WHERE id=?", (npc_id,)).fetchone()
                if not row or row["user_id"] != viewer.user_id:
                    raise AccessDenied("Cannot edit another player's voyage NPC.")
                con.execute(
                    """UPDATE voyage_npcs SET name=?,ship_role=?,memorable_detail=?,why_remembered=?,relationship=?,party_permission=?,status=?,updated_at=? WHERE id=?""",
                    values + (npc_id,),
                )
                return npc_id
            cur = con.execute(
                """INSERT INTO voyage_npcs(user_id,name,ship_role,memorable_detail,why_remembered,relationship,party_permission,status,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                (viewer.user_id,) + values,
            )
            return int(cur.lastrowid)

    def list_voyage_npcs(self, viewer: Viewer, target_user_id: str | None = None) -> list[dict[str, Any]]:
        if viewer.is_dm:
            clause, params = ("", ()) if target_user_id is None else ("WHERE v.user_id=?", (target_user_id,))
        else:
            if target_user_id and target_user_id != viewer.user_id:
                raise AccessDenied("Cannot view another player's voyage NPC drafts.")
            clause, params = "WHERE v.user_id=?", (viewer.user_id,)
        with self.db.connect() as con:
            rows = con.execute(
                f"""SELECT v.*,u.player_name,u.character_name FROM voyage_npcs v JOIN users u ON u.user_id=v.user_id
                    {clause} ORDER BY v.updated_at DESC""", params
            ).fetchall()
        return [dict(r) for r in rows]

    def dm_review_voyage_npc(self, viewer: Viewer, npc_id: int, status: str, dm_notes: str, publish: bool = False, updates: dict[str, Any] | None = None) -> None:
        if not viewer.is_dm:
            raise AccessDenied("DM only")
        with self.db.connect() as con:
            row = con.execute("SELECT * FROM voyage_npcs WHERE id=?", (npc_id,)).fetchone()
            if not row:
                return
            current = dict(row)
            if updates:
                for key in ["name", "ship_role", "memorable_detail", "why_remembered", "relationship"]:
                    if key in updates:
                        current[key] = updates[key]
            con.execute(
                """UPDATE voyage_npcs SET name=?,ship_role=?,memorable_detail=?,why_remembered=?,relationship=?,status=?,dm_notes=?,updated_at=? WHERE id=?""",
                (current["name"], current["ship_role"], current["memorable_detail"], current["why_remembered"], current["relationship"], status, dm_notes, utc_now(), npc_id),
            )
            if publish and current["party_permission"]:
                body = f"{current['memorable_detail']}\n\nRemembered because: {current['why_remembered']}\n\nRelationship: {current['relationship']}"
                meta = json.dumps({"where_met": "Aboard the voyage to Teralis", "source": "voyage_npc", "source_id": npc_id})
                con.execute(
                    "INSERT INTO published_content(kind,title,body,meta_json,updated_at,published) VALUES('person',?,?,?,?,1)",
                    (current["name"], body, meta, utc_now()),
                )

    def get_private_item(self, viewer: Viewer, target_user_id: str) -> dict[str, Any] | None:
        self._require_self_or_dm(viewer, target_user_id)
        with self.db.connect() as con:
            row = con.execute("SELECT * FROM private_items WHERE user_id=?", (target_user_id,)).fetchone()
        return dict(row) if row else None

    def save_private_item(self, viewer: Viewer, target_user_id: str, title: str, mechanics: str, dm_notes: str = "") -> None:
        if not viewer.is_dm:
            raise AccessDenied("Only the DM can define or update starting magic items.")
        with self.db.connect() as con:
            con.execute(
                """INSERT INTO private_items(user_id,title,mechanics,dm_notes,updated_at) VALUES(?,?,?,?,?)
                   ON CONFLICT(user_id) DO UPDATE SET title=excluded.title,mechanics=excluded.mechanics,dm_notes=excluded.dm_notes,updated_at=excluded.updated_at""",
                (target_user_id, title, mechanics, dm_notes, utc_now()),
            )

    def list_party_cards(self) -> list[dict[str, Any]]:
        with self.db.connect() as con:
            rows = con.execute(
                """SELECT c.user_id,u.player_name,u.character_name,c.public_text,c.portrait_path,c.updated_at
                   FROM public_party_cards c JOIN users u ON u.user_id=c.user_id WHERE u.role='player' ORDER BY u.player_name"""
            ).fetchall()
        return [dict(r) for r in rows]

    def save_party_card(self, viewer: Viewer, target_user_id: str, public_text: str, portrait_path: str | None = None) -> None:
        self._require_self_or_dm(viewer, target_user_id)
        with self.db.connect() as con:
            con.execute(
                "UPDATE public_party_cards SET public_text=?,portrait_path=?,updated_at=? WHERE user_id=?",
                (public_text, portrait_path, utc_now(), target_user_id),
            )

    def list_notes(self, viewer: Viewer, target_user_id: str | None = None) -> list[dict[str, Any]]:
        target = target_user_id or viewer.user_id
        self._require_self_or_dm(viewer, target)
        with self.db.connect() as con:
            rows = con.execute("SELECT * FROM notes WHERE user_id=? ORDER BY updated_at DESC", (target,)).fetchall()
        return [dict(r) for r in rows]

    def save_note(self, viewer: Viewer, title: str, body: str, note_id: int | None = None, attachment_type: str | None = None, attachment_id: str | None = None) -> int:
        if viewer.is_dm:
            raise AccessDenied("DM notes are intentionally outside this player-facing repository.")
        with self.db.connect() as con:
            if note_id:
                row = con.execute("SELECT user_id FROM notes WHERE id=?", (note_id,)).fetchone()
                if not row or row["user_id"] != viewer.user_id:
                    raise AccessDenied("Cannot edit another player's note.")
                con.execute(
                    "UPDATE notes SET title=?,body=?,attachment_type=?,attachment_id=?,updated_at=? WHERE id=?",
                    (title, body, attachment_type, attachment_id, utc_now(), note_id),
                )
                return note_id
            cur = con.execute(
                "INSERT INTO notes(user_id,title,body,attachment_type,attachment_id,updated_at) VALUES(?,?,?,?,?,?)",
                (viewer.user_id, title, body, attachment_type, attachment_id, utc_now()),
            )
            return int(cur.lastrowid)

    def delete_note(self, viewer: Viewer, note_id: int) -> None:
        if viewer.is_dm:
            raise AccessDenied("DM cannot delete player notes.")
        with self.db.connect() as con:
            con.execute("DELETE FROM notes WHERE id=? AND user_id=?", (note_id, viewer.user_id))

    def add_published_content(self, viewer: Viewer, kind: str, title: str, body: str = "", meta: dict[str, Any] | None = None) -> int:
        if not viewer.is_dm:
            raise AccessDenied("DM only")
        with self.db.connect() as con:
            cur = con.execute(
                "INSERT INTO published_content(kind,title,body,meta_json,updated_at,published) VALUES(?,?,?,?,?,1)",
                (kind, title, body, json.dumps(meta or {}), utc_now()),
            )
            return int(cur.lastrowid)

    def list_published_content(self, kind: str | None = None) -> list[dict[str, Any]]:
        with self.db.connect() as con:
            if kind:
                rows = con.execute("SELECT * FROM published_content WHERE published=1 AND kind=? ORDER BY updated_at DESC", (kind,)).fetchall()
            else:
                rows = con.execute("SELECT * FROM published_content WHERE published=1 ORDER BY updated_at DESC").fetchall()
        out = []
        for r in rows:
            item = dict(r)
            item["meta"] = json.loads(item.pop("meta_json") or "{}")
            out.append(item)
        return out

    def get_dnc_state(self) -> dict[str, Any]:
        with self.db.connect() as con:
            row = con.execute("SELECT state_json FROM dnc_state WHERE singleton_id=1").fetchone()
        return json.loads(row["state_json"])

    def save_dnc_state(self, viewer: Viewer, state: dict[str, Any], *, dm_only: bool = False) -> None:
        if dm_only and not viewer.is_dm:
            raise AccessDenied("DM only")
        with self.db.connect() as con:
            con.execute(
                "UPDATE dnc_state SET state_json=?,updated_at=? WHERE singleton_id=1",
                (json.dumps(state), utc_now()),
            )
