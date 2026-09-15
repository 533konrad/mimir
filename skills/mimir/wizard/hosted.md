# Hosted sandbox — when you cannot reach the user's computer

Read this when Mimir runs inside a chat app instead of on the user's machine:
Claude (claude.ai, the desktop and mobile apps), ChatGPT, Microsoft 365
Copilot (an agent with skills), or a similar web app. You may be able to run
Python and write files, but only into a temporary sandbox the user cannot
see, usually without internet access from code, and it disappears with the
conversation. So the vault is built there and handed over as one zip file.
Everything else in `WIZARD.md` stays; this file overrides the parts that
assume a local disk and ends with what to propose when something breaks.

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

- **Hosted**: a chat app with a code sandbox. Claude.ai or the Claude apps,
  ChatGPT, Microsoft 365 Copilot and the like. This is hosted even when a
  filesystem connector is installed; see the rule above.
- **Local**: Claude Code, Codex CLI, GitHub Copilot in an editor or CLI, or
  any agent whose shell runs on the user's own machine. Follow `WIZARD.md`
  as written, not this file.
- **A folder the user already shared with you** (e.g. Cowork mounts one):
  treat that folder as local and build into it with the script.

Only when none of that settles it, ask one question, inside the Step 1
message rather than before it:
PL: "Rozmawiamy w aplikacji (Claude, ChatGPT, Copilot), czy w terminalu na Twoim komputerze?"
EN: "Are we talking in an app (Claude, ChatGPT, Copilot), or in a terminal on your computer?"

## Before Step 5: find your tools

Both checks run in your own code sandbox, which asks nobody:

1. **The build script.** Your skill files sit somewhere in the sandbox, and
   the path differs per app. Find it once:
   ```sh
   find / -name build_vault.py -path "*scripts*" 2>/dev/null | head -1
   ```
   That path is `<script>` below.
2. **Where downloadable files go.** Use the first row that fits:

   | App | Folder | How the user gets the file |
   |---|---|---|
   | Claude | `/mnt/user-data/outputs` | it shows up as a file to download |
   | ChatGPT | `/mnt/data` | link it as `sandbox:/mnt/data/<file>` |
   | Microsoft 365 Copilot, others | the folder your app returns generated files from; if unsure, the working directory | offer the file the way your app returns generated files |

   That folder is `<downloads>` below.

## The one command that hands the vault over

After every step that changes the vault or `.mimir/state.md`, refresh the
download:

```sh
python3 <script> --pack /tmp/mimir/<folder> <downloads>/<folder>.zip
```

The zip has the vault folder at its root and is rewritten on every call;
nothing inside the vault changes. Share the link to it whenever you mention it.

## What changes, step by step

**Step 1, privacy line.** Use the honest version:
PL: "budujemy tutaj, w tej rozmowie, a na końcu pobierasz gotowy folder jako
jeden plik zip. Hasła nigdy nie są potrzebne."
EN: "we build it right here in this chat, and at the end you download the
finished folder as one zip file. No passwords, ever."

**Step 2, links.** Code in these sandboxes usually has no internet, so never
fetch links from Python. Open them only with the app's own browsing or web
tool, if you have one. Without it, go straight to "Alternatywnie:" /
"Alternatively:" and ask for a pasted bio.

**Step 5, build.** Same script, same profile, with these differences:

- `vault_path` is `/tmp/mimir/<folder>`. Default folder name: `drugi-mozg`
  in Polish, `second-brain` in English; let them rename it.
- Run `MIMIR_NO_OPEN=1 python3 <script> profile.json`, without `--open`:
  there is no file manager.
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
   "Otwórz ten folder w Claude Code albo innym agencie na komputerze i
   powiedz: podłącz GitHub. Mimir zrobi to w 5 minut." Do not walk them
   through web uploads.
3. **Zostaw w Dokumentach / keep it in Documents**: the no-backup warning
   from `wizard/storage-local.md`, once.

Record the choice in the marker, then `--pack`.

**Step 9, finish screen.** Replace "how to come back" with what works from
a chat app:

- The assistant layer (`CLAUDE.md`, `AGENTS.md`, `context/me.md`) loads by
  itself when the folder is opened in an AI tool on their computer (Claude
  Code, Codex, GitHub Copilot).
- Only if they picked the assistant: in Claude or ChatGPT they can create a
  Project, paste `CLAUDE.md` into its instructions and add `context/me.md`
  and `context/goals.md` to its files.
- To continue later: a new chat in the same app, attach the zip, say
  "dokończ Mimira" / "finish Mimir".

## Coming back in a hosted chat

When the user attaches a zip (or its files) and asks to finish or change
something, unpack it into `/tmp/mimir/` and follow "Coming back to an
existing folder" in `WIZARD.md` on that folder. Every rule still holds:
files that are there stay byte-identical, you only add. Hand the result back
with `--pack` under a new name, `<folder>-<YYYY-MM-DD>.zip`, so their earlier
download stays a valid copy.

## When something breaks here

The general rule is in `WIZARD.md`, "When something goes wrong": one plain
sentence about what happened, the recommended move, one alternative, two
attempts per path. What is specific to chat apps:

| What happened | Recommended move | Alternative |
|---|---|---|
| `find` returns no `build_vault.py` | build the tree by hand from `templates/vault-spec.md` (create-if-missing, both ends of every map link), then zip it with Python's `zipfile` | the hand-over |
| No code execution at all | say how to turn it on: Claude: Settings → Capabilities → Code execution and file creation; ChatGPT and Microsoft 365 Copilot: it is the admin's setting, ask whoever manages the workspace | the hand-over |
| The build or the pack times out | run the same command again: it only fills gaps | build now, `--pack` in a separate call |
| The zip exists but no download appears | save it once to the next folder from the table in "Before Step 5" and link it again | offer the most important files one by one (`README.md`, `moc/home.md`, the seed notes) if the app can return single files |
| Nothing can be downloaded at all | the hand-over | paste the seed notes into the chat as text, each with its path, for the user to save |

**The hand-over** (from `WIZARD.md`) keeps the interview: print the profile
as one `Mimir profile:` block and suggest the route that is known to work,
Claude with its free plan, where pasting the block builds the vault without
asking again.

## If they have to leave

Before the goodbye line, make sure the latest zip exists and give its link
again: in a sandbox, anything not downloaded is gone when the chat ends.
Before Step 5 there is nothing to lose but the two-minute interview.
