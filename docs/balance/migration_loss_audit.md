# PoC → C# Migration-Loss Audit (Triage)

**Date:** 2026-06-08. **Method:** four parallel ground-truth passes (status-effects, AI/movement,
items/loot/spells, combat/monsters/bosses) comparing the Python PoC (`~/development/rlike`) against the
current C# codebase. **Purpose:** make the losses KNOWN rather than discovered ad hoc, so a balance pass
doesn't trip over a fourth false premise mid-tune. **This is a triage list, not a mandate to restore
everything.**

## Headline

The migration did **not** hemorrhage systems. Core combat math, every Phase-19 monster special, the pity
system, in-run identification, the full spell set (exceeds the PoC's catalog), corpses, and ground hazards
(Fire + PoisonGas — the complete PoC set) all survived **fully wired**. The damage is a **narrow, recurring
seam**: status effects that are *applied* by the spell/item layer but whose payload is *never consumed* —
plus a handful of isolated drops. Three confirmed losses (faction wire, hazard-avoidance, haste/tar) were
all invisible to the harness, which is why they rotted silently.

## The one B1–B2 gate — verified and CLEARED

Of every finding, only **Speed/Sluggish (haste/tar)** plausibly affected B1–B2 tuning. **Verified 2026-06-08:
no gate.** Those items ARE in B1–B2 loot (`scroll_of_haste` B1, band_min 1; `potion_of_speed`/`wand_of_haste`/
`tar_potion` B2, band_min 2), but the soak bot **never uses them** — `BotBrain.DecideInternal` emits only
Heal/Attack/Move/Wait, and "potion" detection everywhere filters on `Consumable.IsHealing == true`. Speed/tar
are invisible to the bot (not even picked up). Fixed-scenario assertions don't grant them either. So the inert
effect cannot pollute B1–B2 numbers. Speed/Sluggish restore → **Track-2**, and it's **necessary-but-not-
sufficient**: the bot needs a non-healing use-policy (new `BotAction` types) before haste/tar show up in soak
survival at all. Verify-first paid off: present in loot, but cleanly sorted to Track-2 for the cost of one check.
Everything else is deep-region, gear-curve (muted because assertions are at *baseline gear*), or superseded.

---

## RESTORE-NOW (cheap; clear loss or gates near-term work)

| Feature | What it was (PoC) | What survived (C#) | Cost | Note |
|---|---|---|---|---|
| **Speed/Sluggish (haste & tar)** | Real haste = `LightningReflexesEffect` → `speed_tracker.set_temporary_bonus(0.5)`, consumed by `roll_for_bonus_attack` (`speed_bonus_tracker.py:276`); tar = `add_debuff(0.25)`. Worked. | `SpeedEffect.SpeedBonusRatio` / `SluggishEffect.SpeedPenaltyRatio` **set-but-never-read**; `SpeedBonusTracker` has no temporary/debuff slot. Haste potion, scroll_of_haste, tar potion all **inert**. | hours | One tracker change (temporary-bonus + debuff term) resurrects 2 potions + a scroll. **The B1–B2 gate.** |
| **Aggravation faction-targeting** | `EnragedAgainstFactionEffect.target_faction` consumed by `basic_monster.py:844` to retarget a monster onto a chosen faction. | `AggravatedEffect.TargetFaction` **set** (`SpellResolver.cs:709`) but read by nothing. Faction registry + `ChooseTarget` are fully ported — only the override branch was lost. | trivial-rewire (~25–40 lines) | The "turn-monsters-on-each-other" pillar. Land alongside B1–B2. Deep-region counter (not a B1–B2 gate). |

## RESTORE-LATER (real loss; schedule when its region/need arrives)

| Feature | What it was (PoC) | What survived (C#) | Cost | When |
|---|---|---|---|---|
| **Monster hazard-avoidance** | Weighted A* cost (`entity.py:530`, fire +10) — **all** monsters preferred safe routes; decayed with hazard. | `Pathfinder.AStar` has only binary `avoidTiles` hard-skip, used by the player bot only; no monster passes it. Hazard damage data (`GroundHazard.CurrentDamage`) exists, unused by AI. | hours | Before B3+ (where player AoE/hazard tools come online). General AI fidelity. |
| **Chest quality tiers** | `Chest.loot_quality` (common→legendary) → scaled item count + rare-biased tables. | `ChestLootGenerator` draws 2–3 from the shared depth pool — no tier, no count scaling. Chests = floor drops. | hours | Before loot-curve work. Only silently-lost item with real player-facing bite. |
| **Graded % resistances** | 0–100% per-type dict + equipment aggregation + 100=immune; bosses used `fire:100, cold:75`. | Binary only: one resist (half) + one vuln (double). `DamageModifiers.cs:24`. | real-chunk | Before elemental bosses / resistance rings. Fine for current shallow monsters. |
| **Ring effects — Clarity, Invisibility** | confusion-immunity; on-descend invisibility N turns. | enum + YAML present; **inert** (no-op). Both reuse effects that already exist (`DisorientationEffect`, `InvisibilityEffect`). | trivial each | When ring content matters. Cheapest two ring wins. |
| **Ring effects — Resistance, Searching, Wizardry, Luck** | resistance%, trap/secret reveal, caster +duration/dmg, crit+loot. | enum + YAML; **inert**, need new plumbing. | hours each | With ring content. (Luck doubles as the unknown-ring fallback — masks YAML typos; flag.) |
| **Monster potion-quaff / scroll-use** | `monster_item_usage.py` — scrolls ON, potions OFF; monsters quaffed heals / read scrolls. | Quaff branch exists (`BasicMonsterAI.cs:97`) but gated on `CanUseItems`, which has no YAML field → always false. Scroll-use not ported. | potion: trivial; scroll: real-chunk | When monster item-use is wanted; needs a balance reason. |

## DROP-AS-SUPERSEDED (gone by design — confirm and move on)

| Feature | Why it's not a loss |
|---|---|
| **Boss system** (enrage / multi-phase / dialogue / named dragons: Dragon Lord, Demon King, Zhyraxion) | Replaced by **The Weighing** tribunal endgame (`src/Logic/Endgame/`, [[project_weighing_arena_decision]]). Deliberate narrative redesign. |
| **Player XP / leveling** | `PLAYER_PROGRESSION_DOCTRINE` explicitly rejects XP-for-boons. (Latent: dead `Fighter.Xp` field on player — harmless set-but-unread.) |
| **Level-scaled LootRarity/LootGenerator** | Superseded by the band+EV model — and was **dead-in-PoC too** (no callers). Not a migration loss. |
| **Zombie-swarm / SlimeAI hostile-all archetypes** | Slime identity is now engulf/split; hostile-all survives as the temporary `EnragedEffect`. Deliberate redesign. |
| **Monster portal curiosity** | Forced displacement (`PortalSystem`) covers the tactical case; voluntary use was flavor. |
| **Enraged damage/accuracy multipliers (2.0×/0.5×)** | **Never lived in either codebase** — set-but-unread in the PoC too. If wanted, it's net-new design, not a restore. |

## NOT-A-LOSS / CLEANUP

- **Species-ability stub** (`TurnController.cs:335`) — no player species/monster-ability system ever existed
  in the PoC; forward-looking placeholder. Leave.
- **Stale comments to fix** (they assert false premises — exactly the trap this audit guards against):
  `AggravatedEffect.cs:11` "faction system not yet implemented" (it is); `SpellResolver.cs:102` raise-dead
  "stub" (it's wired); `DungeonFloorBuilder.cs:622` pity "not yet ported" (it landed).
- **Lich Soul Bolt retune** — PoC 0.35/cd4 vs C# 0.18/cd8. Balance retune, not a loss; confirm intentional.

## Harness blindness (the systemic accountability flag)

None of the inert effects are catchable by the current suite — tests assert the effect *component is
attached*, never that it changes an outcome; no scenario exercises haste/tar/aggravation/hazard-fields/
rage-multipliers. So they stayed green in CI while mechanically dead. **Rule:** any restore ships with a
scenario that exercises its outcome, or it rots again.
