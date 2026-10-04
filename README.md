# Priscilla Player Portal — Editable Build

This is the refreshed public player portal for **Priscilla, Queen of the Desert**.

## What changed

- **Campaign Journal** is now **Episodes**.
- Episode 1 is included as **The One With Dingoes & Crowns**.
- Added an in-app **Edit Portal** page.
- You can edit the Home page, Voyage Prep, Known World intro, session schedule, locked-page text, and all Episodes **without touching Python**.
- You can create Episode 2, Episode 3, and so on directly in the app.
- Party blurbs and portraits no longer use the old SQLite profile table. They are saved as normal repository files.
- The original Dingoes & Crowns implementation is preserved in `portal/pages.py` and remains locked for now.

## The one important setup: make Save permanent

Streamlit Community Cloud can erase files written only to its local disk during a redeploy. This build therefore knows how to save edits **back to your GitHub repository**.

You only have to configure this once.

### 1. Create a GitHub fine-grained personal access token

In GitHub, create a fine-grained token that has access only to this Priscilla repository and grant it:

- **Contents: Read and write**

You do not need broader account permissions.

### 2. Add these to Streamlit Secrets

Open the deployed Streamlit app settings → **Secrets** and add:

```toml
GITHUB_TOKEN = "paste-your-token-here"
GITHUB_REPO = "YOUR-GITHUB-USERNAME/Priscilla"
GITHUB_BRANCH = "main"
```

Optional: if you do not want every person with the portal link to use Edit Portal, add:

```toml
EDITOR_PASSWORD = "whatever-password-you-want"
```

If `EDITOR_PASSWORD` is omitted, editing is intentionally open to anyone with the portal URL.

**Never put the GitHub token directly into a file in this repository.** Keep it only in Streamlit Secrets.

## Normal use after setup

Open the portal and choose **✏️ Edit Portal** from the sidebar.

From there you can:

- edit Episode 1
- change its title
- publish/unpublish it
- create the next episode
- edit Home
- edit Voyage Prep
- edit the Known World intro
- change the Sunday schedule wording
- change Coming Soon text

Click **Save**. The app updates immediately and commits the change back to GitHub, so it survives future Streamlit redeploys.

## Party page

Each player can still upload a portrait and type what the others know about their character. With the GitHub Secrets above configured, those entries are also committed to the repository and persist across redeploys.

## Deploying this replacement

Replace the files in the existing GitHub repository with the contents of this build and keep Streamlit pointed to:

- branch: `main`
- main file: `app.py`

The existing public Streamlit URL can remain the same.
