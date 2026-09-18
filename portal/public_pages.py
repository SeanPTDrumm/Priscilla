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


def party(root: Path):
    data = load_yaml(root / "content" / "party.yaml")
    heading("The Party", "PREGAME ROSTER")
    if data.get("intro"):
        st.write(data["intro"])

    members = data.get("members", [])
    cols = st.columns(2)
    for i, member in enumerate(members):
        with cols[i % 2]:
            portrait = member.get("portrait", "").strip()
            if portrait:
                p = root / "assets" / portrait
                if p.exists():
                    st.image(str(p), use_container_width=True)
            st.markdown(
                '<div class="portal-card">'
                f'<div class="portal-kicker">{html.escape(member.get("player",""))}</div>'
                f'<h3>{html.escape(member.get("character","Coming soon"))}</h3>'
                f'<div>{html.escape(member.get("blurb",""))}</div>'
                '</div>',
                unsafe_allow_html=True,
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
