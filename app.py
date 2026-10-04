from __future__ import annotations

from pathlib import Path
import base64
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request

import streamlit as st
import yaml

from portal.db import Database
from portal.repository import PortalRepository
from portal.ui import apply_theme
from portal import public_pages


# =========================================================
# APP SETUP
# =========================================================

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "portal.sqlite3"

st.set_page_config(
    page_title="Priscilla Player Portal",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme(st)

# Keep the original architecture available for the preserved D&C prototype.
db = Database(DB_PATH)
db.init_schema()
repo = PortalRepository(db)


# =========================================================
# SMALL FILE / GITHUB SAVE LAYER
# =========================================================


def _github_config() -> tuple[str, str, str]:
    """Read optional persistence settings from Streamlit Secrets."""
    try:
        token = str(st.secrets.get("GITHUB_TOKEN", "")).strip()
        repo_name = str(st.secrets.get("GITHUB_REPO", "")).strip()
        branch = str(st.secrets.get("GITHUB_BRANCH", "main")).strip() or "main"
    except Exception:
        token, repo_name, branch = "", "", "main"
    return token, repo_name, branch


def _editor_password() -> str:
    try:
        return str(st.secrets.get("EDITOR_PASSWORD", ""))
    except Exception:
        return ""


def _github_enabled() -> bool:
    token, repo_name, _ = _github_config()
    return bool(token and repo_name)


def _github_api(url: str, token: str, method: str = "GET", payload: dict | None = None):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Priscilla-Player-Portal",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, headers=headers, data=data, method=method)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _save_to_github(relative_path: str, payload_bytes: bytes, message: str) -> tuple[bool, str]:
    token, repo_name, branch = _github_config()
    if not token or not repo_name:
        return False, "Permanent GitHub saving is not connected yet."

    quoted_path = "/".join(urllib.parse.quote(part) for part in relative_path.split("/"))
    base_url = f"https://api.github.com/repos/{repo_name}/contents/{quoted_path}"

    sha = None
    try:
        current = _github_api(f"{base_url}?ref={urllib.parse.quote(branch)}", token)
        sha = current.get("sha")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                detail = str(exc)
            return False, f"GitHub read failed: {detail}"
    except Exception as exc:
        return False, f"Could not reach GitHub: {exc}"

    body = {
        "message": message,
        "content": base64.b64encode(payload_bytes).decode("ascii"),
        "branch": branch,
    }
    if sha:
        body["sha"] = sha

    try:
        result = _github_api(base_url, token, method="PUT", payload=body)
        commit_sha = (result.get("commit") or {}).get("sha", "")
        suffix = f" ({commit_sha[:7]})" if commit_sha else ""
        return True, f"Saved permanently to GitHub{suffix}."
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8")
        except Exception:
            detail = str(exc)
        return False, f"GitHub rejected the save: {detail}"
    except Exception as exc:
        return False, f"Could not save to GitHub: {exc}"


def _save_bytes(relative_path: str, data: bytes, message: str) -> tuple[bool, bool, str]:
    """Save locally now; save to GitHub too when configured."""
    local_path = ROOT / relative_path
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_bytes(data)

    if not _github_enabled():
        return True, False, (
            "Saved in the running app. Once GitHub saving is connected, edits will also survive redeploys."
        )

    ok, msg = _save_to_github(relative_path, data, message)
    return ok, ok, msg


def _save_text(relative_path: str, text: str, message: str) -> tuple[bool, bool, str]:
    return _save_bytes(relative_path, text.encode("utf-8"), message)


def _show_save(result: tuple[bool, bool, str]):
    ok, persisted, message = result
    if ok and persisted:
        st.success(message)
    elif ok:
        st.warning(message)
    else:
        st.error(message)


def _load_yaml(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    return yaml.safe_load(path.read_text(encoding="utf-8")) or ({} if default is None else default)


def _dump_yaml(data) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


# =========================================================
# EPISODES
# =========================================================


def _episode_files() -> list[Path]:
    folder = ROOT / "content" / "episodes"
    folder.mkdir(parents=True, exist_ok=True)
    files = list(folder.glob("episode_*.md"))

    def number(path: Path) -> int:
        match = re.search(r"episode_(\d+)", path.stem)
        return int(match.group(1)) if match else 0

    return sorted(files, key=number)


def _episode_number(path: Path) -> int:
    match = re.search(r"episode_(\d+)", path.stem)
    return int(match.group(1)) if match else 0


def _episode_title(path: Path) -> str:
    number = _episode_number(path)
    if not path.exists():
        return f"Episode {number}"
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("# "):
            heading = line[2:].strip().replace("*", "")
            # If the heading already starts with Episode N —, return just the title part.
            match = re.match(rf"Episode\s+{number}\s*[—-]\s*(.+)", heading, flags=re.I)
            if match:
                return match.group(1).strip()
            return heading
    return f"Episode {number}"


def episodes_page():
    st.markdown('<div class="portal-kicker">THE STORY SO FAR</div>', unsafe_allow_html=True)
    st.title("Episodes")
    st.write("Previously… on *Priscilla, Queen of the Desert*.")

    files = _episode_files()
    if not files:
        st.info("No episodes have been published yet.")
        return

    for i, path in enumerate(reversed(files)):
        number = _episode_number(path)
        title = _episode_title(path)
        with st.expander(f"Episode {number} — {title}", expanded=(i == 0)):
            st.markdown(path.read_text(encoding="utf-8"))

    st.caption("To change an episode or add the next one, open ✏️ Edit Portal.")


# =========================================================
# DURABLE PARTY PROFILES
# =========================================================


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "player"


def _find_portrait(player: str) -> Path | None:
    folder = ROOT / "assets" / "party_portraits"
    slug = _slug(player)
    for ext in ("png", "jpg", "jpeg", "webp"):
        candidate = folder / f"{slug}.{ext}"
        if candidate.exists():
            return candidate
    return None


def party_page():
    st.markdown('<div class="portal-kicker">THE VOYAGE HAS ALREADY STARTED</div>', unsafe_allow_html=True)
    st.title("The Party")
    st.write(
        "You have all been aboard the same crowded ship for about three months. "
        "Share whatever the others might reasonably have learned about your character. "
        "A sentence is plenty. Write more if you want."
    )

    data = _load_yaml(ROOT / "content" / "party.yaml", {"members": []})
    members = data.get("members", [])
    placeholder = ROOT / "assets" / "party_unknown.png"
    cols = st.columns(3)

    for i, member in enumerate(members):
        player = str(member.get("player", "Player"))
        slug = _slug(player)
        text_path = ROOT / "content" / "party_profiles" / f"{slug}.md"
        public_text = text_path.read_text(encoding="utf-8") if text_path.exists() else ""
        portrait_path = _find_portrait(player)

        with cols[i % 3]:
            st.markdown(
                f'<div class="portal-kicker" style="text-align:center;margin-top:.4rem;">{html.escape(player.upper())}</div>',
                unsafe_allow_html=True,
            )
            if portrait_path:
                st.image(str(portrait_path), use_container_width=True)
            elif placeholder.exists():
                st.image(str(placeholder), use_container_width=True)

            upload = st.file_uploader(
                "Upload or replace portrait",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"portrait_{player}",
            )
            text = st.text_area(
                "What might the others know about you?",
                value=public_text,
                placeholder="A sentence is enough. Write more if you want.",
                height=120,
                key=f"party_text_{player}",
            )

            if st.button("Save", key=f"save_party_{player}", use_container_width=True):
                _show_save(_save_text(
                    f"content/party_profiles/{slug}.md",
                    text,
                    f"Update {player} party profile",
                ))

                if upload is not None:
                    ext = Path(upload.name).suffix.lower().lstrip(".") or "png"
                    # Remove old local portrait variants so the newest one is shown immediately.
                    portrait_folder = ROOT / "assets" / "party_portraits"
                    portrait_folder.mkdir(parents=True, exist_ok=True)
                    for old_ext in ("png", "jpg", "jpeg", "webp"):
                        old = portrait_folder / f"{slug}.{old_ext}"
                        if old.exists() and old_ext != ext:
                            old.unlink()
                    _show_save(_save_bytes(
                        f"assets/party_portraits/{slug}.{ext}",
                        upload.getvalue(),
                        f"Update {player} party portrait",
                    ))
                st.rerun()

    if _github_enabled():
        st.caption("Party entries are saved permanently to the GitHub repository.")
    else:
        st.caption("Party editing works now. Permanent saving will be switched on with the one-time GitHub connection.")


# =========================================================
# EDIT PORTAL
# =========================================================


def _editor_unlocked() -> bool:
    required = _editor_password()
    if not required:
        return True
    if st.session_state.get("priscilla_editor_unlocked"):
        return True

    st.subheader("Editor access")
    entered = st.text_input("Editor password", type="password")
    if st.button("Unlock editor", type="primary"):
        if entered == required:
            st.session_state["priscilla_editor_unlocked"] = True
            st.rerun()
        else:
            st.error("That password is not correct.")
    return False


def _replace_episode_heading(body: str, number: int, title: str) -> str:
    desired = f"# Episode {number} — {title.strip() or 'Untitled'}"
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("# "):
            lines[i] = desired
            return "\n".join(lines).rstrip() + "\n"
    return desired + "\n\n" + body.lstrip()


def _edit_episodes():
    files = _episode_files()

    if files:
        labels = [f"Episode {_episode_number(p)} — {_episode_title(p)}" for p in files]
        selected_label = st.selectbox("Choose an episode", labels)
        path = files[labels.index(selected_label)]
        number = _episode_number(path)
        current_title = _episode_title(path)
        current_body = path.read_text(encoding="utf-8")

        title = st.text_input("Episode title", value=current_title, key=f"episode_title_{number}")
        body = st.text_area("Episode recap", value=current_body, height=620, key=f"episode_body_{number}")

        if st.button("Save Episode", type="primary", key=f"save_episode_{number}"):
            final_body = _replace_episode_heading(body, number, title)
            result = _save_text(
                f"content/episodes/{path.name}",
                final_body,
                f"Update Episode {number}: {title.strip() or 'Untitled'}",
            )
            _show_save(result)
            st.rerun()

        st.markdown("---")

    with st.expander("➕ Add the next episode", expanded=not bool(files)):
        next_number = max([_episode_number(p) for p in files] + [0]) + 1
        new_title = st.text_input("Episode title", value="The One With…", key="new_episode_title")
        new_body = st.text_area(
            "Episode recap",
            value="## Previously… on *Priscilla, Queen of the Desert*\n\n",
            height=420,
            key="new_episode_body",
        )
        if st.button(f"Create Episode {next_number}", type="primary", key="create_episode"):
            text = f"# Episode {next_number} — {new_title.strip() or 'Untitled'}\n\n{new_body.lstrip()}"
            result = _save_text(
                f"content/episodes/episode_{next_number:02d}.md",
                text,
                f"Add Episode {next_number}: {new_title.strip() or 'Untitled'}",
            )
            _show_save(result)
            st.rerun()


def editor_page():
    st.markdown('<div class="portal-kicker">CHANGE THE SITE WITHOUT TOUCHING PYTHON</div>', unsafe_allow_html=True)
    st.title("Edit Portal")

    if not _editor_unlocked():
        return

    if _github_enabled():
        st.success("Permanent saving is connected. Changes made here survive Streamlit redeploys.")
    else:
        st.warning(
            "The editor works, but permanent saving is not connected yet. "
            "We only need to do that one-time connection after this version is live."
        )

    tabs = st.tabs(["Episodes", "Home", "Voyage Prep", "Known World", "Schedule", "Locked Pages"])

    with tabs[0]:
        _edit_episodes()

    with tabs[1]:
        path = ROOT / "content" / "home.md"
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        body = st.text_area("Home page", value=current, height=380, key="edit_home")
        if st.button("Save Home", type="primary", key="save_home"):
            _show_save(_save_text("content/home.md", body, "Edit portal Home page"))

    with tabs[2]:
        path = ROOT / "content" / "voyage.md"
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        body = st.text_area("Voyage Prep", value=current, height=520, key="edit_voyage")
        if st.button("Save Voyage Prep", type="primary", key="save_voyage"):
            _show_save(_save_text("content/voyage.md", body, "Edit Voyage Prep"))

    with tabs[3]:
        path = ROOT / "content" / "known_world.md"
        default = (
            path.read_text(encoding="utf-8")
            if path.exists()
            else "You are outsiders. What your characters know may be rumor, scholarship, religion, old sailors’ tales, or something learned before the crossing."
        )
        body = st.text_area("Known World intro", value=default, height=300, key="edit_known_world")
        if st.button("Save Known World", type="primary", key="save_known_world"):
            _show_save(_save_text("content/known_world.md", body, "Edit Known World intro"))

    with tabs[4]:
        settings_path = ROOT / "content" / "settings.yaml"
        settings = _load_yaml(settings_path, {})
        line1 = st.text_input("First schedule line", value=str(settings.get("session_line_1", "")))
        line2 = st.text_input("Second schedule line", value=str(settings.get("session_line_2", "")))
        if st.button("Save Schedule", type="primary", key="save_schedule"):
            settings["session_line_1"] = line1
            settings["session_line_2"] = line2
            _show_save(_save_text("content/settings.yaml", _dump_yaml(settings), "Edit portal schedule"))

    with tabs[5]:
        coming_path = ROOT / "content" / "coming_soon.yaml"
        coming = _load_yaml(coming_path, {})
        for key in ("dingoes_crowns", "people_places"):
            item = coming.get(key, {})
            title = str(item.get("title", key.replace("_", " ").title()))
            st.markdown(f"### {title}")
            new_text = st.text_area(
                "Coming-soon text",
                value=str(item.get("text", "")),
                key=f"locked_{key}",
            )
            if st.button(f"Save {title}", key=f"save_locked_{key}"):
                coming.setdefault(key, {})["title"] = title
                coming[key]["text"] = new_text
                _show_save(_save_text(
                    "content/coming_soon.yaml",
                    _dump_yaml(coming),
                    f"Edit {title} locked-page text",
                ))


# =========================================================
# NAVIGATION
# =========================================================

page_defs = [
    st.Page(lambda: public_pages.home(ROOT), title="Home", icon="🏠", url_path="home", default=True),
    st.Page(lambda: public_pages.voyage(ROOT), title="Voyage Prep", icon="⛵", url_path="voyage"),
    st.Page(party_page, title="The Party", icon="🛡️", url_path="party"),
    st.Page(lambda: public_pages.known_world(ROOT), title="Known World", icon="🗺️", url_path="known-world"),
    st.Page(episodes_page, title="Episodes", icon="🎬", url_path="episodes"),
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
    st.Page(editor_page, title="Edit Portal", icon="✏️", url_path="edit-portal"),
]

nav = st.navigation(page_defs, position="sidebar")
nav.run()
