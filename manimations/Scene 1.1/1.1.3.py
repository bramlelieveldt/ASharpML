"""   - Animatie 1.1: Wat is geluid, trillingen in de lucht. Vlakke staande golf. **Bram**
     - 1.1.1: Bel gaat af
     - 1.1.2: Lucht begint te trillen
     - 1.1.3: Oor hoort de trillingen
     - 1.1.4: Sinus golf met de deeltjes dichtheid

Render:  manim -pql 1.1.3.py HairResonance
"""

from manim import *
import numpy as np

N = 800  # Amount of air particles (raise for a denser look, lower if rendering is slow)

# --- Plane wave (travels left -> right, longitudinal displacement along x, as in main.py) ---
C = 2.0                # propagation speed [scene units / s]
DRIVE_FREQS = [1.0, 2.0]   # frequency of the 1st and 2nd run [Hz] (2nd = octave higher)
A_REF = 0.20           # displacement amplitude at 1 Hz; scales as 1/f so that k*A stays constant
THERMAL = 0.03         # small random jiggle of the air

# --- Hairs (ordered by length, like along the cochlea) ---
NH = 13                # number of hairs
F_HI, F_LO = 4.0, 0.5  # natural frequency of the shortest / longest hair [Hz]
L_MAX = 2.8            # length of the longest hair (lowest frequency); L is proportional to 1/f
ZETA = 0.10            # damping ratio -> quality factor Q = 1 / (2 zeta) = 5
THETA_RES = 0.35       # swing angle [rad] of a hair that is driven exactly on resonance
Y0 = -3.5              # y-position of the membrane the hairs are attached to
X_FIRST, X_LAST = -5.2, 5.2


class HairResonance(Scene):
    def construct(self):
        rng = np.random.default_rng(11)
        width = config.frame_width
        height = config.frame_height
        XL = -width / 2 - 0.3          # the plane wave starts at the left edge

        # Global clock so everything stays in sync
        clock = ValueTracker(0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        # ---------------- Hairs: short (high f) on the left, long (low f) on the right ----------------
        idx = np.arange(NH)
        f_nat = F_HI * (F_LO / F_HI) ** (idx / (NH - 1))   # natural frequencies [Hz]
        w_nat = 2 * PI * f_nat
        length = L_MAX * F_LO / f_nat                      # longer hair -> lower frequency
        hx = np.linspace(X_FIRST, X_LAST, NH)

        hair_colors = color_gradient([BLUE_C, TEAL_C, GREEN_C, YELLOW_C, ORANGE], NH)
        hair_lines = [Line([x, Y0, 0], [x, Y0 + L, 0], stroke_width=6, color=GREY_B)
                      for x, L in zip(hx, length)]
        hair_tips = [Dot([x, Y0 + L, 0], radius=0.07, color=GREY_B) for x, L in zip(hx, length)]
        hairs = VGroup(*[VGroup(l, d) for l, d in zip(hair_lines, hair_tips)])
        membrane = Line([X_FIRST - 0.6, Y0, 0], [X_LAST + 0.6, Y0, 0], stroke_width=8, color=GREY)

        # State of the damped, driven oscillators (one per hair)
        theta = np.zeros(NH)
        vel = np.zeros(NH)
        env = np.zeros(NH)      # slowly decaying envelope of |theta|, used for colouring
        drive = {"f": DRIVE_FREQS[0], "t0": None}

        def reset_state(f):
            drive["f"], drive["t0"] = f, None
            theta[:] = 0
            vel[:] = 0
            env[:] = 0

        def plane_wave(x, t):
            """Smooth wave-front factor and phase of the plane wave at positions x, time t."""
            f = drive["f"]
            wd, wl = 2 * PI * f, C / f
            tau = t - drive["t0"]
            xr = x - XL
            ramp = np.clip((C * tau - xr) / wl, 0, 1)
            ramp = ramp * ramp * (3 - 2 * ramp)                     # smoothstep
            return ramp, (wd / C) * xr - wd * tau                   # sin(kx - wt), 0 at the front

        def update_hairs(_, dt):
            t = clock.get_value()
            n = max(1, int(np.ceil(dt / 0.004)))                    # sub-steps for a stable integration
            h = dt / n
            wd = 2 * PI * drive["f"]
            for j in range(n):
                if drive["t0"] is None:
                    force = 0.0
                else:
                    ramp, ph = plane_wave(hx, t - dt + (j + 1) * h)
                    # F0 chosen so that an on-resonance hair reaches THETA_RES
                    force = 2 * ZETA * THETA_RES * wd ** 2 * ramp * np.sin(ph)
                acc = force - 2 * ZETA * w_nat * vel - w_nat ** 2 * theta
                vel += acc * h
                theta += vel * h
            env[:] = np.maximum(np.abs(theta), env * np.exp(-2 * dt))
            for i in range(NH):
                tip = np.array([hx[i] + length[i] * np.sin(theta[i]),
                                Y0 + length[i] * np.cos(theta[i]), 0])
                col = interpolate_color(GREY_B, hair_colors[i], min(1.0, env[i] / THETA_RES))
                hair_lines[i].put_start_and_end_on(np.array([hx[i], Y0, 0]), tip)
                hair_lines[i].set_color(col)
                hair_tips[i].move_to(tip)
                hair_tips[i].set_color(col)

        hairs.add_updater(update_hairs)

        # ---------------- Air molecules ----------------
        base = np.column_stack([
            rng.uniform(-width / 2 - 0.3, width / 2 + 0.3, N),
            rng.uniform(Y0 + 0.1, height / 2 + 0.3, N),
        ])
        phase = rng.uniform(0, 2 * PI, (N, 2))
        dots = [Dot(point=(x, y, 0), radius=0.05, color=BLUE) for x, y in base]
        air = VGroup(*dots)

        def update_air(_):
            t = clock.get_value()
            pos = base + THERMAL * np.column_stack([np.sin(1.3 * t + phase[:, 0]),
                                                    np.cos(1.1 * t + phase[:, 1])])
            if drive["t0"] is not None:
                ramp, ph = plane_wave(base[:, 0], t)
                A = A_REF / drive["f"]
                pos[:, 0] += A * ramp * np.sin(ph)                  # x = x0 + A sin(kx0 - wt), as in main.py
            for d, p in zip(dots, pos):
                d.move_to([p[0], p[1], 0])

        air.add_updater(update_air)

        air.set_z_index(0)
        membrane.set_z_index(1)
        hairs.set_z_index(2)

        static = VGroup(air, membrane, hairs)

        def make_label(f):
            return Text(f"f = {f:.1f} Hz", font_size=32).to_corner(UL).set_z_index(3)

        # ---------------- Run the scene once per drive frequency ----------------
        for run, f in enumerate(DRIVE_FREQS):
            reset_state(f)
            label = make_label(f)
            self.play(FadeIn(static), FadeIn(label), run_time=1.5)
            self.wait(2)                                            # still air, hairs at rest

            drive["t0"] = clock.get_value()                         # the plane wave enters from the left

            # Time for the front to reach the resonant hair + ring-up time (~3.5 time constants) + a hold
            i_res = int(np.argmin(np.abs(f_nat - f)))
            T = (hx[i_res] - XL) / C + 3.5 / (ZETA * 2 * PI * f) + 3
            self.wait(T)

            if run < len(DRIVE_FREQS) - 1:
                self.play(FadeOut(static), FadeOut(label), run_time=1)   # reset for the next run

        hairs.clear_updaters()
        air.clear_updaters()