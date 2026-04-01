using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using Godot;

namespace CatacombsOfYarl.Presentation.UI;

/// <summary>
/// Inventory strip panel. Shows the player's current inventory as a horizontal
/// row of item slots, each with an icon and stack count badge.
/// Equipped items get a gold highlight border.
///
/// Click handling bypasses Godot Button hit-testing entirely — the integer
/// stretch scale mode causes Button click rects to be offset from their
/// visual position. Instead, InventoryPanel handles _GuiInput directly and
/// hit-tests against tracked slot rects.
///
/// No .tscn file — built entirely in C# following the same pattern as HUD.cs.
/// </summary>
public sealed partial class InventoryPanel : Control
{
    private const int SlotWidth  = 52;
    private const int SlotHeight = 52;
    private const int IconSize   = 48;
    private const int SlotSeparation = 4;

    private static readonly Color FallbackConsumableColor = new(0.2f, 0.7f, 0.2f, 1f);
    private static readonly Color FallbackDefaultColor    = new(0.5f, 0.5f, 0.5f, 1f);

    /// <summary>
    /// Injected by Main after construction. Used for item sprite lookups.
    /// Must be set before Initialize is called.
    /// </summary>
    public SpriteMapping? SpriteMappingInstance { get; set; }

    private Label? _headerLabel;
    private HBoxContainer? _itemStrip;
    private Label? _emptyLabel;

    // Tracked slot positions for manual hit-testing (bypasses Godot Button coords bug).
    private readonly List<(int ItemId, Rect2 LocalRect)> _slotRects = new();
    private readonly List<(int ItemId, Rect2 LocalRect)> _dropRects = new();

    /// <summary>
    /// Exposes slot rects for the RectDebugDraw overlay. Panel-local coordinates.
    /// </summary>
    public IReadOnlyList<(int ItemId, Rect2 LocalRect)> SlotRects => _slotRects;

    /// <summary>
    /// Fires when the player taps an item slot. Argument is the item's entity ID.
    /// </summary>
    public event Action<int>? ItemTapped;

    /// <summary>Fires when the player taps the drop button on an item slot.</summary>
    public event Action<int>? ItemDropRequested;

    public override void _Ready()
    {
        BuildLayout();
        // Accept mouse input at the panel level for manual hit-testing.
        MouseFilter = MouseFilterEnum.Stop;
    }

    /// <summary>
    /// Handle clicks directly — manual hit-test against slot rects.
    /// Godot's Button hit-testing is broken under integer stretch scale mode
    /// (click rect offset from visual rect). This bypasses it entirely.
    /// </summary>
    public override void _GuiInput(InputEvent @event)
    {
        if (@event is InputEventMouseButton mb && mb.Pressed && mb.ButtonIndex == MouseButton.Left)
        {
            var localPos = mb.Position;
            foreach (var (itemId, rect) in _dropRects)
            {
                if (rect.HasPoint(localPos))
                {
                    AcceptEvent();
                    ItemDropRequested?.Invoke(itemId);
                    return;
                }
            }
            foreach (var (itemId, rect) in _slotRects)
            {
                if (rect.HasPoint(localPos))
                {
                    Diag.Log($"InventoryPanel hit-test: itemId={itemId} at {localPos}");
                    AcceptEvent();
                    ItemTapped?.Invoke(itemId);
                    return;
                }
            }
            // Click was inside the panel but missed all slots — consume it anyway
            // so it doesn't fall through to the game view as a movement tap.
            AcceptEvent();
        }
    }

    public void Initialize(GameState state)
    {
        Refresh(state);
    }

    public void Refresh(GameState state)
    {
        var inventory = state.PlayerInventory;

        // Quick-bar shows consumables only — equippables live in the equipment panel.
        var consumables = inventory?.Items
            .Where(item => item.Get<Consumable>() != null)
            .ToList() ?? new List<Entity>();

        if (_headerLabel != null)
            _headerLabel.Text = $"QUICK-BAR  {consumables.Count}";

        if (_itemStrip == null) return;

        foreach (var child in _itemStrip.GetChildren())
            child.SafeFree();

        _slotRects.Clear();

        if (consumables.Count == 0)
        {
            if (_emptyLabel != null)  _emptyLabel.Visible = true;
            if (_itemStrip != null)   _itemStrip.Visible  = false;
            return;
        }

        if (_emptyLabel != null) _emptyLabel.Visible = false;
        if (_itemStrip != null)  _itemStrip.Visible  = true;

        foreach (var item in consumables)
        {
            var slot = BuildSlot(item, isEquipped: false);
            _itemStrip.AddChild(slot);
        }

        // Compute slot rects after layout resolves.
        CallDeferred(MethodName._ComputeSlotRects);
    }

    private void _ComputeSlotRects()
    {
        _slotRects.Clear();
        _dropRects.Clear();
        if (_itemStrip == null) return;

        var panelOrigin = GetGlobalRect().Position;

        foreach (var child in _itemStrip.GetChildren())
        {
            if (child is Control c && c.HasMeta("item_id"))
            {
                int itemId = (int)c.GetMeta("item_id");
                // Convert slot's global rect to panel-local coords for _GuiInput hit-testing.
                var globalRect = c.GetGlobalRect();
                var localRect = new Rect2(globalRect.Position - panelOrigin, globalRect.Size);
                _slotRects.Add((itemId, localRect));
                Diag.Log($"  slot itemId={itemId} localRect={localRect}");

                // Drop button: top-right 20×20 of the slot
                var dropRect = new Rect2(localRect.Position + new Vector2(localRect.Size.X - 20, 0), new Vector2(20, 20));
                _dropRects.Add((itemId, dropRect));
            }
        }
    }

    // -------------------------------------------------------------------------
    // Layout
    // -------------------------------------------------------------------------

    private void BuildLayout()
    {
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);

        var bg = new ColorRect { Color = new Color(0f, 0f, 0f, 0.65f) };
        bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        bg.MouseFilter = MouseFilterEnum.Ignore;
        AddChild(bg);

        var margin = new MarginContainer();
        margin.AddThemeConstantOverride("margin_left",   12);
        margin.AddThemeConstantOverride("margin_right",  12);
        margin.AddThemeConstantOverride("margin_top",    6);
        margin.AddThemeConstantOverride("margin_bottom", 6);
        margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        margin.MouseFilter = MouseFilterEnum.Ignore;
        AddChild(margin);

        var vbox = new VBoxContainer();
        vbox.AddThemeConstantOverride("separation", 4);
        vbox.MouseFilter = MouseFilterEnum.Ignore;
        margin.AddChild(vbox);

        var headerRow = new HBoxContainer();
        headerRow.MouseFilter = MouseFilterEnum.Ignore;
        vbox.AddChild(headerRow);

        _headerLabel = new Label
        {
            Text = "INVENTORY  0/25",
            SizeFlagsHorizontal = SizeFlags.ExpandFill,
            HorizontalAlignment = HorizontalAlignment.Right,
            MouseFilter = MouseFilterEnum.Ignore,
        };
        _headerLabel.AddThemeFontSizeOverride("font_size", 14);
        headerRow.AddChild(_headerLabel);

        _emptyLabel = new Label
        {
            Text    = "(empty)",
            Visible = true,
            HorizontalAlignment = HorizontalAlignment.Left,
            MouseFilter = MouseFilterEnum.Ignore,
        };
        _emptyLabel.AddThemeFontSizeOverride("font_size", 14);
        _emptyLabel.SelfModulate = new Color(0.6f, 0.6f, 0.6f, 1f);
        vbox.AddChild(_emptyLabel);

        _itemStrip = new HBoxContainer
        {
            Visible             = false,
            SizeFlagsHorizontal = SizeFlags.ExpandFill,
            SizeFlagsVertical   = SizeFlags.ExpandFill,
            MouseFilter         = MouseFilterEnum.Ignore,
        };
        _itemStrip.AddThemeConstantOverride("separation", SlotSeparation);
        vbox.AddChild(_itemStrip);
    }

    // -------------------------------------------------------------------------
    // Per-slot construction (visual only — no click handling on the slot itself)
    // -------------------------------------------------------------------------

    private Control BuildSlot(Entity item, bool isEquipped)
    {
        var slot = new Control
        {
            CustomMinimumSize   = new Vector2(SlotWidth, SlotHeight),
            SizeFlagsHorizontal = SizeFlags.ShrinkBegin,
            MouseFilter         = MouseFilterEnum.Ignore,
        };
        // Store item ID as metadata so _ComputeSlotRects can read it back.
        slot.SetMeta("item_id", item.Id);

        var bg = new ColorRect { Color = new Color(0.15f, 0.15f, 0.2f, 0.6f), MouseFilter = MouseFilterEnum.Ignore };
        bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        slot.AddChild(bg);

        var iconContainer = BuildIconWithBadge(item, isEquipped);
        slot.AddChild(iconContainer);

        var dropBtn = new Label
        {
            Text = "×",
            HorizontalAlignment = HorizontalAlignment.Right,
            VerticalAlignment = VerticalAlignment.Top,
            AnchorLeft   = 0f, AnchorTop    = 0f,
            AnchorRight  = 1f, AnchorBottom = 0f,
            OffsetRight  = -1f, OffsetTop   = 1f, OffsetBottom = 20f,
            MouseFilter  = MouseFilterEnum.Ignore,
        };
        dropBtn.AddThemeFontSizeOverride("font_size", 14);
        dropBtn.SelfModulate = new Color(0.9f, 0.4f, 0.4f, 0.8f);
        slot.AddChild(dropBtn);

        return slot;
    }

    private Control BuildIconWithBadge(Entity item, bool isEquipped)
    {
        var container = new Control
        {
            CustomMinimumSize = new Vector2(IconSize, IconSize),
            MouseFilter = MouseFilterEnum.Ignore,
        };
        container.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);

        var icon = BuildIcon(item, isEquipped);
        icon.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        icon.MouseFilter = MouseFilterEnum.Ignore;
        container.AddChild(icon);

        var consumable = item.Get<Consumable>();
        if (consumable != null)
        {
            var badge = new Label
            {
                Text                = $"{consumable.StackSize}",
                HorizontalAlignment = HorizontalAlignment.Right,
                VerticalAlignment   = VerticalAlignment.Bottom,
                AnchorLeft   = 0f, AnchorTop    = 0f,
                AnchorRight  = 1f, AnchorBottom = 1f,
                OffsetRight  = -2f, OffsetBottom = -1f,
                MouseFilter  = MouseFilterEnum.Ignore,
            };
            badge.AddThemeFontSizeOverride("font_size", 16);
            badge.SelfModulate = Colors.White;
            container.AddChild(badge);
        }

        return container;
    }

    private Control BuildIcon(Entity item, bool isEquipped)
    {
        // Primary: ItemTag.TypeId (set by ItemFactory for all YAML-created items)
        var tag = item.Get<ItemTag>();
        var spriteKey = tag?.TypeId ?? item.Name.ToLowerInvariant().Replace(' ', '_');
        var spritePath = SpriteMappingInstance?.GetItemSpritePath(spriteKey);

        if (spritePath != null)
        {
            var texture = GD.Load<Texture2D>(spritePath);
            if (texture != null)
            {
                var texRect = new TextureRect
                {
                    Texture             = texture,
                    StretchMode         = TextureRect.StretchModeEnum.KeepAspectCentered,
                    CustomMinimumSize   = new Vector2(IconSize, IconSize),
                    SizeFlagsHorizontal = SizeFlags.ShrinkCenter,
                };
                if (isEquipped)
                    texRect.SelfModulate = new Color(1.0f, 0.9f, 0.4f, 1f);
                return texRect;
            }
        }

        return new ColorRect
        {
            Color             = FallbackColor(item),
            CustomMinimumSize = new Vector2(IconSize, IconSize),
            SizeFlagsHorizontal = SizeFlags.ShrinkCenter,
        };
    }

    private static Color FallbackColor(Entity item)
    {
        if (item.Get<Consumable>() != null) return FallbackConsumableColor;
        return FallbackDefaultColor;
    }
}
