using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Presentation.Entities;
using CatacombsOfYarl.Presentation.Map;
using CatacombsOfYarl.Presentation.UI;
using Godot;

namespace CatacombsOfYarl.Presentation.Animation;

/// <summary>
/// Plays turn events as sequential animations.
/// Each event animates in order: move tweens, attack bumps, damage numbers, death fades.
/// Fires AnimationComplete when the full sequence is done.
///
/// Completion detection uses polling (CheckComplete called from GameController._Process)
/// instead of TweenCallback + Callable.From(delegate). The delegate pattern creates a
/// GCHandle on a non-GodotObject instance method that Godot 4.6 C# doesn't reliably
/// release — causing catastrophic memory growth during combat.
/// </summary>
public sealed class TurnAnimator
{
    /// <summary>
    /// Scales all animation durations. 1.0 = normal, 0.25 = fast (auto-explore).
    /// Clamped to 0.05–1.0 so animations never disappear entirely or run slower than normal.
    /// </summary>
    public float SpeedMultiplier
    {
        get => _speedMultiplier;
        set => _speedMultiplier = Math.Clamp(value, 0.05f, 1.0f);
    }
    private float _speedMultiplier = 1.0f;

    // Base durations — scaled by SpeedMultiplier at animation time.
    private float MoveDur => 0.15f * _speedMultiplier;
    private float AttackBumpDur => 0.08f * _speedMultiplier;
    private float AttackReturnDur => 0.08f * _speedMultiplier;
    private float DeathFadeDur => 0.3f * _speedMultiplier;

    private readonly Node _root;
    private readonly EntitySpriteManager _entitySprites;
    private bool _playing;
    // Stored so we can Kill() the previous tween before creating the next one.
    private Tween? _activeTween;
    // Tracks whether any TweenProperty calls were actually made during PlayTurn.
    // If all sprites are null, no tweeners are appended and the tween would hang forever.
    private bool _tweenHasSteps;

    public event Action? AnimationComplete;

    public TurnAnimator(Node root, EntitySpriteManager entitySprites)
    {
        _root = root;
        _entitySprites = entitySprites;
    }

    /// <summary>
    /// Poll from GameController._Process every frame. When the active tween has
    /// finished (IsRunning() returns false), fire AnimationComplete.
    /// No Callable.From, no GCHandle, no delegate — just a bool check per frame.
    /// </summary>
    public void CheckComplete()
    {
        if (!_playing || _activeTween == null) return;
        if (_activeTween.IsRunning()) return;

        Diag.Log("TurnAnimator: tween finished, firing AnimationComplete");
        _activeTween.Kill();
        TweenTracker.Killed();
        _activeTween = null;
        _playing = false;
        AnimationComplete?.Invoke();
    }

    /// <summary>
    /// Play all events from a turn result in sequence.
    /// If no animatable events, completes immediately without allocating a Tween.
    /// </summary>
    public void PlayTurn(TurnResult result)
    {
        if (_playing) return;

        // First pass: check whether there is anything to animate.
        bool hasAnimatable = false;
        foreach (var evt in result.Events)
        {
            if (evt is MoveEvent or AttackEvent or HealEvent or DeathEvent)
            {
                hasAnimatable = true;
                break;
            }
        }

        if (!hasAnimatable)
        {
            AnimationComplete?.Invoke();
            return;
        }

        _playing = true;

        Diag.Log($"TurnAnimator.PlayTurn: creating tween for {result.Events.Count} events");
        if (_activeTween != null) { _activeTween.Kill(); TweenTracker.Killed(); }
        var tween = _root.CreateTween();
        _activeTween = tween;
        TweenTracker.Created();
        tween.SetParallel(false);

        _tweenHasSteps = false;
        foreach (var evt in result.Events)
        {
            if (evt is MoveEvent or AttackEvent or HealEvent or DeathEvent)
                AppendEventAnimation(tween, evt);
        }

        // If all sprites were null (e.g., during floor transitions), no TweenProperty
        // calls were made and the tween has zero tweeners. An empty tween never finishes
        // and Godot logs "started with no Tweeners". Kill it and complete immediately.
        if (!_tweenHasSteps)
        {
            Diag.Log("TurnAnimator: tween has no tweeners, completing immediately");
            tween.Kill();
            TweenTracker.Killed();
            _activeTween = null;
            _playing = false;
            AnimationComplete?.Invoke();
            return;
        }

        // No TweenCallback — completion detected by CheckComplete() polling.
    }

    private void AppendEventAnimation(Tween tween, TurnEvent evt)
    {
        switch (evt)
        {
            case MoveEvent move:
                AnimateMove(tween, move);
                break;

            case AttackEvent attack:
                AnimateAttack(tween, attack);
                break;

            case HealEvent:
                tween.TweenInterval(0.1f * _speedMultiplier);
                _tweenHasSteps = true;
                break;

            case DeathEvent death:
                AnimateDeath(tween, death);
                break;
        }
    }

    private void AnimateMove(Tween tween, MoveEvent move)
    {
        var sprite = _entitySprites.GetSprite(move.ActorId);
        if (sprite == null) return;
        _tweenHasSteps = true;

        var targetPos = IsometricMapper.GridToScreenCenter(move.ToX, move.ToY);
        tween.TweenProperty(sprite, "position", targetPos, MoveDur)
             .SetEase(Tween.EaseType.Out)
             .SetTrans(Tween.TransitionType.Quad);
    }

    private void AnimateAttack(Tween tween, AttackEvent attack)
    {
        var sprite = _entitySprites.GetSprite(attack.ActorId);
        var targetSprite = _entitySprites.GetSprite(attack.TargetId);
        if (sprite == null) return;
        _tweenHasSteps = true;

        if (!attack.Hit)
        {
            // Miss — brief shake
            var origPos = sprite.Position;
            tween.TweenProperty(sprite, "position", origPos + new Vector2(4, -2), AttackBumpDur * 0.5f);
            tween.TweenProperty(sprite, "position", origPos, AttackBumpDur * 0.5f);
            return;
        }

        // Bump toward target
        Vector2 bumpDir = Vector2.Zero;
        if (targetSprite != null)
            bumpDir = (targetSprite.Position - sprite.Position).Normalized() * 8f;

        var startPos = sprite.Position;
        var bumpPos = startPos + bumpDir;

        // Step 1: bump forward
        tween.TweenProperty(sprite, "position", bumpPos, AttackBumpDur)
             .SetEase(Tween.EaseType.Out);

        // Step 2: return to start + flash target red (in parallel)
        tween.TweenProperty(sprite, "position", startPos, AttackReturnDur)
             .SetEase(Tween.EaseType.In);

        if (targetSprite != null)
        {
            // Flash red runs parallel with the return step above.
            tween.Parallel().TweenProperty(targetSprite, "modulate", new Color(2, 0.3f, 0.3f), AttackReturnDur);
            // Step 3: reset modulate back to white (sequential, after the return).
            tween.TweenProperty(targetSprite, "modulate", Colors.White, AttackReturnDur * 0.5f);
        }
    }

    private void AnimateDeath(Tween tween, DeathEvent death)
    {
        var sprite = _entitySprites.GetSprite(death.ActorId);
        if (sprite == null) return;
        _tweenHasSteps = true;

        tween.TweenProperty(sprite, "modulate:a", 0.0f, DeathFadeDur)
             .SetEase(Tween.EaseType.In);
    }
}
