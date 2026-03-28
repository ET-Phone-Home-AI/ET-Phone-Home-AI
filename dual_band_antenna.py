"""
Dual-Band Serpentine Implantable Microstrip Patch Antenna
=========================================================
Analytical design and PSO optimisation based on:
  Karacolak, Hood & Topsakal (2008), IEEE Trans. Microwave Theory Tech., vol. 56, no. 4.

Physics notes
-------------
* Effective length: the serpentine meander contributes sum(L_si) to the electrical
  path while the remaining patch body contributes L_p/2 (shorting-pin PIFA geometry).
  L_eff_f1 = sum(L_si) + L_p/2 + delta_pin
  L_eff_f2 = L_p - L_c + delta_pin      (upper mode controlled by L_c cut)
* S11 model: two parallel RLC resonators; Gamma from combined impedance.
  R_feed = Z0 = 50 Ω represents the impedance-matched feed point after the
  shorting-pin/feed-position transformation (standard PIFA assumption).
* Q_tissue dominates at both bands due to high skin conductivity.

Dependencies: numpy, matplotlib only.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, Circle
import warnings
warnings.filterwarnings("ignore")

# =============================================================================
# SECTION 1 — USER INPUTS
# =============================================================================

f1_MHz = 402        # lower band centre frequency (MHz)
f2_MHz = 2440       # upper band centre frequency (MHz)

eps_r   = 10.2      # substrate relative permittivity (Rogers RO3210)
tan_d   = 0.003     # loss tangent
h       = 0.00254   # substrate thickness per layer (m) — 2 layers → 5.08 mm total

eps_skin_f1   = 46.74   # skin permittivity @ ~400 MHz  (Gabriel et al. 1996)
sigma_skin_f1 = 0.69    # skin conductivity (S/m)
eps_skin_f2   = 38.06   # skin permittivity @ ~2.4 GHz
sigma_skin_f2 = 1.44    # skin conductivity (S/m)

L_sub = 0.0225   # substrate side length (m)
W_sub = 0.0225
L_p   = 0.0220   # patch length (m)
W_p   = 0.01775  # patch width  (m)

# Physical constants
c        = 3e8
mu0      = 4e-7 * np.pi
eps0     = 8.854e-12
Z0_port  = 50.0
sigma_cu = 5.8e7

# PSO hyperparameters
N_PARTICLES = 30
MAX_ITER    = 200
OMEGA_START = 0.9
OMEGA_END   = 0.4
C1 = C2     = 2.0

FREQ_ARRAY = np.linspace(300e6, 3000e6, 500)

# =============================================================================
# SECTION 2 — ANALYTICAL PHYSICS
# =============================================================================

def compute_eps_eff(W, eps_sub, eps_tissue, h_sub):
    """
    Hammerstad-Jensen effective permittivity for microstrip embedded between
    substrate (eps_sub) and tissue superstrate (eps_tissue).

    Parameters
    ----------
    W          : float — strip width (m)
    eps_sub    : float — substrate relative permittivity
    eps_tissue : float — tissue relative permittivity
    h_sub      : float — substrate thickness (m)

    Returns
    -------
    eps_eff : float
    """
    return ((eps_sub + eps_tissue) / 2.0
            + (eps_sub - eps_tissue) / 2.0
            * (1.0 + 12.0 * h_sub / W) ** (-0.5))


def compute_L_eff(L_p_val, slots, h_sub, eps_r_sub, L_c):
    """
    Effective electrical lengths for the two resonant modes.

    The serpentine meander creates a current path whose dominant term is the
    sum of all slot lengths (each slot ≈ one meander arm), plus a base
    contribution from the remaining patch body (L_p/2, PIFA geometry) and
    the shorting-pin end correction delta_pin.

    L_eff_f1 = sum(L_si) + L_p/2 + delta_pin   → fundamental (MICS ~402 MHz)
    L_eff_f2 = L_p - L_c + delta_pin            → upper mode  (ISM ~2440 MHz)

    Parameters
    ----------
    L_p_val   : float                — physical patch length (m)
    slots     : list of (W_si, L_si) — slot parameters
    h_sub     : float                — substrate thickness (m)
    eps_r_sub : float                — substrate permittivity
    L_c       : float                — right-strip material cut (m)

    Returns
    -------
    L_eff_f1, L_eff_f2 : floats (m)
    """
    delta_pin = 0.25 * h_sub * np.sqrt(eps_r_sub)
    L_si_sum  = sum(L_si for (_, L_si) in slots)
    L_eff_f1  = L_si_sum + L_p_val / 2.0 + delta_pin
    L_eff_f2  = max(L_p_val - L_c + delta_pin, 1e-4)
    L_eff_f1  = max(L_eff_f1, 1e-4)
    return L_eff_f1, L_eff_f2


def compute_Q_factors(f_res, eps_eff, h_sub, eps_r_sub, L_eff,
                      eps_skin, sigma_skin):
    """
    Loaded Q via cavity model (4 loss mechanisms).

    Parameters
    ----------
    f_res      : float — resonant frequency (Hz)
    eps_eff    : float — effective permittivity
    h_sub      : float — substrate thickness (m)
    eps_r_sub  : float — substrate permittivity
    L_eff      : float — effective length at this mode (m)
    eps_skin   : float — tissue permittivity at f_res
    sigma_skin : float — tissue conductivity (S/m) at f_res

    Returns
    -------
    Q_L        : float — loaded Q
    R_rad      : float — radiation resistance (Ω)  [for Q_rad calculation]
    """
    omega = 2.0 * np.pi * f_res

    Q_diel = 1.0 / tan_d

    Rs     = np.sqrt(np.pi * f_res * mu0 / sigma_cu)
    Q_cond = (h_sub * np.sqrt(eps_r_sub) * omega) / max(Rs, 1e-30)

    lambda_eff = c / (f_res * np.sqrt(eps_eff))
    R_rad      = max(80.0 * (L_eff / lambda_eff) ** 2 * eps_eff ** (-1.5), 1e-9)
    Q_rad      = (omega * mu0 * h_sub) / (2.0 * R_rad)

    Q_tissue   = (omega * eps0 * eps_skin) / sigma_skin

    Q_L = 1.0 / (1.0/Q_diel + 1.0/Q_cond + 1.0/Q_rad + 1.0/Q_tissue)
    return Q_L, R_rad


def _band_impedance(freq_array, f_res, Q_L):
    """
    Series-RLC input impedance for one resonance, normalised to Z0 at the
    feed point (R_feed = Z0_port, representing the impedance-matched PIFA feed).

    Parameters
    ----------
    freq_array : ndarray — frequencies (Hz)
    f_res      : float   — resonant frequency (Hz)
    Q_L        : float   — loaded Q

    Returns
    -------
    Z_in : complex ndarray (Ω)
    """
    ratio = freq_array / f_res
    return Z0_port * (1.0 + 1j * Q_L * (ratio - 1.0 / ratio))


def compute_S11_curve(freq_array, params):
    """
    S11 (dB) over freq_array.  Two resonances are modelled as parallel RLC
    resonators; Gamma is computed from the combined impedance.

    Parameters
    ----------
    freq_array : ndarray, shape (N,) — Hz
    params     : ndarray, shape (16,)

    Returns
    -------
    S11_dB : ndarray, shape (N,)
    """
    slots, L_c, F_y, P_x, P_y = _unpack_params(params)
    L_eff_f1, L_eff_f2 = compute_L_eff(L_p, slots, h, eps_r, L_c)

    eps_eff_f1 = compute_eps_eff(W_p, eps_r, eps_skin_f1, h)
    eps_eff_f2 = compute_eps_eff(W_p, eps_r, eps_skin_f2, h)

    f_res1 = c / (2.0 * L_eff_f1 * np.sqrt(eps_eff_f1))
    f_res2 = c / (2.0 * L_eff_f2 * np.sqrt(eps_eff_f2))

    Q_L1, _ = compute_Q_factors(f_res1, eps_eff_f1, h, eps_r, L_eff_f1,
                                 eps_skin_f1, sigma_skin_f1)
    Q_L2, _ = compute_Q_factors(f_res2, eps_eff_f2, h, eps_r, L_eff_f2,
                                 eps_skin_f2, sigma_skin_f2)

    Z1 = _band_impedance(freq_array, f_res1, Q_L1)
    Z2 = _band_impedance(freq_array, f_res2, Q_L2)

    # Parallel combination of two resonators
    Z_total = Z1 * Z2 / (Z1 + Z2)

    Gamma  = (Z_total - Z0_port) / (Z_total + Z0_port)
    S11_dB = 20.0 * np.log10(np.maximum(np.abs(Gamma), 1e-12))
    return np.minimum(S11_dB, 0.0)


def evaluate_fitness(params):
    """
    fitness = max(S11@f1, S11@f2).  Minimise (negative = good).

    Returns
    -------
    fitness, S11_f1, S11_f2 : floats (dB)
    """
    S11    = compute_S11_curve(FREQ_ARRAY, params)
    idx_f1 = np.argmin(np.abs(FREQ_ARRAY - f1_MHz * 1e6))
    idx_f2 = np.argmin(np.abs(FREQ_ARRAY - f2_MHz * 1e6))
    s1 = float(S11[idx_f1])
    s2 = float(S11[idx_f2])
    return max(s1, s2), s1, s2


# =============================================================================
# SECTION 3 — PSO
# =============================================================================

_mm = 1e-3
LOWER = np.array([
    -8*_mm,  0.5*_mm, 19*_mm,
    -4*_mm,  0.3*_mm, 19*_mm,
     0*_mm,  0.5*_mm, 17*_mm,
     3*_mm,  0.5*_mm, 16.5*_mm,
     6*_mm, -2*_mm,   0.1*_mm,  0.1*_mm,
])
UPPER = np.array([
    -6*_mm,  3*_mm,   21*_mm,
    -3*_mm,  3*_mm,   21*_mm,
     1*_mm,  3*_mm,   18.5*_mm,
     4.5*_mm,3*_mm,   18.5*_mm,
    11*_mm,  2*_mm,   1.5*_mm,  5.0*_mm,
])
NDIM = 16


def _unpack_params(p):
    """Return (slots, L_c, F_y, P_x, P_y) from flat parameter vector."""
    P_s   = [p[0], p[3], p[6], p[9]]
    W_s   = [p[1], p[4], p[7], p[10]]
    L_s   = [p[2], p[5], p[8], p[11]]
    slots = list(zip(W_s, L_s))
    return slots, p[12], p[13], p[14], p[15]


def _slot_bbox(i, P_s, W_s, L_s):
    """
    Return (x_lo, x_hi, y_lo, y_hi) bounding box of slot i in metres.
    Odd slots (i=0,2) open from the bottom edge; even (i=1,3) from the top.
    """
    x_lo = P_s[i] - W_s[i] / 2
    x_hi = P_s[i] + W_s[i] / 2
    if i % 2 == 0:   # bottom-opening
        y_lo = -L_p / 2
        y_hi = -L_p / 2 + L_s[i]
    else:             # top-opening
        y_lo = L_p / 2 - L_s[i]
        y_hi =  L_p / 2
    return x_lo, x_hi, y_lo, y_hi


def _point_in_slot(px, py, P_s, W_s, L_s):
    """Return True if point (px, py) falls inside any slot's footprint."""
    for i in range(4):
        x_lo, x_hi, y_lo, y_hi = _slot_bbox(i, P_s, W_s, L_s)
        if x_lo < px < x_hi and y_lo < py < y_hi:
            return True
    return False


def check_constraints(p):
    """
    Return True if particle satisfies all geometric constraints.

    Constraints (all lengths in metres):
      L_si < L_p
      P_s1 - W_s1/2 > -10.75 mm
      P_s4 + W_s4/2 <  7.0 mm
      P_si + W_si/2 < P_s(i+1) - W_s(i+1)/2   for i = 1,2,3
      L_c < L_s4
      Feed point (0, F_y) must lie on copper — not inside any slot
      Shorting pin (pin_x, pin_y) must lie on copper — not inside any slot
    """
    P_s = [p[0], p[3], p[6], p[9]]
    W_s = [p[1], p[4], p[7], p[10]]
    L_s = [p[2], p[5], p[8], p[11]]
    L_c = p[12]
    F_y = p[13]
    P_x = p[14]
    P_y = p[15]

    if any(L_s[i] >= L_p for i in range(4)):
        return False
    if P_s[0] - W_s[0] / 2 <= -10.75 * _mm:
        return False
    if P_s[3] + W_s[3] / 2 >= 7.0 * _mm:
        return False
    for i in range(3):
        if P_s[i] + W_s[i] / 2 >= P_s[i+1] - W_s[i+1] / 2:
            return False
    if L_c >= L_s[3]:
        return False

    # Feed (x=0, y=F_y) must be on copper patch and not in any slot
    if _point_in_slot(0.0, F_y, P_s, W_s, L_s):
        return False

    # Shorting pin must not be inside any slot
    pin_x = P_s[2] - W_s[2] / 2 - P_x
    pin_y = L_p / 2 - P_y
    if _point_in_slot(pin_x, pin_y, P_s, W_s, L_s):
        return False

    return True


def _random_valid_particle(rng):
    """Rejection-sample a random particle satisfying all constraints."""
    for _ in range(20000):
        p = rng.uniform(LOWER, UPPER)
        if check_constraints(p):
            return p
    return (LOWER + UPPER) / 2.0


def run_PSO(n_particles=N_PARTICLES, max_iter=MAX_ITER, seed=42):
    """
    Particle Swarm Optimisation over the 16-D geometry space.

    Parameters
    ----------
    n_particles : int
    max_iter    : int
    seed        : int

    Returns
    -------
    gbest_params  : ndarray (16,)
    gbest_fitness : float (dB)
    history       : list[float]
    """
    rng   = np.random.default_rng(seed)
    pos   = np.array([_random_valid_particle(rng) for _ in range(n_particles)])
    v_max = 0.2 * (UPPER - LOWER)
    vel   = rng.uniform(-v_max, v_max, size=(n_particles, NDIM))

    pbest_pos = pos.copy()
    pbest_fit = np.array([evaluate_fitness(pos[i])[0] for i in range(n_particles)])

    gi            = int(np.argmin(pbest_fit))
    gbest_params  = pbest_pos[gi].copy()
    gbest_fitness = pbest_fit[gi]
    history       = []

    for it in range(max_iter):
        omega = OMEGA_START - (OMEGA_START - OMEGA_END) * it / max_iter
        r1    = rng.random((n_particles, NDIM))
        r2    = rng.random((n_particles, NDIM))

        vel = (omega * vel
               + C1 * r1 * (pbest_pos - pos)
               + C2 * r2 * (gbest_params - pos))
        vel = np.clip(vel, -v_max, v_max)

        pos = np.clip(pos + vel, LOWER, UPPER)
        for i in range(n_particles):
            if not check_constraints(pos[i]):
                pos[i] = _random_valid_particle(rng)

        for i in range(n_particles):
            fit, s1, s2 = evaluate_fitness(pos[i])
            if fit < pbest_fit[i]:
                pbest_fit[i] = fit
                pbest_pos[i] = pos[i].copy()

        gi2 = int(np.argmin(pbest_fit))
        if pbest_fit[gi2] < gbest_fitness:
            gbest_fitness = pbest_fit[gi2]
            gbest_params  = pbest_pos[gi2].copy()

        history.append(gbest_fitness)

        if (it + 1) % 10 == 0:
            _, s1, s2 = evaluate_fitness(gbest_params)
            print(f"Iter {it+1:3d} | best fitness = {gbest_fitness:7.2f} dB"
                  f" | S11@f1 = {s1:7.2f} dB | S11@f2 = {s2:7.2f} dB")

        if gbest_fitness < -20.0:
            print(f"\n[PSO] Early stop at iter {it+1}:"
                  f" fitness = {gbest_fitness:.2f} dB < −20 dB\n")
            break

    return gbest_params, gbest_fitness, history


# =============================================================================
# SECTION 4 — OUTPUTS
# =============================================================================

def _compute_derived(params):
    """Compute resonant frequencies and bandwidths from optimised params."""
    slots, L_c, F_y, P_x, P_y = _unpack_params(params)
    L_eff_f1, L_eff_f2 = compute_L_eff(L_p, slots, h, eps_r, L_c)

    eps_eff_f1 = compute_eps_eff(W_p, eps_r, eps_skin_f1, h)
    eps_eff_f2 = compute_eps_eff(W_p, eps_r, eps_skin_f2, h)

    f_res1 = c / (2.0 * L_eff_f1 * np.sqrt(eps_eff_f1))
    f_res2 = c / (2.0 * L_eff_f2 * np.sqrt(eps_eff_f2))

    Q_L1, _ = compute_Q_factors(f_res1, eps_eff_f1, h, eps_r, L_eff_f1,
                                 eps_skin_f1, sigma_skin_f1)
    Q_L2, _ = compute_Q_factors(f_res2, eps_eff_f2, h, eps_r, L_eff_f2,
                                 eps_skin_f2, sigma_skin_f2)

    return (f_res1, f_res2,
            1.0 / Q_L1, 1.0 / Q_L2,
            f_res1 / Q_L1 / 1e6, f_res2 / Q_L2 / 1e6)


def print_results_table(params):
    """Print formatted results table."""
    slots, L_c, F_y, P_x, P_y = _unpack_params(params)
    P_s = [params[0], params[3], params[6], params[9]]
    W_s = [params[1], params[4], params[7], params[10]]
    L_s = [params[2], params[5], params[8], params[11]]
    pin_x = P_s[2] - W_s[2] / 2 - P_x
    pin_y = L_p / 2 - P_y

    (f_res1, f_res2, bw1f, bw2f, bw1, bw2) = _compute_derived(params)
    _, S11_f1, S11_f2 = evaluate_fitness(params)
    m = 1e3   # m → mm

    C1W, C2W = 17, 26
    sep = "─" * C1W + "┼" + "─" * C2W

    def row(name, val):
        print(f"│ {name:<{C1W-2}} │ {val:>{C2W-2}} │")

    print("\n┌" + "─" * C1W + "┬" + "─" * C2W + "┐")
    print(f"│{'  OPTIMIZED ANTENNA DESIGN RESULTS':<{C1W+C2W+1}}│")
    print("├" + sep + "┤")
    row("Parameter", "Optimised value")
    print("├" + sep + "┤")
    for i in range(4):
        row(f"P_s{i+1} (mm)", f"{P_s[i]*m:+.4f}")
        row(f"W_s{i+1} (mm)", f"{W_s[i]*m:.4f}")
        row(f"L_s{i+1} (mm)", f"{L_s[i]*m:.4f}")
    row("L_c  (mm)",  f"{L_c*m:.4f}")
    row("F_y  (mm)",  f"{F_y*m:+.4f}")
    row("P_x  (mm)",  f"{P_x*m:.4f}")
    row("P_y  (mm)",  f"{P_y*m:.4f}")
    row("pin_x (mm)", f"{pin_x*m:+.4f}")
    row("pin_y (mm)", f"{pin_y*m:+.4f}")
    print("├" + sep + "┤")
    row("f_res1 (MHz)",  f"{f_res1/1e6:.2f}")
    row("f_res2 (MHz)",  f"{f_res2/1e6:.2f}")
    row("S11 @ f1 (dB)", f"{S11_f1:.2f}")
    row("S11 @ f2 (dB)", f"{S11_f2:.2f}")
    row("BW @ f1 (MHz)", f"{bw1:.2f}")
    row("BW @ f2 (MHz)", f"{bw2:.2f}")
    row("BW @ f1 (%)",   f"{bw1f*100:.2f}")
    row("BW @ f2 (%)",   f"{bw2f*100:.2f}")
    print("└" + "─" * C1W + "┴" + "─" * C2W + "┘\n")


def plot_S11(freq_array, S11_initial, S11_optimized, save_path="S11_plot.png"):
    """
    Plot S11 vs frequency: initial (dashed grey) and optimised (solid blue).
    Shades MICS and ISM bands; marks −10 dB threshold and target frequencies.
    """
    freq_MHz = freq_array / 1e6
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.axvspan(402,  405,  alpha=0.30, color="orange",    label="MICS (402–405 MHz)")
    ax.axvspan(2400, 2480, alpha=0.20, color="peachpuff", label="ISM (2400–2480 MHz)")
    ax.axhline(-10, color="red", linestyle="--", linewidth=1.2, label="−10 dB threshold")
    ax.axvline(f1_MHz, color="steelblue", linestyle=":", linewidth=1.0)
    ax.axvline(f2_MHz, color="steelblue", linestyle=":", linewidth=1.0)
    ax.text(f1_MHz + 15,  -33.5, f"f1={f1_MHz} MHz", fontsize=8, color="steelblue")
    ax.text(f2_MHz + 20,  -33.5, f"f2={f2_MHz} MHz", fontsize=8, color="steelblue")

    ax.plot(freq_MHz, S11_initial,   color="gray",      linestyle="--",
            linewidth=1.2, label="Initial (random)")
    ax.plot(freq_MHz, S11_optimized, color="royalblue", linestyle="-",
            linewidth=2.0, label="Optimised")

    ax.set_xlim(300, 3000)
    ax.set_ylim(-35, 5)
    ax.set_xlabel("Frequency (MHz)", fontsize=12)
    ax.set_ylabel("S11 (dB)", fontsize=12)
    ax.set_title("Serpentine Implantable Antenna — Return Loss", fontsize=13)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"[Plot] Saved: {save_path}")


def plot_geometry(params, save_path="geometry_plot.png"):
    """
    Top-view patch geometry drawn to scale.

    Coordinate convention (matches Karacolak 2008 fig.):
      x-axis  → W_p direction (17.75 mm wide);  P_si are x-positions
      y-axis  → L_p direction (22 mm tall);      L_si are slot heights

    Slots are interdigitated: odd slots (S1, S3) open from the bottom edge
    and even slots (S2, S4) open from the top edge, creating the serpentine
    current path.
    """
    slots_wl, L_c, F_y, P_x, P_y = _unpack_params(params)
    P_s = [params[0], params[3], params[6], params[9]]
    W_s = [params[1], params[4], params[7], params[10]]
    L_s = [params[2], params[5], params[8], params[11]]
    pin_x = P_s[2] - W_s[2] / 2 - P_x
    pin_y = L_p / 2 - P_y
    m = 1e3   # m → mm

    fig, ax = plt.subplots(figsize=(7, 9))

    # Substrate (square — same in both axes)
    ax.add_patch(Rectangle((-L_sub/2*m, -L_sub/2*m), L_sub*m, L_sub*m,
                            linewidth=1.5, edgecolor="black",
                            facecolor="lightgray", label="Substrate", zorder=1))

    # Copper patch — W_p along x, L_p along y
    ax.add_patch(Rectangle((-W_p/2*m, -L_p/2*m), W_p*m, L_p*m,
                            linewidth=1.2, edgecolor="goldenrod",
                            facecolor="#C8A000", label="Copper patch", zorder=2))

    # Slots — interdigitated: odd from bottom, even from top
    for i, (Ps, Ws, Ls) in enumerate(zip(P_s, W_s, L_s)):
        if i % 2 == 0:   # S1, S3 — open from bottom edge
            sy0 = -L_p / 2 * m
        else:             # S2, S4 — open from top edge
            sy0 = (L_p / 2 - Ls) * m
        ax.add_patch(Rectangle((Ps*m - Ws*m/2, sy0), Ws*m, Ls*m,
                                linewidth=0.8, edgecolor="dimgray",
                                facecolor="white", zorder=3))
        label_y = sy0 + Ls*m/2
        ax.text(Ps*m, label_y, f"S{i+1}\nW={Ws*m:.1f}\nL={Ls*m:.1f}",
                ha="center", va="center", fontsize=6, color="dimgray", zorder=4)

    # Feed point (on the patch, x=0 along width centre, y=F_y along length)
    ax.plot(0, F_y*m, "ro", markersize=9, zorder=6,
            label=f"Feed (0, {F_y*m:.2f} mm)")

    # Shorting pin
    ax.add_patch(Circle((pin_x*m, pin_y*m), radius=0.3,
                         color="black", zorder=6,
                         label=f"Pin ({pin_x*m:.2f}, {pin_y*m:.2f}) mm"))

    # Dimension annotations
    # Width arrow along x at bottom of patch
    ax.annotate("", xy=(W_p/2*m, -L_p/2*m - 1.8),
                xytext=(-W_p/2*m, -L_p/2*m - 1.8),
                arrowprops=dict(arrowstyle="<->", color="black", lw=1.0))
    ax.text(0, -L_p/2*m - 2.8, f"W_p = {W_p*m:.2f} mm",
            ha="center", va="top", fontsize=8)

    # Length arrow along y at right of patch
    ax.annotate("", xy=(W_p/2*m + 1.8, L_p/2*m),
                xytext=(W_p/2*m + 1.8, -L_p/2*m),
                arrowprops=dict(arrowstyle="<->", color="black", lw=1.0))
    ax.text(W_p/2*m + 2.5, 0, f"L_p = {L_p*m:.1f} mm",
            ha="left", va="center", fontsize=8, rotation=90)

    ax.set_xlim(-14, 14)
    ax.set_ylim(-16, 15)
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)", fontsize=11)
    ax.set_ylabel("y (mm)", fontsize=11)
    ax.set_title("Optimised Patch Geometry", fontsize=13)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.85)
    ax.grid(True, linestyle=":", alpha=0.4)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"[Plot] Saved: {save_path}")


# =============================================================================
# SECTION 5 — MAIN
# =============================================================================

def main():
    print("=" * 62)
    print("  Dual-Band Serpentine Implantable Patch Antenna")
    print("  Karacolak, Hood & Topsakal (2008) — Analytical + PSO")
    print("=" * 62)
    print(f"  Target  f1 = {f1_MHz} MHz   f2 = {f2_MHz} MHz")
    print(f"  Rogers RO3210: eps_r={eps_r}, tan_d={tan_d}, h={h*1e3:.2f} mm/layer")
    print("=" * 62)

    # Initial random design (for plot comparison)
    rng0      = np.random.default_rng(0)
    p_init    = _random_valid_particle(rng0)
    S11_init  = compute_S11_curve(FREQ_ARRAY, p_init)
    fit0, s10, s20 = evaluate_fitness(p_init)
    print(f"\nInitial random design: fitness={fit0:.2f} dB  "
          f"(S11@f1={s10:.2f}, S11@f2={s20:.2f})\n")

    # PSO
    print("Running PSO...\n")
    gbest, gfit, history = run_PSO()

    S11_opt = compute_S11_curve(FREQ_ARRAY, gbest)

    print_results_table(gbest)

    plot_S11(FREQ_ARRAY, S11_init, S11_opt)
    plot_geometry(gbest)

    # Convergence plot
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(range(1, len(history)+1), history, color="royalblue", linewidth=1.5)
    ax.axhline(-20, color="red", linestyle="--", linewidth=1, label="−20 dB target")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Best Fitness (dB)")
    ax.set_title("PSO Convergence")
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig("convergence_plot.png", dpi=150)
    plt.close()
    print("[Plot] Saved: convergence_plot.png")
    print("\nDone.")


if __name__ == "__main__":
    main()
