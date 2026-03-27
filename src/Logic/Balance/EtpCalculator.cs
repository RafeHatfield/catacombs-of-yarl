using CatacombsOfYarl.Logic.Content;

namespace CatacombsOfYarl.Logic.Balance;

/// <summary>
/// Minimal ETP (Effective Threat Points) calculator for dungeon generation.
/// Returns etp_base from the monster definition. The full band-scaling system
/// (etp_config.yaml, depth multipliers, pity tracking) is a future milestone.
/// </summary>
public static class EtpCalculator
{
    /// <summary>ETP cost of spawning one instance of this monster.</summary>
    public static int GetEtp(MonsterDefinition def) => def.EtpBase;

    /// <summary>
    /// True if adding addEtp to currentEtp stays within the room budget.
    /// When allowSpike is true, budget is relaxed to 150% (matches Python pity system intent).
    /// </summary>
    public static bool FitsInBudget(int currentEtp, int addEtp, int maxEtp, bool allowSpike)
        => (currentEtp + addEtp) <= (allowSpike ? (int)(maxEtp * 1.5) : maxEtp);
}
