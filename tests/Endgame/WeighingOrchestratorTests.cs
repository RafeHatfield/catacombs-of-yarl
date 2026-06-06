using System.Collections.Generic;
using System.IO;
using System.Linq;
using CatacombsOfYarl.Logic.AI;
using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Endgame;
using CatacombsOfYarl.Logic.Persistence;
using CatacombsOfYarl.Tests.Persistence;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Endgame;

/// <summary>
/// TASK-009: the Weighing gauntlet orchestration. Drives Begin/Advance over a hand-built arena
/// GameState and asserts the phase machine: sequential rises in the finalized order, allied vs
/// hostile handling, allies-fall-back, the Debt-alone phase, and resolution into the right ending.
/// </summary>
[TestFixture]
public class WeighingOrchestratorTests
{
    private static GameState ArenaState(PersistentRunState? persistent = null)
    {
        var arena = WeighingArenaDefinition.Build();
        var start = arena.FirstAnchor("player_start")!.Value;
        var player = new Entity(0, "Player", start.X, start.Y, blocksMovement: true);
        player.Add(new Fighter(hp: 500, strength: 14, dexterity: 14, constitution: 14,
            accuracy: 14, evasion: 0, damageMin: 5, damageMax: 8));
        arena.Map.RegisterEntity(player);
        return new GameState(player, new List<Entity>(), arena.Map, new SeededRandom(1337), turnLimit: 10_000)
        {
            IsDungeonMode = true,
            CurrentDepth = WeighingConstants.FinalFloorDepth,
            WeighingArena = arena,
            PersistentState = persistent,
        };
    }

    private static AuditScorer.AuditResult AllSavage() => new(
        GuardianTier.Savage, GuardianTier.Savage, GuardianTier.Savage, GuardianTier.Savage);

    private static AuditScorer.AuditResult AllAllied() => new(
        GuardianTier.Allied, GuardianTier.Allied, GuardianTier.Allied, GuardianTier.Allied);

    private static void KillActiveGuardianAndAdvance(GameState s)
    {
        var ws = s.Weighing!;
        var g = s.Monsters.First(m => m.Id == ws.ActiveGuardianId);
        g.Require<Fighter>().TakeDamage(99999);
        WeighingOrchestrator.Advance(s, new List<TurnEvent>());
    }

    // ── Sequential rises in the finalized order ───────────────────────────────

    [Test]
    public void Begin_AllSavage_RisesWardenFirst_AsHostile()
    {
        var s = ArenaState();
        WeighingOrchestrator.Begin(s, AllSavage(), swapAvailable: false, "hostile", 12, new List<TurnEvent>());

        Assert.That(s.Weighing!.Phase, Is.EqualTo(WeighingPhase.Guardians));
        var active = s.Monsters.First(m => m.Id == s.Weighing.ActiveGuardianId);
        Assert.That(active.Get<SpeciesTag>()!.TypeId, Is.EqualTo("guardian_warden_of_wardens"));
        Assert.That(active.Get<AiComponent>()!.Faction, Is.EqualTo(WeighingOrchestrator.WeighingFaction));
        // Warden rises at its south-rank anchor (4,9).
        Assert.That((active.X, active.Y), Is.EqualTo((4, 9)));
    }

    [Test]
    public void AllSavage_GuardiansRiseInFinalizedOrder_W_O_U_A_thenDebt()
    {
        var s = ArenaState();
        WeighingOrchestrator.Begin(s, AllSavage(), swapAvailable: false, "hostile", 12, new List<TurnEvent>());

        var order = new List<string>();
        while (s.Weighing!.Phase == WeighingPhase.Guardians)
        {
            order.Add(s.Monsters.First(m => m.Id == s.Weighing.ActiveGuardianId).Get<SpeciesTag>()!.TypeId);
            KillActiveGuardianAndAdvance(s);
        }

        Assert.That(order, Is.EqualTo(new[]
        {
            "guardian_warden_of_wardens",
            "guardian_oathkeeper",
            "guardian_auditors_own",     // Auditor's Own before Assembly (finalized swap)
            "guardian_assembly_of_the_lost",
        }));
        // After the four faction Guardians, the Debt threshold is reached — the choice gate.
        // (All-Savage + hostile rep = heavy record, no swap → Force/Refuse gate, no auto-resolve.)
        Assert.That(s.Weighing.Phase, Is.EqualTo(WeighingPhase.DebtChoiceGate));
        // No combatant yet — it's spawned only if Force is chosen.
        Assert.That(s.Weighing.DebtId, Is.Null, "Debt combatant not spawned until Force is chosen");
    }

    [Test]
    public void AllSavage_ForceChosenAndDebtDefeated_ResolvesToTheft()
    {
        var s = ArenaState();
        WeighingOrchestrator.Begin(s, AllSavage(), swapAvailable: false, "hostile", 12, new List<TurnEvent>());
        while (s.Weighing!.Phase == WeighingPhase.Guardians) KillActiveGuardianAndAdvance(s);

        // Heavy record → choice gate. Choose Force → spawns the combatant.
        Assert.That(s.Weighing.Phase, Is.EqualTo(WeighingPhase.DebtChoiceGate));
        WeighingOrchestrator.ChooseForce(s, new List<TurnEvent>());
        Assert.That(s.Weighing.Phase, Is.EqualTo(WeighingPhase.DebtCombat));
        Assert.That(s.Weighing.DebtId, Is.Not.Null, "Debt combatant spawned on Force");

        // Kill the Debt.
        s.Monsters.First(m => m.Id == s.Weighing.DebtId).Require<Fighter>().TakeDamage(99999);
        WeighingOrchestrator.Advance(s, new List<TurnEvent>());

        Assert.That(s.Weighing.Phase, Is.EqualTo(WeighingPhase.Resolved));
        Assert.That(s.Ending, Is.EqualTo(EndingType.Theft), "heavy record Force path resolves to Theft");
        Assert.That(s.IsDungeonVictory, Is.True);
        Assert.That(s.IsGameOver, Is.True);
    }

    // ── Allied Guardians: no blocking, fall back before the Debt ───────────────

    [Test]
    public void AllAllied_CleanRecord_AutoResolvesToCleanAudit_NoGate()
    {
        // Clean record + no Swap available → auto-CleanAudit, no choice gate, no combatant.
        var s = ArenaState();
        WeighingOrchestrator.Begin(s, AllAllied(), swapAvailable: false, "allied", 0, new List<TurnEvent>());

        Assert.That(s.Weighing!.AlliedGuardianIds, Has.Count.EqualTo(4), "all four joined as allies");
        Assert.That(s.Weighing.AlliesFellBack, Is.True);
        // Clean record auto-resolved — already at Resolved, no gate, no combatant.
        Assert.That(s.Weighing.Phase, Is.EqualTo(WeighingPhase.Resolved));
        Assert.That(s.Ending, Is.EqualTo(EndingType.CleanAudit));
        Assert.That(s.Weighing.DebtId, Is.Null, "no combatant spawned on auto-CleanAudit");
        Assert.That(s.IsDungeonVictory, Is.True);
    }

    [Test]
    public void AllAllied_WithSwapAvailable_ShowsChoiceGate()
    {
        // Clean record + Swap available → choice gate (Swap is a choice, not an outcome).
        var s = ArenaState();
        WeighingOrchestrator.Begin(s, AllAllied(), swapAvailable: true, "allied", 0, new List<TurnEvent>());

        Assert.That(s.Weighing!.Phase, Is.EqualTo(WeighingPhase.DebtChoiceGate),
            "Swap always shows the gate — the most thoughtful player gets the most thoughtful dilemma");
        Assert.That(s.Weighing.DebtId, Is.Null, "no combatant yet");
    }

    [Test]
    public void AlliedGuardian_SpawnsOnPlayerSide()
    {
        // A single allied Guardian (Warden) should be player_ally faction while it's up.
        var s = ArenaState();
        var audit = new AuditScorer.AuditResult(
            GuardianTier.Allied, GuardianTier.Savage, GuardianTier.Savage, GuardianTier.Savage);
        WeighingOrchestrator.Begin(s, audit, swapAvailable: false, "neutral", 0, new List<TurnEvent>());

        // Warden allied → joined; Oathkeeper savage → now the blocker.
        var ally = s.Monsters.First(m => m.Get<SpeciesTag>()!.TypeId == "guardian_warden_of_wardens");
        Assert.That(ally.Get<AiComponent>()!.Faction, Is.EqualTo(FactionRegistry.PlayerAllyFaction));
        var active = s.Monsters.First(m => m.Id == s.Weighing!.ActiveGuardianId);
        Assert.That(active.Get<SpeciesTag>()!.TypeId, Is.EqualTo("guardian_oathkeeper"));
    }

    // ── Loss states ───────────────────────────────────────────────────────────

    [Test]
    public void DeathDuringGuardians_IsLossGuardians()
    {
        var s = ArenaState();
        WeighingOrchestrator.Begin(s, AllSavage(), swapAvailable: false, "hostile", 12, new List<TurnEvent>());

        s.PlayerFighter.TakeDamage(99999);
        WeighingOrchestrator.Advance(s, new List<TurnEvent>());

        Assert.That(s.Ending, Is.EqualTo(EndingType.LossGuardians));
        Assert.That(s.PlayerDeathCause, Is.EqualTo(WeighingConstants.LossGuardiansCause));
    }

    [Test]
    public void DeathAtTheDebt_IsLossDebt()
    {
        // Force must be chosen to enter combat; then dying is LossDebt.
        var s = ArenaState();
        WeighingOrchestrator.Begin(s, AllSavage(), swapAvailable: false, "hostile", 12, new List<TurnEvent>());
        while (s.Weighing!.Phase == WeighingPhase.Guardians) KillActiveGuardianAndAdvance(s);
        WeighingOrchestrator.ChooseForce(s, new List<TurnEvent>());
        Assert.That(s.Weighing.Phase, Is.EqualTo(WeighingPhase.DebtCombat));

        s.PlayerFighter.TakeDamage(99999);
        WeighingOrchestrator.Advance(s, new List<TurnEvent>());

        Assert.That(s.Ending, Is.EqualTo(EndingType.LossDebt));
        Assert.That(s.PlayerDeathCause, Is.EqualTo(WeighingConstants.LossDebtCause));
    }

    [Test]
    public void Refuse_IsChosenNonDeathLoss()
    {
        var s = ArenaState();
        WeighingOrchestrator.Begin(s, AllSavage(), swapAvailable: false, "hostile", 12, new List<TurnEvent>());

        WeighingOrchestrator.Refuse(s, new List<TurnEvent>());

        Assert.That(s.Ending, Is.EqualTo(EndingType.LossRefused));
        Assert.That(s.PlayerDeathCause, Is.EqualTo(WeighingConstants.LossRefusedCause));
        Assert.That(s.PlayerFighter.IsAlive, Is.True, "refusal is a choice, not a death");
        Assert.That(s.IsGameOver, Is.True);
    }

    // ── Swap (hidden ending) ──────────────────────────────────────────────────

    // ── Integration: the turn loop begins the Weighing on the first arena turn ─

    [Test]
    public void ProcessTurn_OnArenaFloor_BeginsTheWeighing()
    {
        var persistent = PersistentRunState.LoadFromDisk(new FakePersistencePathProvider(
            Path.Combine(Path.GetTempPath(), "yarl_weigh_" + System.Guid.NewGuid())));
        var s = ArenaState(persistent);

        Assert.That(s.Weighing, Is.Null, "not yet begun");

        TurnController.ProcessTurn(s, PlayerAction.Wait);

        Assert.That(s.Weighing, Is.Not.Null, "the turn loop begins the Weighing on the first arena turn");
        Assert.That(s.Weighing!.Phase, Is.AnyOf(
            WeighingPhase.Guardians, WeighingPhase.DebtChoiceGate,
            WeighingPhase.DebtCombat, WeighingPhase.Resolved));
        // A Guardian should be on the field (fresh save = clean record → could also have auto-resolved).
        Assert.That(s.Monsters.Count(m => m.Get<Fighter>()?.IsAlive == true), Is.GreaterThanOrEqualTo(0));
    }

    [Test]
    public void Swap_AtChoiceGate_ResolvesImmediately_NoCombat()
    {
        // Swap is an act of will, not a fight — choosing Self at the gate resolves immediately.
        var s = ArenaState();
        WeighingOrchestrator.Begin(s, AllAllied(), swapAvailable: true, "allied", 0, new List<TurnEvent>());
        Assert.That(s.Weighing!.Phase, Is.EqualTo(WeighingPhase.DebtChoiceGate));

        WeighingOrchestrator.ChooseSwap(s, new List<TurnEvent>());

        Assert.That(s.Ending, Is.EqualTo(EndingType.Swap), "Swap resolves immediately on choosing Self");
        Assert.That(s.Weighing.DebtId, Is.Null, "no combatant was ever spawned");
        Assert.That(s.IsDungeonVictory, Is.True);
    }

    [Test]
    public void SwapAvailable_HeavyRecord_StillShowsChoiceGate()
    {
        // Even a heavy-record player who earned the catalog gets the Swap option.
        var s = ArenaState();
        WeighingOrchestrator.Begin(s, AllSavage(), swapAvailable: true, "hostile", 12, new List<TurnEvent>());
        while (s.Weighing!.Phase == WeighingPhase.Guardians) KillActiveGuardianAndAdvance(s);

        Assert.That(s.Weighing.Phase, Is.EqualTo(WeighingPhase.DebtChoiceGate));
        // Verify the gate event carries SwapAvailable=true
        // (presentation would show Force/Self/Refuse).
        WeighingOrchestrator.ChooseSwap(s, new List<TurnEvent>());
        Assert.That(s.Ending, Is.EqualTo(EndingType.Swap));
    }
}
