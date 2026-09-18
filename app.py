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

# Preserve the original repository/database architecture.
# The public hub itself no longer uses PINs or player accounts.
db = Database(DB_PATH)
db.init_schema()
repo = PortalRepository(db)

page_defs = [
    st.Page(lambda: public_pages.home(ROOT), title="Home", icon="🏠", url_path="home", default=True),
    st.Page(lambda: public_pages.voyage(ROOT), title="Voyage Prep", icon="⛵", url_path="voyage"),
    st.Page(lambda: public_pages.invitation(ROOT), title="The Invitation", icon="✉️", url_path="invitation"),
    st.Page(lambda: public_pages.party(ROOT), title="The Party", icon="🛡️", url_path="party"),
    st.Page(lambda: public_pages.known_world(ROOT), title="Known World", icon="🗺️", url_path="known-world"),

    # The original working D&C implementation remains untouched in portal/pages.py.
    # This route is intentionally locked until Sean is ready to expose it.
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
        lambda: public_pages.locked(ROOT, "campaign_journal"),
        title="Campaign Journal 🔒",
        icon="📖",
        url_path="campaign-journal",
    ),
    st.Page(
        lambda: public_pages.locked(ROOT, "letters_handouts"),
        title="Letters & Handouts 🔒",
        icon="📜",
        url_path="letters-handouts",
    ),
]

nav = st.navigation(page_defs, position="sidebar")
nav.run()
