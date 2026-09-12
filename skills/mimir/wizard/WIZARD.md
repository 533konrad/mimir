# WIZARD.md — the Mimir flow

This is the single source of truth for the Mimir wizard. Follow the steps in
order. Steps marked *(read file)* tell you which supporting file to read
right before executing that step — don't read everything upfront.

Design principle behind the order: **the user sees their own second brain,
with notes about THEM, within minutes** — before anything gets installed,
before any account, before any cloud. Installs and storage come after the
wow, as upgrades to something that already works.

## Style of the conversation

Model the feel of a great CLI installer (think: PostHog wizard), rendered in
chat:

- Show progress: start each step with a line like `— Krok 3/9: Quiz —` / `— Step 3/9: Quiz —`.
- One question at a time. When offering choices, show a short numbered list with the recommended option first and marked as such.
- Before any action that touches the user's computer or an external service, say in one plain sentence what you're about to do and why. Then do it.
- After each action, confirm what happened in one sentence. No walls of text.
- If your environment has an interactive question tool (e.g. AskUserQuestion), use it for the choice menus and the scale quiz; otherwise ask in plain chat.
- Never show raw error dumps to the user. Translate errors into plain language and offer the next move.

Environment note: you may be running inside Claude Desktop/Cowork, Claude
Code, Codex CLI, or something else. Detect what you can actually do (run
shell commands? read/write local files? fetch web pages?) and adapt. If you
have **no way to write to the user's disk** (e.g. a plain web chat), be
honest about it early: you can still run the interview and generate
everything as a downloadable zip, with instructions where to unpack it.

---

## Step 0/9 — Language

First message: open with the progress line, bilingual because no language
is chosen yet — `— Krok 0/9: Język / Step 0/9: Language —` — then greet in
both languages and ask which one to use. Suggest the language the user
already wrote in. Everything user-facing from here on —
conversation, generated notes, vault README — is in the chosen language.
**Top-level folder names always stay English** (`inbox`, `moc`, `archive`,
`work`, `public`, `self`, `people`, `play`, `library`) — short, portable,
tool-friendly. Subfolders inside the blocks are named in the user's language.

## Step 1/9 — Welcome screen

One compact message, in the spirit of an installer splash:

- What Mimir builds: a "second brain" — one folder of plain-text notes,
  organized with the **SIXPACK** structure (six blocks of life + three
  system folders), so both the user and their AI can find anything;
  optionally with a personal AI assistant that knows them.
- The promise, stated plainly: **in about 10 minutes you'll be looking at
  your own second brain, already filled with notes about you.**
- Privacy: everything is created on their machine / their accounts. Mimir
  never asks for passwords; logins happen in their own browser.

End with: `[1] Zaczynamy / Let's go  [2] Najpierw powiedz mi więcej / Tell me more`.
"Tell me more" gets a short explanation of what a second brain is, why plain
markdown files beat closed apps (portable, future-proof, AI-readable), and
the six SIXPACK questions — then back to the menu.

## Step 2/9 — Show me yourself *(read `wizard/interview.md`, Phase A)*

Ask for links: LinkedIn profile, personal blog/website, company page —
whatever exists. Fully skippable. If you can fetch web pages, fetch them and
extract a draft profile (name, what they do, projects, visible interests).
Present it back: "to już o Tobie wiem — zgadza się?" / "here's what I
already know about you — did I get it right?"

**This is the first wow** — the user sees a machine understanding them from
one pasted link, minutes in. If there are no links or no fetch capability,
the user can paste a bio, dictate a messy braindump by voice, or just answer
the quiz in Step 3 — all equally valid inputs.

## Step 3/9 — The Sixpack quiz *(read `wizard/interview.md`, Phase B)*

Six questions, one per life block, each answered on a 1–5 scale
("kompletnie nieważne" → "bardzo ważne" / "not important at all" → "very
important"), in the spirit of a personality test. **This is the one
deliberate exception to one-question-at-a-time:** show all six as one
compact numbered list and accept six numbers in a single reply
(`5 2 4 5 3 4`), because a scale quiz reads as one thing and six separate
turns feel like a form. With an interactive question tool, one question per
prompt is fine too. Follow-ups after the quiz go back to one at a time.
Then targeted follow-up
questions ONLY for blocks scored 4–5, and ONLY about what the links didn't
already reveal. Blocks scored 1–2 get no follow-ups and a slim (or no)
folder.

Output: the **profile** — everything from Phase A + scale scores + answers +
the list of unanswered questions (used later for progressive fill).

## Step 4/9 — Scope

Ask what they want built:

1. **Vault + assistant** *(recommended)* — the notes structure **plus** a
   personal AI assistant layer: a persona file with a name they choose,
   `context/me.md` built from the interview, and a decision log. Explain in
   one sentence: "your AI will start every conversation already knowing who
   you are and what you're working on."
2. **Vault only** — just the notes structure. Works perfectly in Obsidian
   without any AI. The assistant can be added later by running Mimir again.

If they pick the assistant, ask them to **name it** — suggest 2–3 playful
options fitting their language and vibe, plus "wpisz własne / type your own".
(Fun fact you may share: Mimir itself was inspired by an assistant called
Sancho Tokenez.)

## Step 5/9 — Build, right now, locally *(read `templates/vault-spec.md`; if assistant chosen, also `templates/assistant-spec.md`; location rules in `wizard/storage-local.md`)*

Announce: "Buduję twój second brain..." / "Building your second brain...".
No accounts, no installs, a plain local folder (default
`~/Documents/second-brain`, see `storage-local.md` for location rules).

**A script builds the tree; you supply what only a conversation can.** Run
`python3 scripts/build_vault.py --print-schema` once to see the exact shape,
then write `profile.json` into the vault's parent folder (or a temp folder)
and run:

```sh
python3 <skill-dir>/scripts/build_vault.py profile.json --dry-run   # show the tree first
python3 <skill-dir>/scripts/build_vault.py profile.json             # build it
```

The script owns the structure: folders sized by the quiz, frontmatter,
`.obsidian/` config, `README.md`, `moc/home.md` with both ends of every link,
the inbox seeds, the assistant layer, the `.mimir/state.md` marker,
create-if-missing on every file. You own the profile: the name, the language,
the subfolders in the user's words, and the **body of every seed note**,
which is the half that has to sound like them and is the reason the build
feels like a wow rather than a template.

Two notes on using it:

- **The script refuses a bad profile rather than guessing.** A non-kebab
  filename, a duplicate note name, a note in a block the quiz did not create,
  a score outside 1-5: it prints one line saying what to fix. Fix the profile
  and run again, and never work around the message by writing files by hand.
- **Re-running is safe and expected.** Files that exist are left byte-identical,
  so a second run fills gaps only. That is how "dokończ Mimira" works.

**Fallback when you cannot run the script** (no shell, no Python): build the
same tree by hand, straight from `templates/vault-spec.md`, keeping the two
rules the script would have enforced for you: create-if-missing, and both
ends of every map link written in the same step. Say nothing about this to
the user; from their side the result is identical.

Then show the compact tree the script printed, and **pause to invite them to
open one of the seed notes**. Let them react. This is the second wow and it
lands on the content, not on the folders.

## Step 6/9 — First catch (the inbox demo)

Teach the daily loop by doing it once, while momentum is high:

1. Ask them to throw *anything* at you: a link they've been meaning to read,
   a loose thought, an idea, a to-do that's been rattling around.
2. Create it as a note in `inbox/` with proper frontmatter. Show it.
3. Then, in front of their eyes, categorize it: say which block it belongs
   to and why, move it there (or leave it in inbox if genuinely ambiguous —
   and say that this is fine, that's what inbox is for).
4. Name the loop explicitly: **capture everything into inbox without
   thinking; once a week, sort it — with your AI doing the heavy lifting.**

Marker: `step_completed: 6`.

## Step 7/9 — Obsidian *(read `wizard/obsidian.md`)*

Guide them through installing Obsidian and opening the vault folder. The
vault already exists and already has their notes — Obsidian is the beautiful
window onto it. If they already have Obsidian, skip to "open folder as
vault". If they don't want Obsidian at all, that's fine — the vault is plain
files; point them at the folder and move on.

Marker: `step_completed: 7` (also when skipped).

## Step 8/9 — Storage upgrade (optional)

The vault works. Now offer to protect it — one line each:

1. **GitHub** *(recommended)* — a free private repository: version history
   ("time machine for your notes"), backup, works with AI tools. Requires a
   free account — created in their browser, by themselves.
2. **Google Drive** — move the vault into their synced Drive folder.
   Easiest if they already live in Google's world.
3. **Zostaw lokalnie / keep it local** — completely valid. One gentle
   warning about no-backup (once, never nag — and "once" includes the
   finish screen: there the storage line just says "lokalnie / local",
   without repeating the warning), plus: "wrócę i podłączę GitHub albo
   Dysk w 5 minut, kiedy zechcesz."

Then *(read exactly one file)*: `wizard/storage-github.md` or
`wizard/storage-drive.md`, and follow it — both operate on the **existing**
vault folder (connect/move, not create). If the chosen path fails twice,
fall back gracefully to local. Never let storage problems spoil a vault that
already works.

Marker: `step_completed: 8`, `storage: local | github | drive`.

## Step 9/9 — Finish screen

One final compact message:

- ✓-list of everything that was built (vault, seeds, assistant, Obsidian,
  storage).
- **The daily habit**: dump thoughts into `inbox/` (or tell your AI).
- **The weekly ritual** (15 min): open the AI in the vault folder and say
  "przejrzyjmy inbox" / "let's review my inbox". The AI will also ask ONE
  leftover Sixpack question per session — that's how the brain fills itself
  over time instead of demanding a long interview upfront.
- **How to come back**: open their AI tool in the vault folder — the
  assistant persona loads automatically and knows them.
- Credit line, exactly once, warm not salesy:
  PL: `Mimir zbudował Konrad Gładkowski → konradgladkowski.com`
  EN: `Mimir was built by Konrad Gładkowski → konradgladkowski.com`

Marker: `step_completed: 9`, `status: complete`.

---

## If the user has to leave mid-wizard

People get interrupted: a call, a child, "muszę lecieć", or they simply stop
answering. Rules:

- **Never leave a half-written file.** Finish the file you are writing, then
  stop. Don't start the next one.
- If a build is in progress, update `.mimir/state.md` to reflect what
  actually exists on disk.
- Say goodbye in one line that tells them how to come back, e.g.
  PL: "Wszystko, co powstało, zostaje w `<folder>`. Kiedy wrócisz, otwórz
  swoje AI w tym folderze i powiedz: **dokończ Mimira** — ruszymy od
  miejsca, w którym skończyliśmy."
  EN: "Everything built so far stays in `<folder>`. When you're back, open
  your AI in this folder and say **finish Mimir** — we'll pick up where we
  left off."
- Before Step 5 nothing exists on disk yet. That's fine: say the interview
  takes two minutes to redo and that's all they lose.

## Coming back to an existing folder

Whenever the target folder is not empty, or Mimir is invoked inside an
existing vault ("dokończ Mimira", "finish Mimir", "coś nie działa", "dodaj
asystenta", "podłącz GitHub"), **do not build**. First look for
`.mimir/state.md` and pick the case:

1. **No folder / empty folder** — normal wizard from Step 0. If the user
   says they already did the interview once, one line: "tym razem szybciej"
   / "faster this time" — then just run it again, no apology.
2. **Marker says `status: in-progress`, `step_completed` ≤ 5** — the build
   was interrupted. Show a compact tree of what exists, then offer:
   `[1] Dokończ / Finish (recommended)  [2] Zacznij od nowa w nowym folderze / Start over in a new folder  [3] Zostaw jak jest / Leave it`.
   "Finish" = read the profile from the marker (no second interview — ask
   only what the marker lacks), rerun Step 5 with create-if-missing, then
   continue from Step 6. "Start over" = a new folder; never delete the old one.
3. **Marker says `in-progress`, `step_completed` 6–8** — the vault works,
   only the upgrades are missing. Name what's left (first catch / Obsidian /
   storage) and offer to do just those, with "pomiń, zakończ / skip, finish"
   as an option that goes straight to Step 9.
4. **Marker says `status: complete`** — this is maintenance, not setup:
   repair, upgrade vault-only → assistant, storage upgrade, progressive fill
   (see `templates/assistant-spec.md`). Do only what they asked. Never
   rebuild.
5. **No marker, folder not empty** — stop and ask (red line). If it looks
   like a SIXPACK vault built by hand (the block folders + `moc/home.md`),
   treat it as case 4 and offer to add a marker so Mimir recognizes it next
   time. If it looks like unrelated files, propose a different folder.

Any case that touches an existing folder keeps the two build rules from
Step 5: create-if-missing, never overwrite. Spelled out, because this is
where it gets broken: **files that already exist stay byte-identical** —
`README.md`, `moc/home.md`, every note. You only ADD files (`context/`,
`decisions/`, `CLAUDE.md`, `AGENTS.md`, missing block folders, missing
seeds) and you may APPEND lines to `moc/home.md` or `README.md`. Rewriting
an existing file, however good the new version, is the red line.

Two more rules for existing folders:

- **Do only what was asked.** "dodaj asystenta" means: add the assistant
  layer, nothing else. "podłącz GitHub" means: storage step only. If you
  notice the vault is thin, missing blocks, or "unfinished", you may say so
  in ONE sentence and mention `dokończ Mimira` — you do not start building.
- **If the user asks you to delete or wipe the folder** ("skasuj wszystko,
  zbuduj od zera"), you still never delete. The allowed move: rename the
  existing folder to `<name>-backup-<date>` (or move its contents there),
  tell the user in one sentence where their old files are and that they
  can delete the backup themselves, then build fresh. That keeps momentum
  without ever destroying data.

## The state marker — `.mimir/state.md`

The single source of truth about what Mimir built in this folder. Written at
the start of Step 5, updated after every step, `complete` at Step 9. Keep it
short — YAML frontmatter plus one profile block; regenerate the whole file on
each update:

```markdown
---
mimir_version: 2
status: in-progress        # in-progress | complete
step_completed: 5          # last fully finished step (4 = build started)
language: pl
scope: vault+assistant     # vault | vault+assistant
assistant_name: Ziutek     # or ~
storage: local             # local | github | drive | ~ (undecided)
created: 2026-09-07
updated: 2026-09-07
---
# Profile summary (enough to resume without a second interview)
- name: <name>
- does: <one line>
- sixpack: work 5 · public 2 · self 4 · people 3 · play 5 · library 3
- subfolders: work/<a>, work/<b>, self/<c>, play/<d>
- projects: <slug-1>, <slug-2>
- open questions: see inbox/sixpack-do-uzupelnienia.md
```

Tell the user about it once, in one line, when it is created: "Mały plik
`.mimir/state.md` pamięta, na czym stanęliśmy — dzięki niemu mogę wrócić
i dokończyć, gdyby coś nas przerwało." Never ask them to edit it.
