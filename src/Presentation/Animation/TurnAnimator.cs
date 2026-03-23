using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Presentation.Entities;
using CatacombsOfYarl.Presentation.Map;
using Godot;

namespace CatacombsOfYarl.Presentation.Animation;

/// <summary>
/// Plays turn events as sequential animations.
/// Each event animates in order: move tweens, attack bumps, damage numbers, death fades.
/// Fires AnimationComplete when the full sequence is done.
///
/// Sprite positions are driven by tweens — the EntitySpriteManager snaps to
/// final positions after animation completes.
/// </summary>
public sealed class TurnAnimator
{
    private const float MoveDuration = 0.15f;
    private const float AttackBumpDuration = 0.08f;
    private const float AttackReturnDuration = 0.08f;
    private const float DeathFadeDuration = 0.3f;
    private const float DamageNumberDuration = 0.6f;

    private readonly Node _root;
    private readonly EntitySpriteManager _entitySprites;
    private bool _playing;

    public event Action? AnimationComplete;

    public TurnAnimator(Node root, EntitySpriteManager entitySprites)
    {
        _root = root;
        _entitySprites = entitySprites;
    }

    /// <summary>
    /// Play all events from a turn result in sequence.
    /// If no animatable events, completes immediately.
    /// </summary>
    public void PlayTurn(TurnResult result)
    {
        if (_playing) return;

        var animatableEvents = result.Events
            .Where(e => e is MoveEvent or AttackEvent or HealEvent or DeathEvent)
            .ToList();

        if (animatableEvents.Count == 0)
        {
            // Nothing to animate — fire immediately via deferred call
            _root.CallDeferred(Node.MethodName.SetProcessMode, (int)Node.ProcessModeEnum.Inherit);
            AnimationComplete?.Invoke();
            return;
        }

        _playing = true;

        // Build a tween chain for all events
        var tween = _root.CreateTween();
        tween.SetParallel(false); // Sequential

        foreach (var evt in animatableEvents)
        {
            AppendEventAnimation(tween, evt);
        }

        tween.TweenCallback(Callable.From(OnTweenComplete));
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
                // Brief pause to let heal land — actual visual is a number popup
                tween.TweenInterval(0.1f);
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

        var targetPos = IsometricMapper.GridToScreenCenter(move.ToX, move.ToY);
        tween.TweenProperty(sprite, "position", targetPos, MoveDuration)
             .SetEase(Tween.EaseType.Out)
             .SetTrans(Tween.TransitionType.Quad);
    }

    private void AnimateAttack(Tween tween, AttackEvent attack)
    {
        var sprite = _entitySprites.GetSprite(attack.ActorId);
        var targetSprite = _entitySprites.GetSprite(attack.TargetId);
        if (sprite == null) return;

        if (!attack.Hit)
        {
            // Miss — brief shake
            var origPos = sprite.Position;
            tween.TweenProperty(sprite, "position", origPos + new Vector2(4, -2), AttackBumpDuration * 0.5f);
            tween.TweenProperty(sprite, "position", origPos, AttackBumpDuration * 0.5f);
            return;
        }

        // Bump toward target
        Vector2 bumpDir = Vector2.Zero;
        if (targetSprite != null)
        {
            bumpDir = (targetSprite.Position - sprite.Position).Normalized() * 8f;
        }

        var startPos = sprite.Position;
        var bumpPos = startPos + bumpDir;

        tween.TweenProperty(sprite, "position", bumpPos, AttackBumpDuration)
             .SetEase(Tween.EaseType.Out);
        tween.TweenProperty(sprite, "position", startPos, AttackReturnDuration)
             .SetEase(Tween.EaseType.In);

        // Flash target red on hit
        if (targetSprite != null && attack.Hit)
        {
            tween.Parallel().TweenProperty(targetSprite, "modulate", new Color(2, 0.3f, 0.3f), AttackBumpDuration);
            tween.Parallel().TweenProperty(targetSprite, "modulate", Colors.White, AttackReturnDuration);
        }
    }

    private void AnimateDeath(Tween tween, DeathEvent death)
    {
        var sprite = _entitySprites.GetSprite(death.ActorId);
        if (sprite == null) return;

        tween.TweenProperty(sprite, "modulate:a", 0.0f, DeathFadeDuration)
             .SetEase(Tween.EaseType.In);
    }

    private void OnTweenComplete()
    {
        _playing = false;
        AnimationComplete?.Invoke();
    }
}
