#!/usr/bin/env python3
"""
Hydraulic resistance of a drilled hole -> coefficients for porousBafflePressureAMI.

The loss through a short bore is written as a sum of handbook loss coefficients
(Idelchik), referred to the mean velocity U in the bore:

    dp / rho = zeta * U^2 / 2,     zeta = zeta_entrance + lambda * L/d + zeta_exit

The boundary condition imposes (kinematic pressure, incompressible solvers):

    dp / rho = (D * nu * U + 0.5 * I * U^2) * L

With D = 0 (inertia-dominated flow), matching both gives

    k2 = zeta / 2          (the form  -dp/rho = k2 U^2)
    I  = 2 * k2 / L = zeta / L      [1/m]

Example (values used in the project, 5 mm hole through a 5 mm blade):

    python hole_resistance.py --d 0.005 --L 0.005 --zeta-in 0.15 --lam 0.05 --zeta-out 1.0

    zeta = 0.15 + 0.05 + 1.00 = 1.20  ->  k2 = 0.60  ->  I = 240 1/m
"""
from __future__ import annotations

import argparse


def coefficients(d: float, L: float, zeta_in: float, lam: float, zeta_out: float) -> dict:
    zeta_fric = lam * L / d
    zeta = zeta_in + zeta_fric + zeta_out
    k2 = 0.5 * zeta
    I = 2.0 * k2 / L
    return dict(zeta_in=zeta_in, zeta_fric=zeta_fric, zeta_out=zeta_out, zeta=zeta, k2=k2, I=I)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--d", type=float, required=True, help="hole diameter [m]")
    ap.add_argument("--L", type=float, required=True, help="hole length = blade thickness [m]")
    ap.add_argument("--zeta-in", type=float, default=0.5,
                    help="entrance loss coefficient (0.5 sharp edge; lower for a rounded edge, from Idelchik)")
    ap.add_argument("--lam", type=float, default=0.05, help="Darcy friction factor in the bore [-]")
    ap.add_argument("--zeta-out", type=float, default=1.0,
                    help="exit loss coefficient (1.0 = Borda-Carnot expansion into a large space)")
    ap.add_argument("--U", type=float, nargs="*", default=[],
                    help="optional bore velocities [m/s] to tabulate the kinematic pressure drop")
    a = ap.parse_args()

    c = coefficients(a.d, a.L, a.zeta_in, a.lam, a.zeta_out)
    print(f"zeta_entrance            = {c['zeta_in']:.3f}")
    print(f"zeta_friction = lam*L/d  = {c['zeta_fric']:.3f}")
    print(f"zeta_exit                = {c['zeta_out']:.3f}")
    print(f"zeta (sum)               = {c['zeta']:.3f}")
    print(f"k2 = zeta/2              = {c['k2']:.3f}")
    print(f"I  = 2 k2 / L            = {c['I']:.1f} 1/m   (with D = 0, length = {a.L} m)")
    if a.U:
        print("\n  U [m/s]   dp/rho [m2/s2]   dp [kPa] (water, 998 kg/m3)")
        for U in a.U:
            dpk = c["k2"] * U**2
            print(f"  {U:7.2f}   {dpk:14.3f}   {dpk * 998 / 1000:10.3f}")
    print("\nporousBafflePressureAMI entries:")
    print(f"    D       0;\n    I       {c['I']:.4g};\n    length  {a.L};")


if __name__ == "__main__":
    main()
