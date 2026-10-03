"""   - Animatie 1.1: Wat is geluid, trillingen in de lucht. Vlakke staande golf. **Bram**
     - 1.1.1: Bel gaat af
     - 1.1.2: Lucht begint te trillen
     - 1.1.3: Oor hoort de trillingen
     - 1.1.4: Sinus golf met de deeltjes dichtheid

Render:  manim -pql 1.1.1.py BellStrike
"""

from manim import *
import numpy as np

N = 900  # Amount of air particles (raise for a denser look, lower if rendering is slow)

# --- Wave parameters (spherical wave, emitted from the bell) ---
C = 2.5            # propagation speed [scene units / s]
WL = 1.4           # wavelength [scene units]
FREQ = C / WL      # frequency [Hz]
A0 = 0.16          # displacement amplitude close to the bell
R_REF = 1.5        # amplitude falls off as sqrt(R_REF / r) beyond this radius
TAU = 3.0          # ring-down time of the bell [s]
RAMP = 0.4         # time over which the emission fades in [s]
THERMAL = 0.03     # small random jiggle of the air before the strike
R_EXCL = 1.5       # no particles inside this radius (the bell lives here)

# --- Bell geometry / motion ---
OFFSET = np.array([0, -0.15, 0])         # centres the bell body on the origin
HANG = np.array([0, 1.15, 0]) + OFFSET   # point the bell hangs from
PIVOT = np.array([0, 0.70, 0]) + OFFSET  # pivot of the clapper
BOB = 0.10                               # floating amplitude
PULL, HIT = -0.35, 0.60                  # clapper angles [rad]: pulled back / at impact


def build_bell():
    """Bell drawn from Manim primitives. Submobjects: [clapper, handle, body]."""
    handle = Annulus(inner_radius=0.08, outer_radius=0.15, color=GOLD_E).move_to([0, 1.0, 0])

    right = np.array([[0, 0.90, 0], [0.28, 0.86, 0], [0.45, 0.62, 0], [0.52, 0.20, 0],
                      [0.58, -0.20, 0], [0.72, -0.50, 0], [0.95, -0.62, 0]])
    bottom = np.array([[0.5, -0.64, 0], [0, -0.65, 0], [-0.5, -0.64, 0]])
    left = right[::-1] * np.array([-1, 1, 1])
    body = VMobject()
    body.set_points_smoothly(np.vstack([right, bottom, left]))
    body.set_fill(GOLD, opacity=1).set_stroke(GOLD_E, width=3)

    clapper = VGroup(
        Line([0, 0.70, 0], [0, 0.70 - 1.55, 0], color=GREY_B, stroke_width=4),
        Dot([0, 0.70 - 1.55, 0], radius=0.11, color=GOLD_E),
    )
    # clapper first so the body hides the string; the ball sticks out below the lip
    return VGroup(clapper, handle, body).shift(OFFSET)


def clapper_angle(s):
    """Clapper angle as a function of time s relative to the moment of impact."""
    if s < -1.0:
        return 0.0
    if s < -0.35:                       # pull back
        return PULL * smooth((s + 1.0) / 0.65)
    if s < 0:                           # swing towards the bell wall
        return PULL + (HIT - PULL) * rush_into((s + 0.35) / 0.35)
    return HIT * np.exp(-4 * s) * np.cos(2 * PI * 1.2 * s)   # rebound, damped


class BellStrike(Scene):
    def construct(self):
        rng = np.random.default_rng(7)
        width = self.camera.frame_width
        height = self.camera.frame_height

        # Global clock so everything (bell, air) stays in sync
        clock = ValueTracker(0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        strike_t = [None]   # time of impact, set when the strike is scheduled
        float_t0 = [0.0]    # start of the floating motion

        # ---------------- 1. Bell appears, floating ----------------
        bell = build_bell()
        bell_base = bell.copy()

        def update_bell(m):
            t = clock.get_value()
            s = t - strike_t[0] if strike_t[0] is not None else -10
            m.become(bell_base)
            m[0].rotate(clapper_angle(s), about_point=PIVOT)
            shake = 0.05 * np.exp(-s) * np.sin(2 * PI * 6 * s) if s > 0 else 0.0
            sway = 0.03 * np.sin(0.9 * (t - float_t0[0]))
            m.rotate(sway + shake, about_point=HANG)
            m.shift(UP * BOB * np.sin(1.1 * (t - float_t0[0])))

        self.play(FadeIn(bell), run_time=1.5)
        float_t0[0] = clock.get_value()
        bell.add_updater(update_bell)
        self.wait(1.5)

        # ---------------- 2. Air particles surround the bell ----------------
        base = np.zeros((0, 2))
        while len(base) < N:
            cand = np.column_stack([
                rng.uniform(-width / 2 - 0.3, width / 2 + 0.3, N),
                rng.uniform(-height / 2 - 0.3, height / 2 + 0.3, N),
            ])
            cand = cand[np.hypot(cand[:, 0], cand[:, 1]) > R_EXCL]
            base = np.vstack([base, cand])
        base = base[:N]

        r0 = np.hypot(base[:, 0], base[:, 1])          # distance to the bell centre
        unit = base / r0[:, None]                      # radial unit vectors
        phase = rng.uniform(0, 2 * PI, (N, 2))         # random phases for the jiggle

        dots = [Dot(point=(x, y, 0), radius=0.05, color=BLUE) for x, y in base]
        air = VGroup(*dots)

        def update_air(_):
            t = clock.get_value()
            pos = base + THERMAL * np.column_stack([np.sin(1.3 * t + phase[:, 0]),
                                                    np.cos(1.1 * t + phase[:, 1])])
            if strike_t[0] is not None:
                s = t - strike_t[0]
                if s > 0:
                    # Retarded time: the wave reaches a particle at distance r0 after r0 / C
                    tr = s - r0 / C
                    amp = (A0 * np.sqrt(R_REF / np.maximum(r0, R_REF))   # spreading
                           * np.exp(-np.maximum(tr, 0) / TAU)            # bell rings down
                           * np.clip(tr / RAMP, 0, 1))                   # zero ahead of the front
                    disp = amp * np.sin(2 * PI * FREQ * tr)
                    pos = pos + disp[:, None] * unit                     # radial (longitudinal) motion
            for d, p in zip(dots, pos):
                d.move_to([p[0], p[1], 0])

        self.play(FadeIn(air), run_time=2)
        air.add_updater(update_air)
        self.wait(2)

        # ---------------- 3. Strike: spherical wave leaves the bell ----------------
        strike_t[0] = clock.get_value() + 1.0   # clapper pulls back, then hits 1 s from now
        self.wait(1.0 + 12)

        bell.clear_updaters()
        air.clear_updaters()