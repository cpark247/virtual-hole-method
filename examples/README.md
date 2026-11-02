# Demonstration case (planned)

A generic case without project geometry, so the method can be tried in minutes:

**Channel with an inclined plate** (the test case of [results, steps 1–2](../docs/results.md#step-1-2d-test-coupling-with-and-without-the-jump)). A periodic channel driven by a constant pressure gradient, with a "hole" made of two `cyclicACMI` patches on either side of the plate.

| Variant | What it shows |
|---|---|
| `periodicOnly/` | Hole patches without a jump: the through-flow keeps increasing |
| `virtualHole/` | Same with `porousBafflePressureAMI`: steady through-flow and a pressure drop across the hole |
| `nonConforming3D/` | 3D, with different meshes on the two sides of the plate |

Each variant will be a complete OpenFOAM-9 case (`0.orig/`, `constant/`, `system/`, `Allrun`).
