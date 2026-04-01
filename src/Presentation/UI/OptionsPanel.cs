using Godot;

namespace CatacombsOfYarl.Presentation.UI;

/// <summary>
/// Options panel shown from the main menu.
///
/// Currently contains a tileset selector. The selection is boot-time only —
/// changing it writes to config/game_settings.yaml and shows a "Restart to apply"
/// notice. No hot-swap; the engine picks up the new value on next launch.
/// </summary>
public sealed partial class OptionsPanel : Control
{
    [Signal] public delegate void BackRequestedEventHandler();

    // The ID that was actually loaded at boot (passed in from Main so we can detect changes).
    private readonly string _loadedTilesetId;

    // Ordered list of (id, display name) pairs. Small and fixed — no need to scan disk.
    private static readonly (string Id, string DisplayName)[] KnownTilesets =
    [
        ("ultimate_fantasy", "Ultimate Fantasy"),
        ("16bit_fantasy",    "16-Bit Fantasy"),
    ];

    // Current selection index into KnownTilesets
    private int _selectedIndex;

    // Live UI references so we can update text after _Ready
    private TouchButton? _cycleBtn;
    private Label?       _restartLabel;

    public OptionsPanel(string loadedTilesetId)
    {
        _loadedTilesetId = loadedTilesetId;
        // Find the starting selection — default to index 0 if ID not recognised.
        _selectedIndex = FindIndex(loadedTilesetId);
    }

    public override void _Ready()
    {
        BuildLayout();
    }

    private void BuildLayout()
    {
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        MouseFilter = MouseFilterEnum.Stop;

        // Semi-transparent dark backdrop — matches MainMenuPanel / other menu panels.
        var bg = new ColorRect
        {
            Color       = new Color(0f, 0f, 0f, 0.85f),
            MouseFilter = MouseFilterEnum.Ignore,
        };
        bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        AddChild(bg);

        // Centered content column
        var vbox = new VBoxContainer { MouseFilter = MouseFilterEnum.Ignore };
        vbox.SetAnchorsAndOffsetsPreset(LayoutPreset.Center);
        vbox.GrowHorizontal    = GrowDirection.Both;
        vbox.GrowVertical      = GrowDirection.Both;
        vbox.CustomMinimumSize = new Vector2(320, 0);
        vbox.AddThemeConstantOverride("separation", 24);
        AddChild(vbox);

        // Title
        var title = new Label
        {
            Text                = "Options",
            HorizontalAlignment = HorizontalAlignment.Center,
            MouseFilter         = MouseFilterEnum.Ignore,
        };
        title.AddThemeFontSizeOverride("font_size", 36);
        vbox.AddChild(title);

        // Section label
        var sectionLabel = new Label
        {
            Text                = "Tileset",
            HorizontalAlignment = HorizontalAlignment.Center,
            MouseFilter         = MouseFilterEnum.Ignore,
        };
        sectionLabel.AddThemeFontSizeOverride("font_size", 18);
        sectionLabel.AddThemeColorOverride("font_color", new Color(0.65f, 0.65f, 0.65f, 1f));
        vbox.AddChild(sectionLabel);

        // Cycle button — label shows current selection, press advances to next.
        _cycleBtn = new TouchButton
        {
            Text              = CycleBtnText(),
            FontSize          = 22,
            BackgroundColor   = new Color(0.25f, 0.25f, 0.35f, 0.95f),
            CustomMinimumSize = new Vector2(280, 56),
        };
        _cycleBtn.Pressed += OnCyclePressed;
        vbox.AddChild(_cycleBtn);

        // "Restart to apply" notice — only visible when a change has been made this session.
        _restartLabel = new Label
        {
            Text                = "Restart to apply",
            HorizontalAlignment = HorizontalAlignment.Center,
            MouseFilter         = MouseFilterEnum.Ignore,
            Visible             = false,
        };
        _restartLabel.AddThemeFontSizeOverride("font_size", 16);
        _restartLabel.AddThemeColorOverride("font_color", new Color(0.9f, 0.75f, 0.3f, 1f));
        vbox.AddChild(_restartLabel);

        // Back button
        var backBtn = new TouchButton
        {
            Text              = "← Back",
            FontSize          = 22,
            BackgroundColor   = new Color(0.35f, 0.2f, 0.2f, 0.95f),
            CustomMinimumSize = new Vector2(280, 56),
        };
        backBtn.Pressed += () => EmitSignal(SignalName.BackRequested);
        vbox.AddChild(backBtn);
    }

    // -------------------------------------------------------------------------
    // Tileset cycling
    // -------------------------------------------------------------------------

    private void OnCyclePressed()
    {
        // Advance to next tileset, wrapping around.
        _selectedIndex = (_selectedIndex + 1) % KnownTilesets.Length;

        var (newId, _) = KnownTilesets[_selectedIndex];

        // Update button label
        if (_cycleBtn != null)
            _cycleBtn.Text = CycleBtnText();

        // Show or hide the "restart" notice based on whether the selection differs from boot.
        if (_restartLabel != null)
            _restartLabel.Visible = newId != _loadedTilesetId;

        // Persist to game_settings.yaml immediately so the value survives if the user
        // closes without returning to the main menu.
        WriteTilesetSetting(newId);
    }

    private string CycleBtnText()
    {
        var (_, displayName) = KnownTilesets[_selectedIndex];
        return $"Tileset: {displayName}  →";
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private static int FindIndex(string id)
    {
        for (int i = 0; i < KnownTilesets.Length; i++)
        {
            if (KnownTilesets[i].Id == id) return i;
        }
        return 0;
    }

    /// <summary>
    /// Write the new tileset ID into config/game_settings.yaml.
    ///
    /// Strategy: read the current file text, replace the `tileset:` line, write back.
    /// Simple string replacement is intentional — YamlDotNet round-trips would strip
    /// comments and reformat the file. We preserve the file exactly except for that one line.
    ///
    /// Uses ProjectSettings.GlobalizePath to get the real filesystem path. This is
    /// correct on desktop/editor. On mobile, res:// is read-only inside the .pck — a
    /// proper settings migration to user:// would be needed there, but that's deferred.
    /// </summary>
    private static void WriteTilesetSetting(string tilesetId)
    {
        const string resPath = "res://config/game_settings.yaml";

        try
        {
            // Read current contents
            string currentText;
            using (var readFile = Godot.FileAccess.Open(resPath, Godot.FileAccess.ModeFlags.Read))
            {
                if (readFile == null)
                {
                    GD.PrintErr("[OptionsPanel] Cannot open game_settings.yaml for reading.");
                    return;
                }
                currentText = readFile.GetAsText();
            }

            // Replace the tileset: line, preserving the rest of the file verbatim.
            // Handles both quoted ("value") and unquoted (value) forms on the RHS.
            var lines = currentText.Split('\n');
            bool replaced = false;
            for (int i = 0; i < lines.Length; i++)
            {
                if (lines[i].TrimStart().StartsWith("tileset:", System.StringComparison.Ordinal))
                {
                    lines[i] = $"tileset: \"{tilesetId}\"";
                    replaced = true;
                    break;
                }
            }

            if (!replaced)
            {
                // Field not found — append it so the file stays valid.
                var list = new System.Collections.Generic.List<string>(lines) { $"tileset: \"{tilesetId}\"" };
                lines = list.ToArray();
            }

            var newText = string.Join('\n', lines);

            // Write back via Godot FileAccess (handles res:// correctly on desktop/editor).
            using var writeFile = Godot.FileAccess.Open(resPath, Godot.FileAccess.ModeFlags.Write);
            if (writeFile == null)
            {
                GD.PrintErr("[OptionsPanel] Cannot open game_settings.yaml for writing. " +
                            "On mobile, res:// is read-only — settings changes won't persist.");
                return;
            }
            writeFile.StoreString(newText);
            GD.Print($"[OptionsPanel] Tileset setting saved: {tilesetId}");
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"[OptionsPanel] Failed to write game_settings.yaml: {ex.Message}");
        }
    }
}
