# Build Notes — Editable Player Portal Refresh

## Goal

Reset the Player Portal around one simple rule: normal campaign maintenance should happen **inside the portal**, not by hand-editing Python or Markdown in GitHub.

## Current public structure

- Home
- Voyage Prep
- The Party
- Known World
- Episodes
- Dingoes & Crowns — locked
- People & Places — locked
- Homebrew & Common Law
- Edit Portal

## Episodes

Campaign Journal has been replaced by **Episodes**.

Episode 1 is included as:

**The One With Dingoes & Crowns**

Episode metadata lives in `content/episodes/index.yaml`, while recap bodies live in individual Markdown files. The Edit Portal UI manages both.

## Persistence

Streamlit Community Cloud local disk is not reliable across redeploys. The new persistence layer in `portal/storage.py` therefore supports committing edits back to the GitHub repository through the GitHub Contents API.

When `GITHUB_TOKEN` and `GITHUB_REPO` are configured in Streamlit Secrets:

- editor changes persist
- party blurbs persist
- party portrait uploads persist

Without those secrets, changes still work in the current running instance but may disappear after a redeploy.

## Party profiles

The old `open_party_profiles` SQLite workflow is no longer used by the public Party page. Player text now lives in `content/party_profiles/` and portraits in `assets/party_portraits/`, allowing the same GitHub-backed persistence model as the rest of the portal.

## Preserved legacy code

The original repository/database modules and the earlier Dingoes & Crowns prototype remain in place so useful work is not destroyed during the reset. They are not used for ordinary editable portal content.
