# Isometric Tileset Research

_Last verified: 2026-07-12 against commit 86b6f10_

**Date:** 2026-03-30  
**Aesthetic target:** Rogue Wizards — alive, vibrant, readable on mobile  
**Baseline:** Oryx Iso Dungeon (already licensed). Everything below is rated relative to beating it.

---

## #1 — Oryx 16-Bit Fantasy + Iso Dungeon *(full ecosystem)*

**Creator:** Christopher Barrett (Oryx) — former Bungie Creative Director, creator of Realm of the Mad God's art  
**Price:** Already owned — `~/development/oryx/oryx_16-bit_fantasy_1.1` + `oryx_iso_dungeon`  
**Find it:** oryxdesignlab.com

| Criterion | Score |
|-----------|-------|
| Beauty | 8/10 |
| Game Fit | 10/10 |
| Completeness | 9/10 |
| Popularity/Trust | 10/10 |
| Mobile Suitability | 8/10 |

The 16-Bit Fantasy pack is what changes the equation — animated heroes, animated monsters (goblins, skeletons, dragons, bats), items, FX, UI. Layered onto the Iso Dungeon environment tiles, you get something meaningfully closer to the Rogue Wizards aesthetic tier. Every Oryx pack cross-compares, so the ecosystem compounds. Zero Godot friction.

**Concern:** The "everybody recognizes it" problem. If you want a visual identity, this works against you. Walk animations aren't included in 16-Bit Fantasy — idle only.

---

## #2 — GalefireRPG Isometric Dungeon Designer (Full Suite)

**Creator:** GalefireRPG — dedicated iso fantasy asset studio  
**Price:** ~$80–100 for full suite (base + Expansion + Caves + Monster Packs)  
**Find it:** galefirerpg.itch.io

| Criterion | Score |
|-----------|-------|
| Beauty | 9/10 |
| Game Fit | 9/10 |
| Completeness | 7/10 |
| Popularity/Trust | 7/10 |
| Mobile Suitability | 7/10 |

The richest environment art in this list. Hand-crafted, modular isometric dungeon system — torches, ruins, undead, cavern environments, demon fortresses. Warm candlelight and strong color contrast give it the "alive" quality. The modular construction approach means infinite dungeon variety.

**Concern:** Strong on environments, weaker on player/hero characters — would need supplementing. Sprite extraction for Godot takes work. High detail can compress poorly at small sizes; test at target resolution.

---

## #3 — PVGames Medieval Bundle

**Creator:** PVGames — RPG asset studio with active Patreon  
**Price:** ~$60 for the full 10-pack bundle  
**Find it:** pvgames.itch.io

| Criterion | Score |
|-----------|-------|
| Beauty | 8/10 |
| Game Fit | 9/10 |
| Completeness | 9/10 |
| Popularity/Trust | 8/10 |
| Mobile Suitability | 7/10 |

The monster depth here is unmatched — 24+ monsters with full animation sheets, 8 unique boss monsters with walk/KO/battler/face animations, animated dungeon objects (doors, light sources, magic orbs). The Underdeep pack adds cavern/dwarven/drow environments. Patreon means ongoing content drops.

**Concern:** 2.5D perspective, not strict isometric — requires care with your tile layer. Shadows baked into tiles. Godot slicing work needed.

---

## #4 — Epic Isometric

**Creator:** Alex Drummond / WarDrumRPG — Australian artist  
**Price:** ~$20 via Bundle of Holding; individual packs on Roll20  
**Find it:** epicisometric.com

| Criterion | Score |
|-----------|-------|
| Beauty | 9/10 |
| Game Fit | 8/10 |
| Completeness | 7/10 |
| Popularity/Trust | 7/10 |
| Mobile Suitability | 8/10 |

Not pixel art — hand-drawn isometric illustration in the vein of Diablo and Baldur's Gate. Genuinely gorgeous and unlike anything else here. 332-piece dungeon set, 50+ monster tokens, 13 premade maps, transparent PNGs. If you want to not look like a pixel roguelike and instead have an "illustrated adventure" feel, this is the path.

**Concern:** Designed for tabletop VTTs — significant pipeline work for Godot. No walk/attack animations (static). Committing to this style means a full art-direction commitment — it won't mix with pixel UI cleanly.

---

## #5 — Oryx Iso Dungeon + Ultimate Fantasy *(current baseline)*

**Creator:** Oryx  
**Price:** ~$15  
**Find it:** oryxdesignlab.com

| Criterion | Score |
|-----------|-------|
| Beauty | 6/10 |
| Game Fit | 10/10 |
| Completeness | 8/10 |
| Popularity/Trust | 10/10 |
| Mobile Suitability | 9/10 |

Where we are now. It works. It ships games. It does not turn heads. Listed here as the low-risk baseline, not a recommendation to stay here.

---

## Recommendation

**Near-term:** Add **Oryx 16-Bit Fantasy** to what's already licensed — smallest delta for the biggest aesthetic jump, proven mobile-readable, zero Godot friction.

**If the "everyone recognizes Oryx" problem starts to matter:** GalefireRPG is the environment upgrade path; PVGames fills the boss/monster depth gap.

**Wild card:** Rogue Wizards' artist is reportedly a freelancer. Commissioning a custom character layer on top of a licensed environment pack is a path that exists if a truly distinctive look becomes the priority.

---

## Summary Table

| Rank | Pack | Price | Beauty | Game Fit | Integration Effort |
|------|------|-------|--------|----------|--------------------|
| 1 | Oryx 16-Bit Fantasy + Iso Dungeon | ~$40 | 8/10 | 10/10 | Very Low |
| 2 | GalefireRPG Full Suite | ~$80–100 | 9/10 | 9/10 | Medium |
| 3 | PVGames Medieval Bundle | ~$60 | 8/10 | 9/10 | Medium |
| 4 | Epic Isometric | ~$20 | 9/10 | 8/10 | High |
| 5 | Oryx Iso Dungeon + Ultimate Fantasy | ~$15 | 6/10 | 10/10 | Very Low |
