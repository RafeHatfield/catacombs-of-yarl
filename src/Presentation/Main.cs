using Godot;

namespace CatacombsOfYarl.Presentation;

/// <summary>
/// Root node for the game. Orchestrates the presentation layer.
/// Will hold GameState and wire input → TurnController → rendering.
/// </summary>
public partial class Main : Node
{
    public override void _Ready()
    {
        GD.Print("Catacombs of YARL — presentation layer loaded.");
        GD.Print($"Viewport: {GetViewport().GetVisibleRect().Size}");
    }
}
