from pathlib import Path
import base64
import html
import streamlit as st
import streamlit.components.v1 as components

BASE = Path(__file__).parent
ASSETS = BASE / "assets"

st.set_page_config(
    page_title="Priscilla, Queen of the Desert",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- visual system ----------
st.markdown("""
<style>
:root {
  --ink:#241b16;
  --red:#741b16;
  --gold:#b7863a;
  --paper:#efe2bf;
  --paper2:#f7edcf;
  --night:#111a28;
}
.stApp {
  background:
    radial-gradient(circle at top right, rgba(135,91,48,.10), transparent 28rem),
    linear-gradient(180deg, #f3e8c8 0%, #eadab1 100%);
  color:var(--ink);
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg,#111722 0%,#1b1819 100%);
  border-right:1px solid rgba(183,134,58,.35);
}
[data-testid="stSidebar"] * { color:#f0e2bf; }
[data-testid="stSidebar"] .stRadio label { padding:.25rem 0; }
.block-container { padding-top:1.25rem; max-width:1180px; }
h1,h2,h3 {
  font-family: Georgia, 'Times New Roman', serif;
  color:var(--red);
}
.hero-wrap {
  border:1px solid rgba(183,134,58,.55);
  border-radius:18px;
  overflow:hidden;
  box-shadow:0 12px 34px rgba(26,18,12,.18);
  margin-bottom:1rem;
  background:#101721;
}
.session-card {
  background:linear-gradient(135deg,#751d18,#401819);
  color:#fff5dc;
  border:1px solid rgba(255,221,150,.35);
  border-radius:16px;
  padding:1rem 1.25rem;
  box-shadow:0 8px 22px rgba(65,20,17,.20);
}
.session-card .big {font:700 1.55rem Georgia,serif;}
.session-card .small {color:#ecd7ab; letter-spacing:.05em;}
.portal-card {
  background:rgba(255,255,255,.36);
  border:1px solid rgba(83,56,32,.28);
  border-radius:15px;
  padding:1rem 1.1rem;
  min-height:150px;
  box-shadow:0 4px 15px rgba(63,42,24,.07);
}
.portal-card h3 {margin:.1rem 0 .5rem 0;}
.portal-card.locked {
  background:rgba(56,47,44,.08);
  border-style:dashed;
  opacity:.78;
}
.eyebrow {
  color:#7b5d36;
  text-transform:uppercase;
  letter-spacing:.16em;
  font-size:.76rem;
  font-weight:700;
}
.soft {
  color:#665447;
}
.voyage-prompt {
  padding:1rem 1.15rem;
  border-left:4px solid #8c2820;
  background:rgba(255,255,255,.28);
  border-radius:8px;
}
.example {
  background:rgba(112,74,39,.07);
  border-radius:10px;
  padding:.65rem .8rem;
  margin:.35rem 0;
}
.party-card {
  padding:.9rem 1rem;
  border:1px solid rgba(87,55,28,.25);
  border-radius:12px;
  background:rgba(255,255,255,.32);
  margin-bottom:.65rem;
}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

def asset_path(name):
    return ASSETS / name

def show_svg(name):
    p = asset_path(name)
    if p.exists():
        st.image(str(p), use_container_width=True)

def download_file(name, label):
    p = asset_path(name)
    if p.exists():
        with open(p, "rb") as f:
            st.download_button(label, f, file_name=p.name, use_container_width=True)

def render_pdf(name, height=890):
    p = asset_path(name)
    if not p.exists():
        st.warning("PDF asset not found.")
        return
    data = base64.b64encode(p.read_bytes()).decode("utf-8")
    components.html(
        f'<iframe src="data:application/pdf;base64,{data}" '
        f'width="100%" height="{height}" style="border:0;border-radius:12px;"></iframe>',
        height=height + 10,
        scrolling=True,
    )

# ---------- navigation ----------
st.sidebar.markdown("## PRISCILLA")
st.sidebar.caption("QUEEN OF THE DESERT")
page = st.sidebar.radio(
    "Portal",
    ["Home", "The Invitation", "The Voyage", "The Party", "Known World", "Coming Soon"],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")
st.sidebar.markdown("**Sundays · 6:00 PM**")
st.sidebar.caption("Wrap by 8:30–9:00 PM at the latest.")

# ---------- home ----------
if page == "Home":
    st.markdown('<div class="eyebrow">Player Portal</div>', unsafe_allow_html=True)
    show_svg("arrival_night.svg")

    st.markdown("""
    <div class="session-card">
      <div class="small">OUR REGULAR GAME</div>
      <div class="big">Sunday · 6:00 PM</div>
      <div>We will wrap by <b>8:30–9:00 PM at the latest.</b></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## Welcome to Teralis")
    st.write(
        "A few hours before dawn, your ship entered the crowded harbor of Sydire. "
        "This portal is the place for campaign handouts, the map, pre-game odds and ends, "
        "and — once play begins — the things your party discovers."
    )

    st.markdown("### What you need now")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="portal-card">
          <div class="eyebrow">Available now</div>
          <h3>The Invitation</h3>
          <p>The original campaign invite, character setup, Discord and D&D Beyond links.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="portal-card">
          <div class="eyebrow">One tiny bit of homework</div>
          <h3>The Voyage</h3>
          <p>Give Sean one person your character met during the crossing. One sentence is enough.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="portal-card">
          <div class="eyebrow">Player reference</div>
          <h3>Known World</h3>
          <p>Your starting map and the bits of Teralis the party is allowed to know.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### This portal will grow with the campaign")
    d1, d2, d3, d4 = st.columns(4)
    for col, title, text in [
        (d1, "🎲 Dingoes & Crowns", "Interactive table game — coming soon."),
        (d2, "📖 Campaign Log", "Sessions, choices and consequences."),
        (d3, "🧭 People & Places", "Faces and locations you discover."),
        (d4, "✉️ Letters & Handouts", "Clues, notes, documents and other suspicious paperwork."),
    ]:
        with col:
            st.markdown(
                f'<div class="portal-card locked"><div class="eyebrow">Coming soon</div>'
                f'<h3>{title}</h3><p>{text}</p></div>',
                unsafe_allow_html=True,
            )

# ---------- invitation ----------
elif page == "The Invitation":
    st.title("The Invitation")
    st.write("The original player invitation and pre-game setup, kept here so nobody has to hunt for it.")
    download_file("player_invite.pdf", "Download the original invitation")
    with st.expander("View the invitation here", expanded=True):
        render_pdf("player_invite.pdf")

# ---------- voyage ----------
elif page == "The Voyage":
    show_svg("voyage_night.svg")
    st.title("Someone You Met on the Voyage")
    st.markdown("""
    <div class="voyage-prompt">
      Your character spent roughly <b>three months aboard a crowded passenger ship</b> before reaching Teralis.
      Give Sean <b>one person your character met or got to know during the crossing.</b>
      <br><br>
      This does not need to be a backstory. A vague sentence is completely fine.
      If inspiration strikes, you can make them as elaborate as you want.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Easy examples")
    examples = [
        "An older passenger I played cards with most nights.",
        "A sailor I drank with a few times. We liked each other well enough.",
        "A merchant who annoyed me for almost the entire crossing.",
        "A kid who kept asking questions about my weapon.",
        "Someone who was terribly seasick and I ended up helping.",
        "A passenger I became genuinely close to. I have more ideas about them.",
        "I know almost nothing yet — just that we talked often on deck at night.",
    ]
    for ex in examples:
        st.markdown(f'<div class="example">“{ex}”</div>', unsafe_allow_html=True)

    st.caption("No name required. No stat block. No essay. One useful hook is enough.")

    st.markdown("### How did you get the instructions?")
    st.write(
        "**Default:** Captain Dick Boatman gave you the map / instructions aboard ship. "
        "You do not need to invent anything else."
    )
    st.write(
        "If you would rather have received them from someone else, tell Sean who — "
        "the NPC above, another passenger, a sailor, somebody waiting at a previous port, etc."
    )

    with st.form("voyage_note"):
        character = st.text_input("Character name (optional)")
        npc = st.text_area(
            "The person I met on the voyage",
            placeholder="One sentence is enough. Or write a lot. Entirely up to you.",
            height=120,
        )
        use_default = st.checkbox(
            "Captain Dick Boatman gave me the map / instructions.",
            value=True,
        )
        other_source = ""
        if not use_default:
            other_source = st.text_input("Who gave them to you instead?")
        submit = st.form_submit_button("Make my voyage note")

    if submit:
        source = "Captain Dick Boatman." if use_default else (other_source.strip() or "[not decided yet]")
        note = (
            f"PRISCILLA — VOYAGE NOTE\n\n"
            f"Character: {character.strip() or '[not provided]'}\n\n"
            f"Someone I met on the voyage:\n{npc.strip() or '[not provided]'}\n\n"
            f"Who gave me the map / instructions:\n{source}\n"
        )
        st.success("That is plenty.")
        st.code(note, language=None)
        st.download_button(
            "Download this note",
            note,
            file_name=f"{(character.strip() or 'priscilla')}_voyage_note.txt".replace(" ", "_"),
            use_container_width=True,
        )

# ---------- party ----------
elif page == "The Party":
    st.title("The Party")
    st.write(
        "A light pre-game roster for now. This page can get portraits, public character blurbs "
        "and whatever else feels useful before Session 1."
    )

    known = [
        ("Matt", "Elysia Dawnbringer", "Paladin · devotee of Sune"),
        ("Nick", "Wiccan", "Shadar-kai Warlock · Archfey patron"),
        ("Greg", "Melvin Half-Elvin", "Bard · wizard-for-hire, allegedly"),
        ("Jared", "Dwarf Fighter", "Name / public introduction coming soon"),
        ("Bradley", "Character card coming soon", "Details still being added"),
    ]
    cols = st.columns(2)
    for i, (player, pc, blurb) in enumerate(known):
        with cols[i % 2]:
            st.markdown(
                f'<div class="party-card"><div class="eyebrow">{html.escape(player)}</div>'
                f'<h3>{html.escape(pc)}</h3><div class="soft">{html.escape(blurb)}</div></div>',
                unsafe_allow_html=True,
            )

# ---------- known world ----------
elif page == "Known World":
    st.title("Known World")
    st.write(
        "You are outsiders. What your characters know may be rumor, scholarship, religion, "
        "old sailors' tales, or something learned before the crossing. Different characters "
        "may know different things."
    )
    p = asset_path("map.png")
    if p.exists():
        st.image(str(p), caption="Your starting map", use_container_width=True)
        with open(p, "rb") as f:
            st.download_button("Download the map", f, file_name="Teralis_starting_map.png", use_container_width=True)
    with st.expander("Road Moas"):
        st.write("Large flightless draft birds used for overland travel in Teralis.")
        p2 = asset_path("moas.png")
        if p2.exists():
            st.image(str(p2), use_container_width=True)

# ---------- coming soon ----------
elif page == "Coming Soon":
    st.title("Coming Soon")
    st.write("You can see the doors. Most of them are not open yet.")
    cards = [
        ("🎲 Dingoes & Crowns", "An interactive version of Teralis's extremely reputable dice game."),
        ("📖 Campaign Log", "A player-facing record of sessions, major choices and the road behind you."),
        ("🧭 People & Places", "NPCs, cities, inns, shops and landmarks as the party encounters them."),
        ("✉️ Letters & Handouts", "Documents, clues, invitations, notices and other things somebody probably should not have written down."),
    ]
    for title, body in cards:
        st.markdown(
            f'<div class="portal-card locked"><div class="eyebrow">Locked</div>'
            f'<h3>{title}</h3><p>{body}</p></div>',
            unsafe_allow_html=True,
        )
