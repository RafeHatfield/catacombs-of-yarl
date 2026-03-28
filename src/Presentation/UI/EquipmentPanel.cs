using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using Godot;

namespace CatacombsOfYarl.Presentation.UI;

/// <summary>
/// Equipment panel overlay. Shows all 8 equipment slots in a body-map layout
/// and a horizontal "In Pack" strip of equippable inventory items.
///
/// Layout (portrait, 720px wide):
///
///   [Head]
///   [LeftRing] [Neck] [RightRing]
///   [OffHand]  [Chest] [MainHand]
///   [Feet]
///   ─────────────────────────────
///   IN PACK
///   [item] [item] [item] …
///
/// Tapping an occupied equipment slot → UnequipRequested event.
/// Tapping an In Pack item → EquipRequested event.
/// Tap outside panel or the [✕] button → Close().
///
/// Manual hit-testing (same approach as InventoryPanel) bypasses Godot Button
/// click-rect offset bug under integer stretch scale mode.
/// </summary>
public sealed partial class EquipmentPanel : Control
{
    private const int SlotSize       = 90;  // px — each equipment slot is a square
    private const int PackSlotSize   = 76;  // px — smaller slots in the In Pack strip
    private const int SlotLabelH     = 20;  // px — slot label below each slot

    private static readonly Color SlotBgEmpty    = new(0.12f, 0.12f, 0.18f, 0.9f);
    private static readonly Color SlotBgOccupied = new(0.18f, 0.16f, 0.10f, 0.95f);
    private static readonly Color SlotHighlight  = new(0.85f, 0.70f, 0.15f, 0.50f);
    private static readonly Color PackSlotBg     = new(0.12f, 0.12f, 0.18f, 0.9f);
    private static readonly Color FallbackWeapon = new(0.9f, 0.75f, 0.1f, 1f);
    private static readonly Color FallbackArmor  = new(0.2f, 0.4f, 0.9f, 1f);
    private static readonly Color FallbackRing   = new(0.7f, 0.3f, 0.8f, 1f);
    private static readonly Color FallbackDefault= new(0.5f, 0.5f, 0.5f, 1f);

    /// <summary>Fires when the player taps an occupied equipment slot to unequip it.</summary>
    public event Action<EquipmentSlot>? UnequipRequested;

    /// <summary>Fires when the player taps an In Pack item to equip it.</summary>
    public event Action<int>? EquipRequested;

    // Hit-test tracking — (slot/itemId, localRect relative to this panel).
    private readonly List<(EquipmentSlot Slot, Rect2 Rect)> _equippedRects = new();
    private readonly List<(int ItemId, Rect2 Rect)>         _packRects     = new();

    // Slot row containers — rebuilt each Refresh.
    private Control? _slotGrid;
    private Control? _packStrip;

    public override void _Ready()
    {
        BuildLayout();
        MouseFilter = MouseFilterEnum.Stop;
        Visible = false;
    }

    public void Show(GameState state)
    {
        Visible = true;
        Refresh(state);
    }

    public void Refresh(GameState state)
    {
        if (!IsInsideTree() || !Visible) return;
        RebuildSlotGrid(state);
        RebuildPackStrip(state);
        CallDeferred(MethodName._ComputeHitRects);
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Input — manual hit-test against tracked rects
    // ─────────────────────────────────────────────────────────────────────────

    public override void _GuiInput(InputEvent @event)
    {
        if (@event is InputEventMouseButton mb && mb.Pressed && mb.ButtonIndex == MouseButton.Left)
        {
            var pos = mb.Position;

            // Check equipment slots first.
            foreach (var (slot, rect) in _equippedRects)
            {
                if (rect.HasPoint(pos))
                {
                    AcceptEvent();
                    UnequipRequested?.Invoke(slot);
                    return;
                }
            }

            // Check In Pack items.
            foreach (var (itemId, rect) in _packRects)
            {
                if (rect.HasPoint(pos))
                {
                    AcceptEvent();
                    EquipRequested?.Invoke(itemId);
                    return;
                }
            }

            // Click landed outside all interactive slots.
            // If it's also outside the visible panel container, close (tap-outside-to-dismiss).
            bool insidePanel = _panelContainer != null &&
                new Rect2(_panelContainer.Position, _panelContainer.Size).HasPoint(pos);
            if (!insidePanel)
                Hide();

            AcceptEvent();
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Layout construction (once in _Ready)
    // ─────────────────────────────────────────────────────────────────────────

    private Control? _panelContainer;

    private void BuildLayout()
    {
        // Full-viewport backdrop — semi-transparent black, eats all clicks.
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);

        var backdrop = new ColorRect
        {
            Color       = new Color(0f, 0f, 0f, 0.60f),
            MouseFilter = MouseFilterEnum.Ignore,
        };
        backdrop.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        AddChild(backdrop);

        // Centered panel container — anchored to center, sized to fit content.
        // MouseFilter=Ignore so all clicks bubble up to EquipmentPanel._GuiInput,
        // where the unified hit-test runs against tracked slot rects.
        _panelContainer = new Control
        {
            AnchorLeft   = 0.5f, AnchorRight  = 0.5f,
            AnchorTop    = 0.5f, AnchorBottom  = 0.5f,
            OffsetLeft   = -340f, OffsetRight  = 340f,
            OffsetTop    = -320f, OffsetBottom = 320f,
            MouseFilter  = MouseFilterEnum.Ignore,
        };
        AddChild(_panelContainer);

        // Panel background.
        var panelBg = new ColorRect { Color = new Color(0.07f, 0.07f, 0.12f, 0.97f) };
        panelBg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        panelBg.MouseFilter = MouseFilterEnum.Ignore;
        _panelContainer.AddChild(panelBg);

        // Inner VBox for all panel content.
        var margin = new MarginContainer();
        margin.AddThemeConstantOverride("margin_left",   16);
        margin.AddThemeConstantOverride("margin_right",  16);
        margin.AddThemeConstantOverride("margin_top",    12);
        margin.AddThemeConstantOverride("margin_bottom", 16);
        margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        margin.MouseFilter = MouseFilterEnum.Ignore;
        _panelContainer.AddChild(margin);

        var vbox = new VBoxContainer();
        vbox.AddThemeConstantOverride("separation", 8);
        vbox.MouseFilter = MouseFilterEnum.Ignore;
        margin.AddChild(vbox);

        // Header row: title + close button.
        var headerRow = new HBoxContainer();
        headerRow.MouseFilter = MouseFilterEnum.Ignore;
        vbox.AddChild(headerRow);

        var titleLabel = new Label
        {
            Text                = "EQUIPMENT",
            SizeFlagsHorizontal = SizeFlags.ExpandFill,
            HorizontalAlignment = HorizontalAlignment.Left,
            MouseFilter         = MouseFilterEnum.Ignore,
        };
        titleLabel.AddThemeFontSizeOverride("font_size", 26);
        titleLabel.AddThemeColorOverride("font_color", Colors.White);
        headerRow.AddChild(titleLabel);

        var closeBtn = new TouchButton
        {
            Text              = "✕",
            FontSize          = 24,
            BackgroundColor   = new Color(0.4f, 0.1f, 0.1f, 0.9f),
            CustomMinimumSize = new Vector2(44, 44),
        };
        closeBtn.Pressed += Hide;
        headerRow.AddChild(closeBtn);

        // Slot grid placeholder — rebuilt each Refresh.
        _slotGrid = new Control
        {
            CustomMinimumSize   = new Vector2(0, SlotSize * 4 + SlotLabelH * 4 + 8 * 3),
            SizeFlagsHorizontal = SizeFlags.ExpandFill,
            MouseFilter         = MouseFilterEnum.Ignore,
        };
        vbox.AddChild(_slotGrid);

        // Divider.
        var divider = new ColorRect
        {
            Color             = new Color(0.4f, 0.4f, 0.5f, 0.6f),
            CustomMinimumSize = new Vector2(0, 1),
            MouseFilter       = MouseFilterEnum.Ignore,
        };
        vbox.AddChild(divider);

        // In Pack label.
        var packLabel = new Label
        {
            Text        = "IN PACK",
            MouseFilter = MouseFilterEnum.Ignore,
        };
        packLabel.AddThemeFontSizeOverride("font_size", 18);
        packLabel.AddThemeColorOverride("font_color", new Color(0.75f, 0.75f, 0.75f, 1f));
        vbox.AddChild(packLabel);

        // Pack strip placeholder — rebuilt each Refresh.
        _packStrip = new Control
        {
            CustomMinimumSize   = new Vector2(0, PackSlotSize),
            SizeFlagsHorizontal = SizeFlags.ExpandFill,
            MouseFilter         = MouseFilterEnum.Ignore,
        };
        vbox.AddChild(_packStrip);
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Slot grid — rebuilt each Refresh()
    // ─────────────────────────────────────────────────────────────────────────

    private void RebuildSlotGrid(GameState state)
    {
        if (_slotGrid == null) return;

        foreach (var child in _slotGrid.GetChildren())
            child.SafeFree();

        var equipment = state.Player.Get<Equipment>();

        // Body-map rows, each as an HBoxContainer.
        // Rows are stacked in a VBox positioned to fill _slotGrid.
        var vbox = new VBoxContainer();
        vbox.AddThemeConstantOverride("separation", 8);
        vbox.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        vbox.MouseFilter = MouseFilterEnum.Ignore;
        _slotGrid.AddChild(vbox);

        // Row 1: Head (center)
        vbox.AddChild(MakeSingleSlotRow(EquipmentSlot.Head, "Head", equipment));

        // Row 2: RightRing | Neck | LeftRing  (person faces us — their right is our left)
        vbox.AddChild(MakeTripleSlotRow(
            EquipmentSlot.RightRing, "R. Ring",
            EquipmentSlot.Neck,      "Neck",
            EquipmentSlot.LeftRing,  "L. Ring",
            equipment));

        // Row 3: MainHand | Chest | OffHand  (person faces us — their right hand is our left)
        vbox.AddChild(MakeTripleSlotRow(
            EquipmentSlot.MainHand, "Main Hand",
            EquipmentSlot.Chest,    "Chest",
            EquipmentSlot.OffHand,  "Off Hand",
            equipment));

        // Row 4: Feet (center)
        vbox.AddChild(MakeSingleSlotRow(EquipmentSlot.Feet, "Feet", equipment));
    }

    /// <summary>A row with one slot centered using expand-fill spacers.</summary>
    private Control MakeSingleSlotRow(EquipmentSlot slot, string label, Equipment? equipment)
    {
        var row = new HBoxContainer();
        row.SizeFlagsHorizontal = SizeFlags.ExpandFill;
        row.MouseFilter = MouseFilterEnum.Ignore;

        row.AddChild(new Control { SizeFlagsHorizontal = SizeFlags.ExpandFill, MouseFilter = Control.MouseFilterEnum.Ignore });
        row.AddChild(BuildEquipSlot(slot, label, equipment));
        row.AddChild(new Control { SizeFlagsHorizontal = SizeFlags.ExpandFill, MouseFilter = Control.MouseFilterEnum.Ignore });

        return row;
    }

    /// <summary>
    /// A row with three slots distributed evenly using expand-fill spacers between them.
    /// Four equal spacers ensure the outer slots are inset symmetrically and the
    /// center slot lands exactly at the horizontal midpoint of the panel.
    /// </summary>
    private Control MakeTripleSlotRow(
        EquipmentSlot slotL, string labelL,
        EquipmentSlot slotC, string labelC,
        EquipmentSlot slotR, string labelR,
        Equipment? equipment)
    {
        var row = new HBoxContainer();
        row.SizeFlagsHorizontal = SizeFlags.ExpandFill;
        row.MouseFilter = MouseFilterEnum.Ignore;

        row.AddChild(new Control { SizeFlagsHorizontal = SizeFlags.ExpandFill, MouseFilter = Control.MouseFilterEnum.Ignore });
        row.AddChild(BuildEquipSlot(slotL, labelL, equipment));
        row.AddChild(new Control { SizeFlagsHorizontal = SizeFlags.ExpandFill, MouseFilter = Control.MouseFilterEnum.Ignore });
        row.AddChild(BuildEquipSlot(slotC, labelC, equipment));
        row.AddChild(new Control { SizeFlagsHorizontal = SizeFlags.ExpandFill, MouseFilter = Control.MouseFilterEnum.Ignore });
        row.AddChild(BuildEquipSlot(slotR, labelR, equipment));
        row.AddChild(new Control { SizeFlagsHorizontal = SizeFlags.ExpandFill, MouseFilter = Control.MouseFilterEnum.Ignore });

        return row;
    }

    private Control BuildEquipSlot(EquipmentSlot slot, string slotLabel, Equipment? equipment)
    {
        var item = equipment?.GetSlot(slot);
        bool occupied = item != null;

        var container = new VBoxContainer
        {
            CustomMinimumSize = new Vector2(SlotSize, SlotSize + SlotLabelH),
            MouseFilter       = MouseFilterEnum.Ignore,
        };
        container.AddThemeConstantOverride("separation", 2);
        // Store slot as metadata for hit-rect association.
        container.SetMeta("equip_slot", (int)slot);

        // Slot box.
        var slotBox = new Control
        {
            CustomMinimumSize = new Vector2(SlotSize, SlotSize),
            MouseFilter       = MouseFilterEnum.Ignore,
        };

        var bg = new ColorRect
        {
            Color       = occupied ? SlotBgOccupied : SlotBgEmpty,
            MouseFilter = MouseFilterEnum.Ignore,
        };
        bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        slotBox.AddChild(bg);

        if (occupied)
        {
            // Gold highlight border for occupied slots.
            var highlight = new ColorRect
            {
                Color             = SlotHighlight,
                CustomMinimumSize = new Vector2(0, 0),
                MouseFilter       = MouseFilterEnum.Ignore,
            };
            highlight.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
            highlight.OffsetLeft = 2; highlight.OffsetTop = 2;
            highlight.OffsetRight = -2; highlight.OffsetBottom = -2;
            slotBox.AddChild(highlight);

            // Item icon.
            var icon = BuildItemIcon(item!, SlotSize - 8);
            icon.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
            icon.OffsetLeft = 4; icon.OffsetTop = 4;
            icon.OffsetRight = -4; icon.OffsetBottom = -4;
            icon.MouseFilter = MouseFilterEnum.Ignore;
            slotBox.AddChild(icon);
        }
        else
        {
            // Empty slot: show slot name as placeholder.
            var emptyLabel = new Label
            {
                Text                = slotLabel,
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment   = VerticalAlignment.Center,
                MouseFilter         = MouseFilterEnum.Ignore,
            };
            emptyLabel.AddThemeFontSizeOverride("font_size", 13);
            emptyLabel.AddThemeColorOverride("font_color", new Color(0.4f, 0.4f, 0.5f, 1f));
            emptyLabel.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
            slotBox.AddChild(emptyLabel);
        }

        container.AddChild(slotBox);

        // Item name below slot (occupied) or slot label (empty but smaller).
        var nameLabel = new Label
        {
            Text                = occupied ? TruncateName(item!.Name, 10) : "",
            HorizontalAlignment = HorizontalAlignment.Center,
            CustomMinimumSize   = new Vector2(SlotSize, SlotLabelH),
            MouseFilter         = MouseFilterEnum.Ignore,
        };
        nameLabel.AddThemeFontSizeOverride("font_size", 13);
        nameLabel.AddThemeColorOverride("font_color",
            occupied ? new Color(1f, 0.92f, 0.65f, 1f) : new Color(0.4f, 0.4f, 0.5f, 1f));
        container.AddChild(nameLabel);

        return container;
    }

    // ─────────────────────────────────────────────────────────────────────────
    // In Pack strip — rebuilt each Refresh()
    // ─────────────────────────────────────────────────────────────────────────

    private void RebuildPackStrip(GameState state)
    {
        if (_packStrip == null) return;

        foreach (var child in _packStrip.GetChildren())
            child.SafeFree();

        var inventory = state.PlayerInventory;
        var equipment = state.Player.Get<Equipment>();

        // Collect equipped item IDs so we can exclude them from the pack display.
        var equippedIds = new HashSet<int>();
        if (equipment != null)
            foreach (EquipmentSlot slot in Enum.GetValues<EquipmentSlot>())
            {
                var e = equipment.GetSlot(slot);
                if (e != null) equippedIds.Add(e.Id);
            }

        // Only show equippable items that are in inventory (not currently equipped).
        var equippables = inventory?.Items
            .Where(item => item.Get<Equippable>() != null && !equippedIds.Contains(item.Id))
            .ToList() ?? new List<Entity>();

        var hbox = new HBoxContainer();
        hbox.AddThemeConstantOverride("separation", 6);
        hbox.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        hbox.MouseFilter = MouseFilterEnum.Ignore;
        _packStrip.AddChild(hbox);

        if (equippables.Count == 0)
        {
            var emptyLabel = new Label
            {
                Text        = "(none)",
                MouseFilter = MouseFilterEnum.Ignore,
            };
            emptyLabel.AddThemeFontSizeOverride("font_size", 16);
            emptyLabel.AddThemeColorOverride("font_color", new Color(0.45f, 0.45f, 0.5f, 1f));
            hbox.AddChild(emptyLabel);
            return;
        }

        foreach (var item in equippables)
        {
            var slot = BuildPackSlot(item);
            hbox.AddChild(slot);
        }
    }

    private Control BuildPackSlot(Entity item)
    {
        var container = new Control
        {
            CustomMinimumSize = new Vector2(PackSlotSize, PackSlotSize),
            MouseFilter       = MouseFilterEnum.Ignore,
        };
        container.SetMeta("pack_item_id", item.Id);

        var bg = new ColorRect { Color = PackSlotBg, MouseFilter = MouseFilterEnum.Ignore };
        bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        container.AddChild(bg);

        var icon = BuildItemIcon(item, PackSlotSize - 8);
        icon.OffsetLeft = 4; icon.OffsetTop = 4;
        icon.OffsetRight = -4; icon.OffsetBottom = -4;
        icon.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        icon.MouseFilter = MouseFilterEnum.Ignore;
        container.AddChild(icon);

        // Item name tooltip-style label at bottom.
        var nameLabel = new Label
        {
            Text                = TruncateName(item.Name, 8),
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment   = VerticalAlignment.Bottom,
            MouseFilter         = MouseFilterEnum.Ignore,
            AnchorLeft   = 0f, AnchorTop    = 0f,
            AnchorRight  = 1f, AnchorBottom = 1f,
            OffsetRight  = -2f, OffsetBottom = -2f,
        };
        nameLabel.AddThemeFontSizeOverride("font_size", 11);
        nameLabel.AddThemeColorOverride("font_color", new Color(0.85f, 0.85f, 0.85f, 1f));
        container.AddChild(nameLabel);

        return container;
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Hit rect computation (deferred — called after layout resolves)
    // ─────────────────────────────────────────────────────────────────────────

    private void _ComputeHitRects()
    {
        _equippedRects.Clear();
        _packRects.Clear();

        var panelOrigin = GetGlobalRect().Position;

        // Walk slot grid: find Control nodes with "equip_slot" metadata.
        if (_slotGrid != null)
            WalkForEquipSlots(_slotGrid, panelOrigin);

        // Walk pack strip: find Control nodes with "pack_item_id" metadata.
        if (_packStrip != null)
            WalkForPackItems(_packStrip, panelOrigin);
    }

    private void WalkForEquipSlots(Node node, Vector2 panelOrigin)
    {
        if (node is Control c && c.HasMeta("equip_slot"))
        {
            var slot = (EquipmentSlot)(int)c.GetMeta("equip_slot");
            // Only add to hit list if the slot is occupied (the equip_slot container is
            // always present, but we only want clicks on occupied slots to fire Unequip).
            // We determine "occupied" by checking if the slotBox child has an item icon.
            // Simpler: the EquipRequested/UnequipRequested logic in _GuiInput guards.
            // Include all slots in hit rects; TurnController's ResolveUnequip guards empty slots.
            var globalRect = c.GetGlobalRect();
            var localRect = new Rect2(globalRect.Position - panelOrigin, globalRect.Size);
            _equippedRects.Add((slot, localRect));
        }

        foreach (var child in node.GetChildren())
            WalkForEquipSlots(child, panelOrigin);
    }

    private void WalkForPackItems(Node node, Vector2 panelOrigin)
    {
        if (node is Control c && c.HasMeta("pack_item_id"))
        {
            int itemId = (int)c.GetMeta("pack_item_id");
            var globalRect = c.GetGlobalRect();
            var localRect = new Rect2(globalRect.Position - panelOrigin, globalRect.Size);
            _packRects.Add((itemId, localRect));
            return; // Don't descend into pack slot children.
        }

        foreach (var child in node.GetChildren())
            WalkForPackItems(child, panelOrigin);
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Helpers
    // ─────────────────────────────────────────────────────────────────────────

    private static Control BuildItemIcon(Entity item, int size)
    {
        var spriteKey = item.Name.ToLowerInvariant().Replace(' ', '_');
        var spritePath = SpriteMapping.GetItemSpritePath(spriteKey);

        if (spritePath != null)
        {
            var texture = GD.Load<Texture2D>(spritePath);
            if (texture != null)
            {
                return new TextureRect
                {
                    Texture             = texture,
                    StretchMode         = TextureRect.StretchModeEnum.KeepAspectCentered,
                    CustomMinimumSize   = new Vector2(size, size),
                    SizeFlagsHorizontal = SizeFlags.ShrinkCenter,
                };
            }
        }

        return new ColorRect
        {
            Color             = FallbackEquipColor(item),
            CustomMinimumSize = new Vector2(size, size),
        };
    }

    private static Color FallbackEquipColor(Entity item)
    {
        var eq = item.Get<Equippable>();
        if (eq == null) return FallbackDefault;
        return eq.Slot switch
        {
            EquipmentSlot.LeftRing or EquipmentSlot.RightRing or EquipmentSlot.Neck => FallbackRing,
            _ => eq.IsWeapon ? FallbackWeapon : FallbackArmor,
        };
    }

    private static string TruncateName(string name, int maxLen) =>
        name.Length <= maxLen ? name : name[..maxLen] + "…";
}
