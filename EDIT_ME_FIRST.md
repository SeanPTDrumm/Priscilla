# EDIT ME FIRST

You can change the normal wording and images without editing Python.

## The files you are most likely to edit

### `content/home.md`
Home-page words.

### `content/voyage.md`
Everything written on Voyage Prep.

### `content/invitation.md`
The short heading / words above the embedded invitation PDF.

### `content/party.yaml`
Player names, character names, blurbs, and optional portrait filenames.

### `content/settings.yaml`
Session time wording and the filename of the home image.

### `content/coming_soon.yaml`
Words shown on locked pages.

### `assets/`
Images, PDFs, maps and portraits.

## Changing an image

Upload the replacement image into `assets/`.

For the Home image, either:
- replace `assets/home_harbor_night.png` with another image using the same filename, or
- change `home_hero:` in `content/settings.yaml`.

## Important

You normally should **not** need to edit `app.py`.

Dingoes & Crowns is intentionally locked. Its original working code remains preserved in
`portal/pages.py`.
