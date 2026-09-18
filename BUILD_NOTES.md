# Build Notes — September 12, 2026

## Implementation plan used

1. Keep the Player Portal physically and logically separate from the DM Codex.
2. Put authorization in the server-side repository layer, not in hidden UI widgets.
3. Use SQLite for local persistence and PBKDF2-hashed PINs for friendly table privacy.
4. Build the useful pre-game workflow first: voyage motivation, voyage NPC, map/letter origin, and private item view.
5. Keep public sections empty-by-default and publish-only.
6. Make Dingoes & Crowns useful now without inventing missing core result rules.
7. Add DM review/publishing tools and automated role-isolation tests.

## Source/access gaps

The runtime used for this build could read the uploaded Player Portal seed, player invitation, current Disadvantages handout, and supplied cover image. It could **not** access Sean's Windows project root at:

`C:\Users\seanp\.codex\.chatgpt-projects\g-p-6a89ff2c3df88191806b50b814277ec5`

Therefore it could not directly confirm `campaign_updates/` readability or create the folder as a true sibling on that drive. This downloadable folder should be placed there as `Priscilla_Player_Portal_Streamlit/`.

The exact named sources below were also not available in the accessible uploaded/File Library sources:

- `campaign_updates/PC_CARDS_AND_MAGIC_ITEMS_SEED.md`
- `priscilla-player-portal-mockup.html`

Those gaps did not block the safe prototype. Private item content was left blank rather than reconstructed, and the visual treatment follows the seed's written description pending comparison with the approved mockup.

## Verification

Backend syntax compilation succeeded and all seven automated tests passed, including cross-player isolation for private prompt answers, notes, starting items, and voyage-NPC drafts.
