# Interview — links first, quiz second

Goal: after this step you know the user well enough to build a vault that
feels like *theirs* on first open — with as few questions as possible.
Output is the **profile** used in the Build step and, if the assistant layer
is chosen, in `context/me.md`.

Rules of engagement:

- One thing at a time, conversational, in the user's language. React to
  answers like a curious human, not a form.
- Everything is skippable — "nie wiem / skip" is a valid answer. A thin
  profile still works; an interrogation kills the mood.
- Total budget: **5–7 minutes**. The links do the heavy lifting so the
  questions don't have to.

## Phase A — links (the first wow)

Ask: "Masz LinkedIn, bloga, stronę firmy albo inny profil publiczny? Wklej
linki — z nich wyciągnę, kim jesteś, zamiast Cię przesłuchiwać." / "Got a
LinkedIn, a blog, a company page? Paste links — I'll learn who you are from
them instead of interrogating you."

If you can fetch web pages, fetch each link and extract into a draft profile:

- **name** and what they do (headline, bio, about)
- **work signals** → block `work`: employer/company, role, own products,
  clients mentioned
- **public signals** → block `public`: posts, talks, podcast, newsletter,
  articles — anything they publish
- **play/self signals** → blocks `play`/`self`: hobbies, interests, causes
  mentioned in bios
- **current projects**: anything described in present tense ("building X",
  "launching Y")

Present the draft back in 5–7 lines: "Tyle już o Tobie wiem — zgadza się?
Co poprawić?" One correction round, then move on. **Pause for their
reaction** — seeing a machine understand them from one link is the first
wow of the whole flow; don't trample it with the next question.

No links, no fetch capability, or the user prefers not to share? Equally
good inputs, offer them in this order:

1. paste any bio/description they already have ("wklej cokolwiek — notkę o
   sobie, opis z CV, stopkę maila"),
2. **dictate a messy braindump by voice** if their tool supports voice input
   ("opowiedz mi o sobie na głos, ja to poukładam") — accept raw unpunctuated
   text and structure it yourself,
3. skip straight to the quiz — Phase B alone still produces a good profile.

## Phase B — the Sixpack quiz

Frame it in one sentence: "Sześć krótkich pytań w stylu testu osobowości —
odpowiedzi ustawią kształt Twojego second brain." Use the interactive
question tool if available; otherwise numbered options in chat.

Six questions, one per block, answered on a 1–5 scale
(1 = kompletnie nieważne / not important at all, 5 = bardzo ważne / very
important). Suggested phrasings (adapt freely):

| Block | PL | EN |
|---|---|---|
| work | "Praca zarobkowa — firma, produkty, klienci, etat: jak dużą część Twojego życia zajmuje?" | "Paid work — company, products, clients, job: how big a part of your life?" |
| public | "Tworzenie na zewnątrz — posty, wystąpienia, treści, marka osobista?" | "Creating in public — posts, talks, content, personal brand?" |
| self | "Praca nad sobą — wartości, cele, zdrowie, nauka, refleksja?" | "Inner work — values, goals, health, learning, reflection?" |
| people | "Ludzie — relacje, rodzina, sieć kontaktów, notatki o osobach?" | "People — relationships, family, network, notes about people?" |
| play | "Pasje i hobby — rzeczy robione dla frajdy?" | "Passions and hobbies — things done for the joy of it?" |
| library | "Zbieranie wiedzy — linki, książki, narzędzia, pomysły od innych?" | "Collecting knowledge — links, books, tools, other people's ideas?" |

### Follow-ups — only where it matters

Ask follow-ups ONLY for blocks scored **4–5**, and ONLY about what Phase A
didn't already reveal. One or two questions per hot block, no more:

| Block (4–5) | Ask | Becomes |
|---|---|---|
| work | "Z czego konkretnie żyjesz? Firmy, produkty, klienci?" + "Jakie 1–3 rzeczy z deadlinem teraz prowadzisz?" | subfolders per venture + seed note per project |
| public | "Gdzie publikujesz albo chcesz publikować? Podcast, LinkedIn, blog, scena?" | subfolders per channel |
| self | "Co ćwiczysz albo rozwijasz? Filozofia, cele, zdrowie, języki?" + "Co chcesz, żeby za rok było inne?" | subfolders + goals note |
| people | "Chcesz notatki o konkretnych osobach? Jeśli tak: pełne imiona czy inicjały?" (privacy: recommend initials if the vault will ever sync anywhere) | flat folder + privacy rule in README |
| play | "Jakie pasje? Wymień — każda większa dostanie swój folder." | subfolders per passion |
| library | "Co najczęściej zbierasz? Linki, książki, przepisy, cytaty, pomysły?" | subfolders per collection type |

Blocks scored **3**: flat folder, no follow-ups. Blocks scored **1–2**: ask
once, briefly, whether to create an empty flat folder or skip it entirely
("dodam kiedyś, jak zechcesz").

Also ask everyone (quick, once): "Gdzie dziś lądują twoje notatki i pomysły?
Telefon, karteczki, głowa?" — this tells you what habit the inbox replaces,
and lets you say later: "wszystko, co dziś ląduje w [ich odpowiedź], od
teraz wrzucasz do inbox."

## What NOT to ask

No questions about health conditions, finances in numbers, relationships in
detail, or anything sensitive. The vault is theirs to fill with private
things later; the interview only needs the shape of their life, not its
contents. If the user volunteers something sensitive, don't copy it into
seed notes — keep seeds neutral.

## Profile (the output)

Assemble internally:

- name, what they do, tone preference (if assistant chosen)
- per block: scale score, subfolders (user's language), facts from links,
  answers from follow-ups
- current projects with a one-line "done looks like"
- **unanswered questions list** — every follow-up that was skipped or never
  asked (blocks 3–5 only). This seeds `inbox/sixpack-do-uzupelnienia.md`
  and drives progressive fill (see `templates/assistant-spec.md`). The
  interview being short is a feature BECAUSE this list exists — the brain
  fills itself over the coming weeks, one question at a time.

Before moving on, show a 5-line summary back to the user and ask "Zgadza
się? / Did I get that right?" — one correction round max, then proceed.
