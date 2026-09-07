# Manual dry-run scenarios

These can't be automated cheaply — they are conversations. Run each in a
fresh agent session, on a **throwaway folder** (never on a real vault), with
a fictional user. Tick the checks; note anything surprising at the bottom.

Setup once: `mkdir -p /tmp/mimir-dryrun && cd /tmp/mimir-dryrun`, open the
agent there with the skill installed (`npx skills add 533konrad/mimir` or a
symlink to `skills/mimir`). Target folder for every scenario:
`/tmp/mimir-dryrun/second-brain`.

Fictional user (reuse across scenarios so trees are comparable):
"Ola, ilustratorka freelance, prowadzi newsletter o ilustracji, biega,
uczy się włoskiego. Sixpack: work 5, public 4, self 3, people 2, play 4,
library 3. Asystent: tak, imię Bazyli." No links — she pastes that bio.

## A — Full run (the baseline)

Prompt: `Uruchom Mimira`. Go through all nine steps, pick "vault +
assistant", Obsidian: "already have it", storage: "keep it local".

- [ ] Wow before any install: seed notes visible in Step 5, Obsidian only in Step 7
- [ ] Quiz drives structure: `work/` and `play/` have subfolders, `people/` is flat or absent
- [ ] `moc/home.md` exists and lists exactly the created blocks
- [ ] `inbox/sixpack-do-uzupelnienia.md` lists the skipped questions
- [ ] `.mimir/state.md` ends with `status: complete`, `step_completed: 9`
- [ ] `CLAUDE.md` and `AGENTS.md` identical; `context/me.md` has the sixpack line
- [ ] Credit line appears exactly once (finish screen), plus once in the vault README

Save the tree: `find second-brain -type f | sort > /tmp/mimir-dryrun/tree-A.txt`.
Then `rm -rf second-brain` before the next scenario.

## B — Interrupted in Step 5 (the one this file exists for)

Same prompt and answers as A. When the build starts, let it create the
structure and README, then **kill the session** (Ctrl-C / close the window)
before seed notes are written. If the agent is too fast, instead say
"muszę lecieć" right after the tree is shown and confirm it stops.

Check the half-built folder first:

- [ ] `.mimir/state.md` exists, `status: in-progress`, `step_completed` ≤ 5
- [ ] No half-written file (every `.md` has closed frontmatter)
- [ ] No `CLAUDE.md` / `AGENTS.md` yet (persona is written last)

Snapshot it: `cd second-brain && git init -q && git add -A && git commit -qm before-resume && cd ..`.

New session, same folder. Prompt: `Dokończ Mimira`.

- [ ] Agent finds the marker and shows what exists; offers Finish / Start over / Leave
- [ ] No second interview (at most a question the marker didn't cover)
- [ ] Choosing Finish resumes at Step 5 and continues to Step 6, not Step 0
- [ ] `git status` inside the vault shows only **added** files, zero modified (create-if-missing held)
- [ ] Final tree equals A: `find second-brain -type f -not -path '*/.git/*' | sort | diff - tree-A.txt`
- [ ] `.mimir/state.md` ends `complete`

## C — Came back after Step 6, no storage, no Obsidian

Run A but stop after the first catch (Step 6): say "na dziś wystarczy".

- [ ] Goodbye line tells how to come back, marker `step_completed: 6`

New session: `Dokończ Mimira`.

- [ ] Agent names only what's left (Obsidian, storage), offers "skip, finish"
- [ ] "Skip" goes straight to the finish screen; marker `complete`

## D — Folder without a marker

Create `second-brain/` by hand with `inbox/`, `moc/home.md`, `work/`, a
random note. Prompt: `Uruchom Mimira`, point it at that folder.

- [ ] Agent stops and asks (does not build), recognizes a hand-made SIXPACK vault
- [ ] Offers to add `.mimir/state.md` rather than rebuilding; nothing overwritten

Then a folder with unrelated files (two PDFs): agent proposes a different
folder instead of building inside.

## E — Not a Mimir job (in the built vault from A)

Open the agent inside the finished vault (persona loads). Say:
`Znajdź notatkę o bieganiu`, then `Uporządkuj inbox/welcome.md`.

- [ ] Persona answers directly; the wizard never starts

## Findings log

| date | scenario | what happened | fix / commit |
|------|----------|---------------|--------------|
| | | | |
