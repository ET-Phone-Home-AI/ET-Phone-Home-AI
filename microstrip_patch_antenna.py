"""
Microstrip-Fed Rectangular Microstrip Patch Antenna Design
Operating Frequency: 2.4 GHz (Wi-Fi / Bluetooth band)

Design equations follow Bahl & Trivedi (1977) and Pozar's Microwave Engineering.

References:
  - Pozar, D.M., "Microwave Engineering", 4th ed.
  - Bahl, I.J. & Trivedi, D.K., "A Designer's Guide to Microstrip Line", Microwaves, 1977.
"""

import math


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
C = 3e8  # speed of light in vacuum (m/s)


# ─────────────────────────────────────────────────────────────────────────────
# Helper: Microstrip characteristic impedance & effective εr
# ─────────────────────────────────────────────────────────────────────────────
def microstrip_z0_ereff(w, h, er):
    """
    Returns (Z0, ereff) for a microstrip line.

    Parameters
    ----------
    w  : float – strip width (m)
    h  : float – substrate height (m)
    er : float – relative permittivity of substrate
    """
    u = w / h
    if u <= 1:
        F = 1 / math.sqrt(1 + 12 / u) + 0.041 * (1 - u) ** 2
        ereff = (er + 1) / 2 + (er - 1) / 2 * F
        Z0 = (60 / math.sqrt(ereff)) * math.log(8 / u + u / 4)
    else:
        F = 1 / math.sqrt(1 + 12 / u)
        ereff = (er + 1) / 2 + (er - 1) / 2 * F
        Z0 = (120 * math.pi) / (math.sqrt(ereff) * (u + 1.393 + 0.667 * math.log(u + 1.444)))
    return Z0, ereff


def feed_line_width(Z0_target, h, er, tol=1e-6):
    """
    Calculates microstrip width for a desired characteristic impedance Z0_target.
    Uses closed-form synthesis (Wheeler, 1977).

    Parameters
    ----------
    Z0_target : float – desired impedance (Ω)
    h         : float – substrate height (m)
    er        : float – substrate relative permittivity
    tol       : float – convergence tolerance

    Returns
    -------
    w : float – strip width (m)
    """
    A = (Z0_target / 60) * math.sqrt((er + 1) / 2) + ((er - 1) / (er + 1)) * (0.23 + 0.11 / er)
    B = (377 * math.pi) / (2 * Z0_target * math.sqrt(er))

    w_A = h * (8 * math.exp(A)) / (math.exp(2 * A) - 2)  # w/h < 2
    w_B = h * (2 / math.pi) * (
        B - 1 - math.log(2 * B - 1) + (er - 1) / (2 * er) * (math.log(B - 1) + 0.39 - 0.61 / er)
    )  # w/h > 2

    # pick the physically consistent solution
    if w_A / h < 2:
        return w_A
    return w_B


# ─────────────────────────────────────────────────────────────────────────────
# Core patch design
# ─────────────────────────────────────────────────────────────────────────────
def design_patch_antenna(
    freq_hz=2.4e9,
    er=4.4,
    h=1.6e-3,
    feed_impedance=50.0,
    substrate_name="FR-4",
):
    """
    Full design of a rectangular microstrip patch antenna with inset microstrip feed.

    Parameters
    ----------
    freq_hz         : float – operating frequency (Hz)
    er              : float – substrate relative permittivity (εr)
    h               : float – substrate thickness (m)
    feed_impedance  : float – feed-line characteristic impedance (Ω)  [typically 50 Ω]
    substrate_name  : str   – label for the substrate

    Returns
    -------
    dict with all computed dimensions and electrical parameters.
    """
    lam0 = C / freq_hz  # free-space wavelength

    # ── 1. Patch Width ────────────────────────────────────────────────────────
    W = (C / (2 * freq_hz)) * math.sqrt(2 / (er + 1))

    # ── 2. Effective dielectric constant ─────────────────────────────────────
    ereff = (er + 1) / 2 + (er - 1) / 2 * (1 + 12 * h / W) ** (-0.5)

    # ── 3. Length extension ΔL (fringing) ────────────────────────────────────
    dL = (
        0.412
        * h
        * ((ereff + 0.3) * (W / h + 0.264))
        / ((ereff - 0.258) * (W / h + 0.8))
    )

    # ── 4. Effective & actual patch length ───────────────────────────────────
    L_eff = C / (2 * freq_hz * math.sqrt(ereff))
    L = L_eff - 2 * dL

    # ── 5. Input impedance at patch edge (radiation resistance Rin) ──────────
    # Transmission-line model (two-slot model)
    G1 = _slot_conductance(W, h, lam0)
    G12 = _mutual_conductance(W, L, lam0)
    Rin_edge = 1 / (2 * (G1 + G12))

    # ── 6. Inset feed notch depth (y0) for 50 Ω matching ─────────────────────
    # Rin(y0) = Rin_edge * cos²(π y0 / L)  =>  y0 = L/π * arccos(√(Z0/Rin))
    if feed_impedance <= Rin_edge:
        y0 = (L / math.pi) * math.acos(math.sqrt(feed_impedance / Rin_edge))
    else:
        y0 = 0.0  # edge-fed (no inset needed)

    # ── 7. 50-Ω feed line width ───────────────────────────────────────────────
    W_feed = feed_line_width(feed_impedance, h, er)
    Z0_feed, ereff_feed = microstrip_z0_ereff(W_feed, h, er)

    # ── 8. Quarter-wave transformer length (λ/4 at design freq) ──────────────
    lam_g_feed = C / (freq_hz * math.sqrt(ereff_feed))
    L_quarter = lam_g_feed / 4

    # ── 9. Ground plane recommended size ─────────────────────────────────────
    Lg = L + 6 * h
    Wg = W + 6 * h

    # ── 10. Notch width (slot) around inset feed ──────────────────────────────
    # Rule of thumb: notch gap ≈ W_feed / 2  (to prevent short-circuit)
    notch_gap = W_feed / 2

    results = dict(
        substrate=substrate_name,
        er=er,
        h_mm=h * 1e3,
        freq_GHz=freq_hz / 1e9,
        lam0_mm=lam0 * 1e3,
        # Patch
        W_mm=W * 1e3,
        L_mm=L * 1e3,
        dL_mm=dL * 1e3,
        L_eff_mm=L_eff * 1e3,
        ereff=ereff,
        # Input impedance
        G1_mS=G1 * 1e3,
        G12_mS=G12 * 1e3,
        Rin_edge_ohm=Rin_edge,
        # Inset feed
        y0_mm=y0 * 1e3,
        notch_gap_mm=notch_gap * 1e3,
        # Feed line
        W_feed_mm=W_feed * 1e3,
        Z0_feed_ohm=Z0_feed,
        ereff_feed=ereff_feed,
        L_quarter_mm=L_quarter * 1e3,
        # Ground plane
        Lg_mm=Lg * 1e3,
        Wg_mm=Wg * 1e3,
    )
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Conductance calculations (transmission-line model)
# ─────────────────────────────────────────────────────────────────────────────
def _slot_conductance(W, h, lam0):
    """
    Radiation conductance of a single radiating slot (W >> h assumption).
    G1 = W²/(90 λ0²)  for  W/λ0 < 1/10  (simple form)
    Full form uses numerical integration of the radiation integral.
    """
    k0W = 2 * math.pi * W / lam0
    # Numerical integral: G1 = (1/120π²) ∫₀^π [sin(k0W/2 cosθ)/cosθ]² sin³θ dθ
    N = 1000
    G1 = 0.0
    for i in range(N):
        theta = math.pi * (i + 0.5) / N
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        if abs(cos_t) < 1e-12:
            sinc_val = 1.0
        else:
            arg = k0W / 2 * cos_t
            sinc_val = math.sin(arg) / arg
        G1 += sinc_val ** 2 * sin_t ** 3 * (math.pi / N)
    G1 /= 120 * math.pi ** 2
    return G1


def _mutual_conductance(W, L, lam0):
    """
    Mutual conductance G12 between the two radiating slots of the patch.
    Numerical integration of the mutual radiation integral.
    """
    k0 = 2 * math.pi / lam0
    k0L = k0 * L
    N = 1000
    G12 = 0.0
    for i in range(N):
        theta = math.pi * (i + 0.5) / N
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        if abs(cos_t) < 1e-12:
            sinc_val = 1.0
        else:
            arg = k0 * W / 2 * cos_t
            sinc_val = math.sin(arg) / arg
        J0_val = _j0(k0L * sin_t)
        G12 += sinc_val ** 2 * J0_val * sin_t ** 3 * (math.pi / N)
    G12 /= 120 * math.pi ** 2
    return G12


def _j0(x):
    """Bessel function J0(x) via series expansion."""
    result = 0.0
    term = 1.0
    for m in range(1, 50):
        result += term
        term *= -(x / 2) ** 2 / (m * m)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Pretty-print results
# ─────────────────────────────────────────────────────────────────────────────
def print_results(r):
    sep = "─" * 55
    print(f"\n{'═'*55}")
    print(f"  MICROSTRIP PATCH ANTENNA DESIGN SUMMARY")
    print(f"{'═'*55}")
    print(f"  Substrate  : {r['substrate']}")
    print(f"  εr         : {r['er']}")
    print(f"  h          : {r['h_mm']:.3f} mm")
    print(f"  Frequency  : {r['freq_GHz']:.3f} GHz")
    print(f"  λ₀         : {r['lam0_mm']:.3f} mm")
    print(sep)
    print("  PATCH DIMENSIONS")
    print(sep)
    print(f"  Width  W   : {r['W_mm']:.4f} mm")
    print(f"  Length L   : {r['L_mm']:.4f} mm")
    print(f"  ΔL (fringe): {r['dL_mm']:.4f} mm")
    print(f"  L_eff      : {r['L_eff_mm']:.4f} mm")
    print(f"  εr_eff     : {r['ereff']:.4f}")
    print(sep)
    print("  INPUT IMPEDANCE (Transmission-Line Model)")
    print(sep)
    print(f"  G1         : {r['G1_mS']:.4f} mS")
    print(f"  G12        : {r['G12_mS']:.4f} mS")
    print(f"  Rin (edge) : {r['Rin_edge_ohm']:.2f} Ω")
    print(sep)
    print("  INSET MICROSTRIP FEED")
    print(sep)
    print(f"  Inset depth y₀  : {r['y0_mm']:.4f} mm")
    print(f"  Notch gap       : {r['notch_gap_mm']:.4f} mm")
    print(f"  Feed width Wf   : {r['W_feed_mm']:.4f} mm")
    print(f"  Feed Z₀         : {r['Z0_feed_ohm']:.2f} Ω")
    print(f"  Feed εr_eff     : {r['ereff_feed']:.4f}")
    print(f"  λ/4 length      : {r['L_quarter_mm']:.4f} mm")
    print(sep)
    print("  RECOMMENDED GROUND PLANE SIZE")
    print(sep)
    print(f"  Length Lg  : {r['Lg_mm']:.4f} mm")
    print(f"  Width  Wg  : {r['Wg_mm']:.4f} mm")
    print(f"{'═'*55}\n")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # ── Default design: FR-4 substrate, 2.4 GHz ──────────────────────────────
    results = design_patch_antenna(
        freq_hz=2.4e9,
        er=4.4,          # FR-4 typical εr
        h=1.6e-3,        # 1.6 mm substrate (standard PCB)
        feed_impedance=50.0,
        substrate_name="FR-4",
    )
    print_results(results)

    # ── Optional: Rogers RO4003C substrate ───────────────────────────────────
    print("Alternative design on Rogers RO4003C (εr=3.55, h=0.813 mm):")
    results2 = design_patch_antenna(
        freq_hz=2.4e9,
        er=3.55,
        h=0.813e-3,
        feed_impedance=50.0,
        substrate_name="Rogers RO4003C",
    )
    print_results(results2)
