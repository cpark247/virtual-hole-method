# Workflow: from a solid blade to virtual holes

[← Overview](../README.md) · [Method](method.md) · [Hydraulic resistance](hydraulic-resistance.md) · [Results](results.md) · [Limitations](limitations.md)

This is the workflow used in the project: a single blade passage of the impeller in an MRF frame, about 1 M cells, k-ω SST. Single-phase runs used `pimpleFoam`; two-phase runs used a `multiphaseEulerFoam`-based solver. It needs only standard OpenFOAM-9 utilities and the boundary condition from this repository.

> The dictionary excerpts below are **templates** with generic names and placeholder coordinates. Check the keywords against the annotated dictionaries shipped with your OpenFOAM version before use.

## Overview

```
solid-blade case (converged)          ── unchanged geometry and mesh
   │
   ├─ 1  define holes: centre on each blade side + diameter
   ├─ 2  topoSet        → one face set per hole and blade side (face centres inside the hole circle)
   ├─ 3  createBaffles  → each pair of face sets becomes a cyclicACMI pair (+ non-overlap wall patches)
   ├─ 4  fields         → porousBafflePressureAMI on p / p_rgh, cyclicACMI on all other fields
   ├─ 5  coefficients   → I from tools/hole_resistance.py
   └─ 6  run            → initialise from the solid-blade solution
```

A new variant (hole position, diameter or number) repeats steps 1–3 on a clean copy of the original mesh. That takes minutes. No CAD change, no remeshing, and no local refinement are needed. Local refinement around the holes was tried in an early test and turned out to be unnecessary.

## 1. Define the holes

For each hole you need its centre on the pressure side, its centre on the suction side and its diameter. In the project: five holes at mid-span, d = 5 mm, through a 5 mm thick blade.

## 2. Select the faces (`topoSet`)

Select the blade-wall faces whose centres lie inside a short cylinder of the hole diameter, placed on one side of the blade. Restrict the selection to the blade patch so that no internal faces are picked up. Do this once per hole and side.

```c++
// system/topoSetDict  (template, one hole, pressure side)
actions
(
    {
        name    hole1_ps;
        type    faceSet;
        action  new;
        source  cylinderToFace;
        p1      (x1 y1 z1);      // axis start, just outside the pressure-side surface
        p2      (x2 y2 z2);      // axis end, just inside the blade
        radius  0.0025;          // d/2
    }
    {
        name    hole1_ps;
        type    faceSet;
        action  subset;          // keep only faces on the blade wall
        source  patchToFace;
        patch   blade;
    }
    // ... same for hole1_ss on the suction side, and for holes 2-5
);
```

Then convert each face set to a face zone for `createBaffles`, either with `setsToZones` or with a `faceZoneSet` action in the same `topoSetDict`.

## 3. Create the `cyclicACMI` pairs (`createBaffles`)

For each hole, the pressure-side and suction-side zones become the two halves of a `cyclicACMI` pair:

| Setting | Value |
|---|---|
| Patch type | `cyclicACMI` |
| Neighbour | the other side of the same hole (`hole1_ps` ↔ `hole1_ss`) |
| Non-overlap patch | a `wall` patch per side (e.g. `hole1_ps_blockage`), required by `cyclicACMI`. It takes the part of each face not covered by the other side, so it must carry the **same boundary conditions as the blade wall** |

Afterwards, `constant/polyMesh/boundary` should list, per hole, two `cyclicACMI` patches and two wall patches. Run `checkMesh` and look at the AMI weight summary written at solver start-up. The sum of weights tells you how much of each face is coupled.

### Check the hole area

The selected faces approximate the circle. Their total area should be close to πd²/4, because the loss coefficients refer to the velocity in the hole ([hydraulic-resistance.md](hydraulic-resistance.md#4-things-to-watch)). A function object prints it:

```c++
// system/controlDict, functions
hole1Area
{
    type            surfaceFieldValue;
    libs            ("libfieldFunctionObjects.so");
    regionType      patch;
    name            hole1_ps;
    operation       areaSum;
    fields          ();
    writeControl    onEnd;
}
```

## 4. Boundary conditions

Template assignment; the essential part is the jump on the pressure field that the solver solves for.

| Field | Hole patches (`hole*_ps`, `hole*_ss`) | Non-overlap patches |
|---|---|---|
| `p` (single-phase) / `p_rgh` (multiphase) | `porousBafflePressureAMI` with `patchType cyclicACMI` | as blade wall |
| `p` (multiphase) | `cyclicACMI` | as blade wall |
| `U`, `U.*` | `cyclicACMI` | as blade wall (no slip) |
| `k`, `omega`, `nut`, `alpha.*`, size-group fields | `cyclicACMI` | as blade wall (wall functions) |

```c++
// 0/p_rgh (multiphase) - both patches of each hole pair
hole1_ps
{
    type            porousBafflePressureAMI;
    patchType       cyclicACMI;
    jump            uniform 0;
    D               0;
    I               240;          // tools/hole_resistance.py
    length          0.005;
    phi             phi.water;
    rho             rho.water;
    phase           water;
    value           uniform 0;
}
```

For single-phase `pimpleFoam` / `simpleFoam`, drop the three phase entries.

## 5. Coefficients

```bash
python3 tools/hole_resistance.py --d <d> --L <blade thickness> --zeta-in <Idelchik> --lam <λ> --zeta-out 1.0
```

The loss coefficients and their sources are in [hydraulic-resistance.md](hydraulic-resistance.md).

## 6. Run

- **Initialise from the converged solid-blade solution.** Only the boundary has changed, so the existing fields are a valid starting point.
- For the two-phase cases in the project, the run was started from a solid-blade solution with a fully developed air pocket. This shows directly whether the holes can remove an existing accumulation ([results, step 6](results.md#step-6-two-phase-flushing-and-head-recovery)).
- Useful monitors:
  - flow through each hole: `surfaceFieldValue`, `operation sum`, field `phi` on each hole patch;
  - pressure difference across each hole;
  - head, from the area-averaged total or static pressure at the inlet and outlet of the passage.

## Changing a variant

| Change | What to redo |
|---|---|
| Hole position or number | Steps 1–3 on a clean copy of the mesh; copy the fields (or rerun the field set-up script) |
| Hole diameter | Steps 1–3 and 5 (ζ<sub>friction</sub> depends on L/d) |
| Blade thickness | Step 5 (`length` and `I`) |
| Edge rounding | Step 5 (ζ<sub>entrance</sub>) |

The case set-up is easy to script, so a parametric study over hole layouts can run unattended.
