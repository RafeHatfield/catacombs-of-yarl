namespace CatacombsOfYarl.Logic.ECS;

public sealed class ChestComponent : IComponent
{
    public Entity? Owner { get; set; }

    public bool IsOpen { get; set; }

    /// <summary>Item type IDs resolved at floor-gen time. Consumed when chest is opened.</summary>
    public List<string> LootItemIds { get; init; } = new();
}
