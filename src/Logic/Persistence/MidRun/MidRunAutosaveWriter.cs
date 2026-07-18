namespace CatacombsOfYarl.Logic.Persistence.MidRun;

/// <summary>
/// Off-critical-path autosave for the mid-run file (M1.4 §File + write discipline). The caller
/// snapshots the GameState on the game thread (SaveMidRun — deterministic, state-safe) and hands the
/// resulting immutable DTO here; the JSON serialization and the atomic .tmp→Move write happen on a
/// background worker.
///
/// LATEST-WINS, NEVER REORDERED: only the most recent snapshot is pending at any time (a newer one
/// supersedes an unwritten older one), and all writes are serialized through a single gate, so the
/// file on disk always ends on the most recent turn — no stale write can land after a newer one.
/// </summary>
public sealed class MidRunAutosaveWriter : IDisposable
{
    private readonly string _path;
    private readonly object _stateLock = new();   // guards _pending / _worker
    private readonly object _writeGate = new();    // serializes actual file writes (no torn .tmp)
    private MidRunSaveDto? _pending;
    private Task? _worker;
    private volatile bool _disposed;

    public MidRunAutosaveWriter(string path) => _path = path;

    /// <summary>Queue a snapshot for background write. Returns immediately.</summary>
    public void RequestWrite(MidRunSaveDto dto)
    {
        lock (_stateLock)
        {
            if (_disposed) return;
            _pending = dto;                                   // supersede any unwritten snapshot
            if (_worker == null || _worker.IsCompleted)
                _worker = Task.Run(DrainLoop);
        }
    }

    private void DrainLoop()
    {
        while (true)
        {
            MidRunSaveDto? dto;
            lock (_stateLock)
            {
                dto = _pending;
                _pending = null;
                if (dto == null) return;
            }
            WriteAtomic(dto);
        }
    }

    /// <summary>Write a snapshot synchronously NOW (floor descent, app pause), superseding anything
    /// pending. Blocks until the file is written — the caller wants it durable before proceeding.</summary>
    public void FlushSync(MidRunSaveDto dto)
    {
        lock (_stateLock) { _pending = null; }               // this write is the latest
        WriteAtomic(dto);
    }

    /// <summary>Wait for any in-flight background write to finish (e.g. before app exit).</summary>
    public void WaitForIdle()
    {
        Task? w;
        lock (_stateLock) { w = _worker; }
        try { w?.Wait(); } catch { /* best-effort */ }
    }

    private void WriteAtomic(MidRunSaveDto dto)
    {
        lock (_writeGate)                                     // only one writer touches the file at a time
        {
            try { MidRunFile.SaveMidRunToFile(dto, _path); }
            catch { /* autosave is best-effort; a failed write must never crash a turn */ }
        }
    }

    public void Dispose()
    {
        _disposed = true;
        WaitForIdle();
    }
}
