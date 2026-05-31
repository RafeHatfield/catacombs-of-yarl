# Memo Content Handoff: catalog_referenced

One memo. The {catalog_entry} live-lookup beat. This is the one flagged as where the Under-Warden becomes unsettling, and it carries unique wiring requirements because of the live lookup. Read the wiring notes below before integrating.

---

## File: `config/under_warden/memos.yaml` addition

### Add: `formal_complaint.catalog_referenced` (fires first time the past-self catalog is non-empty)

```yaml
formal_complaint.catalog_referenced:
  register: direct
  subject: "Archival irregularity: familiar-authored commentary, past-self sub-archive"
  body:
    - |
      **Summary:** A review of the past-self sub-archive has identified commentary entries exceeding the scope of factual documentation. The familiar bound to the visiting party is reminded of archival standards. Corrective guidance follows.

      In the course of routine maintenance of the attrition records, this office has reviewed the catalog entries associated with the visiting party's prior terminations. The entries are, in the main, factually adequate: floor, cause, disposition of recovered inventory. This office records its appreciation for the inclusion of these particulars.

      A number of entries, however, contain commentary that this office must, with respect, flag as irregular. The most recent such entry reads, in the familiar's own hand:

      > {catalog_entry}

      This office notes the following. The attrition sub-archive exists to record the fact of termination and the disposition of associated assets. It does not exist to record the familiar's assessment of the terminated party's character, disposition, manner, or the familiar's own sentiment regarding the loss. Entries of this nature complicate retrieval, exceed the allotted field length, and introduce subjective material into what is, by design, an objective record.

      The familiar is a registered instrument of conscience and is, this office understands, operating within its binding. This office casts no aspersion on the instrument's function. It observes only that the instrument's commentary, however sincerely entered, is not admissible as archival fact, and requests that future entries be confined to the documented particulars.

      The entry quoted above has been retained in the record, annotated as familiar-authored, and flagged for the familiar's reference. No correction to the underlying termination record is required.

      This office trusts the familiar will adjust its practice accordingly.

      Regards,
      The Under-Warden
```

---

## Wiring notes (important - this memo differs from the others)

**The {catalog_entry} slot is a live lookup, not a record field.** Unlike {floor}, {cause_of_death}, {run_number} etc., which fill from PastSashaRecord fields, {catalog_entry} must surface the *rendered text of the most recent past-self's catalog entry* - i.e. the output of CatalogEntryRenderer for the most recently freed past-self. The slot fill is the actual Hollowmark-voice catalog line the player would see on the Freed-Past-Selves page, quoted verbatim inside the memo.

This means the substitution pipeline for this memo needs access to CatalogEntryRenderer at memo-render time, not just the raw persistence fields. Flagging because it's more wiring than any other slot.

**The memo is written to be slot-agnostic.** {catalog_entry} could surface any of the eight catalog template categories (early_disaster through the_recent_one). The Under-Warden's framing - that the entry is "improperly subjective material exceeding factual scope" - is pitched at the category of thing, not at specific content. It works whether the surfaced entry is the heaviest (the_one_we_kept, "I miss that one") or the most comic (early_disaster, the troll line). Do not special-case the framing per entry; the single framing is intended to land against all of them.

**Firing condition.** Fires the first time the past-self catalog is non-empty - i.e. the first time the player has freed a past-self via the Possessed-Corpse spell-break encounter (Variant 3). This is single-shot (body[0] only, fires once ever, persisted in the under_warden namespace). The player reaching this state implies they're already deep into the possession-and-death systems, which is why the memo is pitched at formal_complaint tone rather than polite.

**Tone keying.** Keyed to formal_complaint because catalog-non-empty correlates with the player being well into the escalation arc (they've died to the Under-Warden, freed a past-self, accumulated record). If the tone-progression logic would put a given player at a lower tone when this fires, flag it - we may need to decide whether catalog_referenced overrides the current tone or respects it. My assumption is it fires at formal_complaint regardless, because the content is written at that register. Confirm or raise.

---

## Design intent (for context, not implementation)

This is the memo where the Under-Warden quotes a familiar's grief and files it as a clerical irregularity. He reads Hollowmark's tender, dark-comic remembrance of a dead Sasha and his only available response is to flag it as improperly subjective documentation that complicates retrieval and exceeds field length. He is not cruel; he is incapable of registering grief as anything but a category error in the record. He corrects her for feeling something, and doesn't know that's what he's doing.

The horror is the gap between Hollowmark's quoted voice (warm, grieving) and the Under-Warden's response (purely procedural). The quoted entry does the emotional work; the Under-Warden's annotation makes the clinical misreading legible to the player. Calling Hollowmark "the instrument" and "the familiar" throughout - never her name - is the dehumanization that mirrors the Unit framing applied to Sasha.

This is the only place in the game where the Under-Warden's voice and Hollowmark's voice appear in the same text. The contrast is the entire point.

---

## Still outstanding in memo content

- **final_audit canonicals** for the major incident types. HELD pending the endgame design lock. Reason: the Weighing's audit and its outcome memos (Clean Audit memo, Theft memo, loss-state memos per plan_end_game.md) overlap conceptually with the between-runs final_audit tone. Drafting final_audit memos now risks redundancy or conflict with the endgame audit content. Reconcile after the endgame structure is confirmed, so we don't build two competing "Under-Warden's final word" surfaces.

After final_audit is reconciled and drafted, the between-runs memo content is feature-complete.
