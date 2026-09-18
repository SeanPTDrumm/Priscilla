from __future__ import annotations

from pathlib import Path
import base64
import html
import yaml
import streamlit as st
import streamlit.components.v1 as components

from .ui import empty_state


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_settings(root: Path) -> dict:
    return load_yaml(root / "content" / "settings.yaml")


def heading(title: str, kicker: str | None = None):
    if kicker:
        st.markdown(
            f'<div class="portal-kicker">{html.escape(kicker)}</div>',
            unsafe_allow_html=True,
        )
    st.title(title)


def home(root: Path):
    settings = load_settings(root)
    hero = root / "assets" / settings.get("home_hero", "")
    if hero.exists():
        st.image(str(hero), use_container_width=True)

    st.markdown((root / "content" / "home.md").read_text(encoding="utf-8"))

    line1 = html.escape(settings["session_line_1"])
    line2 = html.escape(settings["session_line_2"])
    st.markdown(
        '<div class="portal-session">'
        f'<div class="portal-session-main">{line1}</div>'
        f'<div>{line2}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _embedded_pdf(path: Path, height: int = 900):
    if not path.exists():
        empty_state(st, "This PDF has not been added yet.")
        return
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    components.html(
        f'<iframe src="data:application/pdf;base64,{encoded}" '
        f'width="100%" height="{height}" style="border:0;border-radius:10px;"></iframe>',
        height=height + 15,
        scrolling=True,
    )


def homebrew_common_law(root: Path):
    st.markdown((root / "content" / "homebrew.md").read_text(encoding="utf-8"))

    invite = root / "assets" / "Priscilla_Player_Invite.pdf"
    with st.expander("View the Original Invitation", expanded=True):
        _embedded_pdf(invite, height=880)

    disadvantages = root / "assets" / "Priscilla_Disadvantages.pdf"
    with st.expander("View Disadvantages for Bonus Feats", expanded=False):
        _embedded_pdf(disadvantages, height=880)

def voyage(root: Path):
    st.markdown((root / "content" / "voyage.md").read_text(encoding="utf-8"))



def _party_db(root: Path):
    from .db import Database
    return Database(root / "data" / "portal.sqlite3")


def _get_party_profile(root: Path, player_name: str) -> dict:
    db = _party_db(root)
    with db.connect() as con:
        row = con.execute(
            "SELECT player_name, public_text, portrait_blob, portrait_mime, updated_at "
            "FROM open_party_profiles WHERE player_name=?",
            (player_name,),
        ).fetchone()
    return dict(row) if row else {
        "player_name": player_name,
        "public_text": "",
        "portrait_blob": None,
        "portrait_mime": None,
        "updated_at": "",
    }


def _save_party_profile(root: Path, player_name: str, public_text: str, upload) -> None:
    from .db import utc_now
    db = _party_db(root)
    existing = _get_party_profile(root, player_name)
    portrait_blob = existing.get("portrait_blob")
    portrait_mime = existing.get("portrait_mime")
    if upload is not None:
        portrait_blob = upload.getvalue()
        portrait_mime = upload.type or "image/png"

    with db.connect() as con:
        con.execute(
            """INSERT INTO open_party_profiles(player_name, public_text, portrait_blob, portrait_mime, updated_at)
               VALUES(?,?,?,?,?)
               ON CONFLICT(player_name) DO UPDATE SET
                 public_text=excluded.public_text,
                 portrait_blob=excluded.portrait_blob,
                 portrait_mime=excluded.portrait_mime,
                 updated_at=excluded.updated_at""",
            (player_name, public_text, portrait_blob, portrait_mime, utc_now()),
        )


def party(root: Path):
    heading("The Party", "THE VOYAGE HAS ALREADY STARTED")
    st.write(
        "You have all been aboard the same crowded ship for about three months. "
        "You may have become friends, barely spoken, or simply noticed each other around the ship. "
        "Share whatever the others might reasonably have learned about your character. "
        "A sentence is plenty. Write more if you want."
    )

    data = load_yaml(root / "content" / "party.yaml")
    members = data.get("members", [])
    placeholder = root / "assets" / "party_unknown.png"

    cols = st.columns(3)
    for i, member in enumerate(members):
        player = member.get("player", "Player")
        profile = _get_party_profile(root, player)
        with cols[i % 3]:
            st.markdown(
                f'<div class="portal-kicker" style="text-align:center;margin-top:.4rem;">{html.escape(player.upper())}</div>',
                unsafe_allow_html=True,
            )

            portrait_blob = profile.get("portrait_blob")
            if portrait_blob:
                st.image(portrait_blob, use_container_width=True)
            elif placeholder.exists():
                st.image(str(placeholder), use_container_width=True)

            upload = st.file_uploader(
                "Upload or replace portrait",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"portrait_{player}",
            )
            text = st.text_area(
                "What might the others know about you?",
                value=profile.get("public_text", ""),
                placeholder="A sentence is enough. Write more if you want.",
                height=120,
                key=f"party_text_{player}",
            )
            if st.button("Save", key=f"save_party_{player}", use_container_width=True):
                _save_party_profile(root, player, text, upload)
                st.success("Saved.")
                st.rerun()

            if profile.get("public_text"):
                st.caption("Visible to everyone who opens the Party page.")

    st.caption(
        "Note: these entries are stored by the running Streamlit app. "
        "A full app redeploy can reset them, so Your Friendly Dungeon Master should copy anything important into the campaign record."
    )

def known_world(root: Path):
    heading("Known World", "WHAT THE PARTY MAY KNOW")
    st.write(
        "You are outsiders. What your characters know may be rumor, scholarship, religion, "
        "old sailors’ tales, or something learned before the crossing."
    )
    map_path = root / "assets" / "teralis_starting_map.png"
    if map_path.exists():
        st.image(str(map_path), caption="Your starting map", use_container_width=True)
        st.download_button(
            "Download the starting map",
            map_path.read_bytes(),
            file_name="Teralis_Starting_Map.png",
            mime="image/png",
            use_container_width=True,
        )
    else:
        empty_state(st, "The starting map has not been added yet.")


def locked(root: Path, key: str):
    data = load_yaml(root / "content" / "coming_soon.yaml")
    item = data[key]
    heading(item["title"], "COMING SOON")
    st.markdown(
        '<div class="portal-empty"><strong>🔒 Locked for now.</strong><br><br>'
        + html.escape(item["text"])
        + '</div>',
        unsafe_allow_html=True,
    )
