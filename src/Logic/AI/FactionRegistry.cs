namespace CatacombsOfYarl.Logic.AI;

/// <summary>
/// Static hostility matrix between factions. Port of PoC components/faction.py.
///
/// PoC faction mapping to C# YAML strings:
///   PLAYER        → "player"
///   ORC_FACTION   → "orc"        (orcs, trolls)
///   UNDEAD        → "undead"     (zombies, skeletons, wraiths, lich)
///   CULTIST       → "cultist"    (cultist_blademaster, cultist variants)
///   INDEPENDENT   → "beast"      (spiders, slimes, fire_beetle — C# merged PoC INDEPENDENT + HOSTILE_ALL)
///   NEUTRAL       → "neutral"    (default for unset factions)
///   "monsters"    → treated as "neutral" (fire_beetle YAML uses this; functionally equivalent)
///
/// Rules (from PoC HOSTILITY_MATRIX):
/// - Same faction → never hostile
/// - Player ↔ all monster factions: hostile
/// - Orc: attacks undead, beast. Neutral with cultist.
/// - Undead: attacks all living (orc, cultist, beast, neutral)
/// - Cultist: territorial — attacks orc, undead, beast, neutral
/// - Beast (PoC INDEPENDENT): attacks everything except same faction
/// - Neutral: only hostile to player and beast
/// </summary>
public static class FactionRegistry
{
    /// <summary>
    /// Returns true if entities of factionA would attack entities of factionB.
    /// Uses the directional PoC matrix — checks both directions for full coverage.
    /// </summary>
    public static bool AreHostile(string factionA, string factionB)
    {
        // Normalize: "monsters" → "neutral" (fire_beetle YAML quirk)
        string a = Normalize(factionA);
        string b = Normalize(factionB);

        if (a == b) return false;

        // Player is hostile to everything, everything is hostile to player
        if (a == "player" || b == "player") return true;

        return IsHostile(a, b) || IsHostile(b, a);
    }

    /// <summary>
    /// Directional hostility: does attacker want to attack target?
    /// Matches PoC HOSTILITY_MATRIX[attacker][target].
    /// </summary>
    private static bool IsHostile(string attacker, string target) =>
        (attacker, target) switch
        {
            // ORC_FACTION: attacks undead, beast. Neutral with cultist.
            ("orc", "undead") => true,
            ("orc", "beast") => true,
            ("orc", "neutral") => false,
            ("orc", "cultist") => false,

            // UNDEAD: attacks all living factions
            ("undead", "orc") => true,
            ("undead", "cultist") => true,
            ("undead", "beast") => true,
            ("undead", "neutral") => true,

            // CULTIST: territorial — attacks all intruders
            ("cultist", "orc") => true,
            ("cultist", "undead") => true,
            ("cultist", "beast") => true,
            ("cultist", "neutral") => true,

            // BEAST (PoC INDEPENDENT): predators — attack everything
            ("beast", "orc") => true,
            ("beast", "undead") => true,
            ("beast", "cultist") => true,
            ("beast", "neutral") => true,

            // NEUTRAL: only hostile to player (handled above) and beast
            ("neutral", "beast") => true,

            _ => false,
        };

    /// <summary>
    /// Target priority when multiple hostiles exist. Higher = preferred.
    /// Matches PoC TARGET_PRIORITY_MATRIX. 0 = won't target.
    /// </summary>
    public static int GetTargetPriority(string attackerFaction, string targetFaction)
    {
        string attacker = Normalize(attackerFaction);
        string target = Normalize(targetFaction);

        if (target == "player") return 10;

        return (attacker, target) switch
        {
            // Orc: player > undead > beast
            ("orc", "undead") => 6,
            ("orc", "beast") => 4,

            // Undead: player > living flesh (orc/cultist) > beast > neutral
            ("undead", "orc") => 7,
            ("undead", "cultist") => 7,
            ("undead", "beast") => 5,
            ("undead", "neutral") => 5,

            // Cultist: player > undead > orc/beast
            ("cultist", "orc") => 5,
            ("cultist", "undead") => 6,
            ("cultist", "beast") => 4,
            ("cultist", "neutral") => 4,

            // Beast: player > orc/cultist > neutral > undead (no flesh)
            ("beast", "orc") => 6,
            ("beast", "cultist") => 6,
            ("beast", "neutral") => 5,
            ("beast", "undead") => 3,

            // Neutral: player > beast
            ("neutral", "beast") => 3,

            _ => 0,
        };
    }

    private static string Normalize(string faction) =>
        faction == "monsters" ? "neutral" : faction;
}
