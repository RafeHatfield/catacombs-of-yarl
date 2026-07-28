using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;

namespace CatacombsOfYarl.Logic.Voice;

/// <summary>
/// Presentation-agnostic voice delivery scheduler (docs/systems/voice_delivery.md §Scheduler). Given
/// the trigger families raised on a turn, it picks at most one line to deliver under shuffle-bag,
/// one-shot, priority, cooldown, and silence rules, and returns it for the ribbon (5b) to render.
///
/// TWO RECONSTRUCT-class dependencies, caller-provided and never serialized (same pattern as
/// GameState.BoonTable): <see cref="VoiceLineRegistry"/> (the line pools) and
/// <see cref="VoiceTierMetadata"/> (per-family tiers). The mutable run state — bags, fired-set,
/// floor-silence flag, cooldown counter, ribbon history, and the dedicated voice Rng — is the
/// SERIALIZE-class state the mid-run save persists.
///
/// THE ONE RULE (invariant, verified by the non-consumption tests): every non-render path returns null
/// WITHOUT mutating any state. Consumption — the single bag draw, one-shot burn, cooldown stamp, and
/// history push — happens only on the delivery path, after every gate has passed.
///
/// STOP-FLAG (5a → Voice thread): <see cref="VoiceTierMetadata"/> has no authored content yet. The
/// Voice thread must author the tier YAML (fields: ambient_cutoff_tier; per family key/tier and the
/// optional once_per_run + cooldown_exempt flags; family order = tie-break). Until then the scheduler
/// is exercised by fixtures. Line-pool authoring (VoiceLineRegistry) is the Voice thread's existing job.
///
/// GAMEPLAY ISOLATION: the scheduler takes no GameState and never touches the gameplay Rng — all
/// randomness is its own <see cref="_rng"/>. Gameplay hash sequences are identical whether or not the
/// scheduler runs (proven by the isolation soak).
/// </summary>
public sealed class VoiceScheduler
{
    /// <summary>Mixed into the run seed so the voice stream is independent of the gameplay stream.</summary>
    public const int RngSeedSalt = unchecked((int)0x5643_4F49);   // "VCOI"

    /// <summary>Minimum turns between delivered lines (cooldown-exempt families bypass this).</summary>
    public const int CooldownTurns = 3;

    /// <summary>Ribbon history depth retained in the run save.</summary>
    public const int HistoryCap = 20;

    private const int NoDeliveryYet = int.MinValue;

    private readonly VoiceLineRegistry _registry;   // RECONSTRUCT — caller-provided, never serialized
    private readonly VoiceTierMetadata _meta;       // RECONSTRUCT — caller-provided, never serialized
    private readonly SeededRandom _rng;             // SERIALIZE via (Seed, CallCount)
    private readonly Dictionary<string, List<int>> _bags;   // SERIALIZE — remaining draw order per family
    private readonly HashSet<string> _fired;        // SERIALIZE — one-shot families already fired this run
    private readonly List<VoiceHistoryEntry> _history;      // SERIALIZE — last HistoryCap delivered lines
    private bool _currentFloorSilenced;             // SERIALIZE — post-Marya / shut-up mute of this floor
    private int _lastDeliveredTurn;                 // SERIALIZE — cooldown counter (turn of last delivery)

    /// <summary>Fresh scheduler for a new run. The voice Rng seed is runSeed XOR the salt.</summary>
    public VoiceScheduler(VoiceLineRegistry registry, VoiceTierMetadata meta, int runSeed)
        : this(registry, meta, new SeededRandom(runSeed ^ RngSeedSalt),
               new Dictionary<string, List<int>>(StringComparer.Ordinal),
               new HashSet<string>(StringComparer.Ordinal),
               currentFloorSilenced: false, lastDeliveredTurn: NoDeliveryYet,
               history: new List<VoiceHistoryEntry>())
    {
    }

    private VoiceScheduler(VoiceLineRegistry registry, VoiceTierMetadata meta, SeededRandom rng,
        Dictionary<string, List<int>> bags, HashSet<string> fired, bool currentFloorSilenced,
        int lastDeliveredTurn, List<VoiceHistoryEntry> history)
    {
        _registry = registry;
        _meta = meta;
        _rng = rng;
        _bags = bags;
        _fired = fired;
        _currentFloorSilenced = currentFloorSilenced;
        _lastDeliveredTurn = lastDeliveredTurn;
        _history = history;
    }

    /// <summary>
    /// Rebuild a scheduler at a saved position (construct-then-restore; registry + meta are RECONSTRUCT,
    /// caller-provided). Mirrors <see cref="SeededRandom.Restore"/> for the voice Rng.
    /// </summary>
    public static VoiceScheduler Restore(VoiceLineRegistry registry, VoiceTierMetadata meta,
        int rngSeed, long rngCallCount, IEnumerable<(string Family, int[] Remaining)> bags,
        IEnumerable<string> fired, bool currentFloorSilenced, int lastDeliveredTurn,
        IEnumerable<VoiceHistoryEntry> history)
    {
        var bagMap = new Dictionary<string, List<int>>(StringComparer.Ordinal);
        foreach (var (family, remaining) in bags)
            if (remaining.Length > 0) bagMap[family] = remaining.ToList();

        return new VoiceScheduler(registry, meta, SeededRandom.Restore(rngSeed, rngCallCount),
            bagMap, new HashSet<string>(fired, StringComparer.Ordinal),
            currentFloorSilenced, lastDeliveredTurn, history.ToList());
    }

    // ── delivery ─────────────────────────────────────────────────────────────────

    /// <summary>
    /// Consider the trigger families raised this turn and deliver at most one line. Returns null (and
    /// consumes NOTHING) whenever no line renders. All probes are supplied by the caller (5b): the mode
    /// setting, the tier of the line currently on the ribbon (for the strictly-higher supersede rule),
    /// and whether the ribbon surface is available.
    /// </summary>
    /// <param name="triggerFamilies">Family keys raised this turn (duplicates and unknowns are ignored).</param>
    /// <param name="mode">Verbose / Tactical / Silent (device setting, passed in — never stored).</param>
    /// <param name="currentTurn">The run turn count, for cooldown + history.</param>
    /// <param name="currentRibbonTier">Tier of the line currently displayed, or null if the ribbon is empty.</param>
    /// <param name="surfaceAvailable">False when 5b cannot render right now (probe).</param>
    public VoiceDelivery? TryDeliver(IReadOnlyList<string> triggerFamilies, VoiceMode mode,
        int currentTurn, int? currentRibbonTier = null, bool surfaceAvailable = true)
    {
        // Global silence gates — nothing renders, nothing consumes.
        if (mode == VoiceMode.Silent) return null;
        if (_currentFloorSilenced) return null;
        if (!surfaceAvailable) return null;

        // Eligible candidates: known family, non-empty pool, mode-visible, not an already-fired one-shot.
        VoiceFamilyMeta? best = null;
        foreach (var family in triggerFamilies)
        {
            var meta = _meta.Get(family);
            if (meta == null) continue;                                        // unknown family — not schedulable
            if (mode == VoiceMode.Tactical && meta.Tier <= _meta.AmbientCutoffTier) continue;  // ambient, hidden
            if (meta.OncePerRun && _fired.Contains(meta.Key)) continue;        // one-shot already spent
            var pool = _registry.GetPool(family);
            if (pool == null || pool.Count == 0) continue;                     // no lines to draw

            // Highest tier wins; ties broken by family declaration order (lower Order wins).
            if (best == null || meta.Tier > best.Tier || (meta.Tier == best.Tier && meta.Order < best.Order))
                best = meta;
        }
        if (best == null) return null;                                         // priority loss / nothing eligible

        // Cooldown — the winner must clear it unless its family is exempt. (long math avoids sentinel overflow.)
        if (!best.CooldownExempt && (long)currentTurn - _lastDeliveredTurn < CooldownTurns) return null;

        // Ribbon supersede — a new line only lands if strictly higher than what is already showing.
        if (currentRibbonTier is int shown && best.Tier <= shown) return null;

        // ── every gate passed: CONSUME exactly once ──
        string line = DrawFromBag(best.Key);
        if (best.OncePerRun) _fired.Add(best.Key);
        _lastDeliveredTurn = currentTurn;
        _history.Add(new VoiceHistoryEntry(best.Key, line, currentTurn));
        if (_history.Count > HistoryCap) _history.RemoveRange(0, _history.Count - HistoryCap);

        return new VoiceDelivery(best.Key, line, best.Tier);
    }

    /// <summary>Mute the current floor (post-Marya flag, or the shut-up action). Cleared on floor entry.</summary>
    public void SilenceCurrentFloor() => _currentFloorSilenced = true;

    /// <summary>Clear the floor-silence flag on entering a new floor (the game is a one-way descent).</summary>
    public void OnFloorEntered() => _currentFloorSilenced = false;

    // ── shuffle bag ──────────────────────────────────────────────────────────────

    private string DrawFromBag(string family)
    {
        var pool = _registry.GetPool(family)!;     // guaranteed non-empty by the eligibility filter
        if (!_bags.TryGetValue(family, out var bag) || bag.Count == 0)
        {
            bag = ShuffledIndices(pool.Count);     // reshuffle only on exhaustion
            _bags[family] = bag;
        }
        int idx = bag[0];
        bag.RemoveAt(0);
        return pool[idx];
    }

    /// <summary>Fisher–Yates permutation of [0, n) drawing ONLY from the dedicated voice Rng.</summary>
    private List<int> ShuffledIndices(int n)
    {
        var order = new List<int>(n);
        for (int i = 0; i < n; i++) order.Add(i);
        for (int i = n - 1; i > 0; i--)
        {
            int j = _rng.Next(i + 1);
            (order[i], order[j]) = (order[j], order[i]);
        }
        return order;
    }

    // ── serialization accessors (read-only snapshots for MidRunSerializer) ─────────

    public int RngSeed => _rng.Seed;
    public long RngCallCount => _rng.CallCount;
    public bool CurrentFloorSilenced => _currentFloorSilenced;
    public int LastDeliveredTurn => _lastDeliveredTurn;

    /// <summary>Non-empty bags in canonical (ordinal-key) order; each bag's remaining draw order intact.</summary>
    public IEnumerable<(string Family, int[] Remaining)> BagsSnapshot() =>
        _bags.Where(kv => kv.Value.Count > 0)
             .OrderBy(kv => kv.Key, StringComparer.Ordinal)
             .Select(kv => (kv.Key, kv.Value.ToArray()));

    /// <summary>Fired one-shot family keys in canonical order.</summary>
    public IEnumerable<string> FiredSnapshot() => _fired.OrderBy(k => k, StringComparer.Ordinal);

    /// <summary>Ribbon history in chronological (delivery) order — order is significant.</summary>
    public IReadOnlyList<VoiceHistoryEntry> HistorySnapshot() => _history;
}

/// <summary>A line the scheduler chose to deliver this turn: its family, resolved text, and tier.</summary>
public sealed record VoiceDelivery(string Family, string Line, int Tier);

/// <summary>One entry of the run-scoped ribbon history (delivered line text + the turn it fired).</summary>
public sealed record VoiceHistoryEntry(string Family, string Line, int Turn);
