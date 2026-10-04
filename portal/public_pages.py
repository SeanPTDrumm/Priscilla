from __future__ import annotations

from pathlib import Path
import base64
import html
import re

import streamlit as st
import streamlit.components.v1 as components
import yaml

from .storage import editor_password, github_enabled, save_bytes, save_text, show_save_result
from .ui import empty_state


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def dump_yaml(data) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


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

    index_path = root / "content" / "episodes" / "index.yaml"
    if index_path.exists():
        episodes = load_yaml(index_path).get("episodes", [])
        published = [x for x in episodes if x.get("published", True)]
        if published:
            latest = sorted(published, key=lambda x: int(x.get("number", 0)))[-1]
            st.markdown(
                '<div class="portal-card">'
                '<div class="portal-kicker">LATEST EPISODE</div>'
                f'<strong>Episode {int(latest["number"])} — {html.escape(str(latest["title"]))}</strong><br>'
                '<span>Open <em>Episodes</em> in the sidebar for the story so far.</span>'
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


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "player"


def _party_text_path(root: Path, player: str) -> Path:
    return root / "content" / "party_profiles" / f"{_slug(player)}.md"


def _find_portrait(root: Path, player: str) -> Path | None:
    folder = root / "assets" / "party_portraits"
    slug = _slug(player)
    for ext in ("png", "jpg", "jpeg", "webp"):
        path = folder / f"{slug}.{ext}"
        if path.exists():
            return path
    return None


def party(root: Path):
    heading("The Party", "THE VOYAGE HAS ALREADY STARTED")
    st.write(
        "You have all been aboard the same crowded ship for about three months. "
        "Share whatever the others might reasonably have learned about your character. "
        "A sentence is plenty. Write more if you want."
    )

    data = load_yaml(root / "content" / "party.yaml")
    members = data.get("members", [])
    placeholder = root / "assets" / "party_unknown.png"

    cols = st.columns(3)
    for i, member in enumerate(members):
        player = member.get("player", "Player")
        text_path = _party_text_path(root, player)
        public_text = text_path.read_text(encoding="utf-8") if text_path.exists() else ""
        portrait_path = _find_portrait(root, player)

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
                text_rel = f"content/party_profiles/{_slug(player)}.md"
                text_result = save_text(root, text_rel, text, f"Update {player} party profile")
                show_save_result(text_result)

                if upload is not None:
                    suffix = Path(upload.name).suffix.lower().lstrip(".") or "png"
                    if suffix not in {"png", "jpg", "jpeg", "webp"}:
                        suffix = "png"
                    portrait_rel = f"assets/party_portraits/{_slug(player)}.{suffix}"
                    portrait_result = save_bytes(
                        root,
                        portrait_rel,
                        upload.getvalue(),
                        f"Update {player} party portrait",
                    )
                    show_save_result(portrait_result)
                st.rerun()

    if github_enabled():
        st.caption("Party entries are saved back to the GitHub repository and survive Streamlit redeploys.")
    else:
        st.caption("Party entries can be edited here now. Add the GitHub Secrets described in README.md to make them permanent across redeploys.")


def known_world(root: Path):
    heading("Known World", "WHAT THE PARTY MAY KNOW")
    intro_path = root / "content" / "known_world.md"
    if intro_path.exists():
        st.markdown(intro_path.read_text(encoding="utf-8"))
    else:
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


def episodes(root: Path):
    heading("Episodes", "THE STORY SO FAR")
    st.write("Previously… on *Priscilla, Queen of the Desert*.")

    index_path = root / "content" / "episodes" / "index.yaml"
    if not index_path.exists():
        empty_state(st, "No episodes have been published yet.")
        return

    episodes_data = load_yaml(index_path).get("episodes", [])
    episodes_data = [x for x in episodes_data if x.get("published", True)]
    episodes_data = sorted(episodes_data, key=lambda x: int(x.get("number", 0)), reverse=True)

    if not episodes_data:
        empty_state(st, "No episodes have been published yet.")
        return

    for idx, ep in enumerate(episodes_data):
        number = int(ep.get("number", 0))
        title = str(ep.get("title", "Untitled"))
        file_name = str(ep.get("file", f"episode_{number:02d}.md"))
        path = root / "content" / "episodes" / file_name
        label = f"Episode {number} — {title}"
        with st.expander(label, expanded=(idx == 0)):
            if path.exists():
                st.markdown(path.read_text(encoding="utf-8"))
            else:
                empty_state(st, "This episode recap has not been added yet.")

    st.caption("Want to change a title or recap? Open ✏️ Edit Portal in the sidebar.")


def _editor_unlocked() -> bool:
    required = editor_password()
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


def _save_editor_text(root: Path, rel: str, text: str, message: str):
    result = save_text(root, rel, text, message)
    show_save_result(result)


def editor(root: Path):
    heading("Edit Portal", "CHANGE THE SITE WITHOUT TOUCHING PYTHON")

    if not _editor_unlocked():
        return

    if github_enabled():
        st.success("Permanent saving is connected to GitHub.")
    else:
        st.warning(
            "Editing works, but permanent GitHub saving is not connected yet. "
            "Use the one-time Streamlit Secrets setup in README.md so edits survive redeploys."
        )

    tabs = st.tabs(["Episodes", "Home", "Voyage Prep", "Known World", "Schedule", "Locked Pages"])

    with tabs[0]:
        _edit_episodes(root)

    with tabs[1]:
        path = root / "content" / "home.md"
        body = st.text_area("Home page", value=path.read_text(encoding="utf-8"), height=360, key="edit_home")
        if st.button("Save Home", key="save_home", type="primary"):
            _save_editor_text(root, "content/home.md", body, "Edit portal home page")

    with tabs[2]:
        path = root / "content" / "voyage.md"
        body = st.text_area("Voyage Prep", value=path.read_text(encoding="utf-8"), height=520, key="edit_voyage")
        if st.button("Save Voyage Prep", key="save_voyage", type="primary"):
            _save_editor_text(root, "content/voyage.md", body, "Edit Voyage Prep")

    with tabs[3]:
        path = root / "content" / "known_world.md"
        default = path.read_text(encoding="utf-8") if path.exists() else (
            "You are outsiders. What your characters know may be rumor, scholarship, religion, "
            "old sailors’ tales, or something learned before the crossing."
        )
        body = st.text_area("Known World intro", value=default, height=260, key="edit_known_world")
        if st.button("Save Known World", key="save_known_world", type="primary"):
            _save_editor_text(root, "content/known_world.md", body, "Edit Known World intro")

    with tabs[4]:
        settings_path = root / "content" / "settings.yaml"
        settings = load_yaml(settings_path)
        line1 = st.text_input("First schedule line", value=settings.get("session_line_1", ""))
        line2 = st.text_input("Second schedule line", value=settings.get("session_line_2", ""))
        if st.button("Save Schedule", key="save_schedule", type="primary"):
            settings["session_line_1"] = line1
            settings["session_line_2"] = line2
            _save_editor_text(root, "content/settings.yaml", dump_yaml(settings), "Edit portal schedule")

    with tabs[5]:
        coming_path = root / "content" / "coming_soon.yaml"
        coming = load_yaml(coming_path)
        for key in ("dingoes_crowns", "people_places"):
            item = coming[key]
            st.markdown(f"### {item['title']}")
            new_text = st.text_area("Coming-soon text", value=item.get("text", ""), key=f"locked_{key}")
            if st.button(f"Save {item['title']}", key=f"save_locked_{key}"):
                coming[key]["text"] = new_text
                _save_editor_text(root, "content/coming_soon.yaml", dump_yaml(coming), f"Edit {item['title']} locked-page text")


def _edit_episodes(root: Path):
    index_rel = "content/episodes/index.yaml"
    index_path = root / index_rel
    data = load_yaml(index_path) if index_path.exists() else {"episodes": []}
    episode_rows = sorted(data.get("episodes", []), key=lambda x: int(x.get("number", 0)))

    if episode_rows:
        labels = [f"Episode {int(x['number'])} — {x['title']}" for x in episode_rows]
        selected_label = st.selectbox("Choose an episode", labels, key="episode_picker")
        selected_index = labels.index(selected_label)
        selected = episode_rows[selected_index]
        number = int(selected["number"])
        file_name = selected.get("file", f"episode_{number:02d}.md")
        episode_path = root / "content" / "episodes" / file_name
        body_default = episode_path.read_text(encoding="utf-8") if episode_path.exists() else ""

        title = st.text_input("Episode title", value=selected.get("title", ""), key=f"episode_title_{number}")
        published = st.checkbox("Visible to players", value=bool(selected.get("published", True)), key=f"episode_published_{number}")
        body = st.text_area("Episode recap", value=body_default, height=620, key=f"episode_body_{number}")

        if st.button("Save Episode", key=f"save_episode_{number}", type="primary"):
            body_result = save_text(root, f"content/episodes/{file_name}", body, f"Update Episode {number} recap")
            show_save_result(body_result)

            for row in episode_rows:
                if int(row.get("number", 0)) == number:
                    row["title"] = title.strip() or "Untitled"
                    row["published"] = published
            data["episodes"] = episode_rows
            index_result = save_text(root, index_rel, dump_yaml(data), f"Update Episode {number} details")
            show_save_result(index_result)

        st.markdown("---")

    with st.expander("➕ Add a new episode", expanded=not bool(episode_rows)):
        next_number = max([int(x.get("number", 0)) for x in episode_rows] + [0]) + 1
        new_title = st.text_input("Title", value="The One With…", key="new_episode_title")
        new_body = st.text_area(
            "Recap",
            value="## Previously… on *Priscilla, Queen of the Desert*\n\n",
            height=420,
            key="new_episode_body",
        )
        new_published = st.checkbox("Publish immediately", value=True, key="new_episode_published")
        if st.button(f"Create Episode {next_number}", key="create_episode", type="primary"):
            file_name = f"episode_{next_number:02d}.md"
            body_result = save_text(root, f"content/episodes/{file_name}", new_body, f"Add Episode {next_number} recap")
            show_save_result(body_result)
            episode_rows.append({
                "number": next_number,
                "title": new_title.strip() or "Untitled",
                "file": file_name,
                "published": new_published,
            })
            data["episodes"] = episode_rows
            index_result = save_text(root, index_rel, dump_yaml(data), f"Add Episode {next_number}")
            show_save_result(index_result)
            st.rerun()
