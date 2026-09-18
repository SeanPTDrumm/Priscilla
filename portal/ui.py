from __future__ import annotations

from pathlib import Path

import yaml

CSS = r"""
<style>
:root {
  --ink:#281f18;
  --parchment:#efe0b8;
  --parchment-2:#f6edcf;
  --wine:#7f1d1d;
  --gold:#b99245;
  --night:#171b1c;
  --night-2:#22282a;
}
html, body, [class*="css"] { font-family: Georgia, 'Palatino Linotype', serif; }
.stApp { background: linear-gradient(180deg,#141719,#1b1d1d); }
[data-testid="stSidebar"] { background:#121617; border-right:1px solid #55452d; }
[data-testid="stSidebar"] * { color:#eadfbd; }
.block-container {
  max-width: 1120px;
  background: linear-gradient(180deg,var(--parchment-2),var(--parchment));
  color: var(--ink);
  border: 1px solid #7b6745;
  border-radius: 10px;
  box-shadow: 0 16px 44px rgba(0,0,0,.35);
  padding: 2.1rem 2.5rem 3rem;
  margin-top: 1.35rem;
  margin-bottom: 2rem;
}
h1,h2,h3,h4 { font-family: Georgia, 'Palatino Linotype', serif; color:#521515 !important; letter-spacing:.01em; }
h1 { border-bottom:1px solid #a7894e; padding-bottom:.45rem; }
p,li,label,.stMarkdown { color:var(--ink); }
.portal-kicker { text-transform:uppercase; letter-spacing:.18em; font-size:.75rem; color:#6f5a34; }
.portal-card { border:1px solid #b79b63; background:rgba(255,250,230,.55); padding:1rem 1.1rem; border-radius:8px; margin:.55rem 0 1rem; }
.portal-empty { border:1px dashed #a88d58; padding:1.2rem; border-radius:8px; color:#66573c; background:rgba(255,255,255,.2); }
.portal-private { border-left:4px solid #7f1d1d; background:#f4e7c5; padding:.8rem 1rem; margin:.6rem 0 1rem; }
.portal-shared { border-left:4px solid #8e733e; background:#f5e9c8; padding:.8rem 1rem; margin:.6rem 0 1rem; }
.stButton>button, .stDownloadButton>button { border:1px solid #7f1d1d; background:#7f1d1d; color:#fff5db; border-radius:6px; }
.stButton>button:hover, .stDownloadButton>button:hover { border-color:#9c762c; background:#651717; color:#fff; }
[data-baseweb="input"] input, textarea, [data-baseweb="select"] > div { background:#fff8df !important; color:#281f18 !important; }
hr { border-color:#b99b60; }

.portal-session {
  border-top:1px solid #a7894e;
  border-bottom:1px solid #a7894e;
  padding:1.1rem .4rem;
  margin:1rem 0 .25rem;
  text-align:center;
}
.portal-session-main {
  font-size:1.55rem;
  font-weight:700;
  color:#521515;
  margin-bottom:.2rem;
}
</style>

"""


def apply_theme(st) -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def empty_state(st, text: str) -> None:
    st.markdown(f'<div class="portal-empty">{text}</div>', unsafe_allow_html=True)


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))
