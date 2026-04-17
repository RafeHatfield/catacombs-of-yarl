using Godot;
using System.Globalization;
// Alias to resolve ambiguity with System.IO.FileAccess
using GodotFileAccess = Godot.FileAccess;

namespace CatacombsOfYarl.Presentation;

/// <summary>
/// Loads tile theme configuration from config/tile_themes.yaml.
///
/// Uses manual line-by-line YAML parsing instead of YamlDotNet because
/// InvariantGlobalization=true (required for iOS NativeAOT) breaks YamlDotNet's
/// deserialization. The tile_themes.yaml format is simple enough for a hand-rolled parser.
///
/// YAML structure handled:
///   tile_root: "..."          — top-level string
///   tile_pattern: "..."       — top-level string
///   default_theme: grey_stone — top-level string (unquoted ok)
///
///   themes:                   — starts theme section
///     grey_stone:             — theme name (indented 2)
///       floor_primary: [1091]              — role with int array (indented 4)
///       floor_accent: [1034, 1090, 1089]   — role with int array
///       ...
///
/// Uses Godot's FileAccess for res:// path resolution — on iOS/Android, res:// files
/// are packed inside the .pck bundle and cannot be read via System.IO.File.
/// </summary>
public static class TileThemeLoader
{
    private const string ConfigPath = "res://config/tile_themes.yaml";

    /// <summary>
    /// Load tile theme config from config/tile_themes.yaml.
    /// Throws FileNotFoundException if the file is absent.
    /// Throws InvalidOperationException if parsing fails.
    /// </summary>
    public static TileThemeConfig Load()
    {
        using var file = GodotFileAccess.Open(ConfigPath, GodotFileAccess.ModeFlags.Read);
        if (file == null)
        {
            throw new System.IO.FileNotFoundException(
                $"Tile theme config not found: {ConfigPath}. " +
                "Ensure config/tile_themes.yaml exists and is included in the Godot export.");
        }

        var yaml = file.GetAsText();
        var config = ParseYaml(yaml);

        if (config == null)
            throw new System.InvalidOperationException($"Failed to parse tile theme config: {ConfigPath}");

        GD.Print($"[TileThemeLoader] Loaded {config.Themes.Count} theme(s): {string.Join(", ", config.Themes.Keys)}");
        return config;
    }

    /// <summary>
    /// Load tile theme config with a safe fallback: if the file is missing or
    /// parsing fails, returns a minimal config with an empty theme dictionary.
    /// The caller should handle empty Themes gracefully (DungeonRenderer skips tiles
    /// and logs errors rather than crashing).
    /// </summary>
    public static TileThemeConfig LoadWithFallback()
    {
        try
        {
            return Load();
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"[TileThemeLoader] Failed to load tile themes: {ex.Message} — using empty config.");
            return new TileThemeConfig();
        }
    }

    // -------------------------------------------------------------------------
    // Manual YAML parser
    //
    // The YAML has three structural levels:
    //   Level 0 (no indent):   top-level keys (tile_root, tile_pattern, default_theme, themes:)
    //   Level 1 (2 spaces):    theme names inside themes: block
    //   Level 2 (4+ spaces):   role keys inside each theme, with [comma,separated] array values
    //   Level 3 (6+ spaces):   sub-entries of wall_autotile and wall_diagonal blocks
    //
    // Parser state machine:
    //   Start         — reading top-level keys
    //   InThemes      — reading theme-level keys (theme names)
    //   InThemeRoles  — reading role keys for a specific theme
    //   InAutotile    — reading int-keyed sub-entries of wall_autotile block
    //   InDiagonal    — reading string-keyed sub-entries of wall_diagonal block
    // -------------------------------------------------------------------------

    private enum ParseState { Start, InThemes, InThemeRoles, InAutotile, InDiagonal }

    private static TileThemeConfig? ParseYaml(string yaml)
    {
        var config = new TileThemeConfig();
        var state = ParseState.Start;
        string? currentThemeName = null;
        TileThemeData? currentThemeData = null;

        foreach (var rawLine in yaml.Split('\n'))
        {
            var line = rawLine.TrimEnd('\r');

            // Skip blank lines and full-line comments
            var trimmed = line.TrimStart();
            if (trimmed.Length == 0 || trimmed[0] == '#')
                continue;

            // Strip inline comments (space + #)
            var content = StripInlineComment(trimmed);
            if (content.Length == 0) continue;

            // Measure indentation depth (number of leading spaces)
            int indent = CountLeadingSpaces(line);

            // Parse "key: value" — value may be empty (block opener like "themes:")
            int colonIdx = content.IndexOf(':');
            if (colonIdx < 0) continue;

            var key = content[..colonIdx].Trim();
            var rawValue = colonIdx + 1 < content.Length
                ? content[(colonIdx + 1)..].Trim()
                : "";
            var value = Unquote(rawValue);

            // ------------------------------------------------------------------
            // State transitions based on indentation
            // ------------------------------------------------------------------

            if (indent == 0)
            {
                // Top-level key — commit any in-progress theme before resetting
                if (currentThemeName != null && currentThemeData != null)
                    config.Themes[currentThemeName] = currentThemeData;
                state = ParseState.Start;
                currentThemeName = null;
                currentThemeData = null;

                switch (key)
                {
                    case "tile_root":
                        config.TileRoot = value;
                        break;
                    case "tile_pattern":
                        config.TilePattern = value;
                        break;
                    case "default_theme":
                        config.DefaultTheme = value;
                        break;
                    case "themes":
                        // Enter themes block — next indented lines are theme names
                        state = ParseState.InThemes;
                        break;
                }
                continue;
            }

            if ((state == ParseState.InThemes || state == ParseState.InThemeRoles || state == ParseState.InAutotile || state == ParseState.InDiagonal) && indent == 2)
            {
                // Theme name line: "  grey_stone:" — value should be empty
                // Commit previous theme if any
                if (currentThemeName != null && currentThemeData != null)
                    config.Themes[currentThemeName] = currentThemeData;

                currentThemeName = key;
                currentThemeData = new TileThemeData();
                state = ParseState.InThemeRoles;
                continue;
            }

            // ------------------------------------------------------------------
            // InAutotile: reading bitmask→tileId pairs at indent >= 6
            // These are the sub-entries of wall_autotile: { 0: 186, 1: 187, ... }
            // Keys are integers (bitmask 0–15); values are tile IDs.
            // ------------------------------------------------------------------
            if (state == ParseState.InAutotile && indent >= 6)
            {
                if (currentThemeData == null) continue;

                // Key is the bitmask (0–15), value is the tile ID
                if (int.TryParse(key, NumberStyles.Integer, CultureInfo.InvariantCulture, out int bitmask) &&
                    int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out int tileId))
                {
                    currentThemeData.WallAutotile[bitmask] = tileId;
                }
                else
                {
                    GD.PrintErr($"[TileThemeLoader] Could not parse autotile entry '{key}: {value}' in theme '{currentThemeName}'.");
                }
                continue;
            }

            // ------------------------------------------------------------------
            // InDiagonal: reading named corner role → tileId pairs at indent >= 6
            // These are the sub-entries of wall_diagonal:
            //   corner_outer_nw: 189
            //   corner_outer_ne: 190
            //   ...
            // Keys are strings; values are tile IDs.
            // ------------------------------------------------------------------
            if (state == ParseState.InDiagonal && indent >= 6)
            {
                if (currentThemeData == null) continue;

                if (int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out int diagTileId))
                {
                    currentThemeData.WallDiagonal[key] = diagTileId;
                }
                else
                {
                    GD.PrintErr($"[TileThemeLoader] Could not parse diagonal entry '{key}: {value}' in theme '{currentThemeName}'.");
                }
                continue;
            }

            // If we were in InAutotile or InDiagonal but hit indent < 6, return to InThemeRoles.
            // A role line at indent 4 means we've left the sub-block.
            if ((state == ParseState.InAutotile || state == ParseState.InDiagonal) && indent >= 4)
            {
                state = ParseState.InThemeRoles;
                // Fall through to InThemeRoles handling below
            }

            if ((state == ParseState.InThemeRoles || state == ParseState.InAutotile || state == ParseState.InDiagonal) && indent >= 4)
            {
                // Role line: "    floor_primary: [860]"
                if (currentThemeData == null) continue;

                if (key == "wall_autotile")
                {
                    // Mapping block — enter autotile sub-state.
                    // Entries will be read on subsequent lines at indent >= 6.
                    state = ParseState.InAutotile;
                    continue;
                }

                if (key == "wall_diagonal")
                {
                    // Mapping block — enter diagonal sub-state.
                    // Entries will be read on subsequent lines at indent >= 6.
                    state = ParseState.InDiagonal;
                    continue;
                }

                // Value must be a bracketed int list: [1, 2, 3]
                var ids = ParseIntList(rawValue);

                switch (key)
                {
                    case "floor_primary":   currentThemeData.FloorPrimary   = ids; break;
                    case "floor_accent":    currentThemeData.FloorAccent    = ids; break;
                    case "floor_dark":      currentThemeData.FloorDark      = ids; break;
                    case "floor_interior":  currentThemeData.FloorInterior  = ids; break;
                    case "floor_worn":      currentThemeData.FloorWorn      = ids; break;
                    case "stair_down":      currentThemeData.StairDown      = ids; break;
                    case "stair_up":        currentThemeData.StairUp        = ids; break;
                    case "door":            currentThemeData.Door           = ids; break;
                    case "bones":           currentThemeData.Bones          = ids; break;
                    default:
                        GD.PrintErr($"[TileThemeLoader] Unknown role key '{key}' in theme '{currentThemeName}'.");
                        break;
                }
                continue;
            }

            // Unexpected indentation level for current state — log and skip.
            // This can happen if the YAML has unexpected structure; be lenient.
            GD.PrintErr($"[TileThemeLoader] Unexpected line at indent={indent} in state={state}: '{content}'");
        }

        // Commit the final theme if we were mid-parse when the file ended
        if (currentThemeName != null && currentThemeData != null)
            config.Themes[currentThemeName] = currentThemeData;

        return config;
    }

    // -------------------------------------------------------------------------
    // Parsing helpers
    // -------------------------------------------------------------------------

    /// <summary>
    /// Parse a bracketed integer list from YAML: "[1091]" or "[1034, 1090, 1089, 1088]"
    /// Returns an empty list on any parse error rather than throwing.
    /// </summary>
    private static List<int> ParseIntList(string raw)
    {
        var result = new List<int>();

        // Strip brackets
        raw = raw.Trim();
        if (raw.StartsWith('[')) raw = raw[1..];
        if (raw.EndsWith(']'))   raw = raw[..^1];

        foreach (var part in raw.Split(','))
        {
            var s = part.Trim();
            if (s.Length == 0) continue;

            if (int.TryParse(s, NumberStyles.Integer, CultureInfo.InvariantCulture, out int id))
                result.Add(id);
            else
                GD.PrintErr($"[TileThemeLoader] Could not parse int '{s}' in list '{raw}'.");
        }

        return result;
    }

    /// <summary>
    /// Strip inline YAML comment: space followed by # and everything after.
    /// Ignores # inside double-quoted strings.
    /// </summary>
    private static string StripInlineComment(string s)
    {
        bool inQuote = false;
        for (int i = 0; i < s.Length; i++)
        {
            if (s[i] == '"') inQuote = !inQuote;
            if (!inQuote && s[i] == '#' && i > 0 && s[i - 1] == ' ')
                return s[..i].TrimEnd();
        }
        return s;
    }

    /// <summary>Strip surrounding double-quotes from a YAML string value.</summary>
    private static string Unquote(string s)
    {
        if (s.Length >= 2 && s[0] == '"' && s[^1] == '"')
            return s[1..^1];
        return s;
    }

    /// <summary>Count leading space characters (not tabs) for indentation detection.</summary>
    private static int CountLeadingSpaces(string line)
    {
        int count = 0;
        foreach (char c in line)
        {
            if (c == ' ') count++;
            else if (c == '\t') count += 2; // treat tab as 2 spaces
            else break;
        }
        return count;
    }
}
