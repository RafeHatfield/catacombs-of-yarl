# Voice Anti-Tell Lint — Family 1 (Static)

**Status:** Spec complete. NOT loaded by the Analyst directly — this is the
**static linter's** spec (the third instrument). A runtime subset is also picked
up by the Analyst's `text_pattern` mechanism as a backstop (see Two Consumers).
**Last updated:** 2026-06-10

---

## What this is, and why it isn't about punctuation

This is the cheapest rung of voice testing: scan the authored writing for
dead-giveaway AI tells before they ever reach a player. It is **not** typography
pedantry. In a game whose whole identity is hand-crafted voice, prose that reads
as machine-generated contaminates the one thing that makes it yours. An em-dash
is the loudest such tell — it pulls the player straight out of the fiction. So
"no em-dashes in authored voice" becomes a standing automatic check over the
script.

This is **Family 1 of three**. The families are ordered by how much *meaning*
the check needs:
- **Family 1 (this doc):** meaning-free pattern. Static, no LLM, no run.
- **Family 2:** meaning, speaker-relative, context-free — "does this line break
  Hollowmark's register on its own?" Static, `llm_judged`, needs a register spec.
- **Family 3:** meaning, context-relative — "does this line fit the moment it
  fired in?" Runtime, `llm_judged`, needs a transcript.

A check climbs only as far as it must, and every check pushes as far *down* the
hierarchy as it will go — the same cheapest-sufficient-instrument logic as the
rest of the design.

---

## Two consumers, two scopes

The rules below are a shared spec with two consumers:

1. **Static linter (primary).** Runs against the authored-content registry with
   **no game run at all** — the cheapest check in the entire system. This is the
   main event. It is also the first of the static linter's jobs; the same
   instrument will later own the dormancy whitelist (`known_inert`, currently in
   silent-failure-inventory.md) and Family 2's register-in-isolation pass.

2. **Analyst `text_pattern` (backstop).** Runs against *rendered* text captured
   in transcripts. Catches the runtime-only failures the static script lint
   structurally cannot see — chiefly un-substituted template variables and
   un-stripped markup that reach the player. Free bonus: this doubles as a
   render/substitution-failure detector.

Same rules, two surfaces. The static lint is the floor; the transcript pass is
the backstop for things that only go wrong at render time.

---

## Scope boundary (redline if wrong)

```yaml
scope:
  include: [voice_lines, murals, signs, memos, weighing_dialogue]
  exclude: [code_identifiers, debug_strings, ui_chrome, log_output]
```

This protects **voice**, not the codebase. It never touches identifiers, debug
strings, or UI chrome — only the narrative surface a player reads.

---

## Character tier — hard-block, deterministic

A string either contains the glyph or it does not. These are never the voice you
want, so they hard-block.

```yaml
character_tier:
  mechanism: text_pattern
  action: hard_block
  blocked:
    em_dash:           { pattern: "—",       reason: "AI tell; only the hyphen - is authored voice" }
    en_dash:           { pattern: "–",       reason: "AI tell" }
    ellipsis_glyph:    { pattern: "…",       reason: "typographic tell; three periods ... are fine" }
    markdown_emphasis: { pattern: "[*`_#]",  reason: "markdown leak; never appears in speech" }

  allowed:               # explicitly NOT blocked — do not flag these
    curly_quotes: "“ ” ‘ ’ are fine; published prose uses them (authored-voice call)"

  markup_aware:          # legitimate in the RAW script; do NOT block here.
                         # Checked in RENDERED text by the Analyst backstop instead.
    bbcode:
      raw_form: "[b], [color=...], etc. — Godot RichTextLabel formatting"
      block_in_script: false
      runtime_check: "BBCode tags reaching the player un-stripped = render bug"
    template_vars:
      raw_form: "{boss}, {name}, etc."
      block_in_script: false
      runtime_check: "an un-substituted {var} reaching the player = substitution bug"
```

The markup-aware handling is the key subtlety: `"You came back, {boss}."` is a
*correct* authored line, not a defect — it is only a bug if `{boss}` survives to
the screen. Blocking braces in the script would false-positive on every
templated line (the "linter fights its own content" trap). So braces and BBCode
are fine in the script and policed in the rendered output, where the same check
catches substitution failures for free.

---

## Phrase tier — flag-for-review, never block

The strongest tells are not characters, they are phrases and shapes. Still
regex, still static, still no LLM. But two problems the character tier does not
have: phrases can be legitimate, and — acute for this game — your intended
register is elevated and mythic, which **overlaps the register the model
defaults to**. A Guardian might authentically say "in the realm of." So the
phrase tier **flags for your review; it never hard-blocks.** A hard block would
fight your own voice.

```yaml
phrase_tier:
  mechanism: text_pattern
  action: flag_for_review        # NEVER hard_block
  rationale: >
    The mythic register (Guardians, the Debt's Deionarra warmth) overlaps
    AI-default elevated phrasing. Blocking would suppress authentic voice.
    A human confirms every hit.
  living_list: true              # Rafe owns this and grows it over time
  seed_patterns:
    - "a testament to"
    - "a (rich )?tapestry of"
    - "not just .+,? (it'?s|but) .+"     # contrastive amplification — high false-positive, fine (review-only)
    - "navigating the complexit"
    - "\\bdelve[sd]?\\b"
    - "in the realm of"
    - "plays a (vital|crucial|key|pivotal) role"
    - "stands as a"
    - "the very fabric of"
  ambiguous_routing: >
    Truly ambiguous hits are not pattern violations — they are register
    questions wearing a regex costume. Route those to Family 2; do not force
    them as Family 1 pattern hits.
```

---

## The discipline (inherited by all three families)

```yaml
discipline:
  canary_required: true
  report_scan_count: true
  whitelist: { entries: [] }
```

- **Canary.** A regex for `—` finds nothing if the pipeline escaped it to
  `\u2014`, and reports clean — a silently-dead check, the exact shape the
  JSON-escaping near-miss showed. So **every rule ships with a fixture
  containing the banned token, confirmed to make the check FIRE.** Same gate as
  the predicates: a check that has never fired is indistinguishable from one
  that cannot.
- **Scan count.** The linter reports scanned-count alongside match-count.
  Silence is only trustworthy with a non-zero scan. Same ran-count invariant now
  standing across the whole testing layer.
- **Whitelist.** Legitimate exceptions get an explicit entry with a reason —
  same pattern as the dormancy `known_inert` whitelist. A whitelisted exception
  is a design act, on the record, not a silent suppression.

---

## What's next — Family 2

Register-in-isolation: the **Loiosh Principle made testable**. Does an authored
line, judged alone, break its speaker's register — Hollowmark tightening under
load rather than speechifying; the orcish cadence of the Oathkeeper; the Debt's
warm inevitability? This is `llm_judged`, still static (no run), and it is the
meaty part of the voice work. It needs one input only you can give: a **register
spec per speaker** — the voice rules each character's lines are judged against.
That is the next design build in this thread.
