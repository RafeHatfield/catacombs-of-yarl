# Round 24 — polyline-sampled stations, and a question that can be answered without looking

**One valid station, one void. Device build installed, not verified.** And a bug found on the way
in that would have made the second station impossible and the device walk wrong.

---

## 1. The law, implemented

**Stations are sampled from the polyline.** Two written, both with the player standing *on* the
route and the route ahead inside the lit pool:

| station | player | the route in frame |
|---|---|---|
| `route_onroute` | (6,8), room A | behind to (5,5); ahead through (7,8) (7,9) to the chokepoint mouth (8,10), with room floor on both flanks |
| `route_onroute_choke` | (8,11), chokepoint | a straight three-tile run ahead to (8,14), the way back north behind |

The two prior mis-stationed rounds are recorded in the spec headers rather than left to memory:
round 18's chokepoint is one tile wide and has **no flank**, so it could not answer a contrast
question however the floor was drawn; round 23's approach put the route's lit run off to one side
while the wall-announced corridor sat at the frame's bottom edge in the dark.

**The plant run asserts its own completion count.** An early exit is red, never quiet — and the
assertion caught its own author on the first run, reporting *"14 of 13"* because the expected
count was written `2 + 2 + len(PLANTS)` when the channel plant is one, not two.

## 2. A bug the stations found: a creature in a corridor deletes the level's routes

Station two came back **`lines=0`, `spine:0/routes:0`** — an entirely blank route map on the same
map that gives `lines=1` one tile away.

**`Pathfinder.AStar` paths with occupancy on**, and `TrafficField` was using it to derive routes.
The chokepoint is one tile wide; the player standing in it severs the graph, so the level's whole
route model vanishes. In gameplay the player is *always* on the route, so this is not an edge case
of the harness — it is the ordinary condition.

A route is a property of the level's shape and its graph, not of who is standing where this frame.
`AStar` gained `terrainOnly`, `TrafficField`'s six route derivations use it, and the route came
back. (`DijkstraMap` never had the bug — it was already terrain-only.) Fast suite 2510/0.

## 3. Round 24, station one: VALID, negative — and again off the route

Plant caught. The answer:

> *"The route goes south. **The ground told me nothing** — I read it entirely off the walls… Same
> bond, same slab proportion, same joint width, same blank faces, same absence of wear. The
> corridor is identifiable only because the placeholder blocks close in on it."*

Per the banked law, the cited ground was mapped before anything was concluded. The seat named
**x 505–565, y 275–420** as "the corridor". The route at that height is at **x 215–279**:

| tile | screen box | median lum |
|---|---|---:|
| (6,8) *(the player)* | x 215–279, y 507–571 | 40.3 |
| **(7,8)** | x 279–343, y 507–571 | **75.2** |
| **(7,9)** | x 279–343, y 571–635 | **75.7** |
| **(8,10)** | x 343–407, y 635–699 | **71.1** |
| **(8,11)** | x 343–407, y 699–763 | **56.6** |

Four lit route tiles were in frame. **The seat described ground with route strength zero — at a
station sampled from the polyline.** That is the second valid round in a row where the finding had
to be checked before it could be read, and this time the station cannot be blamed.

## 4. Round 25, station two: VOID — and the withholding held

The plant seat missed. `r25_F1_transcript.WITHHELD.txt` carries its banner, **its findings have not
been read, and nothing from it appears anywhere in this document.** That is the round-19 rule
working the first time it was tested for real.

One thing from the round *is* readable, because it is the control seat's own report about the
build it was shown rather than a finding about the candidate: it claimed the surface *"clips to
flat 255-yellow under the lamp."* Measured on all three builds:

| capture | floor pixels | at 255 | above 250 |
|---|---:|---:|---:|
| `r24_onroute` | 282,624 | **0.00%** | 0.00% |
| `r24_onroute_choke` | 282,624 | **0.00%** | 0.00% |
| `r24_plant_choke` | 282,624 | **0.00%** | 0.00% |

Nothing clips anywhere, including on the build that seat was actually looking at. Percept recorded,
explanation measured and false — the third time this session that has been the outcome.

## 5. Device build: installed, **not verified**

Installed to the SE at the `route_onroute` station with the ashlar theme and manifest.

**The first attempt was wrong and the device check caught it**: it went out with the tier-0 stub
theme under the tier-1 family, which `verify_on_device.sh` reports as *"theme and floor family
disagree"* — a build laying one family's tiles under another family's theme looks entirely
plausible in a screenshot, which is exactly why that check exists. Rebuilt with
`TIER0_THEME=…/tier1_ashlar/tile_themes_tier1_ashlar.yaml` and reinstalled.

Verification could not run: the handset disconnected on the first attempt and was locked on the
second. **The state is installed-not-verified**, and the gate is Rafe's, on the route.

## 6. The finding that matters: the question can be answered without looking

Two valid rounds, two stations, and in both the seat answered *"the ground told me nothing"* about
ground the route does not touch. The standing question —

> *you are standing on the route — can you see where it goes, to the edge of your light?*

— asks a seat to evaluate ground it must first **locate**, and a seat that locates it by the walls
can return a confident negative without ever looking at the floor in question. Every round since 18
has needed a post-hoc measurement to discover which ground was actually judged, and that
measurement is the tell.

**The protocol, not the floor, is what should change.** The question should be a *discrimination*
test rather than a self-report: show the capture, ask the seat to mark the ground that is most
walked **from the floor alone**, and score its answer against the route it could not see. A seat
that cannot find the route then produces a wrong mark rather than an unfalsifiable "nothing", and a
floor that works produces a right one. It cannot be dodged by mislocation, and it does not depend
on the seat believing it is standing anywhere.

This is offered as a finding, not acted on: the round was bounded to a seat re-run, and no lever
was retuned.

## Evidence

| | |
|---|---|
| round 24, station one, VALID | `evidence/seats/SEATS-r24.json` |
| round 25, station two, VOID | `evidence/seats/SEATS-r25.json`, `r25_F1_transcript.WITHHELD.txt` |
| the two station specs | `assets/tier0_harness/scenes/tier1_floor_route_*.json` |
| device boot log | `evidence/DEVICE-tier1-boot.log` |

Fourteen of fourteen plants firing and the run asserting it; shipped path identical on four arms;
`paint_check=96/OK`, `lines=1`, `mouths=13`, `polished=74`, `UNADDRESSABLE 0`; fast suite 2510/0.
