# Local vault — location rules (used by Step 5 Build)

Every vault starts as a plain local folder — zero accounts, zero setup.
This file defines where it goes and the fallbacks. In Step 8 the user may
upgrade to GitHub/Drive, or keep it local — a completely valid end state.

## Location

Suggest `~/Documents/second-brain` (localized Documents folder on their OS).
Let them rename `second-brain` to anything. Create the folder; if it already
exists and is non-empty, **stop and ask** — never build into someone's
existing files. One exception: a folder that already contains
`.mimir/state.md` is a Mimir vault (possibly half-built) — switch to
"Coming back to an existing folder" in `WIZARD.md` and resume instead of
asking for a new location.

## If they keep it local at Step 8 — say this once (and never nag again)

"Twój second brain będzie żył tylko na tym komputerze. To znaczy: bez kopii.
Jeśli dysk padnie, notatki znikają z nim. Kiedy zechcesz, wrócę i podłączę
GitHub albo Dysk Google w 5 minut — wystarczy powiedzieć."

Also do a small kindness: if the machine clearly has iCloud Drive / OneDrive
syncing the Documents folder anyway (common on macOS/Windows), tell them
they're accidentally covered — their brain is being backed up by their OS.

## Optional: local time machine

If `git` happens to be installed, offer (don't push): "Mogę włączyć lokalną
historię zmian — każda wersja każdej notatki zostaje zapamiętana na tym
komputerze. Bez żadnego konta." If yes:

```sh
cd <vault-folder>
git init -b main
git add -A && git commit -m "Mimir: initial second brain"
```

If git isn't installed, skip silently — don't turn the easy path into an
install marathon.

## No shell access?

Generate the vault as a downloadable zip and tell them exactly where to
unpack it (Documents), then verify together it opened correctly.
