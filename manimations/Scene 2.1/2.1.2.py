"""   - Animatie 2.1: Pythagoras en het monochord
     - 2.1.1: Pythagoras bij het monochord (zijaanzicht)
     - 2.1.2: Bovenaanzicht, brug verplaatsen: octaaf, reine kwint, kwart

Render:  manim -pql 2.1.2.py MonochordIntervals
"""

from manim import *
import numpy as np

N = 2200  # Amount of air particles (raise for a denser look, lower if rendering is slow)

# --- Sound / wave parameters (spherical wave emitted from the centre of each vibrating string) ---
C = 2.5            # propagation speed [scene units / s]
F0 = 1.25          # frequency of the full string [Hz] (wavelength = C / F0 = 2 units)
A0 = 0.14          # displacement amplitude close to a string
R_REF = 1.5        # amplitude falls off as sqrt(R_REF / r) beyond this radius
TAU = 2.5          # ring-down time of a string [s]
RAMP = 0.4         # time over which the emission fades in [s]
THERMAL = 0.03     # small random jiggle of the air
SRC_LIFETIME = 15  # a wave source is dropped after this many seconds (it has died out by then)

# --- Monochords (top view) ---
X_L, X_R = -4.8, 3.8       # fixed ends of the string
BOARD_H = 0.8              # height of the soundboard
A_STR = 0.2                # visual amplitude of the string
X_LABEL = 5.5              # x of the ratio labels
Y1, Y2 = 2.6, 0.7          # y of the original / the second monochord
COL1, COL2 = YELLOW, ORANGE

# (length of vibrating part / full string, name, ratio label shown next to the monochord)
INTERVALS = [
    (1 / 2, "octaaf",       "1 : 2"),
    (2 / 3, "reine kwint",  "2 : 3"),
    (3 / 4, "kwart",        "3 : 4"),
]

# --- Sound graph at the bottom (scrolls to the left, newest sound on the right) ---
GX0, GX1 = -6.0, 6.0
GY, GH = -2.6, 0.85        # baseline y / height of an amplitude of 1
SCROLL = 2.0               # screen units per second
Y_MIN_PARTICLES = -1.5     # air lives above this line, the graph below it

HOLD = 9                   # seconds the sound is shown per interval


def build_monochord(y, ratio, color, name=None, label=None):
    """Top view of a monochord. `ratio` = vibrating length / full length (the bridge sits there)."""
    xb = X_L + ratio * (X_R - X_L)
    board = Rectangle(width=X_R - X_L + 0.8, height=BOARD_H, stroke_color=GOLD_E, stroke_width=2)
    board.set_fill("#2b1d12", opacity=0.95).move_to([(X_L + X_R) / 2, y, 0])
    nuts = VGroup(*[Rectangle(width=0.12, height=BOARD_H * 0.8, stroke_width=0)
                    .set_fill(GREY_B, opacity=1).move_to([x, y, 0]) for x in (X_L, X_R)])
    parts = [board, nuts]
    if ratio < 1:
        rest = Line([xb, y, 0], [X_R, y, 0], stroke_width=3, color=GREY)      # damped part
        bridge = Rectangle(width=0.14, height=BOARD_H * 0.8, stroke_width=0)
        bridge.set_fill(RED, opacity=1).move_to([xb, y, 0])
        parts += [rest, bridge]
    group = VGroup(*parts)

    string = VMobject(stroke_color=color, stroke_width=4)
    string.set_points_as_corners([[X_L, y, 0], [xb, y, 0]])
    group.add(string)
    if label is not None:
        txt = Text(label, font_size=34).move_to([X_LABEL, y + 0.15, 0])
        group.add(txt)
        if name is not None:
            group.add(Text(name, font_size=22, color=GREY_B).next_to(txt, DOWN, buff=0.1))
    group.set_z_index(1)
    string.set_z_index(2)

    curve = VMobject(stroke_color=color, stroke_width=3)
    curve.set_points_as_corners([[GX0, GY, 0], [GX1, GY, 0]])
    curve.set_z_index(3)
    return {"y": y, "xb": xb, "f": F0 / ratio, "color": color, "group": group,
            "string": string, "curve": curve, "vis": ValueTracker(0), "t0": None}


class MonochordIntervals(MovingCameraScene):
    def construct(self):
        rng = np.random.default_rng(21)
        width = config.frame_width
        height = config.frame_height

        clock = ValueTracker(0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        # ---------------- Monochords ----------------
        m1 = build_monochord(Y1, 1.0, COL1, name="grondtoon", label="1 : 1")
        others = [build_monochord(Y2, r, COL2, name=n, label=l) for r, n, l in INTERVALS]
        monos = [m1] + others

        # ---------------- Air particles (these already exist from the previous scene) ----------------
        y_lo, y_hi = Y_MIN_PARTICLES, height / 2 + 0.3
        base = np.column_stack([
            rng.uniform(-width / 2 - 0.3, width / 2 + 0.3, N),
            rng.uniform(y_lo, y_hi, N),
        ])
        phase = rng.uniform(0, 2 * PI, (N, 2))
        template = Dot(ORIGIN, radius=0.05).points.copy()     # set points directly: much faster than move_to
        dots = []
        for x, y in base:
            d = Dot(ORIGIN, radius=0.05, color=BLUE)
            d.points = template + np.array([x, y, 0.0])
            dots.append(d)
        air = VGroup(*dots)
        air.set_z_index(0)

        air_src = []   # active wave sources: {"pos", "f", "t0"}

        def strike(ms):
            """Pluck the given monochords at the same moment."""
            t = clock.get_value()
            for m in ms:
                m["t0"] = t
                air_src.append({"pos": np.array([(X_L + m["xb"]) / 2, m["y"]]), "f": m["f"], "t0": t})

        # ---------------- One driver updates air, strings and graph ----------------
        xg = np.linspace(GX0, GX1, 500)
        u = np.linspace(0, 1, 60)

        def update_all(_):
            t = clock.get_value()

            # air
            pos = base + THERMAL * np.column_stack([np.sin(1.3 * t + phase[:, 0]),
                                                    np.cos(1.1 * t + phase[:, 1])])
            air_src[:] = [s for s in air_src if t - s["t0"] < SRC_LIFETIME]
            for src in air_src:
                s = t - src["t0"]
                if s <= 0:
                    continue
                d = base - src["pos"]
                r = np.maximum(np.hypot(d[:, 0], d[:, 1]), 1e-3)
                tr = s - r / C                                                   # retarded time
                amp = (A0 * np.sqrt(R_REF / np.maximum(r, R_REF))                # spreading
                       * np.exp(-np.maximum(tr, 0) / TAU)                        # string rings down
                       * np.clip(tr / RAMP, 0, 1))                               # zero ahead of the front
                pos = pos + (amp * np.sin(2 * PI * src["f"] * tr))[:, None] * d / r[:, None]
            for i in range(N):
                dots[i].points = template + np.array([pos[i, 0], pos[i, 1], 0.0])

            # strings and graph curves
            for m in monos:
                xs = X_L + u * (m["xb"] - X_L)
                if m["t0"] is None or t < m["t0"]:
                    ys = np.zeros_like(u)
                    sig = np.zeros_like(xg)
                else:
                    s = t - m["t0"]
                    ys = A_STR * np.exp(-s / TAU) * np.sin(PI * u) * np.sin(2 * PI * m["f"] * s)
                    sg = t - (GX1 - xg) / SCROLL - m["t0"]                       # time the sound was made
                    sig = np.where(sg > 0, np.exp(-np.maximum(sg, 0) / TAU) * np.sin(2 * PI * m["f"] * sg), 0.0)
                m["string"].set_points_as_corners(np.column_stack([xs, m["y"] + ys, np.zeros_like(u)]))
                m["curve"].set_points_as_corners(np.column_stack([xg, GY + GH * sig, np.zeros_like(xg)]))
                m["curve"].set_stroke(opacity=m["vis"].get_value())

        driver = Mobject()
        driver.add_updater(update_all)

        # ---------------- Graph furniture ----------------
        baseline = Line([GX0, GY, 0], [GX1, GY, 0], stroke_width=2, color=GREY)
        g_label = Text("geluid", font_size=26).move_to([GX0 + 0.1, GY + 1.1, 0]).align_to([GX0, 0, 0], LEFT)
        t_label = Text("tijd", font_size=22, color=GREY_B).next_to(baseline.get_end(), DOWN, buff=0.15)
        graph_static = VGroup(baseline, g_label, t_label).set_z_index(3)

        # ---------------- Timeline ----------------
        self.add(air, driver, m1["group"], *[m["curve"] for m in monos])

        # Start: the camera comes from the previous scene and settles on the top view.
        # (Placeholder zoom-out; adapt it to however 2.1.1 ends.)
        frame = self.camera.frame
        frame.save_state()
        frame.set_width(6).move_to([0, Y1, 0])
        self.wait(1)
        self.play(Restore(frame), run_time=3)
        self.wait(1)

        # 1. Original monochord is struck, graph appears at the bottom
        self.play(FadeIn(graph_static), run_time=1)
        strike([m1])
        self.play(m1["vis"].animate.set_value(1), run_time=0.5)
        self.wait(HOLD)

        # 2. Second monochord with the bridge at 1/2, 2/3, 3/4
        prev = None
        for m2 in others:
            fades = [FadeOut(prev["group"])] if prev is not None else []
            self.play(m1["vis"].animate.set_value(0),
                      *([prev["vis"].animate.set_value(0)] if prev is not None else []),
                      *fades, run_time=1)
            self.wait(2.5)                                       # old waves die out
            self.play(FadeIn(m2["group"]), run_time=1.5)
            self.wait(1)
            strike([m1, m2])                                     # both struck at the same moment
            self.play(m1["vis"].animate.set_value(1), m2["vis"].animate.set_value(1), run_time=0.5)
            self.wait(HOLD)
            prev = m2

        driver.clear_updaters()