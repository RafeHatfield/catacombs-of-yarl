using CatacombsOfYarl.Logic.Persistence;
using CatacombsOfYarl.Logic.Persistence.Namespaces;

namespace CatacombsOfYarl.Logic.Endgame;

/// <summary>
/// The audit. Deterministic scoring of Sasha's whole record into per-Guardian dispositions
/// and a final ending. This is the convergence point of plan_end_game: possession, memo tone,
/// faction reputation, deaths/past-Sashas, and the excess metric all resolve here.
///
/// Inputs are existing persistence fields plus the excess metric (decision 2). Thresholds are
/// STRAWMAN per decisions 5/6 — the structure is final; the numbers move in the harness balance
/// pass (TASK-011). All scoring is pure and deterministic (no RNG, no time).
/// </summary>
public static class AuditScorer
{
    /// <summary>The four faction-Guardian tiers for a run. The Debt has no tier.</summary>
    public readonly record struct AuditResult(
        GuardianTier WardenOfWardens,
        GuardianTier Oathkeeper,
        GuardianTier AssemblyOfTheLost,
        GuardianTier AuditorsOwn)
    {
        /// <summary>True if any faction Guardian came up Savage — the primary "heavy record" signal.</summary>
        public bool AnySavage =>
            WardenOfWardens == GuardianTier.Savage
            || Oathkeeper == GuardianTier.Savage
            || AssemblyOfTheLost == GuardianTier.Savage
            || AuditorsOwn == GuardianTier.Savage;

        /// <summary>Tier for a given faction Guardian. Throws for <see cref="GuardianId.Debt"/> (unscaled).</summary>
        public GuardianTier TierFor(GuardianId id) => id switch
        {
            GuardianId.WardenOfWardens => WardenOfWardens,
            GuardianId.Oathkeeper => Oathkeeper,
            GuardianId.AssemblyOfTheLost => AssemblyOfTheLost,
            GuardianId.AuditorsOwn => AuditorsOwn,
            _ => throw new System.ArgumentOutOfRangeException(nameof(id), "The Debt does not scale and has no tier."),
        };
    }

    // --- Strawman thresholds (tunable in TASK-011) ---
    private const int AssemblyAlliedMaxDeaths = 2;     // 0-2 deaths
    private const int AssemblyDiminishedMaxDeaths = 5; // 3-5
    private const int AssemblyNeutralMaxDeaths = 10;   // 6-10; 11+ Savage
    private const int WardenDiminishedMaxPossessions = 2; // 1-2
    private const int WardenNeutralMaxPossessions = 5;    // 3-5; 6+ Savage
    private const double AuditorAlliedMaxRate = 0.10;     // excess kills per floor reached
    private const double AuditorDiminishedMaxRate = 0.30;
    private const double AuditorNeutralMaxRate = 0.60;    // >= 0.60 Savage

    /// <summary>
    /// Guardian 1 — Warden-of-Wardens. Possession count + memo tone.
    /// A formal_complaint / final_audit tone is itself savage regardless of count.
    /// </summary>
    public static GuardianTier ScoreWarden(int hallWardenPossessions, string memoTone)
    {
        if (memoTone is "formal_complaint" or "final_audit")
            return GuardianTier.Savage;
        if (hallWardenPossessions <= 0) return GuardianTier.Allied;
        if (hallWardenPossessions <= WardenDiminishedMaxPossessions) return GuardianTier.Diminished;
        if (hallWardenPossessions <= WardenNeutralMaxPossessions) return GuardianTier.Neutral;
        return GuardianTier.Savage;
    }

    /// <summary>
    /// Guardian 2 — Oathkeeper. Orc reputation is the coarse lever; unprovoked orc kills sharpen
    /// the middle. Allied rep → ally; Hostile rep → savage; Neutral splits on whether blood was spilled.
    /// </summary>
    public static GuardianTier ScoreOathkeeper(string orcRepState, int unprovokedOrcKills)
    {
        switch (orcRepState)
        {
            case "allied": return GuardianTier.Allied;
            case "hostile": return GuardianTier.Savage;
            default: // neutral
                return unprovokedOrcKills <= 0 ? GuardianTier.Diminished : GuardianTier.Neutral;
        }
    }

    /// <summary>
    /// Guardian 3 — Assembly of the Lost. Cumulative deaths (the past-Sasha catalog tracks the same
    /// qualifying deaths; deaths is the primary lever).
    /// </summary>
    public static GuardianTier ScoreAssembly(int cumulativeDeaths)
    {
        if (cumulativeDeaths <= AssemblyAlliedMaxDeaths) return GuardianTier.Allied;
        if (cumulativeDeaths <= AssemblyDiminishedMaxDeaths) return GuardianTier.Diminished;
        if (cumulativeDeaths <= AssemblyNeutralMaxDeaths) return GuardianTier.Neutral;
        return GuardianTier.Savage;
    }

    /// <summary>
    /// Guardian 4 — Auditor's Own. The excess metric: unprovoked cross-faction kills normalized by
    /// floors reached (rate, not raw count — descending deeper does not by itself count as cruelty).
    /// </summary>
    public static GuardianTier ScoreAuditor(int totalUnprovokedKills, int floorsReached)
    {
        double rate = totalUnprovokedKills / (double)System.Math.Max(1, floorsReached);
        if (rate < AuditorAlliedMaxRate) return GuardianTier.Allied;
        if (rate < AuditorDiminishedMaxRate) return GuardianTier.Diminished;
        if (rate < AuditorNeutralMaxRate) return GuardianTier.Neutral;
        return GuardianTier.Savage;
    }

    /// <summary>
    /// Score the full audit from persistence + run context. <paramref name="floorsReached"/> is
    /// normally <see cref="WeighingConstants.FinalFloorDepth"/> at the Weighing.
    /// </summary>
    public static AuditResult Score(PersistentRunState persistent, int floorsReached)
    {
        UnderWardenData uw = persistent.UnderWarden;
        string orcRep = persistent.Factions.GetState(FactionsData.OrcFactionId);

        return new AuditResult(
            WardenOfWardens: ScoreWarden(uw.HallWardenPossessionsTotal, uw.LastMemoTone),
            Oathkeeper: ScoreOathkeeper(orcRep, uw.UnprovokedKillsFor(FactionsData.OrcFactionId)),
            AssemblyOfTheLost: ScoreAssembly(uw.CumulativeDeaths),
            AuditorsOwn: ScoreAuditor(uw.TotalUnprovokedKills(), floorsReached));
    }

    /// <summary>
    /// The ending branch (decision 6). Refusal and the two death states resolve directly from the
    /// outcome; survival splits into Swap (chosen, gated on the Hael catalog), Theft (heavy record),
    /// or Clean Audit. "Heavy" strawman: any Savage Guardian, or orc rep Hostile, or high deaths.
    /// </summary>
    public static EndingType DetermineEnding(
        WeighingOutcome outcome,
        AuditResult audit,
        bool swapChosen,
        bool swapAvailable,
        string orcRepState,
        int cumulativeDeaths)
    {
        switch (outcome)
        {
            case WeighingOutcome.Refused:
                return EndingType.LossRefused;
            case WeighingOutcome.DiedToGuardians:
                return EndingType.LossGuardians;
            case WeighingOutcome.DiedToDebt:
                return EndingType.LossDebt;
            case WeighingOutcome.InProgress:
                return EndingType.None;
            case WeighingOutcome.Survived:
                // Swap is the hidden terminus — only when the catalog gate is open and the player chose it.
                if (swapChosen && swapAvailable) return EndingType.Swap;
                bool heavy = audit.AnySavage
                    || orcRepState == "hostile"
                    || cumulativeDeaths > AssemblyNeutralMaxDeaths;
                return heavy ? EndingType.Theft : EndingType.CleanAudit;
            default:
                return EndingType.None;
        }
    }
}
