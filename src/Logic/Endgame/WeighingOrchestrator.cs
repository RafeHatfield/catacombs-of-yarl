using System.Collections.Generic;
using System.Linq;
using CatacombsOfYarl.Logic.AI;
using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Endgame;

/// <summary>The phase of the Weighing gauntlet.</summary>
public enum WeighingPhase
{
    /// <summary>Faction Guardians rising in sequence; the player clears hostile ones one at a time.</summary>
    Guardians,
    /// <summary>
    /// The claim has stated its terms; the player must choose Force / Self (Swap) / Refuse.
    /// No combat entity is present yet. Input is blocked until a choice method is called.
    /// Auto-CleanAudit skips this phase entirely (no choice to make).
    /// </summary>
    DebtChoiceGate,
    /// <summary>Force was chosen; the Debt is a live combatant. Faced alone.</summary>
    DebtCombat,
    /// <summary>The Weighing has resolved into an ending (set on GameState.Ending).</summary>
    Resolved,
}

/// <summary>
/// Live orchestration state for the Weighing. Holds the audit result (per-Guardian tiers, decided
/// once at the start), the rise cursor, and the snapshot inputs the ending branch needs. Self-
/// contained so the orchestrator is testable without re-reading persistence mid-fight.
/// </summary>
public sealed class WeighingState
{
    public WeighingPhase Phase { get; set; } = WeighingPhase.Guardians;
    public int CurrentGuardianIndex { get; set; }
    public AuditScorer.AuditResult Audit { get; set; }

    public bool SwapAvailable { get; set; }
    public bool SwapChosen { get; set; }
    public string OrcRepState { get; set; } = "neutral";
    public int CumulativeDeaths { get; set; }

    /// <summary>The hostile Guardian currently blocking progress (null while none is up).</summary>
    public int? ActiveGuardianId { get; set; }
    /// <summary>Entity IDs of allied Guardians on the field.</summary>
    public List<int> AlliedGuardianIds { get; } = new();
    /// <summary>GuardianId values that allied — needed to emit fallback lines in FallBackAllies.</summary>
    public List<GuardianId> AlliedGuardianTypes { get; } = new();
    public int? DebtId { get; set; }
    public bool AlliesFellBack { get; set; }
}

// ── Events (content/presentation hooks; lines are authored separately) ──────────
public sealed class GuardianRoseEvent : TurnEvent
{
    public GuardianId Guardian { get; init; }
    public GuardianTier Tier { get; init; }
    public int GuardianEntityId { get; init; }
}
public sealed class AlliesFellBackEvent : TurnEvent { }
public sealed class DebtRoseEvent : TurnEvent { }

/// <summary>
/// Emitted when the Debt threshold is reached and a player choice is required.
/// The presentation layer renders Force / (Self if SwapAvailable) / Refuse buttons.
/// Auto-CleanAudit (clean record, no Swap available) never emits this event.
/// </summary>
public sealed class DebtChoiceGateEvent : TurnEvent
{
    /// <summary>Whether the Swap option (Self) should be offered.</summary>
    public bool SwapAvailable { get; init; }
    /// <summary>True on the heavy-record path; false on clean-record-with-Swap.</summary>
    public bool IsHeavyRecord { get; init; }
}

public sealed class WeighingResolvedEvent : TurnEvent { public EndingType Ending { get; init; } }

/// <summary>
/// Drives the Weighing gauntlet (TASK-009). Sequential: the four faction Guardians rise in the
/// finalized order (Warden → Oathkeeper → Auditor's Own → Assembly), each at its arena anchor and
/// at the tier the audit assigned. Allied Guardians join Sasha's side and don't block; hostile ones
/// must be defeated before the next rises. When the faction Guardians are done, allies fall back and
/// the Debt rises — faced alone, always full strength. The outcome resolves into a GameState.Ending
/// via <see cref="AuditScorer.DetermineEnding"/>.
///
/// Guardian stats here are PLACEHOLDER (tier-scaled); the wall's height is tuned in the harness pass
/// (TASK-011). The rise order is a tunable constant per the layout↔audit-content co-design.
/// </summary>
public static class WeighingOrchestrator
{
    /// <summary>Faction string for hostile Guardians — not Sasha's side, so hostile to player + allies.</summary>
    public const string WeighingFaction = "weighing";

    /// <summary>
    /// The finalized rise order (south→north up the hall). Tunable default per the co-design with the
    /// audit dialogue: external grievance → internal reckoning, Assembly last (twinned with the Debt).
    /// </summary>
    public static readonly (GuardianId Id, string Anchor)[] RiseOrder =
    {
        (GuardianId.WardenOfWardens, "guardian_warden"),
        (GuardianId.Oathkeeper, "guardian_oathkeeper"),
        (GuardianId.AuditorsOwn, "guardian_auditor"),
        (GuardianId.AssemblyOfTheLost, "guardian_assembly"),
    };

    /// <summary>Begin the Weighing with explicit inputs (test-friendly).</summary>
    public static void Begin(GameState state, AuditScorer.AuditResult audit, bool swapAvailable,
        string orcRepState, int cumulativeDeaths, List<TurnEvent> events)
    {
        var ws = new WeighingState
        {
            Audit = audit,
            SwapAvailable = swapAvailable,
            OrcRepState = orcRepState,
            CumulativeDeaths = cumulativeDeaths,
            Phase = WeighingPhase.Guardians,
            CurrentGuardianIndex = 0,
        };
        state.Weighing = ws;

        // Emit the audit opening — fires before the first Guardian rises (the narration gate).
        EmitDialogue(state, events, "opening", state.WeighingAudit?.GetOpening());

        RiseUntilBlockedOrDone(state, ws, events);
    }

    /// <summary>Begin the Weighing, scoring the audit from the run's persistence (production path).</summary>
    public static void BeginFromPersistence(GameState state, List<TurnEvent> events)
    {
        var persistent = state.PersistentState;
        if (persistent == null) return;
        var audit = AuditScorer.Score(persistent, WeighingConstants.FinalFloorDepth);
        Begin(state, audit,
            swapAvailable: persistent.Hael.BranchOfPassageUnlocked,
            orcRepState: persistent.Factions.GetState(Persistence.Namespaces.FactionsData.OrcFactionId),
            cumulativeDeaths: persistent.UnderWarden.CumulativeDeaths,
            events);
    }

    /// <summary>
    /// The player declines — a chosen non-death loss. Valid at either the audit or the Debt threshold.
    /// </summary>
    public static void Refuse(GameState state, List<TurnEvent> events)
    {
        var ws = state.Weighing;
        if (ws == null || ws.Phase == WeighingPhase.Resolved) return;
        ws.SwapChosen = false;
        Resolve(state, ws, WeighingOutcome.Refused, events);
    }

    /// <summary>
    /// The player offers himself — the Swap, if the catalog gate is open. Resolves immediately
    /// (the Swap is an act of will, not a fight; no combatant is spawned).
    /// </summary>
    public static void ChooseSwap(GameState state, List<TurnEvent> events)
    {
        var ws = state.Weighing;
        if (ws == null || !ws.SwapAvailable || ws.Phase == WeighingPhase.Resolved) return;
        ws.SwapChosen = true;
        Resolve(state, ws, WeighingOutcome.Survived, events);
    }

    /// <summary>
    /// The player chooses to take Anik by force. Spawns the Debt as a combatant and enters combat.
    /// Only valid at the DebtChoiceGate phase.
    /// </summary>
    public static void ChooseForce(GameState state, List<TurnEvent> events)
    {
        var ws = state.Weighing;
        if (ws == null || ws.Phase != WeighingPhase.DebtChoiceGate) return;
        SpawnDebtCombatant(state, ws, events);
    }

    /// <summary>End-of-turn progression. Called by TurnController after all combat is resolved.</summary>
    public static void Advance(GameState state, List<TurnEvent> events)
    {
        var ws = state.Weighing;
        if (ws == null || ws.Phase == WeighingPhase.Resolved) return;

        // Death during the Weighing → the corresponding loss (distinct cause per phase).
        if (!state.PlayerFighter.IsAlive)
        {
            ResolveDeath(state, ws, events);
            return;
        }

        switch (ws.Phase)
        {
            case WeighingPhase.Guardians:
                if (ws.ActiveGuardianId is int gid && IsAlive(state, gid))
                    return; // still fighting the current hostile Guardian
                // Current Guardian resolved (defeated) — advance the cursor and rise the next.
                ws.ActiveGuardianId = null;
                ws.CurrentGuardianIndex++;
                RiseUntilBlockedOrDone(state, ws, events);
                break;

            case WeighingPhase.DebtChoiceGate:
                return; // waiting for the player to call ChooseForce / ChooseSwap / Refuse

            case WeighingPhase.DebtCombat:
                if (ws.DebtId is int did && IsAlive(state, did))
                    return; // still fighting the Debt
                // Debt defeated on the Force branch → Theft (the heavy record was already confirmed
                // before this phase was entered; clean record auto-resolved before combat started).
                Resolve(state, ws, WeighingOutcome.Survived, events);
                break;
        }
    }

    // ── Internals ───────────────────────────────────────────────────────────────

    private static void RiseUntilBlockedOrDone(GameState state, WeighingState ws, List<TurnEvent> events)
    {
        while (ws.CurrentGuardianIndex < RiseOrder.Length)
        {
            var (id, anchor) = RiseOrder[ws.CurrentGuardianIndex];
            var tier = ws.Audit.TierFor(id);
            var pos = state.WeighingArena?.FirstAnchor(anchor) ?? (state.Player.X, state.Player.Y);

            // Emit the beat dialogue before spawning so narration precedes the rise.
            EmitDialogue(state, events,
                $"{GuardianTypeId(id)}.{tier.ToString().ToLowerInvariant()}",
                state.WeighingAudit?.GetGuardianBeat(id, tier));

            var guardian = SpawnGuardian(state, id, pos, tier, events);

            if (tier == GuardianTier.Allied)
            {
                // An ally joins Sasha's side and does not block the gauntlet — rise the next at once.
                ws.AlliedGuardianIds.Add(guardian.Id);
                ws.AlliedGuardianTypes.Add(id);
                ws.CurrentGuardianIndex++;
                continue;
            }

            // A hostile Guardian blocks until defeated.
            ws.ActiveGuardianId = guardian.Id;
            return;
        }

        // All four faction Guardians resolved → allies fall back, then the Debt rises alone.
        FallBackAllies(state, ws, events);
        RaiseDebt(state, ws, events);
    }

    private static void FallBackAllies(GameState state, WeighingState ws, List<TurnEvent> events)
    {
        if (ws.AlliesFellBack) return;
        ws.AlliesFellBack = true;

        // Emit fallback dialogue before removing entities so narration precedes the withdrawal.
        // Framing narration only fires when at least one ally stood with Sasha (the line
        // "those who stood with you step back" reads nonsensically with no one present).
        if (ws.AlliedGuardianTypes.Count > 0 && state.WeighingAudit != null)
        {
            EmitDialogue(state, events, "ally_fallback.framing",
                state.WeighingAudit.GetAllyFallbackFraming());
            foreach (var guardianId in ws.AlliedGuardianTypes)
                EmitDialogue(state, events, $"ally_fallback.{GuardianFallbackKey(guardianId)}",
                    state.WeighingAudit.GetAllyFallback(guardianId));
        }

        // Remove allied entities — they leave by will (the layout lets them follow; they choose not to).
        foreach (var allyId in ws.AlliedGuardianIds)
        {
            var ally = state.Monsters.FirstOrDefault(m => m.Id == allyId);
            if (ally != null)
            {
                state.Map.UnregisterEntity(ally);
                state.Monsters.Remove(ally);
            }
        }
        events.Add(new AlliesFellBackEvent());
    }

    private static string GuardianFallbackKey(GuardianId id) => id switch
    {
        GuardianId.WardenOfWardens => "warden",
        GuardianId.Oathkeeper => "oathkeeper",
        GuardianId.AssemblyOfTheLost => "assembly",
        GuardianId.AuditorsOwn => "auditor",
        _ => "unknown",
    };

    /// <summary>
    /// Called after all faction Guardians resolve. Emits the Debt's terms (dialogue), then either:
    /// - auto-resolves to CleanAudit when record is clean and Swap is unavailable (no real choice), or
    /// - emits the choice gate (Force / Self / Refuse) for the player to decide.
    /// The combatant is not spawned here; it's spawned only if ChooseForce is called.
    /// </summary>
    private static void RaiseDebt(GameState state, WeighingState ws, List<TurnEvent> events)
    {
        // Emit the claim's terms (dialogue key "debt" resolved by the audit registry).
        EmitDialogue(state, events, "debt", state.WeighingAudit?.GetDebt());
        events.Add(new DebtRoseEvent());

        bool heavy = AuditScorer.IsHeavyRecord(ws.Audit, ws.OrcRepState, ws.CumulativeDeaths);

        // Swap always shows the gate — it's a choice, not an outcome.
        // Clean + no swap = the claim is satisfied; auto-resolve with no decision to make.
        if (!ws.SwapAvailable && !heavy)
        {
            Resolve(state, ws, WeighingOutcome.Survived, events);
            return;
        }

        ws.Phase = WeighingPhase.DebtChoiceGate;
        events.Add(new DebtChoiceGateEvent { SwapAvailable = ws.SwapAvailable, IsHeavyRecord = heavy });
    }

    /// <summary>Spawns the Debt as a live combatant (called by ChooseForce).</summary>
    private static void SpawnDebtCombatant(GameState state, WeighingState ws, List<TurnEvent> events)
    {
        var pos = state.WeighingArena?.FirstAnchor("debt") ?? (state.Player.X, state.Player.Y - 1);
        var debt = new Entity(NextId(state), "The Debt", pos.Item1, pos.Item2, blocksMovement: true);
        // Placeholder stats; tuned in TASK-011.
        debt.Add(new Fighter(hp: 150, strength: 16, dexterity: 14, constitution: 16,
            accuracy: 16, evasion: 3, damageMin: 12, damageMax: 18));
        debt.Add(new AiComponent { AiType = "basic", Faction = WeighingFaction });
        debt.Add(new SpeciesTag("the_debt"));
        state.Map.RegisterEntity(debt);
        state.Monsters.Add(debt);
        ws.DebtId = debt.Id;
        ws.Phase = WeighingPhase.DebtCombat;
    }

    private static Entity SpawnGuardian(GameState state, GuardianId id, (int X, int Y) pos,
        GuardianTier tier, List<TurnEvent> events)
    {
        bool allied = tier == GuardianTier.Allied;
        var (hp, dmgMin, dmgMax) = StatsFor(tier);

        var guardian = new Entity(NextId(state), GuardianName(id), pos.X, pos.Y, blocksMovement: true);
        guardian.Add(new Fighter(hp: hp, strength: 14, dexterity: 13, constitution: 14,
            accuracy: 14, evasion: 2, damageMin: dmgMin, damageMax: dmgMax));
        guardian.Add(new AiComponent
        {
            AiType = "basic",
            Faction = allied ? FactionRegistry.PlayerAllyFaction : WeighingFaction,
        });
        guardian.Add(new SpeciesTag(GuardianTypeId(id)));
        state.Map.RegisterEntity(guardian);
        state.Monsters.Add(guardian);

        events.Add(new GuardianRoseEvent { Guardian = id, Tier = tier, GuardianEntityId = guardian.Id });
        return guardian;
    }

    private static void ResolveDeath(GameState state, WeighingState ws, List<TurnEvent> events)
    {
        var outcome = ws.Phase == WeighingPhase.DebtCombat
            ? WeighingOutcome.DiedToDebt
            : WeighingOutcome.DiedToGuardians;
        Resolve(state, ws, outcome, events);
    }

    private static void Resolve(GameState state, WeighingState ws, WeighingOutcome outcome, List<TurnEvent> events)
    {
        ws.Phase = WeighingPhase.Resolved;
        var ending = AuditScorer.DetermineEnding(
            outcome, ws.Audit, ws.SwapChosen, ws.SwapAvailable, ws.OrcRepState, ws.CumulativeDeaths);
        state.Ending = ending;

        // Losses carry a distinct cause-code the memo evaluator / game-over routing reads.
        state.PlayerDeathCause = ending switch
        {
            EndingType.LossGuardians => WeighingConstants.LossGuardiansCause,
            EndingType.LossDebt => WeighingConstants.LossDebtCause,
            EndingType.LossRefused => WeighingConstants.LossRefusedCause,
            _ => state.PlayerDeathCause,
        };

        // Emit the resolution dialogue before WeighingResolvedEvent so it plays before game-over.
        // LossGuardians / LossDebt are death endings without Debt-specific dialogue (covered by
        // the broader ending-texts batch in a later handoff).
        var resolutionPages = state.WeighingAudit?.GetResolution(ending);
        if (resolutionPages != null && resolutionPages.Count > 0)
            EmitDialogue(state, events, $"resolution.{ending.ToString().ToLowerInvariant()}", resolutionPages);

        events.Add(new WeighingResolvedEvent { Ending = ending });
    }

    private static void EmitDialogue(GameState state, List<TurnEvent> events, string key,
        IReadOnlyList<WeighingDialoguePage>? pages)
    {
        if (pages == null || pages.Count == 0) return;
        events.Add(new WeighingDialogueEvent
        {
            ActorId = state.Player.Id,
            DialogueKey = key,
            Pages = pages,
        });
    }

    private static bool IsAlive(GameState state, int entityId)
    {
        var e = state.Monsters.FirstOrDefault(m => m.Id == entityId);
        return e != null && e.Get<Fighter>()?.IsAlive == true;
    }

    private static int NextId(GameState state)
    {
        int max = state.Player.Id;
        foreach (var m in state.Monsters) if (m.Id > max) max = m.Id;
        return max + 1;
    }

    private static (int Hp, int DmgMin, int DmgMax) StatsFor(GuardianTier tier) => tier switch
    {
        GuardianTier.Savage => (120, 10, 16),
        GuardianTier.Neutral => (80, 6, 10),
        GuardianTier.Diminished => (50, 3, 6),
        GuardianTier.Allied => (90, 7, 11),
        _ => (80, 6, 10),
    };

    private static string GuardianName(GuardianId id) => id switch
    {
        GuardianId.WardenOfWardens => "The Warden-of-Wardens",
        GuardianId.Oathkeeper => "The Oathkeeper",
        GuardianId.AssemblyOfTheLost => "The Assembly of the Lost",
        GuardianId.AuditorsOwn => "The Auditor's Own",
        _ => "Guardian",
    };

    private static string GuardianTypeId(GuardianId id) => id switch
    {
        GuardianId.WardenOfWardens => "guardian_warden_of_wardens",
        GuardianId.Oathkeeper => "guardian_oathkeeper",
        GuardianId.AssemblyOfTheLost => "guardian_assembly_of_the_lost",
        GuardianId.AuditorsOwn => "guardian_auditors_own",
        _ => "guardian",
    };
}
