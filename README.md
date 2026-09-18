# Priscilla Player Portal — V2

A lightweight player-facing hub for **Priscilla, Queen of the Desert**.

This version intentionally removes character-management and magic-item sections.
The immediate purpose is to give the players one attractive place for:

- the recurring Sunday schedule
- the original invitation
- one low-pressure Voyage prompt
- a light Party roster
- the starting map / Known World
- visible locked sections that will open as the campaign develops

## Schedule shown in the app

**Sunday — 6:00 PM**

Wrap by **8:30–9:00 PM at the latest**.

## Replace the existing GitHub files

Upload the contents of this folder into the root of the existing `Priscilla` repository.

Replace:
- `app.py`
- `README.md`
- `requirements.txt`

Keep/upload the included `assets/` files.

Streamlit should continue using:

- Branch: `main`
- Main file path: `app.py`

Once GitHub commits the replacement, Streamlit Community Cloud should normally rebuild automatically.

## Easy art swaps later

The two portal-specific banner files are:

- `assets/arrival_night.svg`
- `assets/voyage_night.svg`

They are intentionally separate from the app code so they can be replaced later with finished approved campaign paintings without rewriting the app.
