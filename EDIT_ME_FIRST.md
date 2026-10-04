# EDITING THE PORTAL

You should no longer need to edit GitHub files by hand for normal campaign updates.

Open the live portal and choose **✏️ Edit Portal** in the sidebar.

From there you can edit:

- Episodes
- Home
- Voyage Prep
- Known World intro
- Session schedule
- Locked-page wording

You can also create the next Episode directly in the app.

## Make Save permanent

For edits to survive Streamlit redeploys, complete the one-time GitHub Secrets setup in `README.md`.

Once that is configured, clicking **Save** in the portal commits the update back to GitHub automatically.

## Party profiles

Players can upload portraits and edit what the others know about their characters on **The Party** page. Those can also be made permanent using the same GitHub Secrets setup.

## Dingoes & Crowns

Dingoes & Crowns remains intentionally locked. The older working prototype is still preserved in `portal/pages.py` for later rescue/rework.
