"""   - Animatie 1.1: Wat is geluid, trillingen in de lucht. Vlakke staande golf. **Bram**
     - 1.1.1: Bel gaat af
     - 1.1.2: Lucht begint te trillen
     - 1.1.3: Oor hoort de trillingen
     - 1.1.4: Sinus golf met de deeltjes dichtheid

Render:  manim -pql 1.1.4.py DensitySine
"""

from manim import *
import numpy as np

# --- Particles: a pool of NMAX, revealed in stages ---
STAGES = [300, 800, 2000, 4000]   # number of particles after each "add more particles" step
NMAX = STAGES[-1]
DOT_RADIUS = 0.035
THERMAL = 0.02                    # small random jiggle of the air

# --- Plane wave (travels left -> right, longitudinal displacement along x, as in main.py) ---
C = 2.4                           # propagation speed [scene units / s]
FREQS = [0.6, 1.2, 2.4]           # frequencies shown one after another [Hz]
KA = 0.45                         # k * A (kept the same for every frequency, so the density swing is too)

# --- Density plot at the bottom ---
NB = 80                           # histogram bins across the screen
BASE_Y = -3.0                     # y of rho = rho_0 (undisturbed density)
PLOT_SCALE = 0.85                 # screen units per unit of rho / rho_0 (clipped to rho_0 +- 1)
Y_MIN_PARTICLES = -1.7            # air lives above this line, the plot below it


class DensitySine(Scene):
    def construct(self):
        rng = np.random.default_rng(5)
        width = config.frame_width
        height = config.frame_height
        XL = -width / 2 - 0.3                  # wave front enters here
        XR = width / 2 + 0.3
        WD = XR - XL                           # width of the region filled with particles

        # Global clock and tracker that fades the wave out when changing frequency
        clock = ValueTracker(0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)
        gain = ValueTracker(1)

        drive = {"f": FREQS[0], "t0": None}

        # ---------------- Particle pool (random order -> any prefix is uniform) ----------------
        base = np.column_stack([
            rng.uniform(XL, XR, NMAX),
            rng.uniform(Y_MIN_PARTICLES, height / 2 + 0.2, NMAX),
        ])
        phase = rng.uniform(0, 2 * PI, (NMAX, 2))

        template = Dot(ORIGIN, radius=DOT_RADIUS).points.copy()    # set points directly: much faster than move_to
        dots = []
        for x, y in base:
            d = Dot(ORIGIN, radius=DOT_RADIUS, color=BLUE)
            d.points = template + np.array([x, y, 0.0])
            dots.append(d)

        n_act = [STAGES[0]]    # particles whose positions are being updated
        n_hist = [STAGES[0]]   # particles included in the density histogram

        # ---------------- Wave ----------------
        def wave_u(x0, t):
            """Displacement u(x0, t) = A sin(k x0 - w t) behind a smooth wave front."""
            if drive["t0"] is None:
                return np.zeros_like(x0)
            f = drive["f"]
            wd, wl = 2 * PI * f, C / f
            k, A = wd / C, KA * wl / (2 * PI)
            tau = t - drive["t0"]
            xr = x0 - XL
            ramp = np.clip((C * tau - xr) / wl, 0, 1)
            ramp = ramp * ramp * (3 - 2 * ramp)
            return gain.get_value() * A * ramp * np.sin(k * xr - wd * tau)

        # ---------------- Density plot objects ----------------
        axis_x0, axis_x1 = -width / 2 + 0.5, width / 2 - 0.5
        baseline = Line([axis_x0, BASE_Y, 0], [axis_x1, BASE_Y, 0], stroke_width=2, color=GREY)
        rho_label = Text("ρ", font_size=30).move_to([axis_x0 - 0.1, BASE_Y + 0.8, 0])
        hist_curve = VMobject(stroke_color=GREEN, stroke_width=4)
        hist_curve.set_points_as_corners([[axis_x0, BASE_Y, 0], [axis_x1, BASE_Y, 0]])
        theory_curve = VMobject(stroke_color=YELLOW, stroke_width=3)
        theory_curve.set_points_as_corners([[axis_x0, BASE_Y, 0], [axis_x1, BASE_Y, 0]])
        plot_group = VGroup(baseline, rho_label, hist_curve)

        edges = np.linspace(-width / 2, width / 2, NB + 1)
        centers = (edges[:-1] + edges[1:]) / 2
        bin_w = edges[1] - edges[0]
        x0_grid = np.linspace(XL, XR, 600)

        def rho_to_y(rho):
            return BASE_Y + PLOT_SCALE * np.clip(rho - 1, -1, 1)

        # One driver updates everything (a plain updater on the dots would be paused while they fade in)
        def update_all(_):
            t = clock.get_value()
            n = n_act[0]
            px = base[:n, 0] + wave_u(base[:n, 0], t) + THERMAL * np.sin(1.3 * t + phase[:n, 0])
            py = base[:n, 1] + THERMAL * np.cos(1.1 * t + phase[:n, 1])
            for i in range(n):
                dots[i].points = template + np.array([px[i], py[i], 0.0])

            # Density from the particles that are currently shown
            m = n_hist[0]
            counts, _ = np.histogram(px[:m], bins=edges)
            rho_h = counts / (m * bin_w / WD)
            hist_curve.set_points_as_corners(np.column_stack([centers, rho_to_y(rho_h), np.zeros(NB)]))

            # Exact density of the wave: rho = dx0 / dx
            xs = x0_grid + wave_u(x0_grid, t)
            rho_t = 1 / np.gradient(xs, x0_grid)
            vis = (xs > -width / 2) & (xs < width / 2)
            if vis.sum() > 2:
                theory_curve.set_points_as_corners(
                    np.column_stack([xs[vis], rho_to_y(rho_t[vis]), np.zeros(vis.sum())]))

        driver = Mobject()
        driver.add_updater(update_all)
        self.add(driver)

        def make_label(f):
            return Text(f"f = {f:.1f} Hz", font_size=32).to_corner(UL)

        # ---------------- 1. Unperturbed air ----------------
        air = VGroup(*dots[:STAGES[0]])
        self.play(FadeIn(air), run_time=1.5)
        self.wait(2)

        # ---------------- 2. Plane wave enters from the left ----------------
        label = make_label(FREQS[0])
        drive["t0"] = clock.get_value()
        self.play(FadeIn(label), run_time=1)
        self.wait(1.5)

        # ---------------- 3. Density plotted at the bottom ----------------
        self.play(FadeIn(plot_group), run_time=1.5)
        self.wait(3.5)

        # ---------------- 4. More particles -> the noisy density converges to a sine ----------------
        self.play(FadeIn(theory_curve), run_time=1)
        self.wait(2)
        for a, b in zip(STAGES[:-1], STAGES[1:]):
            n_act[0] = b
            self.play(FadeIn(VGroup(*dots[a:b])), run_time=1.5)
            n_hist[0] = b
            self.wait(3.5)

        # ---------------- 5. Different frequencies ----------------
        for f in FREQS[1:]:
            self.play(gain.animate.set_value(0), run_time=1.5)      # wave dies out, air settles
            drive["f"], drive["t0"] = f, clock.get_value()          # new plane wave enters from the left
            gain.set_value(1)
            self.play(Transform(label, make_label(f)), run_time=0.5)
            self.wait(WD / C + 5)                                   # front crosses the screen, then hold

        driver.clear_updaters()