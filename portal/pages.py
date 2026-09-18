from __future__ import annotations

import json
import random
import secrets
from pathlib import Path

from .auth import Viewer
from .repository import AccessDenied, PortalRepository
from .ui import empty_state, load_yaml


def heading(st, title: str, kicker: str | None = None):
    if kicker:
        st.markdown(f'<div class="portal-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)


def _show_private_item(st, repo: PortalRepository, viewer: Viewer):
    item = repo.get_private_item(viewer, viewer.user_id)
    st.subheader("Your Special Starting Item")
    if not item or not item.get("title"):
        st.markdown('<div class="portal-private"><strong>Private:</strong> Your item has not been loaded into the portal yet. Nothing is being guessed or copied from the DM Codex.</div>', unsafe_allow_html=True)
        return
    st.markdown('<div class="portal-private"><strong>Private to you and the DM.</strong></div>', unsafe_allow_html=True)
    st.markdown(f"### {item['title']}")
    st.markdown(item["mechanics"] or "_No mechanics entered yet._")


def before_we_begin(st, repo: PortalRepository, viewer: Viewer, root: Path):
    heading(st, "Before We Begin", "PRIVATE CHARACTER SETUP")
    if viewer.is_dm:
        st.info("Player setup answers live in the DM Panel. This page is intentionally player-facing.")
        return

    st.markdown(f"Welcome, **{viewer.player_name}**. These answers are private to you and the DM. Save a draft whenever you like; submit only when you want Sean to review it.")
    prompts = load_yaml(root / "content" / "before_we_begin.yaml")["prompts"]

    for p in prompts:
        current = repo.get_prompt(viewer, viewer.user_id, p["key"]) or {"body": "", "status": "draft"}
        with st.expander(p["title"], expanded=True):
            st.write(p["help"])
            default = current["body"]
            if p["key"] == "how_map_reached_you" and not default:
                default = "Captain Dick Boatman handed it to me aboard ship."
            body = st.text_area("Your answer", value=default, key=f"prompt-{p['key']}", height=130)
            c1, c2, c3 = st.columns([1,1,2])
            with c1:
                if st.button("Save draft", key=f"save-{p['key']}"):
                    repo.save_prompt(viewer, p["key"], body, submit=False)
                    st.success("Draft saved privately.")
            with c2:
                if st.button("Submit", key=f"submit-{p['key']}"):
                    repo.save_prompt(viewer, p["key"], body, submit=True)
                    st.success("Submitted to the DM review queue.")
            with c3:
                st.caption(f"Current status: {current.get('status','draft')}")

    st.divider()
    st.subheader("Create someone from the voyage")
    st.write("You spent three months surrounded by passengers and crew. Create one person your character met and got to know. This stays private until the DM reviews it, and it never publishes automatically.")
    existing = repo.list_voyage_npcs(viewer)
    if existing:
        st.caption(f"You have {len(existing)} saved voyage NPC submission(s).")
        for row in existing:
            with st.expander(f"{row['name'] or 'Unnamed voyage NPC'} · {row['status']}"):
                st.write(row["memorable_detail"] or "No memorable detail yet.")
                st.caption("Party may know" if row["party_permission"] else "Keep private for now")

    with st.form("voyage_npc_form", clear_on_submit=True):
        name = st.text_input("Name")
        ship_role = st.text_input("Role aboard ship")
        memorable = st.text_area("One memorable detail")
        why = st.text_area("Why does your character remember them?")
        relationship = st.selectbox("How did your character feel about them?", ["Liked", "Disliked", "Trusted", "Feared", "Owed them", "Was owed by them", "It's complicated"])
        party_permission = st.checkbox("The party may currently know about this person")
        col1, col2 = st.columns(2)
        save = col1.form_submit_button("Save private draft")
        submit = col2.form_submit_button("Submit to DM")
        if save or submit:
            if not name.strip():
                st.error("Give them a name first.")
            else:
                repo.save_voyage_npc(viewer, {
                    "name": name.strip(), "ship_role": ship_role.strip(), "memorable_detail": memorable.strip(),
                    "why_remembered": why.strip(), "relationship": relationship, "party_permission": party_permission,
                }, submit=submit)
                st.success("Saved privately." if save else "Submitted to the DM review queue.")

    st.divider()
    _show_private_item(st, repo, viewer)


def party(st, repo: PortalRepository, viewer: Viewer, root: Path):
    heading(st, "The Party", "WHAT THE CHARACTERS CHOOSE TO SHARE")
    st.write("These cards contain only information a player has deliberately chosen to reveal to the party. Character-sheet statistics and private backstory are not imported automatically.")
    cards = repo.list_party_cards()
    for card in cards:
        name = card["character_name"] or "Character not yet established"
        st.markdown(f"### {name}")
        st.caption(f"Player: {card['player_name']}")
        st.markdown(f'<div class="portal-card">{card["public_text"]}</div>', unsafe_allow_html=True)
        if not viewer.is_dm and viewer.user_id == card["user_id"]:
            with st.expander("Edit what I share"):
                text = st.text_area("Public party-card text", value=card["public_text"], key=f"party-card-{card['user_id']}")
                if st.button("Publish my card text", key=f"party-save-{card['user_id']}"):
                    repo.save_party_card(viewer, viewer.user_id, text)
                    st.success("Your public card has been updated.")
        st.divider()


def dingoes_crowns(st, repo: PortalRepository, viewer: Viewer, root: Path):
    heading(st, "Dingoes & Crowns", "SHARED TABLE GAME")
    st.markdown((root / "content" / "dnc_rules.md").read_text(encoding="utf-8"))
    state = repo.get_dnc_state()

    st.subheader("The Throw")
    last = state.get("last_roll")
    if last:
        st.markdown(f"## ⚄ {last['dice'][0]} · {last['dice'][1]} · {last['dice'][2]}")
        st.caption(f"Thrown by {last['by']} · total {sum(last['dice'])}")
    else:
        empty_state(st, "No throw has been made yet.")
    c1, c2 = st.columns(2)
    if c1.button("Throw 3d6", use_container_width=True):
        dice = [secrets.randbelow(6) + 1 for _ in range(3)]
        state["last_roll"] = {"dice": dice, "by": viewer.player_name}
        repo.save_dnc_state(viewer, state)
        st.rerun()
    if c2.button("Refresh shared table", use_container_width=True):
        st.rerun()

    st.subheader("Call & Cover")
    with st.form("dnc_call"):
        call = st.text_input("Call / bet")
        stake = st.number_input("Stake", min_value=0, step=1, value=1)
        if st.form_submit_button("Call it publicly") and call.strip():
            state = repo.get_dnc_state()
            state.setdefault("calls", []).append({"by": viewer.player_name, "call": call.strip(), "stake": int(stake)})
            repo.save_dnc_state(viewer, state)
            st.rerun()
    calls = state.get("calls", [])
    if calls:
        for row in reversed(calls[-10:]):
            st.write(f"**{row['by']}** — {row['call']} · stake **{row['stake']}**")
    else:
        empty_state(st, "No public calls yet.")

    st.subheader("Available side bet")
    side_bets = load_yaml(root / "content" / "side_bets.yaml")["bets"]
    if st.button("Generate a side bet"):
        state = repo.get_dnc_state()
        chosen = random.choice(side_bets)
        state["available_bets"] = [chosen]
        repo.save_dnc_state(viewer, state)
        st.rerun()
    if state.get("available_bets"):
        st.markdown(f'<div class="portal-shared"><strong>{state["available_bets"][0]}</strong><br><small>Prototype optional wager; not a core result rule.</small></div>', unsafe_allow_html=True)

    st.subheader("Pot calculator")
    c1, c2, c3 = st.columns(3)
    players = c1.number_input("Players in main pot", min_value=1, value=5, step=1)
    ante = c2.number_input("Ante each", min_value=0, value=1, step=1)
    calls_total = c3.number_input("Additional covered stakes", min_value=0, value=0, step=1)
    st.metric("Main pot", int(players * ante + calls_total))
    with st.expander("Side pot calculator"):
        sp = st.number_input("Players in side pot", min_value=2, value=2, step=1)
        ss = st.number_input("Side stake each", min_value=0, value=1, step=1)
        st.metric("Side pot", int(sp * ss))

    st.subheader("The Climb")
    st.metric("Current Climb", state.get("climb", 0))
    st.caption(state.get("climb_note") or "No Climb note has been set.")
    if viewer.is_dm:
        with st.form("climb_form"):
            climb = st.number_input("Climb value", min_value=0, value=int(state.get("climb", 0)), step=1)
            note = st.text_input("Climb note", value=state.get("climb_note", ""))
            if st.form_submit_button("Update shared Climb"):
                state["climb"] = int(climb)
                state["climb_note"] = note
                repo.save_dnc_state(viewer, state, dm_only=True)
                st.rerun()


def people_places(st, repo: PortalRepository, viewer: Viewer, root: Path):
    heading(st, "People & Places", "PUBLISHED BY THE DM")
    people = repo.list_published_content("person")
    places = repo.list_published_content("place")
    st.subheader("People")
    if not people:
        empty_state(st, "No NPCs have been published to the party yet.")
    for x in people:
        st.markdown(f"### {x['title']}")
        where = x.get("meta", {}).get("where_met")
        if where:
            st.caption(f"Met: {where}")
        st.markdown(x["body"])
        st.divider()
    st.subheader("Places")
    if not places:
        empty_state(st, "No places have been published to the party yet.")
    for x in places:
        st.markdown(f"### {x['title']}")
        st.markdown(x["body"])
        st.divider()


def letters_maps(st, repo: PortalRepository, viewer: Viewer, root: Path):
    heading(st, "Letters & Maps", "HANDOUTS THE PARTY ACTUALLY HAS")
    st.subheader("Original campaign invitation")
    invite_path = root / "assets" / "Priscilla_Player_Invite.pdf"
    st.caption("Archive note: where the invitation and current portal rules differ, the current portal rules govern character creation.")
    st.download_button("Download invitation PDF", invite_path.read_bytes(), file_name="Priscilla_Player_Invite.pdf", mime="application/pdf")

    maps = repo.list_published_content("map")
    letters = repo.list_published_content("letter")
    st.subheader("Maps")
    if not maps:
        empty_state(st, "No campaign maps have been deliberately published here yet.")
    for x in maps:
        st.markdown(f"### {x['title']}")
        st.markdown(x["body"])
    st.subheader("Letters & correspondence")
    if not letters:
        empty_state(st, "No in-world correspondence has been deliberately published here yet.")
    for x in letters:
        st.markdown(f"### {x['title']}")
        st.markdown(x["body"])


def character_creation(st, repo: PortalRepository, viewer: Viewer, root: Path):
    heading(st, "Character Creation", "RULES, QUIRKS & OPTIONAL DISADVANTAGES")
    st.markdown((root / "content" / "character_creation.md").read_text(encoding="utf-8"))
    st.divider()
    st.subheader("Disadvantages for Bonus Feats")
    st.download_button(
        "Download current Disadvantages handout",
        (root / "assets" / "Priscilla_Disadvantages_CURRENT.pdf").read_bytes(),
        file_name="Priscilla_Disadvantages_CURRENT.pdf",
        mime="application/pdf",
    )
    data = load_yaml(root / "content" / "disadvantages.yaml")
    for category, entries in data["categories"].items():
        with st.expander(category):
            for entry in entries:
                st.markdown(f"**{entry['name']}**")
                st.write(f"Roleplay: {entry['roleplay']}")
                st.write(f"Mechanics: {entry['mechanics']}")
                st.divider()


def journal(st, repo: PortalRepository, viewer: Viewer, root: Path):
    heading(st, "Campaign Journal", "WHAT THE PARTY HAS LEARNED")
    recaps = repo.list_published_content("recap")
    transcripts = repo.list_published_content("transcript")
    discoveries = repo.list_published_content("discovery")
    query = st.text_input("Search published journal", placeholder="Search recaps, transcripts, and discoveries")
    if query.strip():
        q = query.casefold().strip()
        def match(x):
            return q in (x.get("title", "") + " " + x.get("body", "")).casefold()
        recaps = [x for x in recaps if match(x)]
        transcripts = [x for x in transcripts if match(x)]
        discoveries = [x for x in discoveries if match(x)]

    st.subheader("Previously on Priscilla…")
    if not recaps:
        empty_state(st, "No polished session recaps have been published yet.")
    for x in recaps:
        st.markdown(f"### {x['title']}")
        st.markdown(x["body"])
        st.divider()
    st.subheader("Shared discoveries")
    if not discoveries:
        empty_state(st, "No shared discoveries have been published yet.")
    for x in discoveries:
        st.markdown(f"### {x['title']}")
        st.markdown(x["body"])
    st.subheader("Published transcripts")
    if not transcripts:
        empty_state(st, "No raw transcripts have been deliberately published. Recaps and transcripts remain separate.")
    for x in transcripts:
        st.markdown(f"### {x['title']}")
        st.markdown(x["body"])


def my_notes(st, repo: PortalRepository, viewer: Viewer, root: Path):
    heading(st, "My Notes", "PRIVATE & PERSISTENT")
    if viewer.is_dm:
        st.info("Player notes can be reviewed from the DM Panel. DM campaign-development notes intentionally do not live in this repository.")
        return
    st.markdown('<div class="portal-private"><strong>Private:</strong> these notes are stored in SQLite, not only in browser session state.</div>', unsafe_allow_html=True)
    with st.form("new_note", clear_on_submit=True):
        title = st.text_input("Title")
        body = st.text_area("Note", height=180)
        attachment_type = st.selectbox("Attach to", ["None", "NPC", "Place", "Map", "Session"])
        attachment_id = st.text_input("Optional known item/session label") if attachment_type != "None" else ""
        if st.form_submit_button("Save note"):
            if not title.strip():
                st.error("Give the note a title.")
            else:
                repo.save_note(viewer, title.strip(), body, attachment_type=None if attachment_type == "None" else attachment_type.lower(), attachment_id=attachment_id or None)
                st.success("Saved.")
                st.rerun()
    notes = repo.list_notes(viewer)
    if not notes:
        empty_state(st, "You do not have any notes yet.")
        return
    export = ["# My Priscilla Notes", ""]
    for note in notes:
        export.extend([f"## {note['title']}", note["body"], ""])
        with st.expander(note["title"]):
            body = st.text_area("Edit note", value=note["body"], key=f"note-body-{note['id']}", height=150)
            c1, c2 = st.columns(2)
            if c1.button("Save changes", key=f"note-save-{note['id']}"):
                repo.save_note(viewer, note["title"], body, note_id=note["id"], attachment_type=note.get("attachment_type"), attachment_id=note.get("attachment_id"))
                st.success("Updated.")
                st.rerun()
            if c2.button("Delete", key=f"note-delete-{note['id']}"):
                repo.delete_note(viewer, note["id"])
                st.rerun()
    st.download_button("Export all my notes as Markdown", "\n".join(export).encode("utf-8"), file_name="Priscilla_My_Notes.md", mime="text/markdown")


def dm_panel(st, repo: PortalRepository, viewer: Viewer, root: Path):
    if not viewer.is_dm:
        st.error("DM access only.")
        return
    heading(st, "DM Panel", "PLAYER-PORTAL PUBLISHING & REVIEW")
    st.warning("This panel is only for material approved to enter the Player Portal. Unrevealed DM lore, future encounters, secret locations, and development notes belong elsewhere.")

    tabs = st.tabs(["Prompt review", "Voyage NPCs", "Private items", "Publish shared content", "Player notes", "D&C table"])
    with tabs[0]:
        rows = repo.list_prompt_reviews(viewer)
        if not rows:
            empty_state(st, "No private prompt answers yet.")
        for row in rows:
            with st.expander(f"{row['player_name']} · {row['prompt_key']} · {row['status']}"):
                body_edit = st.text_area("Private answer", value=row["body"], key=f"pr-body-{row['id']}", height=140)
                notes = st.text_area("DM notes", value=row["dm_notes"], key=f"pr-notes-{row['id']}")
                status = st.selectbox("Status", ["draft", "submitted", "approved", "needs_changes"], index=["draft", "submitted", "approved", "needs_changes"].index(row["status"]) if row["status"] in ["draft", "submitted", "approved", "needs_changes"] else 0, key=f"pr-status-{row['id']}")
                if st.button("Save review", key=f"pr-save-{row['id']}"):
                    repo.dm_review_prompt(viewer, row["id"], status, notes, body=body_edit)
                    st.success("Review saved.")

    with tabs[1]:
        rows = repo.list_voyage_npcs(viewer)
        if not rows:
            empty_state(st, "No voyage NPC submissions yet.")
        for row in rows:
            with st.expander(f"{row['name']} · submitted by {row['player_name']} · {row['status']}"):
                edit_name = st.text_input("Name", value=row["name"], key=f"vn-name-{row['id']}")
                edit_role = st.text_input("Role aboard ship", value=row["ship_role"], key=f"vn-role-{row['id']}")
                edit_memorable = st.text_area("Memorable detail", value=row["memorable_detail"], key=f"vn-mem-{row['id']}")
                edit_why = st.text_area("Why remembered", value=row["why_remembered"], key=f"vn-why-{row['id']}")
                edit_relationship = st.text_input("Relationship", value=row["relationship"], key=f"vn-rel-{row['id']}")
                st.write(f"**Party permission:** {'Yes' if row['party_permission'] else 'No'}")
                notes = st.text_area("DM notes", value=row["dm_notes"], key=f"vn-notes-{row['id']}")
                status = st.selectbox("Status", ["draft", "submitted", "approved", "needs_changes"], key=f"vn-status-{row['id']}", index=2 if row['status']=="approved" else 1 if row['status']=="submitted" else 0)
                publish = st.checkbox("Publish to People & Places now (only works if player granted permission)", key=f"vn-pub-{row['id']}")
                if st.button("Save NPC review", key=f"vn-save-{row['id']}"):
                    repo.dm_review_voyage_npc(viewer, row["id"], status, notes, publish=publish, updates={
                        "name": edit_name, "ship_role": edit_role, "memorable_detail": edit_memorable,
                        "why_remembered": edit_why, "relationship": edit_relationship,
                    })
                    if publish and not row["party_permission"]:
                        st.warning("Not published: the player has not granted party permission.")
                    else:
                        st.success("Review saved.")

    with tabs[2]:
        st.caption("The focused PC_CARDS_AND_MAGIC_ITEMS_SEED.md source was not available to this build, so private items are intentionally not prepopulated. Enter approved item text here rather than guessing.")
        for p in repo.list_players():
            item = repo.get_private_item(viewer, p["user_id"]) or {"title": "", "mechanics": "", "dm_notes": ""}
            with st.expander(f"{p['player_name']} · {p['character_name'] or 'character not established'}"):
                title = st.text_input("Item name", value=item["title"], key=f"item-title-{p['user_id']}")
                mechanics = st.text_area("Private mechanics / player-facing description", value=item["mechanics"], key=f"item-mech-{p['user_id']}", height=160)
                dm_notes = st.text_area("DM-only note within the portal", value=item["dm_notes"], key=f"item-note-{p['user_id']}")
                if st.button("Save private item", key=f"item-save-{p['user_id']}"):
                    repo.save_private_item(viewer, p["user_id"], title, mechanics, dm_notes)
                    st.success("Saved privately.")

    with tabs[3]:
        with st.form("publish_content", clear_on_submit=True):
            kind = st.selectbox("Type", ["person", "place", "map", "letter", "recap", "transcript", "discovery"])
            title = st.text_input("Title")
            body = st.text_area("Shared text", height=180)
            where_met = st.text_input("Where met / context (optional)")
            if st.form_submit_button("Publish to players"):
                if not title.strip():
                    st.error("Title is required.")
                else:
                    repo.add_published_content(viewer, kind, title.strip(), body, {"where_met": where_met} if where_met else {})
                    st.success("Published.")

    with tabs[4]:
        for p in repo.list_players():
            notes = repo.list_notes(viewer, p["user_id"])
            with st.expander(f"{p['player_name']} · {len(notes)} note(s)"):
                if not notes:
                    st.caption("No notes.")
                for n in notes:
                    st.markdown(f"**{n['title']}**")
                    st.write(n["body"])
                    st.divider()

    with tabs[5]:
        state = repo.get_dnc_state()
        st.json(state)
        if st.button("Clear public calls"):
            state["calls"] = []
            repo.save_dnc_state(viewer, state, dm_only=True)
            st.rerun()
        if st.button("Clear current throw"):
            state["last_roll"] = None
            repo.save_dnc_state(viewer, state, dm_only=True)
            st.rerun()
