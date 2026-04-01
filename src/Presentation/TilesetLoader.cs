using Godot;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;
// Alias to resolve ambiguity with System.IO.FileAccess
using GodotFileAccess = Godot.FileAccess;

namespace CatacombsOfYarl.Presentation;

/// <summary>
/// Loads tileset configuration from config/tilesets/{id}.yaml.
///
/// Uses Godot's FileAccess for res:// path resolution — on iOS/Android, res:// files are
/// packed inside the .pck bundle and cannot be read via System.IO.File. FileAccess handles
/// this transparently. This is the same pattern used by Main.ReadGodotResource.
///
/// In debug builds, validates that the frame-1 path for each entity mapping actually
/// exists on disk. Catches YAML typos at boot rather than at first monster spawn.
/// </summary>
public static class TilesetLoader
{
    private const string TilesetsDir = "res://config/tilesets/";
    private const string FallbackId = "ultimate_fantasy";

    private static readonly IDeserializer _deserializer = new DeserializerBuilder()
        .WithNamingConvention(UnderscoredNamingConvention.Instance)
        .IgnoreUnmatchedProperties()
        .Build();

    /// <summary>
    /// Load a tileset by ID from config/tilesets/{id}.yaml.
    /// Throws FileNotFoundException with a clear path message if the file doesn't exist.
    /// </summary>
    public static TilesetConfig Load(string tilesetId)
    {
        var resPath = $"{TilesetsDir}{tilesetId}.yaml";

        using var file = GodotFileAccess.Open(resPath, GodotFileAccess.ModeFlags.Read);
        if (file == null)
        {
            throw new System.IO.FileNotFoundException(
                $"Tileset file not found: {resPath}. " +
                $"Ensure config/tilesets/{tilesetId}.yaml exists and is included in the Godot export.");
        }

        var yaml = file.GetAsText();
        var config = _deserializer.Deserialize<TilesetConfig>(yaml);

        if (config == null)
            throw new System.InvalidOperationException($"Failed to deserialize tileset: {resPath}");

        // Normalize: if Id wasn't set in the YAML, use the requested id.
        if (string.IsNullOrEmpty(config.Id))
            config.Id = tilesetId;

#if DEBUG
        ValidateSpritePaths(config);
#endif

        return config;
    }

    /// <summary>
    /// Load a tileset by ID, falling back to ultimate_fantasy on any error.
    /// Logs a clear error before falling back so the failure is visible.
    /// </summary>
    public static TilesetConfig LoadWithFallback(string tilesetId)
    {
        try
        {
            return Load(tilesetId);
        }
        catch (System.IO.FileNotFoundException ex)
        {
            GD.PrintErr($"[TilesetLoader] {ex.Message} — falling back to '{FallbackId}'.");
            return Load(FallbackId);
        }
        catch (System.Exception ex)
        {
            GD.PrintErr($"[TilesetLoader] Failed to load tileset '{tilesetId}': {ex.Message} — falling back to '{FallbackId}'.");
            return Load(FallbackId);
        }
    }

    /// <summary>
    /// Debug-only: check that the frame-1 resource path exists for each entity mapping.
    /// GD.PrintErr on any missing file so YAML typos surface at boot, not at first spawn.
    /// </summary>
    private static void ValidateSpritePaths(TilesetConfig config)
    {
#if DEBUG
        foreach (var (typeId, spriteValue) in config.Entities)
        {
            var path = ResolveFrame1Path(config, spriteValue);
            if (!ResourceLoader.Exists(path))
                GD.PrintErr($"[TilesetLoader] Missing entity sprite for '{typeId}': {path}");
        }
        // Items use a simpler single-path model — validate the static path directly.
        foreach (var (typeId, spriteValue) in config.Items)
        {
            var path = $"{config.ItemsRoot}/{spriteValue}.png";
            if (!ResourceLoader.Exists(path))
                GD.PrintErr($"[TilesetLoader] Missing item sprite for '{typeId}': {path}");
        }
#endif
    }

    /// <summary>
    /// Resolve the frame-1 resource path for an entity sprite value.
    /// Handles both path-based (FrameStride == 0) and index-based (FrameStride > 0) modes.
    /// Frame 1 is used because it's always the idle/default frame.
    /// </summary>
    private static string ResolveFrame1Path(TilesetConfig config, string spriteValue)
    {
        if (config.FrameStride == 0)
        {
            // Path-based (UF): {SpritesRoot}/{value}_1.png
            return $"{config.SpritesRoot}/{spriteValue}_1.png";
        }
        else
        {
            // Index-based (16bf): index = key * stride + 1 + offset
            if (!int.TryParse(spriteValue, out int creatureKey))
            {
                GD.PrintErr($"[TilesetLoader] Index-based tileset has non-integer creature key: '{spriteValue}'");
                return "";
            }
            int spriteIndex = creatureKey * config.FrameStride + 1 + config.FrameOffset;
            // D2 padding confirmed correct for 16bf: files are creatures_01.png through creatures_396.png.
            // D3 (creatures_001.png) would produce wrong filenames for all entries.
            var filename = config.FramePattern.Replace("{index:D2}", spriteIndex.ToString("D2"));
            return $"{config.SpritesRoot}/{filename}";
        }
    }
}
