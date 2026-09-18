# Priscilla Player Portal — Public Hub

This build starts from the richer Streamlit portal that already contained the working
Dingoes & Crowns implementation.

## What changed

- Removed the PIN / player-login flow from the app.
- Removed private-player pages from navigation.
- Preserved the original backend architecture.
- Preserved the original working D&C code in `portal/pages.py`.
- D&C is currently **locked / Coming Soon**.
- The public hub now focuses on:
  - Home
  - The Invitation
  - Voyage Prep
  - The Party
  - Known World
  - visible locked future sections
- Added the Sunday schedule.
- Added the starting map.
- Made normal wording/settings editable without touching Python.

## Files Sean can edit

- `content/settings.yaml` — schedule wording and home image filename
- `content/home.md` — home wording
- `content/voyage.md` — Voyage Prep wording/examples
- `content/party.yaml` — player/character roster and portrait filenames
- `content/coming_soon.yaml` — locked-page wording
- `assets/` — images and handouts

## Dingoes & Crowns

The original working implementation is still preserved in:

`portal/pages.py` → `dingoes_crowns(...)`

The current navigation does not expose it. Players see a locked Coming Soon page instead.

## GitHub / Streamlit

Upload the contents of this ZIP into the root of the existing GitHub repository,
replacing matching files.

Streamlit stays on:
- branch: `main`
- main file: `app.py`


## Current small revisions

- Voyage Prep is the second navigation item.
- The Invitation is viewed directly in the app; no download is required.
- The Home harbor art was recropped as a clean wide banner.
