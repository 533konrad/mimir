# Vault spec — SIXPACK structure, frontmatter, seeds

The blueprint for what Mimir builds. It's a spec, not a copy-paste bundle:
generate the actual files in the **user's language**, personalized from the
interview profile. Top-level folder names stay English; subfolders inside
blocks are named in the user's language.

## The SIXPACK structure

Three system folders + six life blocks. Each life block answers one
question — that's the whole method, and it belongs in the user's vault
README in their language:

```
<vault>/
  README.md          # how this vault works (skeleton below)
  inbox/             # SYSTEM: everything lands here first, unsorted
  moc/               # SYSTEM: Maps of Content — cross-cutting link maps
  archive/           # SYSTEM: done or dead — moved, never deleted

  work/              # z czego żyję?         (income: company, products, clients)
  public/            # co daję światu?       (brand: content, publishing, stage)
  self/              # kim się staję?        (inner: values, goals, health, learning)
  people/            # z kim żyję?           (relationships, notes about people)
  play/              # co mnie cieszy?       (passions and hobbies)
  library/           # co zbieram od innych? (links, books, tools, ideas)

  .obsidian/         # starter app config (below)
  .mimir/state.md    # Mimir's own build/resume marker (see WIZARD.md) — keep it
```

**Sizing by the quiz** (scale scores from the interview):

- score **4–5** → block gets subfolders (from the interview, user's
  language, short kebab-case) + seed notes
- score **3** → flat folder, no subfolders yet
- score **1–2** → flat folder only if the user said yes; otherwise skip —
  a missing block can be added any time later
- **`people/` never gets subfolders**, even at 4–5 (privacy — see
  interview.md; the rule about initials goes into the README, not into a
  folder tree). Its existence still follows the score: 3–5 → flat folder,
  1–2 → only if the user said yes, otherwise skip like any other block
- `inbox/`, `moc/`, `archive/` are always created

Do NOT create an `attachments/` folder upfront — the `.obsidian` config
points at it and Obsidian creates it automatically on first image paste.
Empty folders get a `.gitkeep` file (git ignores empty folders; the file is
invisible noise, no need to explain it unless asked).

Note filenames: short kebab-case in the user's language is fine
(`wedding-planning.md`, `remont-lazienki.md`) — just keep them unique across
the vault, because wikilinks resolve by filename. That also means **exactly
one `README.md`, at the vault root** — never a README inside a block or
subfolder; a folder's purpose is explained in `moc/home.md`, not in a
second README that would shadow the first one in every wikilink.

## Block boundaries (put these in the user's README too)

The four questions that settle 90% of "where does this go":

- **Does it earn money?** → `work/`. **Given away to build the brand**
  (a podcast, open-source, free content)? → `public/` — even if it's a
  product with code.
- **Content vs contract**: the episode/post/talk itself → `public/`; the
  deal, invoice, client → `work/`.
- **Reflection vs practice**: "what diving taught me about calm" → `self/`;
  "air parameters at 40m" → `play/`.
- **Someone else's vs mine**: collected from others → `library/`; created
  by me → its topic block.

`people/` privacy rule (if the user chose initials in the interview): notes
about people use initials only, never full names — vaults sync and leak.

## Frontmatter — every note gets this

```yaml
---
title: Human-readable title in the user's language
status: active        # active | someday | archive
tags: [lowercase, short]
horizon: quarter      # now | quarter | year | someday | evergreen
created: YYYY-MM-DD
updated: YYYY-MM-DD
moc: "[[block-map]]"  # ONLY if the note belongs to a MOC — see below
---
```

Why it matters (this reasoning belongs in the vault README too): frontmatter
is what makes the vault machine-readable — it's how their AI can answer
"co mam aktywnego na ten kwartał?" without reading every note. The folder
says what the note is ABOUT; `status`/`horizon` say what to DO with it now.
`horizon`: `now` = this week/month, `quarter`, `year`, `someday` =
maybe-one-day, `evergreen` = always true (values, principles, reference).

Notes still sitting in `inbox/` may carry two extra optional fields:
`suggested_folder:` and `suggested_tags:` — the AI's sorting hints, written
when it triages but isn't sure.

## MOC + two-way linking (hard rule)

`moc/` holds Maps of Content: hub notes that link one topic across blocks
(a business lives in `work/` but its marketing notes touch `public/` and its
frameworks sit in `library/` — the MOC is the one place that sees all of it).

- **Always generate `moc/home.md`**: the user's personal map — one line per
  created block with its question and its subfolders, plus a short
  explanation of the MOC idea. This is the vault's front door.
- Create a topic MOC only when a topic lives in 3+ folders and has no
  single view. Don't pre-create empty topic MOCs.
- **The two-way rule, stated verbatim in the user's README:** when a MOC
  links a note, the note gets `moc: "[[moc-name]]"` in its frontmatter —
  both ends, always, at the same time. A one-way link is drift: the map
  silently rots. (Obsidian treats frontmatter wikilinks as real links, so
  graph and backlinks work.)
- **What a MOC may wikilink:** notes only. Folders are not notes — write
  them as inline code (`` `work/rekrutacje/` ``), never as `[[work]]`,
  which Obsidian renders as a dangling link to a note that doesn't exist.
- **Inbox seeds are not wikilinked from `home.md`.** `inbox/welcome.md` and
  `inbox/sixpack-do-uzupelnienia.md` are transient (the user deletes the
  first one as their first triage); mention them as paths in backticks.
  Every note you DO wikilink from `home.md` gets `moc: "[[home]]"` in the
  same write — check this before you show the tree.

## Seed notes (from the profile)

Generate real content, not lorem ipsum — this is half of the wow. For each
block scored 4–5:

1. **One note per current project** → `work/<slug>.md` (or the right
   block) — what it is, what "done" looks like (their words),
   `status: active`, horizon `now` or `quarter`.
2. **Facts extracted from their links** → short notes in the matching
   blocks (e.g. their podcast → `public/`, their hobby → `play/`). A few
   good notes beat many thin ones.
3. **Goals note** → `self/goals-<year>.md` (or their closest subfolder) —
   their answers from the goals question, `horizon: year`.
4. **One library note** if they mentioned tools/books/sources they use.

Always, regardless of scores:

5. **`moc/home.md`** — see above.
6. **`inbox/sixpack-do-uzupelnienia.md`** — checklist of the unanswered
   questions from the interview (one `- [ ]` line each, grouped by block).
   Top of the file, one sentence: "Twój drugi mózg dopyta Cię o te rzeczy
   po jednym pytaniu na raz — albo odpowiedz tu kiedy chcesz."
7. **A welcome note in inbox** → `inbox/welcome.md` — one short paragraph:
   "this folder is where everything lands; here's how the weekly sorting
   works" + an invitation to delete this note as their first inbox triage.

## Vault README skeleton

Write it in the user's language, ~40 lines, warm but tight. Sections:

1. **Czyj to mózg / whose brain** — one line with their name and creation date.
2. **SIXPACK** — the tree above (their actual blocks), each block with its
   one question; name-drop "SIXPACK" once for the curious.
3. **Granice** — the four boundary questions from "Block boundaries".
4. **Frontmatter** — the yaml block + the two-line "why".
5. **MOC** — two sentences: maps live in `moc/`, start at `home.md`; the
   two-way rule verbatim.
6. **Rytm** — capture: everything to `inbox/`, don't sort in the moment;
   weekly: 15 min with the AI to sort inbox + one Sixpack question; anything
   finished/dead → `archive/`, nothing is ever deleted.
7. **Zasady** — plain files beat apps; English block names, their-language
   content; no secrets in the vault if it syncs anywhere (passwords live in
   a password manager, not here).
8. Credit line: `Zbudowane z Mimir — konradgladkowski.com` (or EN equivalent).

## `.obsidian/` starter config

Create exactly these two files (Obsidian generates the rest on first open):

`.obsidian/app.json`:
```json
{
  "newFileLocation": "folder",
  "newFileFolderPath": "inbox",
  "attachmentFolderPath": "attachments",
  "alwaysUpdateLinks": true,
  "useMarkdownLinks": true,
  "showUnsupportedFiles": true
}
```

`.obsidian/appearance.json`:
```json
{ "accentColor": "#7c5cff" }
```

If the vault is a git repo, `.gitignore` should include
`.obsidian/workspace*` — window-state churn that would otherwise pollute
every commit.
