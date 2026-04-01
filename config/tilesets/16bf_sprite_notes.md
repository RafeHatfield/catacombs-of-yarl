# Oryx 16-Bit Fantasy Sprite Notes
# Generated from TASK-005 verification pass (2026-03-30)

## File naming format

### creatures_24x24
Pattern:  oryx_16bit_fantasy_creatures_NN.png
Range:    01-396 (396 files total, no gaps)
Padding:  D2 (minimum 2 digits) — NOT D3 as originally assumed in the plan
          01, 02, ... 09, 10, 11, ... 99, 100, 101, ... 396
C# format specifier: index.ToString("D2")

The plan's draft frame_pattern used {index:D3} — this is WRONG. Must use D2.

### items_16x16
Pattern:  oryx_16bit_fantasy_items_NN.png
Range:    01-308 (308 files total, no gaps)
Padding:  D2 — same scheme as creatures

### classes_26x28
Pattern:  oryx_16bit_fantasy_classes_trans_NN.png
Count:    48 files
Note:     NOT consecutive — numbers encode grid positions in the source sprite sheet
          (03, 05, 07, 09, 11, 13 / 21-26 / 33-38 / 45-50 / 57-62 / 69-74 / 81-86 / 93-98)
          These are alternative player class sprites with transparent backgrounds.
          OUT OF SCOPE for entity mapping. The creature_key creature numbers (key 1-18)
          use creatures_24x24, not classes_26x28.

## Frame stride verification

Creature key entries: 198 named creatures (key file lines 1-206, blank separators excluded)
Total sprite files:   396
Ratio:               396 / 198 = exactly 2 frames per creature

### Stride formula (verified)

  sprite_index = creature_key * frame_stride + animation_frame + frame_offset

With frame_stride=2, frame_offset=-1:
  sprite_index = creature_key * 2 + animation_frame - 1

Verification against known creatures:
  Knight M   (key=1):   frame 0 → 1*2+0-1 =   1 → creatures_01.png ✓
                        frame 1 → 1*2+1-1 =   2 → creatures_02.png ✓
  Orc Fighter (key=137): frame 0 → 137*2+0-1 = 273 → creatures_273.png ✓
                         frame 1 → 137*2+1-1 = 274 → creatures_274.png ✓
  Green Slime (key=115): frame 0 → 115*2+0-1 = 229 → creatures_229.png ✓
                         frame 1 → 115*2+1-1 = 230 → creatures_230.png ✓

Conclusion: frame_stride=2, frame_offset=-1 confirmed correct. No per-entity overrides needed.

## YAML frame_pattern correction for TASK-006

The 16bit_fantasy.yaml tileset must use:

  frame_pattern: "oryx_16bit_fantasy_creatures_{index:D2}.png"   # D2 NOT D3

The plan draft used D3 — this must not be carried forward.

## Key creature mappings (sprite file pairs)

| Our type ID   | Creature key | Sprite files               |
|---------------|-------------|----------------------------|
| player        | 1           | creatures_01, creatures_02 |
| orc/orc_grunt | 137         | creatures_273, creatures_274 |
| orc_brute     | 138         | creatures_275, creatures_276 |
| goblin        | 132         | creatures_263, creatures_264 |
| troll         | 140         | creatures_279, creatures_280 |
| minotaur      | 99          | creatures_197, creatures_198 |
| slime         | 115         | creatures_229, creatures_230 |
| large_slime   | 114         | creatures_227, creatures_228 |
| bat           | 116         | creatures_231, creatures_232 |
| rat/giant_rat | 121         | creatures_241, creatures_242 |
| spider        | 119         | creatures_237, creatures_238 |
| zombie        | 151         | creatures_301, creatures_302 |
| skeleton      | 153         | creatures_305, creatures_306 |
| mummy         | 158         | creatures_315, creatures_316 |
| lich          | 160         | creatures_319, creatures_320 |
| demon         | 102         | creatures_203, creatures_204 |
| golem         | 105         | creatures_209, creatures_210 |
| cultist       | 161         | creatures_321, creatures_322 |

## .gitignore decision

UF sprites at src/Presentation/assets/sprites/ are already committed and tracked by git
(confirmed via git ls-files). No .gitignore rule for sprites exists in the repo.
16bf sprites at src/Presentation/assets/sprites_16bf/ will be treated the same way —
committed to the repo. Repo is private / single-developer. No change to .gitignore needed.

## Copy status

Source directories at ~/development/oryx/oryx_16-bit_fantasy_1.1/Sliced/ need to be
copied into src/Presentation/assets/sprites_16bf/. The Bash tool blocked the cp -r
commands during the TASK-005 agent run. Manual copy required:

  cp -r ~/development/oryx/oryx_16-bit_fantasy_1.1/Sliced/creatures_24x24 \
        src/Presentation/assets/sprites_16bf/creatures_24x24
  cp -r ~/development/oryx/oryx_16-bit_fantasy_1.1/Sliced/items_16x16 \
        src/Presentation/assets/sprites_16bf/items_16x16
  cp -r ~/development/oryx/oryx_16-bit_fantasy_1.1/Sliced/classes_26x28 \
        src/Presentation/assets/sprites_16bf/classes_26x28
