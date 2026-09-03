# Storage: Google Drive

Runs in Step 8, on a vault that **already exists locally**. End state: the
vault folder is **moved** into the user's synced Google Drive folder on this
computer, so Drive handles backup and multi-device access.

Important honesty upfront (one sentence): this path needs the **Google Drive
desktop app** — the vault must be a real folder on disk that Drive syncs.
Notes are plain files; Google Docs won't be involved.

## Find the synced folder

Look for the Drive folder on disk before asking the user anything:

- **macOS**: `~/Library/CloudStorage/GoogleDrive-*/My Drive/` (localized
  names possible, e.g. `Mój dysk`); older installs: `~/Google Drive/`.
- **Windows**: usually `G:\My Drive\` (a virtual drive) or
  `C:\Users\<name>\Google Drive\`.

If found → confirm with the user: "Znalazłem twój folder Dysku Google tutaj:
… — przenoszę tam Twój second brain?" Move the existing vault folder to
`<Drive>/second-brain/` (plain move, nothing rebuilt). If Obsidian is
already open on the vault, tell the user to reopen it from the new location
(Open folder as vault → new path).

If not found → the app isn't installed. Guide them:
https://www.google.com/drive/download/ → install → sign in **in the app
themselves** (never through you) → re-check. If they don't want to install
the app, the vault simply stays local — moving the folder into Drive later
is drag-and-drop.

## Drive-specific settings

- Tell them to make the vault folder **"Available offline"** (right-click in
  Drive) — Obsidian and AI tools need real files, not placeholders. On
  Windows, "streaming" mode can make files virtual; offline/mirror mode
  avoids weird failures.
- Warn once, gently: never edit the same note on two computers at the same
  moment — Drive resolves conflicts by making duplicate files, not by
  merging. For one person this basically never bites.

## No shell access?

If you can't write to disk in this environment, generate the vault as a zip
for download and have them unpack it into the Drive folder — then verify
together that the folder structure looks right.
