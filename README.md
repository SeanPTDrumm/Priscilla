# Priscilla Player Portal

Player-facing Streamlit portal for **Priscilla, Queen of the Desert**.

## What is included

- Branded campaign home page
- Before You Arrive / player handouts
- Voyage Prep form with downloadable player note
- Magic item gallery
- Dingoes & Crowns 3d6 prototype
- Starting map / Road Moas
- Locked teaser sections for future campaign discoveries

## Files

- `app.py` — the Streamlit app
- `requirements.txt` — dependencies
- `assets/` — current campaign art and handouts

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy with Streamlit Community Cloud

1. Put these files in your GitHub repository.
2. In Streamlit Community Cloud, create a new app.
3. Choose the repository and branch.
4. Set the main file path to `app.py`.
5. Deploy.

## Important design rule

This is the **player portal**, not the DM Codex. Do not add unrevealed campaign canon,
DM notes, succession material, or hidden NPC information here.

## Current intentionally unfinished area

The full betting / payout rules for **Dingoes & Crowns** are not yet locked. The current
page provides the shared 3d6 throw and identifies Crown / Pair / Road / Dingoes.
