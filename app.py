from __future__ import annotations

from pathlib import Path
import streamlit as st

from portal.db import Database
from portal.repository import PortalRepository
from portal.ui import apply_theme
from portal import public_pages

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "portal.sqlite3"

st.set_page_config(
    page_title="Priscilla Player Portal",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme(st)

# Keep the original repository/database architecture available for the preserved
# Dingoes & Crowns prototype, while durable player-facing content now lives in
# ordinary repo files that can be saved back to GitHub from the Edit Portal page.
db = Database(DB_PATH)
db.init_schema()
repo = PortalRepository(db)

page_defs = [
    st.Page(lambda: public_pages.home(ROOT), title="Home", icon="🏠", url_path="home", default=True),
    st.Page(lambda: public_pages.voyage(ROOT), title="Voyage Prep", icon="⛵", url_path="voyage"),
    st.Page(lambda: public_pages.party(ROOT), title="The Party", icon="🛡️", url_path="party"),
    st.Page(lambda: public_pages.known_world(ROOT), title="Known World", icon="🗺️", url_path="known-world"),
    st.Page(lambda: public_pages.episodes(ROOT), title="Episodes", icon="🎬", url_path="episodes"),
    st.Page(
        lambda: public_pages.locked(ROOT, "dingoes_crowns"),
        title="Dingoes & Crowns 🔒",
        icon="🎲",
        url_path="dingoes-crowns",
    ),
    st.Page(
        lambda: public_pages.locked(ROOT, "people_places"),
        title="People & Places 🔒",
        icon="🧭",
        url_path="people-places",
    ),
    st.Page(
        lambda: public_pages.homebrew_common_law(ROOT),
        title="Homebrew & Common Law",
        icon="📜",
        url_path="homebrew-common-law",
    ),
    st.Page(
        lambda: public_pages.editor(ROOT),
        title="Edit Portal",
        icon="✏️",
        url_path="edit-portal",
    ),
]

nav = st.navigation(page_defs, position="sidebar")
nav.run()
