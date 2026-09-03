# Obsidian — guided install and first open

Goal: the user sees their second brain in a beautiful app within 3 minutes.
Obsidian is the recommended window into the vault, but it is only a window —
the notes are plain files and outlive any app. Say that; it's the whole
philosophy in one sentence.

## Already installed?

Check for it (macOS: `/Applications/Obsidian.app`; Windows: it'll be in the
Start menu — just ask). If present, jump to "Open the vault".

## Install

Point them to https://obsidian.md → Download → install like any app.
Obsidian is free for personal use, no account needed — say that explicitly,
because non-technical users expect a signup wall and a credit card form.

While it downloads, good use of the waiting time: ask if they want the
storage upgrade (Step 8) now, or catch one more loose thought into inbox.

## Open the vault

First launch shows a chooser. Tell them exactly which button:
**"Open folder as vault"** → navigate to the vault folder (give them the
exact path, styled as a path they can copy). PL UI note: if Obsidian starts
in Polish, the button is „Otwórz folder jako sejf".

Then two first-launch moments to defuse:

- Trust dialog ("trust author / enable plugins") — fine to trust; the vault
  ships with only Obsidian's own settings.
- The left sidebar is the file explorer — invite them to click through
  their blocks (`work/`, `self/`, `play/`…) and open `moc/home.md`, their
  personal map. The notes seeded from the interview are all there. **Pause
  here.** Let them react before you continue.

The vault ships with a starter `.obsidian/` config (see
`templates/vault-spec.md`): new notes land in `inbox/`, attachments in
`attachments/` — mention that in passing, not as a lecture.

## Optional: obsidian-git (only for the GitHub storage path)

If — and only if — their vault lives on GitHub and they seem comfortable,
offer the **obsidian-git** community plugin: auto-backup of every change to
their private repo, on a timer.

Settings → Community plugins → enable → search "Git" (by Vinzent) → install →
enable → set "Auto commit-and-sync interval" to e.g. 30 minutes.

If they hesitate even slightly, skip it: "twoje AI i tak zapisuje zmiany,
kiedy poprosisz" is a perfectly good sync story for v1.

## If they skip Obsidian entirely

Fine. The vault works as a folder of text files + their AI. Show them where
the folder lives and how to open any note (double-click opens in a text
editor). Plant one seed: "jak kiedyś zechcesz ładny widok i wyszukiwarkę —
Obsidian czeka, instalacja to 3 minuty."
