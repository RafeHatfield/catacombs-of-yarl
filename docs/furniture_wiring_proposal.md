# Canon furniture wiring proposal (for Rafe's ruling — issue #51)

Context: the play-review register ruling (2026-08) confirmed canon world tiles 317–324 as a
furniture cluster and substituted 319→table 5053, 321→chairs 5051/5056/5057. This doc proposes how
the *remaining* cluster members should participate in generated floors. **No config is changed
here** — this is a proposal only; the ruling is yours.

## Correction to the task premise (flagging, not guessing)

The task framed 317/318/322/323/324 as "new concepts needing props.yaml wiring." They are already
wired as game-key tile variants:

| game_key | current `tile_ids` | placed in a room recipe? |
|---|---|---|
| `bookshelf` | **[317, 318]** | **NO — placed in zero recipes** |
| `throne` | [322] | yes — ThroneRoom |
| `weapon_rack` | [323, 324] | yes — Armory |
| `desk` | [5062, 5063, 5064] (generated) | yes — Library |
| `table` | [5052, **5053**, 5054, 5055] | yes — Library, Kitchen |
| `chair` | [5051, 5056, 5057] | yes — Library, Kitchen |
| `armor_stand` | [5002] | yes — Armory |

So the real gaps are narrower than "wire five new props." Two items need a decision; two are
already done; one is a genuinely unwired canon tile.

## 1. bookshelf (317 filled / 318 empty) — the real gap

`bookshelf` is a fully-defined prop (game_key + both canon tiles) that **no room recipe ever
places**, so bookshelves never appear in the game. A Library with no bookshelves is the odd
result — its recipe currently is `table (Center) · chair · desk (WallAdjacent) · candelabra`.

**Proposal:** add `bookshelf` to the **Library** recipe as `WallAdjacent`, count 1–3, probability
~0.8 (a library should almost always have them). Suggested: keep `desk` too (a library has both).
Optionally add `bookshelf` to **Storage** at low probability (~0.3) — books get stored.

**Your explicit question — do shelf_bottles rooms want bookshelves?** Recommendation: **no.**
`shelf_bottles` lives in the **Laboratory** recipe and reads as alembics/reagent bottles, a
deliberately distinct concept from books. Mixing bookshelves into the Laboratory blurs the two
room identities. Keep books = Library/Storage, bottles = Laboratory.

## 2. spare table 320 (writing desk with paper + quill) — genuinely unwired

Canon 320 is not referenced anywhere in props.yaml. It reads as a **writing desk** (loose sheet +
quill on top), which matches the existing `desk` game_key's flavor ("A writing desk cluttered with
old papers…") far better than the plain `table`.

**Proposal:** add `320` as a canon variant of the **`desk`** game_key
(`tile_ids: [5062, 5063, 5064, 320]`). This drops a bold canon desk into the Library's existing
desk slot with no recipe change. (Alternative if you'd rather not mix canon into a
mostly-generated key: leave 320 unwired for now — it's low-value on its own.)

## 3. throne 322 & weapon stands 323/324 — already done, no action

Both are wired and placed (ThroneRoom, Armory). Noting them only so the cluster is fully accounted
for. If anything, the *generated* neighbours in those recipes (e.g. `armor_stand` 5002, pending its
canon-derived replacement) are the ones to watch — that's the Part B fineness sweep's job, not this
doc's.

## Summary of what a "yes" would change (config only — RoomPropPlacer recipes + props.yaml)

- Library recipe: `+ bookshelf (WallAdjacent, 1–3, ~0.8)`.
- (optional) Storage recipe: `+ bookshelf (WallAdjacent, 1–2, ~0.3)`.
- `desk` game_key: `tile_ids += 320`.
- Nothing for throne / weapon_rack (already wired + placed).

None of these are made here — awaiting your ruling on #51.
