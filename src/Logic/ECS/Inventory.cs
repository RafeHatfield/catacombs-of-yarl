namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// Holds items an entity is carrying. Items are Entity instances with Consumable/Equippable components.
/// </summary>
public sealed class Inventory : IComponent
{
    public Entity? Owner { get; set; }

    private readonly List<Entity> _items = new();

    public IReadOnlyList<Entity> Items => _items;
    public int Count => _items.Count;

    public void Add(Entity item) => _items.Add(item);

    public bool Remove(Entity item) => _items.Remove(item);

    /// <summary>Find the first item matching a predicate.</summary>
    public Entity? FindFirst(Func<Entity, bool> predicate) => _items.FirstOrDefault(predicate);
}
