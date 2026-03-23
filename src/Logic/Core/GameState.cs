using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Core;

/// <summary>
/// Mutable game state. Holds everything needed to process a turn.
/// Created once at game start, mutated by TurnController each turn.
/// </summary>
public sealed class GameState
{
    public Entity Player { get; }
    public List<Entity> Monsters { get; }
    public GameMap Map { get; }
    public SeededRandom Rng { get; }
    public int TurnCount { get; set; }
    public int TurnLimit { get; set; }

    public GameState(Entity player, List<Entity> monsters, GameMap map, SeededRandom rng, int turnLimit = 100)
    {
        Player = player;
        Monsters = monsters;
        Map = map;
        Rng = rng;
        TurnLimit = turnLimit;
    }

    public Fighter PlayerFighter => Player.Require<Fighter>();
    public Inventory? PlayerInventory => Player.Get<Inventory>();
    public bool IsGameOver => !PlayerFighter.IsAlive || AliveMonsters.Count == 0 || TurnCount >= TurnLimit;
    public bool PlayerWon => PlayerFighter.IsAlive && AliveMonsters.Count == 0;
    public List<Entity> AliveMonsters => Monsters.Where(m => m.Require<Fighter>().IsAlive).ToList();
}
