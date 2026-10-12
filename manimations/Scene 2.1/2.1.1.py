"""   - Animatie 2.1: Het monochord, de snaar en het geluid dat daaruit komt. **Alex**
     - 2.1.1: Wat is een monochord? Pythagoras tokkelt de snaar, de lucht gaat trillen

Render:  manim -pql 2.1.1.py MonochordPluck
"""

from manim import *
import numpy as np

N = 2000  # Amount of air particles (raise for a denser look, lower if rendering is slow)

# --- Wave parameters (spherical wave, emitted from the monochord, same as the bell in 1.1.1) ---
C = 2.5            # propagation speed [scene units / s]
WL = 1.4           # wavelength [scene units]
FREQ = C / WL      # frequency [Hz]  (also the frequency of the string, shown in slow motion)
A0 = 0.16          # displacement amplitude close to the source
R_REF = 1.5        # amplitude falls off as sqrt(R_REF / r) beyond this radius
TAU = 3.0          # ring-down time of the string [s]
RAMP = 0.4         # time over which the emission fades in [s]
THERMAL = 0.03     # small random jiggle of the air before the pluck

# --- Monochord geometry ---
BOX_CENTER = np.array([0.8, -2.35, 0])   # sound box
BOX_W, BOX_H = 7.2, 0.9
X_L, X_R = -2.4, 4.0                     # x of the two fixed bridges
L_STR = X_R - X_L                        # vibrating length of the string
BRIDGE_H = 0.30                          # height of the fixed bridges
Y_STR = BOX_CENTER[1] + BOX_H / 2 + BRIDGE_H   # y of the string at rest
SRC = np.array([0.8, -2.0, 0])           # point the sound seems to come from
STRING_COL = "#EADFB4"

# --- Plucked string (sum of standing waves, n = 1 is the fundamental) ---
PLUCK_P = 0.15     # plucked at this fraction of the string length (seen from the left bridge)
PLUCK_H = 0.35     # how far the string is pulled up [scene units]
N_MODES = 8        # number of harmonics in the vibrating string
N_PTS = 150        # points along the string

# --- Pythagoras ---
PERSON_POS = np.array([-4.4, -3.9, 0])   # point between his feet
PERSON_SCALE = 1.3
SKIN, ROBE, HAIR = "#E3B48A", "#ECECEC", "#D8D8D8"
SHOULDER = PERSON_POS + PERSON_SCALE * np.array([0.5, 1.75, 0])   # right shoulder (the plucking arm)
ARM = 1.1 * PERSON_SCALE                 # length of upper arm and forearm
REST_HAND = np.array([-3.2, -1.5, 0])    # hand held in front of the chest
X_PLUCK = X_L + PLUCK_P * L_STR          # where the hand touches the string


def build_monochord():
    """Monochord drawn from Manim primitives.

    Returns (base, bridges, string):
      base    = [table, box, soundhole]
      bridges = [left, right, movable]  (the movable bridge is parked, it is used later)
      string  = the vibrating string (redrawn every frame)
    """
    tabletop = Rectangle(width=8.0, height=0.2, fill_color="#5C4033", fill_opacity=1,
                         stroke_color="#3B2A20", stroke_width=2).move_to([0.8, -2.9, 0])
    legs = VGroup(*[Rectangle(width=0.2, height=0.9, fill_color="#5C4033", fill_opacity=1,
                              stroke_color="#3B2A20", stroke_width=2).move_to([x, -3.45, 0])
                    for x in (-2.9, 4.5)])
    box = Rectangle(width=BOX_W, height=BOX_H, fill_color="#A8743F", fill_opacity=1,
                    stroke_color="#6B4423", stroke_width=4).move_to(BOX_CENTER)
    hole = Circle(radius=0.18, fill_color="#2B1A0E", fill_opacity=1,
                  stroke_color="#6B4423", stroke_width=3).move_to(BOX_CENTER)
    top = BOX_CENTER[1] + BOX_H / 2

    def bridge(x, h, col):
        return Polygon([x - 0.18, top, 0], [x + 0.18, top, 0], [x, top + h, 0],
                       fill_color=col, fill_opacity=1, stroke_color="#8A6A3A", stroke_width=2)

    bridges = VGroup(bridge(X_L, BRIDGE_H, "#D9B382"),
                     bridge(X_R, BRIDGE_H, "#D9B382"),
                     bridge(3.1, 0.18, "#E8A33D"))      # movable bridge, parked below the string

    string = VMobject(stroke_color=STRING_COL, stroke_width=4)
    string.set_points_as_corners([[X_L, Y_STR, 0], [X_R, Y_STR, 0]])
    return VGroup(legs, tabletop, box, hole), bridges, string


def build_pythagoras():
    """Pythagoras: white robe, long grey beard and hair, golden headband. Right arm is built separately."""
    robe = Polygon([-0.55, 1.9, 0], [0.55, 1.9, 0], [0.85, 0.1, 0], [-0.85, 0.1, 0],
                   fill_color=ROBE, fill_opacity=1, stroke_color=GREY_B, stroke_width=3)
    drape = Polygon([-0.55, 1.9, 0], [-0.15, 1.9, 0], [0.78, 0.6, 0], [0.5, 0.55, 0],
                    fill_color="#3C5A99", fill_opacity=0.9, stroke_width=0)
    feet = VGroup(*[Ellipse(width=0.6, height=0.24, fill_color="#7B4B2A", fill_opacity=1,
                            stroke_width=0).move_to([x, 0.05, 0]) for x in (-0.35, 0.35)])
    left_arm = VGroup(
        Line([-0.5, 1.75, 0], [-0.62, 0.95, 0], color=ROBE, stroke_width=18),
        Dot([-0.62, 0.9, 0], radius=0.09, color=SKIN),
    )
    hair = VGroup(
        Circle(radius=0.47, fill_color=HAIR, fill_opacity=1, stroke_width=0).move_to([0, 2.5, 0]),
        *[Ellipse(width=0.25, height=0.9, fill_color=HAIR, fill_opacity=1,
                  stroke_width=0).move_to([x, 2.15, 0]) for x in (-0.42, 0.42)],
    )
    neck = Rectangle(width=0.2, height=0.2, fill_color=SKIN, fill_opacity=1,
                     stroke_width=0).move_to([0, 1.97, 0])
    head = Circle(radius=0.42, fill_color=SKIN, fill_opacity=1, stroke_width=0).move_to([0, 2.45, 0])
    band = Line([-0.37, 2.62, 0], [0.37, 2.62, 0], color="#C9A227", stroke_width=8)
    eyes = VGroup(*[Dot([x, 2.5, 0], radius=0.035, color="#222222") for x in (-0.15, 0.15)])
    brows = VGroup(Line([-0.23, 2.57, 0], [-0.08, 2.59, 0], color=GREY_C, stroke_width=3),
                   Line([0.08, 2.59, 0], [0.23, 2.57, 0], color=GREY_C, stroke_width=3))
    nose = Dot([0, 2.42, 0], radius=0.05, color="#D49E73")

    # beard: a crescent that hangs from the cheeks down below the chin
    c = np.array([0, 2.45, 0])
    offs = np.array([[-0.38, -0.05, 0], [-0.36, -0.40, 0], [-0.18, -0.85, 0], [0, -1.00, 0],
                     [0.18, -0.85, 0], [0.36, -0.40, 0], [0.38, -0.05, 0],
                     [0.20, -0.22, 0], [0, -0.28, 0], [-0.20, -0.22, 0], [-0.38, -0.05, 0]])
    beard = VMobject()
    beard.set_points_smoothly(c + offs)
    beard.set_fill("#F2F2F2", opacity=1).set_stroke(GREY_B, width=2)

    person = VGroup(robe, drape, feet, left_arm, hair, neck, head, band, eyes, brows, nose, beard)
    return person.scale(PERSON_SCALE, about_point=ORIGIN).shift(PERSON_POS)


def build_arm():
    """Right arm, redrawn every frame by update_arm(). Submobjects: [upper, forearm, elbow, hand]."""
    upper = Line(ORIGIN, RIGHT, color=ROBE, stroke_width=18)
    fore = Line(ORIGIN, RIGHT, color=SKIN, stroke_width=12)
    elbow = Dot(radius=0.08, color=ROBE)
    hand = Dot(radius=0.11, color=SKIN)
    return VGroup(upper, fore, elbow, hand)


def update_arm(arm, hand_target):
    """Two-segment arm (shoulder -> elbow -> hand); the elbow always bends downwards."""
    v = hand_target - SHOULDER
    u = v / np.linalg.norm(v)
    d = min(np.linalg.norm(v), 2 * ARM * 0.999)           # cannot reach further than the arm is long
    hand = SHOULDER + u * d
    elbow = SHOULDER + u * d / 2 + np.array([u[1], -u[0], 0]) * np.sqrt(ARM ** 2 - (d / 2) ** 2)
    arm[0].put_start_and_end_on(SHOULDER, elbow)
    arm[1].put_start_and_end_on(elbow, hand)
    arm[2].move_to(elbow)
    arm[3].move_to(hand)


def pull_height(s):
    """How far the hand has pulled the string up, as a function of time s relative to the release."""
    if s < -0.7:
        return 0.0
    if s < 0:
        return PLUCK_H * smooth((s + 0.7) / 0.7)
    return PLUCK_H


def hand_pos(s):
    """Position of the hand as a function of time s relative to the moment the string is released."""
    touch = np.array([X_PLUCK, Y_STR, 0])
    if s < -1.5:                                           # waiting in front of the chest
        return REST_HAND
    if s < -0.7:                                           # reach for the string
        return interpolate(REST_HAND, touch, smooth((s + 1.5) / 0.8))
    if s < 0:                                              # pull the string up
        return touch + UP * pull_height(s)
    release = touch + UP * PLUCK_H                         # let go, flick away, back to rest
    return interpolate(release, REST_HAND, rush_from(min(s / 1.0, 1.0)))


class MonochordPluck(Scene):
    def construct(self):
        rng = np.random.default_rng(3)
        width = config.frame_width
        height = config.frame_height

        # Global clock so everything (string, arm, air) stays in sync
        clock = ValueTracker(0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        pluck_t = [None]    # time at which the string is released, set when the pluck is scheduled
        air_on = [False]    # air only starts moving once it is on screen

        # ---------------- Objects ----------------
        base, bridges, string = build_monochord()
        person = build_pythagoras()
        arm = build_arm()
        update_arm(arm, REST_HAND)

        # ---------------- String shape ----------------
        xs = np.linspace(0, 1, N_PTS)                       # position along the string, 0 .. 1
        tri = np.where(xs < PLUCK_P, xs / PLUCK_P, (1 - xs) / (1 - PLUCK_P))   # triangle shape under the hand

        def string_y(s):
            """Displacement of the string. Pulled into a triangle, then released: the triangle is a sum
            of standing waves n * pi * x / L, each with its own frequency n * FREQ (higher ones die out faster)."""
            if s < 0:
                return PLUCK_H * smooth(np.clip((s + 0.7) / 0.7, 0, 1)) * tri
            y = np.zeros(N_PTS)
            for n in range(1, N_MODES + 1):
                b = 2 * PLUCK_H / (n ** 2 * PI ** 2 * PLUCK_P * (1 - PLUCK_P)) * np.sin(n * PI * PLUCK_P)
                y += b * np.cos(2 * PI * n * FREQ * s) * np.exp(-s * n ** 2 / TAU) * np.sin(n * PI * xs)
            return y

        # ---------------- Air particles (none inside the monochord or behind Pythagoras) ----------------
        base_p = np.zeros((0, 2))
        while len(base_p) < N:
            cand = np.column_stack([
                rng.uniform(-width / 2 - 0.3, width / 2 + 0.3, N),
                rng.uniform(-height / 2 - 0.3, height / 2 + 0.3, N),
            ])
            in_instrument = ((cand[:, 0] > -3.3) & (cand[:, 0] < 4.9) &
                             (cand[:, 1] > -3.05) & (cand[:, 1] < -1.0))
            in_person = ((cand[:, 0] > -5.7) & (cand[:, 0] < -3.25) &
                         (cand[:, 1] > -4.2) & (cand[:, 1] < 0.1))
            cand = cand[~(in_instrument | in_person)]
            base_p = np.vstack([base_p, cand])
        base_p = base_p[:N]

        rel = base_p - SRC[:2]
        r0 = np.hypot(rel[:, 0], rel[:, 1])                # distance to the sound source
        unit = rel / r0[:, None]                           # radial unit vectors
        phase = rng.uniform(0, 2 * PI, (N, 2))             # random phases for the jiggle

        template = Dot(ORIGIN, radius=0.05).points.copy()  # set points directly: much faster than move_to
        dots = []
        for x, y in base_p:
            d = Dot(ORIGIN, radius=0.05, color=BLUE)
            d.points = template + np.array([x, y, 0.0])
            dots.append(d)
        air = VGroup(*dots)

        # One driver updates everything (a plain updater would be paused while the mobject fades in)
        def update_all(_):
            t = clock.get_value()
            s = t - pluck_t[0] if pluck_t[0] is not None else -10

            string.set_points_as_corners(np.column_stack([X_L + L_STR * xs, Y_STR + string_y(s),
                                                          np.zeros(N_PTS)]))
            update_arm(arm, hand_pos(s))

            if air_on[0]:
                pos = base_p + THERMAL * np.column_stack([np.sin(1.3 * t + phase[:, 0]),
                                                          np.cos(1.1 * t + phase[:, 1])])
                if s > 0:
                    # Retarded time: the wave reaches a particle at distance r0 after r0 / C
                    tr = s - r0 / C
                    amp = (A0 * np.sqrt(R_REF / np.maximum(r0, R_REF))   # spreading
                           * np.exp(-np.maximum(tr, 0) / TAU)            # string rings down
                           * np.clip(tr / RAMP, 0, 1))                   # zero ahead of the front
                    disp = amp * np.sin(2 * PI * FREQ * tr)
                    pos = pos + disp[:, None] * unit                     # radial (longitudinal) motion
                for i in range(N):
                    dots[i].points = template + np.array([pos[i, 0], pos[i, 1], 0.0])

        driver = Mobject()
        driver.add_updater(update_all)
        self.add(driver)

        # ---------------- Layers ----------------
        air.set_z_index(0)
        base.set_z_index(2)
        person.set_z_index(2)
        bridges.set_z_index(3)
        string.set_z_index(4)
        arm.set_z_index(5)

        # ---------------- Texts ----------------
        title = Text("Het monochord", font_size=52).to_edge(UP)
        subtitle = Text("één snaar, gespannen over een klankkast", font_size=28, color=GREY_B)
        subtitle.next_to(title, DOWN, buff=0.2)

        def make_label(text, pos, end, from_side=DOWN):
            t = Text(text, font_size=26).move_to(pos)
            a = Arrow(t.get_edge_center(from_side) + from_side * 0.08, end, buff=0,
                      stroke_width=3, tip_length=0.15, color=GREY_B)
            return VGroup(t, a)

        labels = VGroup(
            make_label("vaste brug", [X_L, -0.35, 0], [X_L, Y_STR + 0.05, 0]),
            make_label("snaar", [0.8, -0.35, 0], [0.8, Y_STR + 0.05, 0]),
            make_label("beweegbare brug", [3.1, -0.35, 0], [3.1, -1.75, 0]),
            make_label("klankkast", [5.9, -2.35, 0], [4.45, -2.35, 0], from_side=LEFT),
        )
        name = Text("Pythagoras", font_size=30).move_to([PERSON_POS[0], 0.3, 0])

        # ---------------- 1. What is a monochord? ----------------
        self.play(Write(title), run_time=1.2)
        self.play(FadeIn(subtitle, shift=UP * 0.2), run_time=1)
        self.wait(0.5)
        self.play(FadeIn(base, shift=UP * 0.3), run_time=1.5)
        self.play(FadeIn(bridges), FadeIn(string), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(l, shift=DOWN * 0.2) for l in labels],
                              lag_ratio=0.5, run_time=3))
        self.wait(2.5)
        self.play(FadeOut(labels), run_time=1)

        # ---------------- 2. Pythagoras appears next to it ----------------
        self.play(FadeIn(person, shift=RIGHT * 0.5), FadeIn(arm), run_time=1.5)
        self.play(FadeIn(name), run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(name), run_time=1)

        # ---------------- 3. Air surrounds the monochord ----------------
        air_on[0] = True
        self.play(FadeIn(air), run_time=2)
        self.wait(2)

        # ---------------- 4. Pluck: spherical wave leaves the monochord ----------------
        pluck_t[0] = clock.get_value() + 1.6   # hand reaches out and pulls, string is released 1.6 s from now
        self.wait(1.6 + 11)

        driver.clear_updaters()