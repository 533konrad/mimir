# Changelog

All notable changes to Mimir are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and the project adheres to
[Semantic Versioning](https://semver.org/).

New changes land under **Unreleased**. A version is cut only when the
maintainer decides to release: the heading gets a number and a date, and the
`version` in `.claude-plugin/plugin.json` moves with it.

## [Unreleased]

### Added

- Claude Code plugin: the repo is its own single-plugin marketplace
  (`claude plugin marketplace add 533konrad/mimir`, then
  `claude plugin install mimir@533konrad`). The README documents both install
  routes and says to pick one, since installing both leaves Mimir in place twice.
- Codex skill picker metadata in `skills/mimir/agents/openai.yaml`.
- `scripts/build_vault.py`: a deterministic vault builder. The wizard writes a
  `profile.json` and the script builds the structure (sizing by quiz,
  frontmatter, Obsidian config, one README, `moc/home.md` with both ends of
  every link, inbox seeds, assistant layer, state marker). Stdlib only, with
  `--dry-run`, `--print-schema` and `--open`; `MIMIR_NO_OPEN` suppresses the
  file manager window. It refuses an invalid profile instead of guessing.
- Every interview question carries a recommended answer.
- Resume after interruption: the `.mimir/state.md` state marker and a
  "coming back to an existing folder" flow with five cases.
- Trigger evals (`evals/run-triggers.py`, `evals/triggers.md`) and manual
  dry-run scenarios (`evals/scenarios.md`).

### Changed

- The skill description is limited to build, finish and upgrade intent, with
  an explicit "do not use for" clause and a "Not a Mimir job" section.
- Step 0 detects the user's language instead of asking for it.
- Step 1 welcome, Step 2 link request and Step 6 opening line rewritten for a
  first-time user; the demo note is no longer called a "catch".
- Step 3 quiz asks one question at a time and explains the 1-5 scale first by
  what it changes (a 5 gets subfolders and seed notes, a 1 is not created).
- Step 5 builds through the script, with a hand-build fallback for
  environments without a shell. Step 6 re-runs the build for the first note.
- README links to konradgladkowski.com carry campaign UTM parameters.

### Fixed

- Existing files stay byte-identical: create-if-missing everywhere, append
  only, and "delete it all" renames the old folder to `<name>-backup-<date>`.
- Requests other than build, finish, add the assistant or connect storage no
  longer start or propose a build.
- The GitHub storage path stops after the second failure and runs
  `gh auth login` only in an interactive terminal.
- MOCs wikilink real notes only, every linked note gets `moc:` in the same
  write, exactly one README at the root, and `people/` never gets subfolders.
- The first note no longer resurrects a block the user declined in the quiz.
- `AGENTS.md` carried the old red lines, so Codex users got outdated rules. It
  now matches `SKILL.md` and names it as the source of truth.

## [2.0.0] - 2026-09-03

### Added

- Mimir v2: the second brain wizard building a SIXPACK vault (six life blocks,
  inbox, maps of content, archive) with an optional AI assistant layer.
- `skills/mimir/` layout for `npx skills add 533konrad/mimir`.
- Three install routes: skills CLI, magic prompt, ZIP download.
