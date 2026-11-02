# Limitations and when to resolve the holes instead

[← Overview](../README.md) · [Method](method.md) · [Hydraulic resistance](hydraulic-resistance.md) · [Workflow](workflow.md) · [Results](results.md)

The Virtual Hole Method is a **design-screening tool**. It ranks hole layouts and predicts the direction and approximate size of their effect at no extra cost per run. It does not replace a geometry-resolved simulation for the final design.

| Limitation | Effect | Mitigation |
|---|---|---|
| Hole outline is the set of blade faces whose centres lie inside the circle | Open area differs from πd²/4 on a coarse blade mesh; for a given Δp, flow through the hole scales with the area | Check the area with `surfaceFieldValue areaSum`. To keep the loss per volume flow, scale `I` by (A<sub>faces</sub>/A<sub>hole</sub>)², or refine the blade-surface mesh |
| Loss coefficients from handbook data for a bore between quiescent spaces | Cross-flow over both openings and rotation are not in ζ | Treat k₂ as a best estimate; for a final design, check one hole with a resolved simulation |
| Jet represented on the blade-surface mesh, not resolved through the bore | Jet shape, direction and mixing near the outlet are only as good as the passage mesh at the blade surface | Use a resolved hole when the near-outlet jet structure itself matters |
| Single-phase ζ in two-phase flow | Gas passing through the hole gets the same resistance as water | Acceptable while the holes mainly carry water, which is their purpose |
| Validation: three flow rates single-phase, nominal flow two-phase (4 %, 5 % gas); impeller head compared with pump head | Absolute head levels not validated; magnitude of the head effect underpredicted in single-phase and overpredicted in two-phase | Use for trends and ranking of variants |
| Single blade passage | Interaction with the casing, and blade-to-blade differences, not included | Run the chosen variant in a full-pump model if required |

A geometry-resolved hole simulation on an unstructured mesh was run in the project for comparison. It captured the same trend with only slightly better accuracy, at the cost of a new CAD model, a new mesh and a much larger computational effort per variant.
