# Plan: Identification System

**Status:** [x] Complete — needs review  
**PoC reference:** `~/development/rlike/config/identification_manager.py`, `~/development/rlike/config/item_appearances.py`, `~/development/rlike/config/factories/_factory_base.py`, `~/development/rlike/config/game_constants.py`, `~/development/rlike/item_functions.py`

---

## What This Plan Does

Items in categories potion / scroll / wand / ring spawn with hidden identity. The player sees
a texture descriptor ("Fizzy Potion") or material name ("Jade Ring") until the item is used or
equipped. Once identified, all future items of that type in the run show their true name.
Appearance assignments are deterministic from run seed and shuffle each new game.

---

## Design Decisions (2026-04-01)

### Sprite approach per category

| Category | Unidentified sprite | Identified sprite |
|---|---|---|
| Potion | One of 3 black mystery sprites (36/37/38), randomized per type | True color sprite per type |
| Scroll | Single rune sprite (`rune_scroll` = 45) | Same sprite — name changes |
| Wand | Single mystery sprite (`unknown_wand` = 50) | True wand sprite per type |
| Ring | Randomized material sprite (one of 5: 76–80) | Same sprite as unidentified |

**Potions:** Three distinct black bottle silhouettes (36, 37, 38) are assigned per type at run
start. The magic conceals the contents — players cannot tell by color what a potion does until
they identify it. Text descriptors are texture/feel-based, never color-based, to avoid
implying any visual information.

### Descriptor pools

**Potions** — texture/feel, never color:
> fizzy · thick · runny · opaque · smoking · syrupy · slimy · chunky · warm · ice-cold ·
> sour-smelling · sweet · acrid · effervescent · cloudy

Max 15 potion types supported. Warn in log if pool exhausted; fallback: "Unknown Potion".

**Wands** — material/feel:
> gnarled oak · smooth birch · rough pine · polished ebony · cracked ivory · cold iron ·
> humming · vibrating · warm copper · heavy lead

Max 10 wand types supported.

**Scrolls** — rune labels (NetHack-style, from PoC):
> KIRJE XIXAXA · ZELGO MER · JUYED AWK YACC · FOOBIE BLETCH · ETAOIN SHRDLU · FNORD ·
> HAPAX LEGOMENON · EIRIS SAZUN · GHOTI · NR 9 · XIXAXA XOXAXA XUXAXA · YUM YUM ·
> PRATYAVAYAH · DAIYEN FOOELS · THARR · VERR YED HORRE · VENZAR BORGAVVE · PRIRUTSENIE

Max 18 scroll types supported.

**Rings** — material name + distinct sprite (5 variants 76–80, text remains unique):
> wooden · iron · copper · bronze · silver · gold · platinum · jade · opal · pearl · ruby ·
> sapphire · ivory · bone · obsidian · moonstone

16 ring types, 5 sprite variants. Multiple types share a sprite; text is the primary identifier.

### Identification triggers

- **Potions / scrolls / wands:** identified when used/read/fired
- **Rings:** identified when equipped (not on pickup)
- **Scroll of Identify:** when used, instantly identifies 1–3 random unidentified item *types*
  from the player's inventory. If the scroll itself is unidentified, using it identifies it
  first (counts as the use trigger), then still applies the 1–3 effect.

### Wand charging gate

An unidentified scroll cannot auto-recharge an unidentified wand on pickup. Scroll goes to
inventory silently (normal pickup toast fires; recharge toast is suppressed). Once both are
identified, the existing `TryRechargeWand` auto-charge behaviour resumes as normal.

Using an unidentified scroll to identify it *consumes* it — it won't recharge the wand.
That is the cost of ignorance. Intentional.

### Stacking rules

- Items stack by `ItemTag.TypeId` (not `Entity.Name`)
- Unidentified items of the same type stack (same appearance by definition — appearance is
  type-level, not instance-level)
- When a type is identified, every item of that type in inventory becomes identified, and
  display updates immediately

### Pre-identification (difficulty-scaled, per-type per run)

The decision is made **once per type** when the first instance of that type is created.
Subsequent instances of the same type inherit the cached decision. This prevents a type from
"flipping" mid-run if a second instance rolls differently.

| Category | Easy | Medium (default) | Hard |
|---|---|---|---|
| Potions | 80% | 50% | 5% |
| Scrolls | 80% | 40% | 5% |
| Wands | 75% | 30% | 0% |
| Rings | 90% | 40% | 0% |
| Weapons / armor / other | 100% | 100% | 100% |

### Display

- Unidentified: "Fizzy Potion", "Scroll labeled ZELGO MER", "Humming Wand", "Jade Ring"
- Identified: "Healing Potion", "Scroll of Identify", "Wand of Fireball", "Ring of Protection"
- No material suffix after ring identification ("Ring of Protection", not "Ring of Protection (jade)")
- Toast on identification: `"You realize this was a Potion of Healing!"`

### Out of scope (deferred)

- Weapon/armor identification or enchantment levels
- Cursed items
- Meta-progression (post-win permanent identification)
- Save/load serialization (defer until save system exists; note hooks in code)
- Master toggle (`identification_system_enabled`)
- Testing mode (all-identified override)

---

## Architecture

### New files

```
src/Logic/Content/IdentificationRegistry.cs  — per-run state: which types are known/decided
src/Logic/Content/AppearancePool.cs          — per-run appearance + mystery sprite assignment
src/Logic/ECS/IdentifiableItem.cs            — component: unidentified/identified display names
```

### Modified files

```
src/Logic/Content/ItemDefinition.cs          — add ItemCategory
src/Logic/Content/ConsumableFactory.cs       — attach ItemTag + IdentifiableItem; apply pre-ID
src/Logic/Content/SpellItemFactory.cs        — attach ItemTag + IdentifiableItem; apply pre-ID
src/Logic/Core/GameState.cs                  — hold IdentificationRegistry + AppearancePool
src/Logic/Core/GameStateFactory.cs           — init registry/pool at run start; carry on floor descent
src/Logic/Core/TurnController.cs             — TryRechargeWand gate; identification on use/equip
src/Logic/ECS/Inventory.cs                   — stack by TypeId instead of Entity.Name
config/entities.yaml                         — add category: field to all items; add scroll_of_identify
config/tilesets/16bit_fantasy.yaml           — add mystery sprite keys (black potions, rune scroll, plain wand)
config/game_settings.yaml                    — add difficulty: field
tests/Core/IdentificationTests.cs            — new test file
```

Note: `ItemFactory.cs` (weapons/armor) needs **no changes** — those items are always identified.

---

## Implementation Notes (2026-04-01)

All 11 tasks complete. 29 new tests added; 763 total passing (up from 734).

**Key decisions:**
- `ItemCategory` enum and `DisplayName`/`Id` fields added to all three definition types (`ItemDefinition`, `ConsumableDefinition`, `SpellDefinition`).
- `ContentLoader` sets `Id` and `Category` on consumables/scrolls/wands after deserialization.
- `IdentificationRegistry` and `AppearancePool` are created by `DungeonFloorBuilder.Build()` (new run) or passed through unchanged (floor transition). Not created in scenario mode (harness unaffected).
- Pre-identification parameters are optional on factory `Create` methods — all existing call sites unchanged.
- `EntityPlacer.FillRooms` now accepts optional identification params and threads them to factory calls.
- `TurnController.TryIdentifyOnUse` is the single point where use/equip triggers identification.
- `TurnController.TryRechargeWand` gates on both scroll AND wand being identified.
- `Inventory.Add` now uses `ItemTag.TypeId` for stacking, falling back to name for untagged items.
- `ItemDisplay` helper in Presentation handles display name + sprite key selection. `ToastLog` handles `IdentificationEvent`.
- `HUD.Refresh` uses `ItemDisplay.GetDisplayName` for equipment summary.
- Scroll of Identify (`spell_id: "identify"`) wired in `SpellResolver`. Identifies 1–3 random unidentified types from inventory; scroll self-identifies via `TryIdentifyOnUse`.
- Deferred: save/load serialization hooks (commented `// TODO: wire to save`), master toggle, testing mode, meta-progression permanent identification.
- One warning: `AppearancePool_DescriptorPoolExhausted_FallsBackGracefully` test deliberately triggers the 16-over-15-pool warning — that's expected.

**Files changed:**
- NEW: `src/Logic/ECS/IdentifiableItem.cs`
- NEW: `src/Logic/Content/IdentificationRegistry.cs`
- NEW: `src/Logic/Content/AppearancePool.cs`
- NEW: `src/Logic/Content/PreIdentification.cs`
- NEW: `src/Logic/Core/Difficulty.cs`
- NEW: `src/Presentation/ItemDisplay.cs`
- NEW: `tests/Core/IdentificationTests.cs`
- MOD: `src/Logic/Content/ItemDefinition.cs` — `ItemCategory` enum + `Category`/`DisplayName` fields
- MOD: `src/Logic/Content/ConsumableDefinition.cs` — `Category`, `DisplayName`, `Id` fields
- MOD: `src/Logic/Content/SpellDefinition.cs` — `Category`, `DisplayName`, `Id` fields
- MOD: `src/Logic/Content/ContentLoader.cs` — sets `Id`/`Category` on consumables/scrolls/wands
- MOD: `src/Logic/Content/ConsumableFactory.cs` — attaches `ItemTag`+`IdentifiableItem`, supports pre-ID params
- MOD: `src/Logic/Content/SpellItemFactory.cs` — attaches `ItemTag`+`IdentifiableItem`, supports pre-ID params
- MOD: `src/Logic/Core/GameState.cs` — `IdentificationRegistry`, `AppearancePool`, `Difficulty` properties
- MOD: `src/Logic/Core/GameStateFactory.cs` — no logic changes (scenario path untouched)
- MOD: `src/Logic/Core/DungeonFloorBuilder.cs` — creates/carries registry+pool; passes to `FillRooms`
- MOD: `src/Logic/Core/EntityPlacer.cs` — optional identification params on `FillRooms`
- MOD: `src/Logic/Core/TurnController.cs` — `TryIdentifyOnUse` helper; identification triggers on use/equip; wand charging gate
- MOD: `src/Logic/Core/TurnEvent.cs` — `IdentificationEvent` added
- MOD: `src/Logic/Core/SeededRandom.cs` — `NextFloat()` added
- MOD: `src/Logic/ECS/Inventory.cs` — stacking by `TypeId` (name fallback preserved)
- MOD: `src/Logic/Combat/SpellResolver.cs` — `"identify"` spell handler
- MOD: `src/Presentation/Entities/ItemSpriteManager.cs` — mystery sprite selection via `ItemDisplay`
- MOD: `src/Presentation/UI/HUD.cs` — equipment summary uses `ItemDisplay.GetDisplayName`
- MOD: `src/Presentation/UI/ToastLog.cs` — `IdentificationEvent` toast handler
- MOD: `config/entities.yaml` — `scroll_of_identify` entry; added to floor item pool
- MOD: `config/tilesets/16bit_fantasy.yaml` — mystery sprite keys added
- MOD: `config/game_settings.yaml` — `difficulty: "medium"` added

---

## Tasks

### TASK-001 — Data model foundation

**Files:** `ItemDefinition.cs`, `config/entities.yaml`, `config/tilesets/16bit_fantasy.yaml`,
`config/game_settings.yaml`

**A. `ItemCategory` enum (logic layer):**
```csharp
public enum ItemCategory { Other, Potion, Scroll, Wand, Ring }
```
Add `public ItemCategory Category { get; set; } = ItemCategory.Other;` to `ItemDefinition`.

**B. `entities.yaml` additions:**
- Add `category:` field to every item. Potions → `potion`, scrolls → `scroll`, wands → `wand`,
  rings → `ring`, everything else → `other` (or omit, defaults to Other).
- Add `scroll_of_identify` entry (category: scroll, spell targeting: self/inventory,
  appropriate spawn weights for depth 1+).

**C. Mystery sprite keys in `16bit_fantasy.yaml`:**
```yaml
# Mystery sprites for unidentified items
unknown_potion_a: "36"   # black bottle variant 1
unknown_potion_b: "37"   # black bottle variant 2
unknown_potion_c: "38"   # black bottle variant 3
unknown_wand: "50"        # plain wooden wand
rune_scroll: "45"         # standard scroll (all scrolls share one sprite)
```
Ring mystery sprites use the existing pool (76–80); no separate key needed.

**D. `game_settings.yaml`:** Add `difficulty: "medium"` (easy / medium / hard).

**Acceptance:** All items in entities.yaml have a category. Mystery sprite keys present in
tileset YAML. `scroll_of_identify` spawns on floor. `dotnet test --filter Category!=Slow` passes.

---

### TASK-002 — `IdentifiableItem` component + `ItemTag` on consumables

**Files:** `src/Logic/ECS/IdentifiableItem.cs`, `ConsumableFactory.cs`, `SpellItemFactory.cs`

`Entity.Name` is immutable (set in constructor). Display name changes on identification require
a separate mechanism. Add a component:

```csharp
public sealed class IdentifiableItem : IComponent
{
    public Entity? Owner { get; set; }
    public string UnidentifiedName { get; init; } = "";  // "Fizzy Potion"
    public string IdentifiedName { get; init; } = "";    // "Healing Potion"
}
```

The display layer checks `registry.IsIdentified(tag.TypeId)` and reads the appropriate field.
`Entity.Name` is never changed.

Both `ConsumableFactory` and `SpellItemFactory` currently **do not attach `ItemTag`** to the
entities they create. This means there is no `TypeId` available on these items today. Fix:
add `entity.Add(new ItemTag { TypeId = def.Id })` in both factories alongside the existing
component setup. Also attach `IdentifiableItem` with `IdentifiedName = def.DisplayName` and
`UnidentifiedName = ""` (pool fills this in TASK-003).

**Acceptance:** A potion entity has `ItemTag` with correct TypeId. It has `IdentifiableItem`
with both name fields set. Test confirms tag survives inventory add/remove.

---

### TASK-003 — `AppearancePool` and `IdentificationRegistry`

**Files:** `AppearancePool.cs`, `IdentificationRegistry.cs`

**`IdentificationRegistry`:**
```csharp
public class IdentificationRegistry
{
    private readonly HashSet<string> _identified = new();
    private readonly HashSet<string> _decidedUnidentified = new();

    public bool IsIdentified(string typeId) => _identified.Contains(typeId);
    public bool HasDecision(string typeId) =>
        _identified.Contains(typeId) || _decidedUnidentified.Contains(typeId);

    /// Returns true if newly identified (false if already known).
    public bool Identify(string typeId) { ... }

    /// Record a pre-ID decision of "unidentified" so the same type doesn't re-roll.
    public void MarkUnidentified(string typeId) { ... }
}
```

**`AppearancePool`:**
- Initialized with run seed + list of all `ItemDefinition`s that have a non-Other category
- Assigns one descriptor per type (shuffle pool, assign in order)
- Potions: assigns descriptor string AND one of the 3 black potion sprite keys (36/37/38),
  cycling through them (type 0 → 36, type 1 → 37, type 2 → 38, type 3 → 36, ...)
- Rings: assigns material name AND a sprite file# (76–80, cycling)
- Wands: assigns material descriptor; sprite is always `unknown_wand`
- Scrolls: assigns rune label; sprite is always `rune_scroll`

```csharp
public string GetDescriptor(string typeId)       // "Fizzy" / "Jade" / "ZELGO MER"
public string GetMysterySprite(string typeId)    // "36" / "77" / "50" / "45"
public string GetDisplayName(string typeId)      // "Fizzy Potion" / "Jade Ring" / etc.
```

`GetDisplayName` is a formatting convenience — category-aware combination of descriptor +
category noun. Lives in logic layer as string formatting only (no Godot).

**Acceptance:** Same seed → same assignments. Different seed → different. Statistical test:
over 100 seeds, all 3 black potion sprites used roughly equally across types. Ring sprites
cycle through 76–80 correctly.

---

### TASK-004 — Wire registry + pool into `GameState`

**Files:** `GameState.cs`, `GameStateFactory.cs`

Add to `GameState`:
```csharp
public IdentificationRegistry IdentificationRegistry { get; init; }
public AppearancePool AppearancePool { get; init; }
```

**`GameStateFactory.CreateInitialState()`:** Initialize both from `GameState.Seed` and the
full list of item definitions from the content bundle.

**Floor descent carry-forward:** `PlayerCarryForward` handles entity state only and cannot
carry `GameState`-level objects. The registry and pool must be passed at the `GameStateFactory`
level when building a new floor's `GameState`. Add an overload or parameter:

```csharp
// New floor in same run — carry registry + pool from previous floor's state
public GameState CreateFloorState(GameState previousFloor, int newDepth) { ... }
```

Registry and pool are passed through unchanged. They are **not** reset between floors; only
reset on new game (`CreateInitialState`).

**Acceptance:** Identify a potion on floor 1, descend. Potion is still identified on floor 2.
Test confirms registry survives `CreateFloorState`.

---

### TASK-005 — Pre-identification at item creation

**Files:** `ConsumableFactory.cs`, `SpellItemFactory.cs`

After creating an item entity and attaching `ItemTag` + `IdentifiableItem` (TASK-002):

```csharp
void ApplyPreIdentification(Entity item, ItemDefinition def,
    IdentificationRegistry registry, AppearancePool pool, Difficulty difficulty)
{
    if (def.Category == ItemCategory.Other) return;

    // Per-type decision: only roll once per type per run
    if (registry.HasDecision(def.Id))
    {
        // Decision already made — nothing to do (item's ID state implicit in registry)
        return;
    }

    float pct = GetPreIdPercent(def.Category, difficulty);
    if (Rng.NextFloat() < pct)
        registry.Identify(def.Id);
    else
        registry.MarkUnidentified(def.Id);
}
```

Also set `IdentifiableItem.UnidentifiedName` from `pool.GetDisplayName(def.Id)` at creation time
(the pool already assigned this at run start, so just read it).

**Acceptance:** Over 500 medium-difficulty games, potion pre-ID rate converges to ~50%.
Same type never "flips" within a run — first instance's decision is always the run's decision.

---

### TASK-006 — Identification on use/equip

**Files:** `TurnController.cs` (item use dispatch), or wherever scroll/potion/wand use and
ring equip is resolved

When a player uses a consumable or equips a ring:
1. Execute the normal effect first
2. Call `registry.Identify(tag.TypeId)` — returns true if newly identified
3. If newly identified → toast: `"You realize this was a [IdentifiableItem.IdentifiedName]!"`
4. If already identified → no toast

Ring identification fires on equip. Effect activates first, then identification check, then
toast if newly identified.

**Acceptance:** Drink unknown potion → effect fires → type identified → toast shown.
Equip unknown ring → bonus applied → type identified → toast shown.
Second use of same identified type → no toast.

---

### TASK-007 — Scroll of Identify effect

**Files:** wherever scroll use effects are dispatched (likely `SpellResolver.cs` or
`TurnController.cs` scroll use handler)

When `scroll_of_identify` fires:
1. Identification-on-use trigger fires first (TASK-006) — scroll becomes identified
2. Gather all unidentified item *types* present in player inventory
   (deduplicate: if 3 "Fizzy Potions", that's one type)
3. If none → toast `"All your items are already identified."` — scroll still consumed
4. Else → randomly select `Math.Min(count, state.Rng.Next(1, 4))` types (1–3)
5. For each: `registry.Identify(typeId)` + toast `"[item display name] identified as [true name]!"`

Use `state.Rng` for determinism.

**Acceptance:** Inventory of 5 unidentified types → 1–3 identified. Empty unidentified
inventory handled cleanly. Statistical test: over 100 uses, average identifications ≈ 2.

---

### TASK-008 — Wand charging gate

**File:** `TurnController.cs` → `TryRechargeWand()`

Add identification check at the top of the method:

```csharp
private static bool TryRechargeWand(GameState state, Entity scroll, SpellEffect scrollSpell,
    List<TurnEvent> events)
{
    var registry = state.IdentificationRegistry;
    var scrollTag = scroll.Get<ItemTag>();
    if (scrollTag != null && !registry.IsIdentified(scrollTag.TypeId))
        return false;  // unidentified scroll goes to inventory normally

    // ... existing wand-finding logic ...

    if (wand == null) return false;

    var wandTag = wand.Get<ItemTag>();
    if (wandTag != null && !registry.IsIdentified(wandTag.TypeId))
        return false;  // unidentified wand — scroll goes to inventory

    // ... existing charge increment + WandRechargeEvent ...
}
```

The normal `PickUpEvent` toast still fires for the scroll (it goes to inventory via the
existing fallthrough path). Only the `WandRechargeEvent` is suppressed. The player sees
"Picked up Scroll labeled ZELGO MER" — not "recharged Wand of Fireball". Correct behavior.

**Acceptance:** Unidentified scroll + matching wand → scroll to inventory, wand unchanged,
pickup toast fires. Both identified → auto-recharge fires as before.

---

### TASK-009 — Stacking by TypeId

**File:** `src/Logic/ECS/Inventory.cs`

Current stacking in `Inventory.Add()` matches on `Entity.Name`. Replace with TypeId matching:

```csharp
var existing = _items.FirstOrDefault(i => {
    var tag = i.Get<ItemTag>();
    var newTag = item.Get<ItemTag>();
    if (tag != null && newTag != null)
        return tag.TypeId == newTag.TypeId && i.Get<Consumable>() != null;
    return i.Name == item.Name && i.Get<Consumable>() != null;  // fallback for untagged
});
```

When a type is identified, the display layer (not the inventory) handles showing the true name.
No inventory mutation needed — identification state lives in the registry, not on the item.

**Acceptance:** Two "Fizzy Potion" entities with same TypeId stack. Identifying the type
doesn't break the stack. Items without ItemTag still stack by name (backward compat).

---

### TASK-010 — Display: names and sprites

**Files:** `ItemSpriteManager.cs`, `HUD.cs` (or wherever item display strings are composed),
`SpriteMapping.cs`

**Item display name helper (presentation layer):**
```csharp
public static string GetDisplayName(Entity item,
    IdentificationRegistry registry, AppearancePool pool)
{
    var tag = item.Get<ItemTag>();
    var idComp = item.Get<IdentifiableItem>();
    if (tag == null || idComp == null) return item.Name;

    return registry.IsIdentified(tag.TypeId)
        ? idComp.IdentifiedName
        : pool.GetDisplayName(tag.TypeId);  // "Fizzy Potion", "Jade Ring", etc.
}
```

**Item sprite selection:**
- Potion unidentified → `pool.GetMysterySprite(typeId)` → one of "36"/"37"/"38"
- Potion identified → normal per-type sprite lookup via tileset (`healing_potion` → "3")
- Scroll → always `rune_scroll` sprite ("45") — name changes, sprite does not
- Wand unidentified → `unknown_wand` sprite ("50")
- Wand identified → normal per-type sprite lookup
- Ring unidentified → `pool.GetMysterySprite(typeId)` → one of "76"–"80"
- Ring identified → same ring sprite (ring appearance doesn't change on identification)

**Acceptance:** Unidentified potion shows black bottle + descriptor name. After identification,
true color sprite and true name. Ring shows correct material sprite pre- and post-identification.
All existing identified items (weapons, armor) unaffected.

---

### TASK-011 — Tests

**File:** `tests/Core/IdentificationTests.cs`

```
AppearancePool_SameSeed_SameAssignments
AppearancePool_DifferentSeed_DifferentAssignments
AppearancePool_PotionSprites_CycleThrough36_37_38
AppearancePool_DescriptorPoolExhausted_FallsBackGracefully
Registry_Identify_MarksAsIdentified
Registry_Identify_ReturnsTrue_OnlyFirstTime
Registry_MarkUnidentified_PreventsFutureRoll
Registry_HasDecision_TrueAfterEitherCall
PreIdentification_DecisionCachedPerType_NotRerolled
PreIdentification_MediumDifficulty_ConvergesTo50Pct  (500 samples)
ConsumableFactory_AttachesItemTag
ConsumableFactory_AttachesIdentifiableItem
UsePotion_UnknownType_IdentifiesType_ToastShown
UsePotion_AlreadyIdentified_NoToast
EquipRing_UnknownType_IdentifiesType
ScrollOfIdentify_1to3RandomTypes_Identified
ScrollOfIdentify_EmptyUnidentifiedInventory_StillConsumed
WandCharging_ScrollUnidentified_GoesToInventory
WandCharging_WandUnidentified_ScrollGoesToInventory
WandCharging_BothIdentified_Recharges
Stacking_SameTypeUnidentified_Stacks
Stacking_IdentifyType_StackIntact
FloorCarryForward_RegistryAndPoolPreserved
FloorCarryForward_NewGame_RegistryReset
```

---

## Implementation Order

1. **TASK-001** — data model + mystery sprite keys + `scroll_of_identify` in YAML
2. **TASK-002** — `IdentifiableItem` component + `ItemTag` on consumable/scroll/wand factories
3. **TASK-003** — `AppearancePool` + `IdentificationRegistry` (pure logic, fully isolated)
4. **TASK-004** — wire into `GameState`, floor carry-forward at factory level
5. **TASK-005** — pre-identification at creation (first live behavior)
6. **TASK-006** — identification on use/equip (core trigger)
7. **TASK-007** — scroll of identify effect
8. **TASK-008** — wand charging gate (one method, low risk)
9. **TASK-009** — stacking by TypeId
10. **TASK-010** — display names and sprites
11. **TASK-011** — test pass (written alongside each task; final pass fills gaps)

---

## Risk Notes

- **Descriptor pool limits:** 15 potion, 10 wand, 18 scroll, 16 ring max. If item definitions
  exceed these counts, log a warning and use "Unknown [Category] #N" fallback.
- **Ring sprites:** 16 types, 5 visual variants. Text is the primary identifier; sprite
  confirms it's a ring. Intentional tradeoff.
- **Scroll sprite:** One sprite for all scrolls. Name is the only differentiator. By design.
- **`ItemFactory` unchanged:** Weapons/armor always identified. Zero changes to that factory.
- **Save/load deferred:** Serialize/Deserialize hooks should be stubbed on both classes but
  not wired into a save system until that system exists. Comment with `// TODO: wire to save`.
- **Harness validation:** After implementation, run existing balance scenarios with medium
  difficulty to confirm `Death%` doesn't spike from the wand charging gate. Key risk: wands
  become harder to keep charged at depths where scroll identification is slow.
