# Bot Persona Survivability Report

**Generated:** 2026-05-22 14:21:16 UTC
**Matrix:** full (15 scenarios)
**Runs per cell:** 50
**Base seed:** 1337

Seeding note: Personas share the same encounter layout (same seed → same spawn positions,
same initial inventory, same map). Combat RNG streams diverge from turn 1 onward as
different personas take different actions and consume different RNG draws.

## Death Rate

| Scenario                                 |     balanced |     cautious |   aggressive |       greedy |  speedrunner |
|------------------------------------------|--------------|--------------|--------------|--------------|--------------|
| depth3_orc_brutal                        |         12 % |          0 % |         18 % |         12 % |          0 % |
| depth3_orc_brutal_keen                   |         12 % |          0 % |         14 % |         12 % |          0 % |
| depth3_orc_brutal_vicious                |          8 % |          0 % |         14 % |          8 % |          0 % |
| depth3_orc_brutal_fine                   |          0 % |          0 % |          4 % |          0 % |          0 % |
| depth3_orc_brutal_masterwork             |          0 % |          0 % |          0 % |          0 % |          0 % |
| depth5_zombie                            |         32 % |          0 % |         32 % |         32 % |          0 % |
| depth5_zombie_keen                       |         94 % |          0 % |        100 % |         94 % |          0 % |
| depth5_zombie_vicious                    |         16 % |          0 % |         18 % |         16 % |          0 % |
| depth5_zombie_fine                       |         14 % |          0 % |         14 % |         14 % |          0 % |
| depth5_zombie_masterwork                 |          2 % |          0 % |          4 % |          2 % |          0 % |
| depth2_orc_baseline                      |          0 % |          0 % |          2 % |          0 % |          0 % |
| depth2_orc_baseline_keen                 |          0 % |          0 % |          2 % |          0 % |          0 % |
| depth2_orc_baseline_vicious              |          0 % |          0 % |          0 % |          0 % |          0 % |
| depth2_orc_baseline_fine                 |          0 % |          0 % |          0 % |          0 % |          0 % |
| depth2_orc_baseline_masterwork           |          0 % |          0 % |          0 % |          0 % |          0 % |

## Average Turns to Clear

| Scenario                                 |     balanced |     cautious |   aggressive |       greedy |  speedrunner |
|------------------------------------------|--------------|--------------|--------------|--------------|--------------|
| depth3_orc_brutal                        |         40.5 |        110.0 |         40.4 |         40.5 |        110.0 |
| depth3_orc_brutal_keen                   |         40.5 |        110.0 |         39.0 |         40.5 |        110.0 |
| depth3_orc_brutal_vicious                |         35.6 |        110.0 |         34.9 |         35.6 |        110.0 |
| depth3_orc_brutal_fine                   |         30.6 |        110.0 |         30.2 |         30.6 |        110.0 |
| depth3_orc_brutal_masterwork             |         28.4 |        110.0 |         28.4 |         28.4 |        110.0 |
| depth5_zombie                            |         55.6 |        150.0 |         56.9 |         55.6 |        150.0 |
| depth5_zombie_keen                       |         61.6 |        150.0 |         56.4 |         61.6 |        150.0 |
| depth5_zombie_vicious                    |         49.8 |        150.0 |         48.8 |         49.8 |        150.0 |
| depth5_zombie_fine                       |         47.7 |        150.0 |         47.0 |         47.7 |        150.0 |
| depth5_zombie_masterwork                 |         43.4 |        150.0 |         43.1 |         43.4 |        150.0 |
| depth2_orc_baseline                      |         25.5 |        100.0 |         25.0 |         25.5 |        100.0 |
| depth2_orc_baseline_keen                 |         26.9 |        100.0 |         26.5 |         26.9 |        100.0 |
| depth2_orc_baseline_vicious              |         21.4 |        100.0 |         21.4 |         21.4 |        100.0 |
| depth2_orc_baseline_fine                 |         19.1 |        100.0 |         19.1 |         19.1 |        100.0 |
| depth2_orc_baseline_masterwork           |         18.4 |        100.0 |         18.3 |         18.4 |        100.0 |

## H_PM (Hits to Kill Monster)

| Scenario                                 |     balanced |     cautious |   aggressive |       greedy |  speedrunner |
|------------------------------------------|--------------|--------------|--------------|--------------|--------------|
| depth3_orc_brutal                        |          6.7 |          0.0 |          6.7 |          6.7 |          0.0 |
| depth3_orc_brutal_keen                   |          6.3 |          0.0 |          6.3 |          6.3 |          0.0 |
| depth3_orc_brutal_vicious                |          4.6 |          0.0 |          4.6 |          4.6 |          0.0 |
| depth3_orc_brutal_fine                   |          4.7 |          0.0 |          4.7 |          4.7 |          0.0 |
| depth3_orc_brutal_masterwork             |          4.1 |          0.0 |          4.1 |          4.1 |          0.0 |
| depth5_zombie                            |          4.5 |          0.0 |          4.5 |          4.5 |          0.0 |
| depth5_zombie_keen                       |         11.3 |          0.0 |         11.3 |         11.3 |          0.0 |
| depth5_zombie_vicious                    |          3.8 |          0.0 |          3.8 |          3.8 |          0.0 |
| depth5_zombie_fine                       |          3.8 |          0.0 |          3.9 |          3.8 |          0.0 |
| depth5_zombie_masterwork                 |          3.3 |          0.0 |          3.3 |          3.3 |          0.0 |
| depth2_orc_baseline                      |          6.1 |          0.0 |          6.1 |          6.1 |          0.0 |
| depth2_orc_baseline_keen                 |          5.9 |          0.0 |          5.8 |          5.9 |          0.0 |
| depth2_orc_baseline_vicious              |          4.1 |          0.0 |          4.2 |          4.1 |          0.0 |
| depth2_orc_baseline_fine                 |          4.4 |          0.0 |          4.4 |          4.4 |          0.0 |
| depth2_orc_baseline_masterwork           |          3.6 |          0.0 |          3.6 |          3.6 |          0.0 |

## H_MP (Monster Hits to Kill Player)

| Scenario                                 |     balanced |     cautious |   aggressive |       greedy |  speedrunner |
|------------------------------------------|--------------|--------------|--------------|--------------|--------------|
| depth3_orc_brutal                        |          8.5 |          0.0 |          8.5 |          8.5 |          0.0 |
| depth3_orc_brutal_keen                   |          8.7 |          0.0 |          8.5 |          8.7 |          0.0 |
| depth3_orc_brutal_vicious                |          8.4 |          0.0 |          8.4 |          8.4 |          0.0 |
| depth3_orc_brutal_fine                   |          8.8 |          0.0 |          8.8 |          8.8 |          0.0 |
| depth3_orc_brutal_masterwork             |          8.9 |          0.0 |          9.0 |          8.9 |          0.0 |
| depth5_zombie                            |          8.2 |          0.0 |          8.2 |          8.2 |          0.0 |
| depth5_zombie_keen                       |          8.4 |          0.0 |          8.4 |          8.4 |          0.0 |
| depth5_zombie_vicious                    |          8.3 |          0.0 |          8.3 |          8.3 |          0.0 |
| depth5_zombie_fine                       |          8.5 |          0.0 |          8.5 |          8.5 |          0.0 |
| depth5_zombie_masterwork                 |          8.7 |          0.0 |          8.7 |          8.7 |          0.0 |
| depth2_orc_baseline                      |          8.4 |          0.0 |          8.4 |          8.4 |          0.0 |
| depth2_orc_baseline_keen                 |          8.8 |          0.0 |          8.8 |          8.8 |          0.0 |
| depth2_orc_baseline_vicious              |          8.9 |          0.0 |          8.9 |          8.9 |          0.0 |
| depth2_orc_baseline_fine                 |          8.7 |          0.0 |          8.8 |          8.7 |          0.0 |
| depth2_orc_baseline_masterwork           |          8.8 |          0.0 |          8.8 |          8.8 |          0.0 |

## Observations

- Cautious persona death rate <= Aggressive on 15/15 scenarios
- Hardest scenario for balanced persona: depth5_zombie_keen (94 % death rate)
- Easiest scenario for balanced persona: depth2_orc_baseline_masterwork (0 % death rate)
