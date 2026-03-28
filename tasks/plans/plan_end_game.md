# Plan: End Game and Victory Conditions

Status: [ ] Not started
PoC reference: config/endings.yaml, components/ai/boss_ai.py, components/ai/lich_ai.py

---

## What It Is

The final dungeon depth contains Zhyraxion (the final boss) and a multi-path confrontation with 5 distinct endings. The boss has multiple forms. The player's prior knowledge (discovered lore, specific items collected) determines which endings are accessible.

---

## Final Boss: Zhyraxion

### The Character

Zhyraxion is a transformed human who became a dragon. He's grieving (his mate Aurelyn was killed), which is the root of the catacombs — the dungeon was Aurelyn's lair, now corrupted. The Ruby Heart artifact is the MacGuffin that connects player to boss.

### Boss Forms

Zhyraxion has three combat forms in sequence:

#### Form 1: `zhyraxion_human`
- Appears human (or partially transformed)
- Moderate HP, uses weapons and spells
- Melee + magic hybrid
- When HP drops below threshold → transforms

#### Form 2: `zhyraxion_full_dragon`
- Full draconic form; massive HP, high damage
- Breath weapon (fire cone, large radius)
- Wing buffet (knockback AoE)
- Phase transition at ~30% HP

#### Form 3: `zhyraxion_grief_dragon`
- Rage/grief form; most powerful
- Enhanced fire attacks
- OathEmbersEffect, OathVenomEffect, OathChainsEffect active
- Can only be ended via combat OR special dialogue option (True Name)

---

## Five Endings

### 1. Keep the Heart (Standard)
- Fight Zhyraxion to defeat
- After defeating Form 3, confrontation scene
- Player keeps Ruby Heart and escapes
- "Standard" victory — good but not perfect

### 2. Give the Heart (Escape Ending)
- During confrontation scene, offer the Ruby Heart to Zhyraxion
- Boss takes it, let's player leave
- Weakest ending (player got scared and gave up the treasure)
- Unlocks early if player wants to bail

### 3. Destroy the Heart
- During confrontation scene, destroy the Ruby Heart
- Zhyraxion is weakened/killed by this (his life force connected to it)
- Morally ambiguous — you destroyed something irreplaceable
- Can unlock a secret ending follow-up

### 4. Speak the True Name (Secret Ending)
- Requires: player discovered the inscription with Zhyraxion's true name earlier in the dungeon
- During confrontation: "I know your name."
- Zhyraxion is bound; cannot attack; full dialogue tree
- Multiple resolution options within this ending
- Only accessible if player found the mural with the true name

### 5. Accept Transformation (Alternate Ending)
- Requires: specific item (Crimson Ritual artifact) collected mid-dungeon
- Player undergoes transformation during confrontation
- Becomes like Zhyraxion; shared ending
- Rare, requires specific run path

---

## Confrontation Chamber

The boss room is the Confrontation Chamber:
- Dedicated room type (not random generation)
- Pre-defined layout from level template
- Scripted encounter triggers (dialogue, phase transitions)
- After boss fight: dialogue/choice triggers automatically

---

## Cutscene / Dialogue System

A minimal interactive narrative system for the ending:
- **Sequential text panels** with "next" button
- **Choice points** — player selects from 2–4 options
- Choices gated by: items in inventory, discovered lore flags, boss HP state
- No voice acting; pure text
- After choice: trigger ending animation/screen

---

## Victory Screen

After successful ending:
- Display chosen ending text
- Statistics summary (turns, deaths, items used, depths cleared)
- "Play Again" and "Return to Menu" buttons
- Meta-progression hook: first win unlocks meta features (item identification persistence, etc.)

---

## Lore Objects (Required for Secret Endings)

Several dungeon features exist primarily to enable secret endings:

- **Mural: Zhyraxion's True Name** — located on depth 3-4; reveals true name for ending 4
- **Crimson Ritual scroll** — rare drop on depth 4-5; enables ending 5
- **Aurelyn's Memory** — lore item; gives dialogue context, unlocks additional ending options

These are placed via level template guarantees (not pure random).

---

## Ruby Heart (MacGuffin)

The Ruby Heart is a key item:
- Appears on depth 5 (guaranteed spawn in specific room)
- Held in inventory for the rest of the run
- Its presence/absence in inventory at confrontation determines endings 1-3
- Cannot be dropped (or dropping has dramatic consequences)

---

## C# Port Checklist

### Boss
- [ ] `zhyraxion_human`, `zhyraxion_full_dragon`, `zhyraxion_grief_dragon` entity definitions
- [ ] Boss AI for each form (separate AI components)
- [ ] Form transition triggers (HP thresholds)
- [ ] Breath weapon (fire cone, AoE)
- [ ] Wing buffet (knockback AoE)
- [ ] Oath effects on Form 3

### Confrontation System
- [ ] Confrontation Chamber room type (guaranteed, pre-designed layout)
- [ ] Phase detection: combat ends → confrontation triggers
- [ ] Dialogue system (sequential panels, branching choices)
- [ ] Ending gates (inventory checks, lore flag checks)
- [ ] 5 ending implementations

### Lore Objects
- [ ] `ruby_heart` key item (guaranteed spawn depth 5)
- [ ] `zhyraxion_true_name` mural (guaranteed, depth 3-4)
- [ ] `crimson_ritual` rare drop item
- [ ] Lore flag tracking (player discovered true name? has ritual artifact?)

### Victory Screen
- [ ] Ending-specific text
- [ ] Statistics summary
- [ ] Play again / return to menu
- [ ] Meta-progression hook (first-win unlock)
