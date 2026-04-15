using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using Godot;

namespace CatacombsOfYarl.Presentation.UI;

/// <summary>
/// Scrollable consumable + wand quick-slot bar. Replaces the old InventoryPanel.
///
/// Layout:
///   [WeaponSlot | separator | ScrollContainer → HBoxContainer of item slots]
///
/// Weapon slot (far left, ~48×48px): shows current MainHand weapon icon + truncated name.
///   Tap  → WeaponTapped (toast stub)
///   Long-press → WeaponLongPressed
///
/// Item slots (right section): 48×48px each, auto-populated from all Consumable or
///   SpellEffect inventory items. No empty placeholders.
///   Tap  → ItemTapped(entityId)
///   Long-press → ItemLongPressed(entityId)
///
/// Slot background tint by type:
///   Health/healing consumables  : dark red    (0.6, 0.15, 0.15, 0.7)
///   Arcane/mana consumables      : dark blue   (0.15, 0.15, 0.6,  0.7)
///   Scrolls (SpellEffect w/o wand): dark amber (0.5, 0.4, 0.1,   0.7)
///   Wands (WandComponent)        : dark purple (0.4, 0.1, 0.5,   0.7)
///   Default                      : dark neutral (0.15, 0.15, 0.2, 0.6)
///
/// Hit-testing bypasses Godot Button click-rect bug under integer stretch scale.
/// All input is handled in _GuiInput with scroll-vs-tap disambiguation:
///   Horizontal drag > 8px → scroll; lift with <8px movement → tap/long-press.
///
/// No .tscn file — built entirely in C#.
/// </summary>
public sealed partial class QuickSlotBar : Control
{
    // ── Slot geometry ─────────────────────────────────────────────────────────
    private const int SlotSize        = 48;
    private const int WeaponSlotWidth = 52;   // slightly wider to fit name label
    private const int SlotGap         = 4;
    private const int SeparatorWidth  = 1;
    private const int IconSize        = 40;   // icon inside the 48px slot
    private const int CornerRadius    = 6;

    // ── Long-press detection constants ────────────────────────────────────────
    private const float LongPressThreshold = 0.4f; // seconds
    private const float DragCancelDistance = 24f;  // cancel long-press if moved > this

    // ── Scroll-vs-tap disambiguation ─────────────────────────────────────────
    private const float ScrollTapThreshold = 8f;  // px — below = tap, above = scroll

    // ── Slot tint colors ─────────────────────────────────────────────────────
    private static readonly Color TintHealth  = new(0.6f,  0.15f, 0.15f, 0.7f);
    private static readonly Color TintArcane  = new(0.15f, 0.15f, 0.6f,  0.7f);
    private static readonly Color TintScroll  = new(0.5f,  0.4f,  0.1f,  0.7f);
    private static readonly Color TintWand    = new(0.4f,  0.1f,  0.5f,  0.7f);
    private static readonly Color TintDefault = new(0.15f, 0.15f, 0.2f,  0.6f);

    // ── Public surface ────────────────────────────────────────────────────────

    /// <summary>Injected by Main after construction. Used for item sprite lookups.</summary>
    public SpriteMapping? SpriteMappingInstance { get; set; }

    /// <summary>Fires when the player taps an item slot. Argument is the item's entity ID.</summary>
    public event Action<int>? ItemTapped;

    /// <summary>Fires when the player long-presses (0.4s) an item slot.</summary>
    public event Action<int>? ItemLongPressed;

    /// <summary>Fires when the player taps the weapon indicator (stub — ranged toggle).</summary>
    public event Action? WeaponTapped;

    /// <summary>Fires when the player long-presses the weapon indicator.</summary>
    public event Action? WeaponLongPressed;

    // ── Slot debug surface ────────────────────────────────────────────────────

    /// <summary>
    /// Exposes item slot rects for RectDebugDraw. Panel-local coordinates.
    /// </summary>
    public IReadOnlyList<(int ItemId, Rect2 LocalRect)> SlotRects => _slotRects;

    // ── Internal nodes ────────────────────────────────────────────────────────
    private Control?       _weaponSlot;
    private TextureRect?   _weaponIcon;
    private Label?         _weaponNameLabel;
    private HBoxContainer? _itemContainer;
    private ScrollContainer? _scrollContainer;

    // ── State ─────────────────────────────────────────────────────────────────
    private readonly List<(int ItemId, Rect2 LocalRect)> _slotRects = new();
    private Rect2 _weaponSlotRect = default(Rect2);

    // Cached per-refresh for identification-aware sprite lookup
    private IdentificationRegistry? _registry;
    private AppearancePool?          _pool;

    // ── Long-press state ──────────────────────────────────────────────────────
    // ItemId >= 0 = item slot pressed; ItemId = -2 = weapon slot pressed
    private int     _pressedId       = -1;
    private Vector2 _pressPosition   = Vector2.Zero;
    private float   _pressHeldTime   = 0f;
    private bool    _longPressFired  = false;

    // ── Scroll state (manual scroll on the ScrollContainer) ──────────────────
    private bool    _isScrolling     = false;
    private float   _scrollStartX    = 0f;
    private int     _scrollOffsetAtDragStart = 0;

    // ── Sentinel for weapon slot ──────────────────────────────────────────────
    private const int WeaponSlotSentinel = -2;

    public override void _Ready()
    {
        BuildLayout();
        // QuickSlotBar intercepts all input; children have MouseFilter=Ignore.
        MouseFilter = MouseFilterEnum.Stop;
    }

    public override void _Process(double delta)
    {
        if (_pressedId == -1 || _longPressFired) return;

        _pressHeldTime += (float)delta;
        if (_pressHeldTime >= LongPressThreshold)
        {
            _longPressFired = true;
            int pressedId = _pressedId;
            _pressedId = -1; // prevent re-firing on the same press

            if (pressedId == WeaponSlotSentinel)
                WeaponLongPressed?.Invoke();
            else
                ItemLongPressed?.Invoke(pressedId);
        }
    }

    /// <summary>
    /// Handle all input in the QuickSlotBar itself.
    ///
    /// Scroll-vs-tap disambiguation:
    ///   On DOWN: record position. Start tracking.
    ///   On MOVE: if horizontal delta > ScrollTapThreshold, enter scroll mode — shift the
    ///     ScrollContainer's scroll offset. Cancel any pending long-press.
    ///   On UP: if scroll mode, finalize. If not scroll mode and within threshold, fire
    ///     tap (or long-press if timer already fired).
    ///
    /// This approach is necessary because ScrollContainer intercepts swipe gestures,
    /// which would prevent GuiInput from receiving them on child nodes.
    /// By setting MouseFilter=Stop on QuickSlotBar and Ignore on all children,
    /// all events land here for manual dispatch.
    /// </summary>
    public override void _GuiInput(InputEvent @event)
    {
        // ── Screen touch (mobile) ─────────────────────────────────────────────
        if (@event is InputEventScreenTouch touch)
        {
            if (touch.Pressed)
                OnPointerDown(touch.Position);
            else
                OnPointerUp(touch.Position);
            AcceptEvent();
            return;
        }

        if (@event is InputEventScreenDrag drag)
        {
            OnPointerMove(drag.Position);
            AcceptEvent();
            return;
        }

        // ── Mouse (desktop) ───────────────────────────────────────────────────
        if (@event is InputEventMouseButton mb && mb.ButtonIndex == MouseButton.Left)
        {
            if (mb.Pressed)
                OnPointerDown(mb.Position);
            else
                OnPointerUp(mb.Position);
            AcceptEvent();
            return;
        }

        if (@event is InputEventMouseMotion motion)
        {
            if (_pressedId != -1 || _isScrolling)
            {
                OnPointerMove(motion.Position);
                AcceptEvent();
            }
        }
    }

    private void OnPointerDown(Vector2 pos)
    {
        _pressPosition          = pos;
        _pressHeldTime          = 0f;
        _longPressFired         = false;
        _isScrolling            = false;
        _scrollStartX           = pos.X;
        _scrollOffsetAtDragStart = _scrollContainer?.ScrollHorizontal ?? 0;

        // Weapon slot hit-test
        if (_weaponSlotRect != default(Rect2) && _weaponSlotRect.HasPoint(pos))
        {
            _pressedId = WeaponSlotSentinel;
            return;
        }

        // Item slot hit-test
        foreach (var (itemId, rect) in _slotRects)
        {
            if (rect.HasPoint(pos))
            {
                _pressedId = itemId;
                return;
            }
        }

        // Pressed in the bar but not on a slot — absorb
        _pressedId = -1;
    }

    private void OnPointerMove(Vector2 pos)
    {
        if (_pressedId == -1 && !_isScrolling) return;

        float dxFromStart = pos.X - _scrollStartX;

        if (!_isScrolling && MathF.Abs(dxFromStart) > ScrollTapThreshold)
        {
            // Transition to scroll mode — cancel long-press
            _isScrolling = true;
            CancelLongPress();
        }

        if (_isScrolling && _scrollContainer != null)
        {
            // Drag left → scroll right (positive offset) and vice versa
            _scrollContainer.ScrollHorizontal = _scrollOffsetAtDragStart + (int)(-dxFromStart);
        }
    }

    private void OnPointerUp(Vector2 pos)
    {
        if (_isScrolling)
        {
            // Scroll gesture ended — no tap
            _isScrolling = false;
            CancelLongPress();
            return;
        }

        // If long-press already fired, just clean up
        if (_longPressFired)
        {
            CancelLongPress();
            return;
        }

        // Tap — fire the right event
        if (_pressedId != -1)
        {
            int pressedId = _pressedId;
            CancelLongPress();

            if (pressedId == WeaponSlotSentinel)
                WeaponTapped?.Invoke();
            else
                ItemTapped?.Invoke(pressedId);
        }
    }

    private void CancelLongPress()
    {
        _pressedId    = -1;
        _pressHeldTime = 0f;
        _longPressFired = false;
    }

    // ── Public API ────────────────────────────────────────────────────────────

    public void Initialize(GameState state) => Refresh(state);

    public void Refresh(GameState state)
    {
        _registry = state.IdentificationRegistry;
        _pool     = state.AppearancePool;

        RefreshWeaponSlot(state);
        RefreshItemSlots(state);

        // Slot rects are only valid after Godot resolves layout — defer.
        CallDeferred(MethodName._ComputeSlotRects);
    }

    // ── Weapon slot ───────────────────────────────────────────────────────────

    private void RefreshWeaponSlot(GameState state)
    {
        if (_weaponIcon == null || _weaponNameLabel == null) return;

        var equip  = state.Player.Get<Equipment>();
        var weapon = equip?.MainHand;

        if (weapon == null)
        {
            _weaponIcon.Texture      = null;
            _weaponNameLabel.Text    = "Fists";
            return;
        }

        var spriteKey  = ItemDisplay.GetSpriteKey(weapon, _registry, _pool);
        var spritePath = SpriteMappingInstance?.GetItemSpritePath(spriteKey);

        if (spritePath != null)
        {
            var texture = GD.Load<Texture2D>(spritePath);
            _weaponIcon.Texture = texture; // null-safe: shows nothing if load fails
        }
        else
        {
            _weaponIcon.Texture = null;
        }

        // Truncate weapon name to ~6 chars to fit the narrow slot
        var name = weapon.Name;
        _weaponNameLabel.Text = name.Length > 6 ? name[..6] : name;
    }

    // ── Item slots ────────────────────────────────────────────────────────────

    private void RefreshItemSlots(GameState state)
    {
        if (_itemContainer == null) return;

        // Clear previous slots
        foreach (var child in _itemContainer.GetChildren())
            child.SafeFree();

        _slotRects.Clear();

        // Filter: consumables and spell items (scrolls, wands) only
        var items = state.PlayerInventory?.Items
            .Where(item => item.Get<Consumable>() != null || item.Get<SpellEffect>() != null)
            .ToList() ?? new List<Entity>();

        foreach (var item in items)
        {
            var slot = BuildItemSlot(item);
            _itemContainer.AddChild(slot);
        }
    }

    private Control BuildItemSlot(Entity item)
    {
        var slot = new Control
        {
            CustomMinimumSize   = new Vector2(SlotSize, SlotSize),
            SizeFlagsHorizontal = SizeFlags.ShrinkBegin,
            SizeFlagsVertical   = SizeFlags.ShrinkCenter,
            // All children Ignore; QuickSlotBar handles everything at the top level.
            MouseFilter         = MouseFilterEnum.Ignore,
        };
        slot.SetMeta("item_id", item.Id);

        // Rounded-corner background via StyleBoxFlat
        var bg = new Panel { MouseFilter = MouseFilterEnum.Ignore };
        bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        var bgStyle = new StyleBoxFlat();
        bgStyle.BgColor = SlotTintColor(item);
        bgStyle.CornerRadiusTopLeft     = CornerRadius;
        bgStyle.CornerRadiusTopRight    = CornerRadius;
        bgStyle.CornerRadiusBottomLeft  = CornerRadius;
        bgStyle.CornerRadiusBottomRight = CornerRadius;
        bg.AddThemeStyleboxOverride("panel", bgStyle);
        slot.AddChild(bg);

        // Icon centered in slot
        var icon = BuildItemIcon(item);
        icon.MouseFilter = MouseFilterEnum.Ignore;
        slot.AddChild(icon);

        // Quantity badge (bottom-right)
        var badgeText = GetBadgeText(item);
        if (badgeText != null)
        {
            var badge = new Label
            {
                Text                = badgeText,
                HorizontalAlignment = HorizontalAlignment.Right,
                VerticalAlignment   = VerticalAlignment.Bottom,
                AnchorLeft   = 0f, AnchorTop    = 0f,
                AnchorRight  = 1f, AnchorBottom = 1f,
                OffsetRight  = -2f, OffsetBottom = -1f,
                MouseFilter  = MouseFilterEnum.Ignore,
            };
            badge.AddThemeFontSizeOverride("font_size", 14);
            badge.SelfModulate = Colors.White;
            slot.AddChild(badge);
        }

        return slot;
    }

    private Control BuildItemIcon(Entity item)
    {
        var spriteKey  = ItemDisplay.GetSpriteKey(item, _registry, _pool);
        var spritePath = SpriteMappingInstance?.GetItemSpritePath(spriteKey);

        if (spritePath != null)
        {
            var texture = GD.Load<Texture2D>(spritePath);
            if (texture != null)
            {
                return new TextureRect
                {
                    Texture             = texture,
                    StretchMode         = TextureRect.StretchModeEnum.KeepAspectCentered,
                    CustomMinimumSize   = new Vector2(IconSize, IconSize),
                    SizeFlagsHorizontal = SizeFlags.ShrinkCenter,
                    SizeFlagsVertical   = SizeFlags.ShrinkCenter,
                    AnchorLeft          = 0.5f - (float)IconSize / (2 * SlotSize),
                    AnchorTop           = 0.5f - (float)IconSize / (2 * SlotSize),
                    AnchorRight         = 0.5f + (float)IconSize / (2 * SlotSize),
                    AnchorBottom        = 0.5f + (float)IconSize / (2 * SlotSize),
                };
            }
        }

        // Fallback: colored rect
        return new ColorRect
        {
            Color             = SlotTintColor(item).Lightened(0.2f),
            CustomMinimumSize = new Vector2(IconSize, IconSize),
            AnchorLeft        = 0.1f, AnchorTop    = 0.1f,
            AnchorRight       = 0.9f, AnchorBottom = 0.9f,
            MouseFilter       = MouseFilterEnum.Ignore,
        };
    }

    private static string? GetBadgeText(Entity item)
    {
        var consumable = item.Get<Consumable>();
        if (consumable != null)
            return $"{consumable.StackSize}";

        var wand = item.Get<WandComponent>();
        if (wand != null)
            return wand.Infinite ? "∞" : $"{wand.Charges}";

        // Scrolls (SpellEffect without Consumable or WandComponent): no badge — single use
        return null;
    }

    private static Color SlotTintColor(Entity item)
    {
        // Wands checked first — they also have SpellEffect
        if (item.Get<WandComponent>() != null) return TintWand;

        var consumable = item.Get<Consumable>();
        if (consumable != null)
        {
            if (consumable.IsPotion && consumable.IsHealing) return TintHealth;
            if (consumable.IsPotion) return TintArcane; // mana/arcane potions are non-healing potions
            return TintDefault;
        }

        var spell = item.Get<SpellEffect>();
        if (spell != null) return TintScroll; // SpellEffect without WandComponent = scroll

        return TintDefault;
    }

    // ── Slot rect computation (deferred — called after layout resolves) ────────

    private void _ComputeSlotRects()
    {
        _slotRects.Clear();

        var panelOrigin = GetGlobalRect().Position;

        // Weapon slot rect
        if (_weaponSlot != null)
        {
            var weaponGlobal = _weaponSlot.GetGlobalRect();
            _weaponSlotRect = new Rect2(weaponGlobal.Position - panelOrigin, weaponGlobal.Size);
        }

        // Item slot rects — must account for scroll offset since containers shift in screen space
        if (_itemContainer == null) return;

        foreach (var child in _itemContainer.GetChildren())
        {
            if (child is Control c && c.HasMeta("item_id"))
            {
                int itemId = (int)c.GetMeta("item_id");
                // GetGlobalRect returns the actual screen-space rect, already offset by scroll.
                // So we just subtract our own origin to get panel-local coords.
                var globalRect = c.GetGlobalRect();
                var localRect  = new Rect2(globalRect.Position - panelOrigin, globalRect.Size);
                _slotRects.Add((itemId, localRect));
            }
        }
    }

    // ── Layout construction ───────────────────────────────────────────────────

    private void BuildLayout()
    {
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);

        // Background
        var bg = new ColorRect { Color = new Color(0f, 0f, 0f, 0.65f) };
        bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        bg.MouseFilter = MouseFilterEnum.Ignore;
        AddChild(bg);

        // Outer margin container
        var margin = new MarginContainer();
        margin.AddThemeConstantOverride("margin_left",   8);
        margin.AddThemeConstantOverride("margin_right",  8);
        margin.AddThemeConstantOverride("margin_top",    8);
        margin.AddThemeConstantOverride("margin_bottom", 8);
        margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        margin.MouseFilter = MouseFilterEnum.Ignore;
        AddChild(margin);

        // Top-level horizontal container: weapon slot + separator + scroll area
        var hbox = new HBoxContainer();
        hbox.AddThemeConstantOverride("separation", 0);
        hbox.MouseFilter = MouseFilterEnum.Ignore;
        margin.AddChild(hbox);

        // ── Weapon slot ───────────────────────────────────────────────────────
        _weaponSlot = BuildWeaponSlot();
        hbox.AddChild(_weaponSlot);

        // 1px vertical separator line
        var separator = new ColorRect
        {
            Color             = new Color(0.5f, 0.5f, 0.6f, 0.8f),
            CustomMinimumSize = new Vector2(SeparatorWidth, 0),
            SizeFlagsVertical = SizeFlags.ExpandFill,
            MouseFilter       = MouseFilterEnum.Ignore,
        };
        hbox.AddChild(separator);

        // Small gap after separator
        var gap = new Control
        {
            CustomMinimumSize = new Vector2(4, 0),
            MouseFilter       = MouseFilterEnum.Ignore,
        };
        hbox.AddChild(gap);

        // ── Scroll area ───────────────────────────────────────────────────────
        // ScrollContainer with MouseFilter=Ignore so QuickSlotBar handles input.
        // We manually drive ScrollHorizontal in OnPointerMove.
        _scrollContainer = new ScrollContainer
        {
            SizeFlagsHorizontal   = SizeFlags.ExpandFill,
            SizeFlagsVertical     = SizeFlags.ExpandFill,
            // Disable the built-in scroll bars — we drive scrolling manually
            HorizontalScrollMode  = ScrollContainer.ScrollMode.ShowNever,
            VerticalScrollMode    = ScrollContainer.ScrollMode.Disabled,
            MouseFilter           = MouseFilterEnum.Ignore,
        };
        hbox.AddChild(_scrollContainer);

        _itemContainer = new HBoxContainer
        {
            SizeFlagsVertical = SizeFlags.ShrinkCenter,
            MouseFilter       = MouseFilterEnum.Ignore,
        };
        _itemContainer.AddThemeConstantOverride("separation", SlotGap);
        _scrollContainer.AddChild(_itemContainer);
    }

    private Control BuildWeaponSlot()
    {
        var weaponSlotStyle = new StyleBoxFlat();
        weaponSlotStyle.BgColor             = new Color(0.2f, 0.18f, 0.1f, 0.8f);
        weaponSlotStyle.CornerRadiusTopLeft     = CornerRadius;
        weaponSlotStyle.CornerRadiusTopRight    = CornerRadius;
        weaponSlotStyle.CornerRadiusBottomLeft  = CornerRadius;
        weaponSlotStyle.CornerRadiusBottomRight = CornerRadius;

        var weaponPanel = new Panel
        {
            CustomMinimumSize = new Vector2(WeaponSlotWidth, SlotSize),
            SizeFlagsVertical = SizeFlags.ShrinkCenter,
            MouseFilter       = MouseFilterEnum.Ignore,
        };
        weaponPanel.AddThemeStyleboxOverride("panel", weaponSlotStyle);

        // Icon area (centered in upper portion)
        _weaponIcon = new TextureRect
        {
            StretchMode         = TextureRect.StretchModeEnum.KeepAspectCentered,
            CustomMinimumSize   = new Vector2(IconSize, IconSize),
            SizeFlagsHorizontal = SizeFlags.ShrinkCenter,
            AnchorLeft          = 0f, AnchorTop    = 0f,
            AnchorRight         = 1f, AnchorBottom = 0.65f,
            MouseFilter         = MouseFilterEnum.Ignore,
        };
        weaponPanel.AddChild(_weaponIcon);

        // Name label (bottom of slot)
        _weaponNameLabel = new Label
        {
            Text                = "—",
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment   = VerticalAlignment.Bottom,
            AnchorLeft          = 0f, AnchorTop    = 0.6f,
            AnchorRight         = 1f, AnchorBottom = 1f,
            OffsetBottom        = -2f,
            MouseFilter         = MouseFilterEnum.Ignore,
            ClipText            = true,
        };
        _weaponNameLabel.AddThemeFontSizeOverride("font_size", 10);
        _weaponNameLabel.SelfModulate = new Color(0.9f, 0.85f, 0.7f, 1f);
        weaponPanel.AddChild(_weaponNameLabel);

        // Store reference so _ComputeSlotRects can get its rect
        _weaponSlot = weaponPanel;
        return weaponPanel;
    }
}
