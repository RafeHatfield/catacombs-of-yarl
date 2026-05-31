# Memo Content Handoff: Session 3

Four new procedural_notice canonicals plus body[1+] variants for the two polite-tier multi-fire triggers from session 2. All BLUF structure, all em-dashes purged.

Key thing in this batch: the body[1+] variants demonstrate the "increasingly weary Under-Warden" progression. Body[0] explains at length; body[1] shortens; body[2] is almost nothing. The closer-courtesy also attrits across the variants (With courtesies -> With regards -> bare signature). That progression is the design payoff and it costs almost nothing to author.

---

## File: `config/under_warden/memos.yaml` additions

### Add: `procedural_notice.death_repeat` (fires on 3rd death across runs)

```yaml
procedural_notice.death_repeat:
  register: direct
  subject: "Recurring attrition: Unit #{run_number}, Floor {floor}"
  body:
    - |
      **Summary:** Third recorded termination of the same visiting party. Pattern logged. Standard review applies.

      The previous two terminations in this descent series produced internal records under Regulation 44-C (Custodial Attrition, Routine). The third instance, as currently filed, exceeds the threshold at which routine records remain routine. This office is therefore filing the present termination under Regulation 44-D (Custodial Attrition, Patterned), which requires this notice be issued to the affected visiting party.

      Cause of present loss: {cause_of_death}, Floor {floor}.

      No remedial action is contemplated. The pattern is noted. The catalog has been updated to reflect three filed entries for this visiting party. Visiting parties whose entries accumulate at this rate may expect a corresponding increase in correspondence from this office.

      Regards,
      The Under-Warden
```

### Add: `procedural_notice.cause_possession_neglect` (fires when home body died during possession)

```yaml
procedural_notice.cause_possession_neglect:
  register: direct
  subject: "Termination by unattended vessel, Floor {floor}"
  body:
    - |
      **Summary:** Termination filed. Cause: vacation of the home vessel during an active inhabitation. The practice is, per Regulation 17-B, neither sanctioned nor recommended.

      The incident log records that on Floor {floor}, the visiting party's home vessel sustained terminal damage while the party itself was occupying an unrelated host. This office wishes to note, for the record, that the relevant regulation (17-B, Unauthorized Translocation, Bilateral Vulnerability) has been in standing since the institution's founding. The regulation's text observes, with what was at the time considered admirable foresight, that practitioners of bilateral occupancy bear administrative responsibility for both vessels concurrently.

      The home vessel has been logged as terminated. The host vessel, this office is informed, has resumed its prior duties without incident.

      This office offers no commentary on the practice itself. The catalog has been updated.

      Regards,
      The Under-Warden
```

### Add: `procedural_notice.audit_warning` (fires when audit counter exceeds threshold)

```yaml
procedural_notice.audit_warning:
  register: direct
  subject: "Audit threshold notification: Standing review status pending"
  body:
    - |
      **Summary:** The audit counter for this visiting party has crossed the threshold for procedural review. The matter is now in standing review.

      Per Regulation 22-A (Cumulative Incident Threshold), this office is required to notify visiting parties when their accumulated administrative footprint exceeds the standard review boundary. The boundary is calculated according to the published schedule, which is, this office notes, available upon request, though it is more commonly observed in retrospect.

      The visiting party identified in the To: line has now produced an administrative footprint of sufficient cumulative size to warrant standing review. The relevant categories include, but are not limited to: filed terminations, unauthorized translocations, items of inventory removed from documented locations, and incidents of practice not enumerated in the visiting parties' descent advisories.

      No remedial action is required at this time. Standing review is a status. It is not, in itself, an action.

      The matter will be reviewed at the next scheduled audit session.

      Regards,
      The Under-Warden
```

### Add: `procedural_notice.run_clean` (fires when current run clean AND previous run clean)

```yaml
procedural_notice.run_clean:
  register: direct
  subject: "Routine correspondence: Floor {floor_best}, consecutive completions"
  body:
    - |
      **Summary:** No incidents of administrative note this descent. This office is, in the absence of other irregularities, obliged to note that the visiting party's presence itself remains the irregularity.

      The descent log for this visit records no terminations, no unauthorized translocations, no items of inventory removed from documented locations, and no incidents of practice not enumerated in the descent advisories. This office is required, per Regulation 4-B (Routine Correspondence Schedule), to acknowledge the visiting party's continued descent at intervals consistent with established procedure.

      Acknowledgment is hereby tendered.

      This office observes, without prejudice, that the visiting party has now completed two consecutive descents without incident. The frequency of these acknowledgments will, per regulation, increase with the duration of the visiting party's continued attendance. Visiting parties whose attendance becomes extended may, on occasion, find the volume of routine correspondence notable.

      The institution's records reflect that no visiting party of the Revenese practice has previously sustained this many consecutive incident-free descents under similar review status. The observation is offered for the record only.

      Regards,
      The Under-Warden
```

---

## File: `config/under_warden/memos.yaml` body[1+] variants

These add variant entries to two triggers already delivered in session 2. The body[0] entries are unchanged from session 2; included here as comments for reference only. Do not overwrite body[0] with the comment text; it is abbreviated here.

### Update: `polite.cause_trap` (add body[1] and body[2])

```yaml
polite.cause_trap:
  register: direct
  subject: "Termination, Floor {floor}, mechanical disposition"
  body:
    # body[0] is the session-2 canonical, unchanged. Full text already committed.
    - |
      [SESSION-2 CANONICAL, UNCHANGED - do not overwrite]
    # body[1] - second fire, shorter, assumes familiarity
    - |
      Mr. of Reven,

      **Summary:** Cause of termination, Floor {floor}: {cause_of_death}. Mechanical disposition re-armed.

      This office observes a recurrence of the previously documented pattern. The relevant floor maps remain available through the established channels.

      The mechanical disposition has been re-armed.

      With regards,
      The Under-Warden
    # body[2] - third fire and beyond, near-silence
    - |
      Mr. of Reven,

      **Summary:** {cause_of_death}, Floor {floor}. Re-armed.

      No comment.

      The Under-Warden
```

### Update: `polite.cause_acid` (add body[1] and body[2])

```yaml
polite.cause_acid:
  register: direct
  subject: "Termination, Floor {floor}, environmental"
  body:
    # body[0] is the session-2 canonical, unchanged. Full text already committed.
    - |
      [SESSION-2 CANONICAL, UNCHANGED - do not overwrite]
    # body[1] - second fire
    - |
      Mr. of Reven,

      **Summary:** Cause of termination, Floor {floor}: {cause_of_death}. Substance variation continues to be noted.

      This office records a second incident of contact with a corrosive substance during descent. The variation in pigmentation across the lower regions has been discussed in correspondence dated the previous descent.

      Replenishment continues.

      With regards,
      The Under-Warden
    # body[2] - third fire and beyond
    - |
      Mr. of Reven,

      **Summary:** {cause_of_death}, Floor {floor}.

      The substance is, in this institution, frequently variable in color. This office has noted that point in prior correspondence.

      The Under-Warden
```

---

## Authoring notes

**On the body[1+] weariness progression.** The variant arc for cause_trap and cause_acid runs from full explanation (body[0]) to compressed familiarity (body[1]) to near-silence (body[2]). The closer-courtesy attrits in parallel: "With courtesies" -> "With regards" -> bare signature. This is intentional and is the design payoff of the multi-fire system. A player who dies to traps five times should feel the Under-Warden's patience wear through the prose. The body[2] versions fire on third death and every subsequent death of that type, so they are the steady state for a player who keeps making the same mistake.

**On run_clean firing conditions.** This memo should fire only when the current run was clean AND the previous run was also clean (two consecutive). Single clean runs do not trigger it; the "consecutive" framing in the text depends on the two-in-a-row condition. If the trigger only checks current-run-clean, the "two consecutive descents" line will misfire on a player's first clean run after a death. Gate on consecutive.

**On audit_warning threshold.** This fires when the audit counter crosses a threshold. The threshold value is your call from harness data; the memo text is written to be threshold-agnostic (it never names a specific number). Tunable without content changes.

**On procedural_notice.death_repeat vs the polite.death_first / cause-specific memos.** death_repeat is the general mortality escalation; it fires on the third death regardless of cause. The cause-specific memos (cause_trap, cause_acid, cause_possession_neglect) fire on their specific causes. A single death could match both death_repeat and a cause-specific trigger. Priority ordering needed: I'd suggest cause-specific wins over death_repeat when both match, because the specific cause is more characterful than the general pattern. Confirm or propose different priority.

**On the {floor_best} slot in run_clean.** This memo uses {floor_best} (best floor reached across all runs) rather than {floor} (death floor), since run_clean has no death floor. Confirm the slot is available in the run_clean trigger context.

---

## Still ahead in memo content

After this batch:

1. **catalog_referenced** as a focused standalone session. The {catalog_entry} live-lookup memo. The one where the character becomes unsettling. Needs careful authoring built around the surfaced catalog entry.

2. **final_audit canonicals** for the major incident types (hall_warden_possession at minimum; possibly a general final_audit). The terminal tone, addressed to the file.

3. **formal_complaint and procedural_notice body[1+] variants** for the repeat-fire triggers in those tiers, if playtest shows they fire often enough to warrant variants.

After those, memo content is feature-complete and we move to the next content surface (general possession trigger pool, ~50-80 lines).
