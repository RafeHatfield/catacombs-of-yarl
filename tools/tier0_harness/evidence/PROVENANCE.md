# Evidence provenance

`ART-LOOP-PROCESS-v0.md` §2.3: *every evidence file records the commit hash of the code that
produced it. A hash mismatch at a ruling invalidates the evidence and forces a re-run.*

## Produced by `fee6cac`

| File | Notes |
|---|---|
| `CONTROLS-transcript.txt` | All five positive controls. Records its own commit at the foot. |
| `corridor_lit.png` | `sha256 3695d88c…` |
| `light_on.png` / `light_off.png` | Control 2 pair. `light_off` is the rig at energy 0. |
| `junction_lit_green.png` | Control 5, at the working radius 5.5. |
| `probe/probe_arms_side_by_side.png` | §6.4 arms under one identical rig. |

**The headline capture's hash is unchanged from the previous commit,** and that is expected
rather than suspicious: neither fix in this round alters rendering. One removes loss conditions
from the game state, the other adds a guard that reads pixels without writing any. A capture that
*had* changed would have meant one of them touched the art path.

## NOT reproduced this round — `DEVICE-boot-diag.log`

**This file was produced by `1b1866b`, not by `fee6cac`.** Under §2.3 that is a hash mismatch, so
**it is not evidence for this round's changes** and must not be read as such. It remains valid
for what it originally showed: that the review corridor loads and renders from the packed `.pck`
on the reference device.

It could not be regenerated because the device refused the launch:

```
NSLocalizedFailureReason = The request was denied by service delegate (SBMainWorkspace)
  for reason: Locked ("Unable to launch com.rafehatfield.catacombsofyarl.tier0 because the
  device was not, or could not be, unlocked").
```

The build carrying both fixes **is installed** on the device (`YARL Tier0`,
`com.rafehatfield.catacombsofyarl.tier0`, verified by control 4). What is outstanding is only the
post-fix boot log. With the phone unlocked:

```bash
xcrun devicectl device process launch --device "Jiminy Cricket" \
  com.rafehatfield.catacombsofyarl.tier0
xcrun devicectl device copy from --device "Jiminy Cricket" \
  --domain-type appDataContainer --domain-identifier com.rafehatfield.catacombsofyarl.tier0 \
  --source Documents/diag.log --destination DEVICE-boot-diag.log
```

The line that closes it out is:

```
[Tier0] losable-state check: turn_limit=2147483647 monsters=0 ending=None alive=True game_over=False
```

Confirmed on desktop at this commit; **unconfirmed on device.**
