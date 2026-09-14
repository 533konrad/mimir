# Hosted sandbox — when you cannot reach the user's computer

Read this when Mimir runs somewhere that is not the user's machine: a skill
uploaded to Claude.ai, a similar web app, or an API container. You can still
run Python and write files, but into a temporary sandbox the user cannot see
and that disappears with the conversation. So the vault is built there and
handed over as one zip file. Everything else in `WIZARD.md` stays; this file
overrides only the parts that assume a local disk.

## No permission pop-ups

A non-technical user who sees "Claude wants to use List Allowed Directories
from Filesystem" before the welcome screen closes the chat. So:

- **Never call a connector or MCP tool** (Filesystem, Desktop Commander, any
  tool that makes the app ask the user for approval) to find out where you
  are, and never use one to build the vault either. The build script needs
  Python next to the files, which a connector cannot give you, and writing
  notes by hand through one brings back exactly the bugs the script fixed.
- Only your own code sandbox, which runs without prompts, is used here.

## How to tell

Decide from what you already know, without trying tools: your system
prompt, the tools you were given, and how the skill was loaded.

- **Hosted**: a chat app (Claude.ai in the browser, the Claude desktop or
  mobile app) with code execution and file creation. This is hosted even
  when a filesystem connector is installed; see the rule above.
- **Local**: Claude Code, Codex CLI, or any agent whose shell runs on the
  user's own machine. Follow `WIZARD.md` as written, not this file.
- **A folder the user already shared with you** (e.g. Cowork mounts one):
  treat that folder as local and build into it with the script.

Only when none of that settles it, ask one question, inside the Step 1
message rather than before it:
PL: "Rozmawiamy w przeglądarce albo aplikacji Claude, czy w terminalu na Twoim komputerze?"
EN: "Are we talking in a browser or the Claude app, or in a terminal on your computer?"

Once you know, a quiet `ls /mnt/user-data` in your own sandbox (no prompt)
tells you where downloadable files go.

## The one command that hands the vault over

After every step that changes the vault or `.mimir/state.md`, refresh the
download:

```sh
python3 <skill-dir>/scripts/build_vault.py --pack /tmp/mimir/<folder> <downloads>/<folder>.zip
```

`<downloads>` is the folder your environment offers the user as files to
download (`/mnt/user-data/outputs` on Claude.ai). The zip has the vault
folder at its root and is rewritten on every call; nothing inside the vault
changes. Share the link to it whenever you mention it.

## What changes, step by step

**Step 1, privacy line.** Use the honest version:
PL: "budujemy tutaj, w tej rozmowie, a na końcu pobierasz gotowy folder jako
jeden plik zip. Hasła nigdy nie są potrzebne."
EN: "we build it right here in this chat, and at the end you download the
finished folder as one zip file. No passwords, ever."

**Step 5, build.** Same script, same profile, with these differences:

- `vault_path` is `/tmp/mimir/<folder>`. Default folder name: `drugi-mozg`
  in Polish, `second-brain` in English; let them rename it.
- No `--open`, and run with `MIMIR_NO_OPEN=1`: there is no file manager.
- Then `--pack` (above) and share the link.

The user cannot click through the folder yet, so the second wow happens in
the chat: show the compact tree, then **paste one seed note in full**, the
most personal one, and ask how it sounds. Say once that nothing can be lost
now: PL: "Plik jest już gotowy do pobrania, więc nic nie przepadnie, nawet
jeśli rozmowa się urwie." EN: "The file is ready to download already, so
nothing gets lost even if this chat drops."

**Step 6, the inbox demo.** Decide the block first, then write the note
there: set `first_catch.path` straight to the target block (or `inbox/`
when it is genuinely ambiguous) and re-run the build. Moving the file
afterwards does not work here, because the next re-run would write it at
the old path again. Explain the categorization in words, exactly as in the
local flow. Update the marker, `--pack`, and say the link holds the new
version.

**Step 7, Obsidian.** Unpacking comes first:

1. PL: "Pobierz plik" (link). EN: "Download the file" (link).
2. Double-click it: macOS and Windows unpack it into a folder next to it.
3. Move that folder into Documents (Dokumenty).
4. Obsidian → "Open folder as vault" (PL: „Otwórz folder jako sejf") → that folder.

Then continue with `wizard/obsidian.md` from "Open the vault". You cannot
check whether Obsidian is installed, so ask instead.

**Step 8, storage.** No automation from here: `gh`, Drive sync and local git
all need the user's machine. Offer, one line each:

1. **Dysk Google / iCloud / OneDrive** *(recommended here)*: put the
   unpacked folder inside the synced folder and it is backed up. If their
   Documents folder is already synced by iCloud or OneDrive, say they are
   covered.
2. **GitHub**: set it up later from an AI tool on their computer. PL:
   "Otwórz ten folder w Claude Code albo Claude Desktop i powiedz: podłącz
   GitHub. Mimir zrobi to w 5 minut." Do not walk them through web uploads.
3. **Zostaw w Dokumentach / keep it in Documents**: the no-backup warning
   from `wizard/storage-local.md`, once.

Record the choice in the marker, then `--pack`.

**Step 9, finish screen.** Replace "how to come back" with what works from
a browser:

- The assistant layer (`CLAUDE.md`, `context/me.md`) loads by itself when
  the folder is opened in an AI tool on their computer (Claude Code, Claude
  Desktop, Codex).
- Only if they picked the assistant: in Claude.ai they can create a Project,
  paste `CLAUDE.md` into its instructions and add `context/me.md` and
  `context/goals.md` to its files.
- To continue later in a browser: a new chat, attach the zip, say
  "dokończ Mimira" / "finish Mimir".

## Coming back in a hosted chat

When the user attaches a zip (or its files) and asks to finish or change
something, unpack it into `/tmp/mimir/` and follow "Coming back to an
existing folder" in `WIZARD.md` on that folder. Every rule still holds:
files that are there stay byte-identical, you only add. Hand the result back
with `--pack` under a new name, `<folder>-<YYYY-MM-DD>.zip`, so their earlier
download stays a valid copy.

## If they have to leave

Before the goodbye line, make sure the latest zip exists and give its link
again: in a sandbox, anything not downloaded is gone when the chat ends.
Before Step 5 there is nothing to lose but the two-minute interview.
