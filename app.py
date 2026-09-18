from pathlib import Path
import random
import streamlit as st

BASE = Path(__file__).parent
ASSETS = BASE / "assets"

st.set_page_config(
    page_title="Priscilla, Queen of the Desert",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- styling ----------
st.markdown("""
<style>
    .stApp {
        background: #efe2bf;
        color: #271d17;
    }
    [data-testid="stSidebar"] {
        background: #1d1714;
    }
    [data-testid="stSidebar"] * {
        color: #f1e2bd;
    }
    h1, h2, h3 {
        color: #741b16;
        font-family: Georgia, 'Times New Roman', serif;
    }
    .priscilla-card {
        background: rgba(255,255,255,.34);
        border: 1px solid rgba(87,55,28,.35);
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        margin: .5rem 0 1rem 0;
        box-shadow: 0 2px 10px rgba(55,35,20,.08);
    }
    .locked {
        opacity: .7;
        border: 1px dashed rgba(116,27,22,.55);
        border-radius: 12px;
        padding: 1rem;
        background: rgba(116,27,22,.05);
    }
    .smallcaps {
        letter-spacing: .12em;
        text-transform: uppercase;
        font-size: .78rem;
        font-weight: 700;
    }
    .quote {
        font-family: Georgia, 'Times New Roman', serif;
        font-style: italic;
        font-size: 1.08rem;
        color: #5b4030;
    }
</style>
""", unsafe_allow_html=True)

def img(name, caption=None, use_container_width=True):
    p = ASSETS / name
    if p.exists():
        st.image(str(p), caption=caption, use_container_width=use_container_width)

def download_asset(filename, label):
    p = ASSETS / filename
    if p.exists():
        with open(p, "rb") as f:
            st.download_button(label, f, file_name=filename)

# ---------- navigation ----------
st.sidebar.markdown("## PRISCILLA")
st.sidebar.caption("Queen of the Desert")
page = st.sidebar.radio(
    "Navigate",
    [
        "Home",
        "Before You Arrive",
        "Voyage Prep",
        "Magic Items",
        "Dingoes & Crowns",
        "Known World",
        "Locked",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.caption("Player portal • D&D 2024 • Level 3")

# ---------- home ----------
if page == "Home":
    img("title_page.png")
    st.markdown("## Welcome to Teralis")
    st.markdown(
        """
        You crossed an ocean to get here.

        A few hours before dawn, your ship entered the crowded harbor of **Sydire**.
        You arrived with whatever you could carry, a few dubious stories about the
        country beyond its walls, and a map whose usefulness remains to be seen.
        """
    )
    st.markdown(
        """
        <div class="priscilla-card">
        <div class="smallcaps">The instruction you can read clearly</div>
        <h3 style="margin-bottom:.2rem;">GO TO THE BLUE OYSTER INN.</h3>
        <h3 style="margin:.2rem 0;">ASK FOR LAVINE.</h3>
        <h3 style="margin:.2rem 0;">SAY THE CAPTAIN SENT YOU.</h3>
        <p>Someone there is waiting for you. <b>And they have 50 gold pieces.</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("You know almost nothing about Teralis. That is intentional.")

# ---------- before you arrive ----------
elif page == "Before You Arrive":
    st.title("Before You Arrive")
    st.markdown("### Build the fun stuff")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Level 3**")
        st.markdown("**D&D 2024 rules**")
        st.markdown("**Standard Array or Point Buy**")
    with c2:
        st.markdown("**You are an outsider.**")
        st.markdown("Your character has recently arrived from overseas.")
    st.markdown(
        """
        **Backstory:** loose concepts are welcome. This should not feel like homework.

        **Quirks:** small habits, preferences, superstitions, mannerisms, beliefs,
        physical oddities, or other details that make the character feel like a person.
        Start with a couple; you may eventually have five.

        **A little something extra:** every character begins with one special magic item
        at DM discretion.

        **Optional disadvantage:** one meaningful mechanical Disadvantage may be taken
        in exchange for one additional Feat.
        """
    )
    col1, col2 = st.columns(2)
    with col1:
        download_asset("player_invite.pdf", "Download Player Invite")
    with col2:
        download_asset("disadvantages.pdf", "Download Disadvantages Handout")

# ---------- voyage prep ----------
elif page == "Voyage Prep":
    st.title("The Voyage")
    st.markdown(
        """
        The crossing took roughly **three months**. You do not need to write a novella.
        Give Sean a few useful hooks and we can build the rest together.
        """
    )
    with st.form("voyage_form"):
        character = st.text_input("Character name")
        why = st.text_area(
            "Why did your character make the voyage to Teralis?",
            placeholder="Adventure? Exile? Following someone? Running from something? Starting over?",
        )
        npc = st.text_area(
            "Who did you meet and get to know aboard the crowded passenger ship?",
            placeholder="A name and a sentence or two is plenty. Invent them or leave Sean room to help.",
        )
        map_origin = st.text_area(
            "How did the map / Blue Oyster instruction reach you?",
            placeholder="Optional. If you leave this blank, Captain Dick Boatman handed it to you.",
        )
        submitted = st.form_submit_button("Prepare my voyage note")
    if submitted:
        map_text = map_origin.strip() or "Captain Dick Boatman handed it to me aboard ship."
        note = f"""PRISCILLA — VOYAGE NOTE

Character: {character or "[unnamed]"}

WHY I CAME TO TERALIS
{why or "[not answered]"}

SOMEONE I MET ABOARD SHIP
{npc or "[not answered]"}

HOW I GOT THE MAP
{map_text}
"""
        st.success("Done. Download this and send it to Sean.")
        st.download_button(
            "Download voyage note",
            note,
            file_name=f"{(character or 'character').replace(' ', '_')}_voyage_note.txt",
        )

# ---------- magic items ----------
elif page == "Magic Items":
    st.title("A Little Something Extra")
    st.caption("Each character begins with one special magic item.")

    items = [
        ("Melvin Half-Elvin", "Melvin's Hat", "melvins_hat.png",
         "+1 Charisma (maximum 20), plus a once-per-dawn reach into the hat for a random prize."),
        ("Jared's Dwarf Fighter", "The Red Pike", "red_pike.png",
         "+1 magical pike. A grisly finishing blow can frighten nearby foes."),
        ("Druid", "The Many-Shaped Clasp", "many_shaped_clasp.png",
         "+1 attack and damage while Wild Shaped, a lingering beast trait after shifting, and one Instinctive Shift per Long Rest."),
    ]
    for owner, title, image_name, blurb in items:
        st.markdown(f"### {title}")
        st.caption(owner)
        cols = st.columns([1.2, 1])
        with cols[0]:
            img(image_name)
        with cols[1]:
            st.markdown(f'<div class="priscilla-card">{blurb}</div>', unsafe_allow_html=True)

    st.markdown("### Sune's Hand Mirror")
    st.caption("Elysia Dawnbringer")
    st.markdown(
        """
        <div class="priscilla-card">
        <b>Grace of Sune:</b> +1 Charisma, maximum 20.<br><br>
        <b>Allure:</b> once per Short Rest.<br>
        <b>Heartthrob:</b> once per Long Rest.<br>
        <b>The Cruel Reflection:</b> a proposed last-resort use of <i>Suggestion</i>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Sickle of the First Court")
    st.caption("Wiccan")
    st.markdown(
        """
        <div class="priscilla-card">
        A ritual sickle and spellcasting focus tied to the First Court. It grants +1 to
        spell attacks, manifests Wiccan's spectral hand, and can borrow unpredictable
        magical power.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- Dingoes & Crowns ----------
elif page == "Dingoes & Crowns":
    st.title("Dingoes & Crowns")
    st.markdown(
        """
        A table game played with **3d6**.

        **ANTE → CALL & COVER → THROW → PAY**
        """
    )

    if "dc_roll" not in st.session_state:
        st.session_state.dc_roll = None

    if st.button("🎲 THROW THE DICE", type="primary", use_container_width=True):
        dice = [random.randint(1, 6) for _ in range(3)]
        st.session_state.dc_roll = dice

    if st.session_state.dc_roll:
        dice = st.session_state.dc_roll
        a, b, c = dice
        st.metric("Throw", f"{a}  •  {b}  •  {c}")
        counts = {n: dice.count(n) for n in set(dice)}
        if len(counts) == 1:
            st.success("CROWN — three of a kind.")
        elif 2 in counts.values():
            st.info("PAIR — two dice match.")
        elif sorted(dice) in ([1,2,3],[2,3,4],[3,4,5],[4,5,6]):
            st.success("ROAD — a three-number run.")
        else:
            st.warning("DINGOES — no Crown, Pair, or Road.")

    st.markdown(
        """
        <div class="priscilla-card">
        <b>Current table concept:</b> NPCs can originate or cover side bets.
        This page is intentionally lightweight until the final betting/pay rules are locked.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- known world ----------
elif page == "Known World":
    st.title("What You Know")
    st.markdown(
        """
        Your character is an outsider. What they know may be rumor, scholarship,
        religion, old sailors' tales, or something learned before the crossing.
        Different characters may know different things.
        """
    )
    img("map.png", caption="Your starting map")
    with st.expander("Road Moas"):
        img("moas.png")
        st.write("Large flightless draft birds used for overland travel in Teralis.")

# ---------- locked ----------
elif page == "Locked":
    st.title("Beyond Sydire")
    st.markdown(
        """
        <div class="locked">
        🔒 <b>Locations</b><br>
        More of Teralis will appear here as you discover it.
        </div><br>
        <div class="locked">
        🔒 <b>People & Factions</b><br>
        Names, faces and relationships will unlock through play.
        </div><br>
        <div class="locked">
        🔒 <b>Campaign Journal</b><br>
        Your story has not happened yet.
        </div>
        """,
        unsafe_allow_html=True,
    )
