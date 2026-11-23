"""All shots of the film, in order. Each shot: (duration_s, function(ctx, u, d), transition-in)."""
import math

from engine import *  # noqa: F401,F403
from sets import *  # noqa: F401,F403

SHOTS = []


def shot(dur, trans="x"):
    def deco(fn):
        SHOTS.append((dur, fn, trans))
        return fn
    return deco


# ================================================================ 1. Dawn over Medina (0-60)
@shot(24, "b")
def s1_city(ctx, u, d):
    k = u / d
    with Cam(ctx, 1.0 + 0.15 * ease(k), 640, 430):
        sky(ctx, NIGHT, horizon=560, t=ease(k) * 0.8, pal2=DAWN)
        stars(ctx, u, 1 - 0.7 * k, y_max=420)
        glow(ctx, 640, 560, 700, C("#e8a06a"), 0.25 * k)
        skyline(ctx, 520, night=0.8 - 0.3 * k, seed=4, scale=0.75, base=shade(MUD, 0.8))
        masjid_ext(ctx, 470, 590, 340, 70, night=0.7 - 0.3 * k)
        skyline(ctx, 640, night=0.75 - 0.3 * k, seed=5, scale=1.2, lit_t=1 - k * 0.5, x0=-300, x1=420)
        skyline(ctx, 640, night=0.75 - 0.3 * k, seed=6, scale=1.2, lit_t=1 - k * 0.5, x0=860, x1=W + 300)
        for px in (300, 900, 1100, 120):
            palm(ctx, px, 640, 230, u, col=C("#141626"))
        ground_band(ctx, 638, C("#151624"))
    vignette(ctx)
    a = ramp(u, 1.5, 3.5) * (1 - ramp(u, 6.5, 8.0))
    if a > 0:
        text_center(ctx, "Abu Bakr", W / 2, 250, 64, GOLD, a, bold=True)
        text_center(ctx, "Mirësia e Fshehtë", W / 2, 320, 38, (1, 0.96, 0.88), a)


@shot(14)
def s1_street(ctx, u, d):
    with Cam(ctx, 1.05, 640 + u * 4, 360):
        street_side(ctx, u, night=0.85, pan=0, ground=560, lit_t=0.0, seed=41, palms=True)
        house(ctx, 560, 560, 180, 150, MUD, win=(0.4, 0.3, 24, 28), lit=0.9 + 0.1 * math.sin(u * 7), night=0.8,
              seed=3)
        glow(ctx, 640, 470, 200, WARM, 0.2)
        dust(ctx, u, 30, (300, 300, 700, 300), (1, 0.85, 0.6), 0.3)
    vignette(ctx)


@shot(22)
def s1_room(ctx, u, d):
    with Cam(ctx, 1.0 + 0.04 * u / d, 640, 380):
        room(ctx, u, sky_pal=NIGHT, dawn=0.2 * u / d)
        lift = ramp(u, d - 7, d - 3)
        person_side(ctx, 260, 600, 230, pose_mix("sit_hug", "sit_up", lift), TOWN[4], facing=1, dark=0.75)
        sleeper(ctx, 980, 610, 230, u)
    vignette(ctx, 0.7)


# ================================================================ 2. The adhan (60-110)
@shot(14, "b")
def s2_bilal(ctx, u, d):
    k = u / d
    with Cam(ctx, 1.1, 640, lerp(520, 360, ease(k))):
        sky(ctx, DAWN, horizon=700, t=k * 0.5, pal2=MORNING)
        stars(ctx, u, 0.5 * (1 - k), y_max=300)
        glow(ctx, 640, 700, 800, C("#ffb070"), 0.3)
        skyline(ctx, 720, night=0.5, seed=9, scale=0.9)
        fill_rect(ctx, 380, 560, 520, 400, shade(MUD, 0.55))
        fill_rect(ctx, 380, 552, 520, 12, shade(MUD, 0.4))
        info = person_back(ctx, 640, 560, 300, BILAL, sway=math.sin(u * 0.9) * 1.2, dark=0.8)
        hx, hy = info["head"]
        for side in (-1, 1):
            capsule(ctx, (640 + side * 48, 560 - 300 * 0.8), (hx + side * 34, hy + 30), 20, shade(BILAL.cloak, 0.8))
            ellipse(ctx, hx + side * 30, hy + 22, 11, 13, shade(BILAL.skin, 0.8))
    vignette(ctx, 0.45)


@shot(10)
def s2_doors(ctx, u, d):
    street_side(ctx, u, night=0.55, ground=600, seed=51, palms=False, pal=mix_pal(DAWN, NIGHT, 0.4))
    for i, dx in enumerate([180, 470, 760, 1050]):
        o = ramp(u, 0.8 + i * 1.6, 2.3 + i * 1.6)
        fill_rect(ctx, dx, 480, 70, 120, C("#2a1a10"))
        if o > 0:
            fill_rect(ctx, dx, 480, 70, 120, WARM, 0.85 * o)
            poly(ctx, [(dx, 600), (dx + 70, 600), (dx + 120, 700), (dx - 50, 700)], WARM, 0.25 * o)
            glow(ctx, dx + 35, 560, 160, WARM, 0.35 * o)
        fill_rect(ctx, dx, 480, 70 * (1 - o * 0.85), 120, shade(WOOD, 0.8))
    w = ramp(u, 6.5, 10)
    if w > 0:
        person_side(ctx, 215 + w * 160, 640, 170, walk_pose(u * 5), TOWN[1], dark=0.7)
    vignette(ctx)


@shot(12)
def s2_walkers(ctx, u, d):
    pan = u * 70
    street_side(ctx, u, night=0.45, pan=pan, ground=560, seed=61, pal=mix_pal(DAWN, MORNING, 0.2))
    for i, (x, s, look) in enumerate([(250, 180, TOWN[0]), (420, 170, TOWN[3]), (640, 185, TOWN[1]),
                                       (860, 175, TOWN[5]), (1040, 165, TOWN[2])]):
        ph = u * 4.2 + i * 1.3
        info = person_side(ctx, x + math.sin(u * 0.5 + i) * 8, 650 + (i % 2) * 18, s, walk_pose(ph), look,
                           dark=0.75)
        if i % 2 == 0:
            lantern(ctx, info["hand"][0], info["hand"][1] + 18, 1.0, u, seed=i)
    vignette(ctx)


@shot(7)
def s2_oldman(ctx, u, d):
    street_side(ctx, u, night=0.35, pan=u * 25, ground=560, seed=71, pal=mix_pal(DAWN, MORNING, 0.35))
    old = walk_pose(u * 2.4, amp=0.5)
    old["torso"] = 16
    info = person_side(ctx, 560 + u * 6, 660, 190, old, Look(C("#cfc6b4"), C("#6a5a48"), C("#f3f1ea")), dark=0.8)
    capsule(ctx, info["hand"], (info["hand"][0] + 22, 660), 5, WOOD)
    person_side(ctx, 680 + u * 6, 660, 120, walk_pose(u * 2.4 + 2, amp=0.6), TOWN[4], dark=0.8)
    vignette(ctx)


@shot(7)
def s2_doorway(ctx, u, d):
    fill_rect(ctx, -100, -100, W + 200, H + 200, C("#20180f"))
    wall_texture(ctx, 0, 0, W, 560, C("#20180f"), n=40)
    ctx.save()
    ctx.rectangle(520, 180, 240, 420)
    ctx.clip()
    sky(ctx, DAWN, horizon=600, t=0.4, pal2=MORNING)
    skyline(ctx, 600, night=0.5, seed=13, scale=0.8)
    ctx.restore()
    straw_floor(ctx, 600, 160, dark=0.5)
    for i in range(4):
        t0 = i * 1.6
        w = ramp(u, t0, t0 + 3.5)
        if 0 < w < 1:
            x = lerp(700, 260, w)
            sc = lerp(220, 300, w)
            person_side(ctx, x, lerp(600, 680, w), sc, walk_pose(u * 4.5 + i), TOWN[i], facing=-1,
                        silhouette=C("#120c07"))
    glow(ctx, 640, 400, 300, C("#ffcf9a"), 0.15)
    vignette(ctx, 0.6)


# ================================================================ 3. Fajr prayer (110-160)
@shot(20, "b")
def s3_rows_back(ctx, u, d):
    with Cam(ctx, 1.0, 640 + math.sin(u * 0.15) * 60, 360):
        masjid_interior(ctx, u, day=0.1, dark=0.75, floor_y=400)
        holy_light(ctx, 640, 300, 14, u, 1.0)
        glow(ctx, 640, 330, 500, GOLD, 0.12)
        for row, (y, s, n) in enumerate([(470, 120, 9), (560, 175, 7), (690, 260, 5)]):
            for i in range(n):
                x = 640 + (i - (n - 1) / 2) * s * 0.5
                look = TOWN[(i + row) % len(TOWN)]
                if row == 1 and i == 4:
                    look = ABU_BAKR
                person_back(ctx, x, y, s, look, dark=lerp(0.55, 0.85, row / 2), bow=0.15)
    vignette(ctx, 0.6)


PRAYER = [(0, "qiyam"), (4, "qiyam"), (5.5, "ruku"), (9, "ruku"), (10.5, "qiyam"), (12, "qiyam"),
          (13.8, "sujud"), (17, "sujud"), (18.5, "jalsa"), (20, "jalsa"), (21.5, "sujud"), (24.5, "sujud"),
          (26, "jalsa"), (40, "jalsa")]


def prayer_pose(u):
    for (t0, p0), (t1, p1) in zip(PRAYER, PRAYER[1:]):
        if t0 <= u < t1:
            return pose_mix(p0, p1, (u - t0) / (t1 - t0))
    return POSES["jalsa"]


@shot(30)
def s3_rows_side(ctx, u, d):
    with Cam(ctx, 1.0 + 0.05 * u / d, 640 - u * 3, 380):
        masjid_interior(ctx, u, day=0.25, dark=0.8, floor_y=420, pillars=True)
        glow(ctx, 1050, 200, 400, C("#ffcf9a"), 0.15)
        holy_light(ctx, 120, 470, 13, u, 1.0)
        p = prayer_pose(u)
        for i in range(8):
            look = ABU_BAKR if i == 2 else TOWN[i % len(TOWN)]
            person_side(ctx, 260 + i * 125, 640, 200, p, look, facing=-1, dark=0.62)
    tint(ctx, C("#1a2440"), 0.1)
    vignette(ctx, 0.6)


# ================================================================ 4. A day in Medina (160-220)
@shot(12, "b")
def s4_sunrise(ctx, u, d):
    k = u / d
    sky(ctx, MORNING, horizon=560)
    glow(ctx, 640, 520 - k * 60, 300, GOLD, 0.8)
    ellipse(ctx, 640, 520 - k * 60, 45, 45, C("#fff1c9"))
    skyline(ctx, 560, seed=17, scale=0.8)
    masjid_ext(ctx, 420, 610, 440, 90)
    ground_band(ctx, 608, SAND)
    for i in range(6):
        w = ramp(u, i * 0.8, i * 0.8 + 9)
        if w <= 0:
            continue
        side = -1 if i % 2 else 1
        x = 640 + side * (40 + w * 520)
        person_side(ctx, x, 660 + (i % 3) * 14, 120, walk_pose(u * 4 + i), TOWN[i], facing=side, dark=0.9)
    vignette(ctx, 0.35)


@shot(12)
def s4_shop(ctx, u, d):
    sky(ctx, DAY, horizon=300)
    fill_rect(ctx, 0, 120, W, 500, C("#b8905f"))
    wall_texture(ctx, 0, 120, W, 500, C("#b8905f"))
    fill_rect(ctx, 250, 260, 520, 300, C("#3b2a1a"))
    o = ramp(u, 0.5, 3)
    for side in (-1, 1):
        cx = 510 + side * 130
        w = 260 * (1 - o * 0.85)
        fill_rect(ctx, cx - w / 2, 260, w, 300, shade(WOOD, 1.1))
    if o > 0.3:
        for i in range(30):
            date_fruit(ctx, 330 + (i % 10) * 18, 500 - (i // 10) * 12, 12, 0.3)
        for i, c in enumerate([C("#9c3d2b"), C("#3a5f7d"), C("#d8b25a")]):
            fill_rect(ctx, 560 + i * 50, 420, 40, 120, c)
    ground_band(ctx, 600, SAND)
    p = dict(POSES["stand"])
    p["arm"] = 40 + 25 * math.sin(u * 2)
    p["el"] = 40
    p["torso"] = 8
    person_side(ctx, 900, 680, 230, p, TOWN[3], facing=-1)
    vignette(ctx, 0.35)


@shot(10)
def s4_goat(ctx, u, d):
    street_side(ctx, u, night=0, pan=u * 60, ground=560, seed=81, pal=DAY)
    info = person_side(ctx, 700, 670, 130, walk_pose(u * 5), TOWN[4], facing=1)
    goat(ctx, 560, 675, 90, u, facing=1)
    ctx.set_line_width(2)
    setc(ctx, C("#5a3b22"))
    ctx.move_to(*info["hand2"])
    ctx.curve_to(640, 640, 620, 640, 600, 615)
    ctx.stroke()
    vignette(ctx, 0.3)


@shot(8)
def s4_water(ctx, u, d):
    sky(ctx, DAY, horizon=520)
    skyline(ctx, 560, seed=91, scale=0.7)
    palm(ctx, 700, 580, 280, u)
    ground_band(ctx, 560, SAND)
    p = walk_pose(u * 3.5)
    p["arm"], p["el"] = 175, -10
    info = person_side(ctx, 300 + u * 70, 610, 140, p, WOMAN_FAR, facing=1)
    hx, hy = info["head"]
    ellipse(ctx, hx, hy - 22, 18, 16, C("#8a5a32"))
    vignette(ctx, 0.3)


@shot(18)
def s4_abubakr_alley(ctx, u, d):
    vx, vy = alley(ctx, u, night=0.0)
    k = ramp(u, 0, 13)
    turn = ramp(u, 13, 16)
    z = lerp(0.0, 0.92, k)
    x = lerp(600, vx + 10, k) + turn * 40
    y = lerp(700, vy + 40, z)
    s = lerp(330, 40, z)
    if turn < 1:
        person_back(ctx, x, y, s, ABU_BAKR, step=u * 4.5, sway=math.sin(u * 4.5) * 2, a=1 - turn)
        ellipse(ctx, x + s * 0.2, y - s * 0.42, s * 0.07, s * 0.06, C("#e8dcc0"), 1 - turn)
    vignette(ctx, 0.35)


# ================================================================ 5. Back in the masjid (220-270)
@shot(15, "b")
def s5_return(ctx, u, d):
    masjid_interior(ctx, u, day=1.0, floor_y=430)
    for i in range(5):
        w = ramp(u, i * 1.5, i * 1.5 + 6)
        sit = ramp(u, i * 1.5 + 6, i * 1.5 + 7.5)
        x = lerp(1350, 300 + i * 170, w)
        if sit < 1:
            person_side(ctx, x, 650, 200, pose_mix(walk_pose(u * 4.5 + i), "jalsa", sit), TOWN[i], facing=-1,
                        dark=0.9)
        else:
            person_side(ctx, x, 650, 200, "jalsa", TOWN[i], facing=-1, dark=0.9)
    vignette(ctx, 0.35)


@shot(27)
def s5_circle(ctx, u, d):
    with Cam(ctx, 1.0 + 0.05 * u / d, 640, 400):
        circle_scene(ctx, u, light_i=1.0, rot=math.sin(u * 0.08) * 8, bow=0.3, day=0.8)
    vignette(ctx, 0.45)


@shot(8)
def s5_light(ctx, u, d):
    fill_rect(ctx, -10, -10, W + 20, H + 20, C("#2c2116"))
    glow(ctx, 640, 360, 600, GOLD, 0.2)
    holy_light(ctx, 640, 360, 30, u, 1.0 + 0.1 * math.sin(u))
    dust(ctx, u, 80, (0, 0, W, H), (1, 0.92, 0.75), 0.5)
    vignette(ctx, 0.6)


# ================================================================ 6. The four questions (270-390)
def memory(ctx, u, which):
    if which == 0:      # fasting: sitting in the noon heat, water untouched
        sky(ctx, DAY, horizon=500)
        glow(ctx, 1000, 120, 500, (1, 0.95, 0.7), 0.5)
        house(ctx, 250, 600, 420, 300, MUD, seed=8)
        poly(ctx, [(250, 600), (670, 600), (760, 700), (250, 700)], (0, 0, 0), 0.0)
        ground_band(ctx, 600, SAND)
        fill_rect(ctx, 250, 600, 420, 120, (0, 0, 0), 0.18)
        person_side(ctx, 470, 650, 210, "jalsa", ABU_BAKR, facing=1)
        ellipse(ctx, 600, 630, 28, 34, C("#8a5a32"))
        ellipse(ctx, 650, 645, 30, 10, C("#6b4b2e"))
    elif which == 1:    # following a funeral
        sky(ctx, MORNING, horizon=520, t=0.5, pal2=DAY)
        skyline(ctx, 560, seed=33, scale=0.8)
        ground_band(ctx, 560, SAND)
        xs = [380 + u * 25, 520 + u * 25, 640 + u * 25, 780 + u * 25]
        for i, x in enumerate(xs):
            p = walk_pose(u * 3 + i, amp=0.6)
            p["arm"], p["el"] = 170, -20
            person_side(ctx, x, 650, 180, p, TOWN[i], facing=1, dark=0.85)
        fill_rect(ctx, xs[0] - 20, 455, xs[-1] - xs[0] + 40, 12, WOOD)
        ellipse(ctx, (xs[0] + xs[-1]) / 2, 445, (xs[-1] - xs[0]) / 2, 22, C("#f4f1ea"))
        person_side(ctx, 220 + u * 25, 650, 180, walk_pose(u * 3, amp=0.6), ABU_BAKR, facing=1)
    elif which == 2:    # feeding a poor man
        sky(ctx, DAY, horizon=400)
        house(ctx, 500, 640, 520, 420, shade(MUD, 0.9), door=True, seed=2)
        ground_band(ctx, 640, SAND)
        poor = Look(C("#8a7b66"), None, C("#7a6e5c"))
        person_side(ctx, 820, 690, 190, "sit_hug", poor, facing=-1, dark=0.9)
        give = ramp(u, 0.5, 2.5)
        p = pose_mix("jalsa", "kneel_give", give)
        info = person_side(ctx, 560, 690, 210, p, ABU_BAKR, facing=1)
        ellipse(ctx, info["hand"][0] + 12, info["hand"][1], 26, 12, C("#d7a35f"))
    else:               # visiting the sick
        room(ctx, u, sky_pal=DAY, lamp=0.4, dawn=1.0, jug=False)
        ill = Look(C("#d8d0c0"), None, C("#efece4"))
        sleeper(ctx, 760, 620, 300, u, ill)
        p = dict(POSES["kneel_give"])
        p["arm"], p["el"] = 55, 30
        person_side(ctx, 420, 650, 230, p, ABU_BAKR, facing=1)
    # soft memory look
    tint(ctx, C("#f3e2c0"), 0.28)
    vignette(ctx, 0.7)


QUESTION_SHOTS = []


def make_question(qi):
    @shot(9, "b" if qi == 0 else "x")
    def q_wide(ctx, u, d):
        li = 1.0 + 0.6 * ramp(u, 2.5, 4) * (1 - ramp(u, 8, 9))
        with Cam(ctx, 1.06, 640, 400):
            circle_scene(ctx, u + qi * 30, light_i=li, rot=-6 + qi * 4, bow=0.7, day=0.75)
        vignette(ctx, 0.45)

    @shot(7)
    def q_pan(ctx, u, d):
        with Cam(ctx, 1.25, 400 + u * 60, 420):
            masjid_interior(ctx, u, day=0.7, floor_y=420, dark=0.85)
            for i in range(9):
                p = dict(POSES["bow_sit"])
                p["head"] = 38 + math.sin(u * 0.7 + i) * 4
                person_side(ctx, 120 + i * 150, 640, 220, p, TOWN[(i + qi) % len(TOWN)], facing=-1, dark=0.7)
        vignette(ctx, 0.5)

    @shot(5)
    def q_memory(ctx, u, d):
        memory(ctx, u, qi)

    @shot(9)
    def q_hand(ctx, u, d):
        with Cam(ctx, 1.0, 640, 420):
            masjid_interior(ctx, u, day=0.7, floor_y=420, dark=0.8)
            holy_light(ctx, 640, 300, 14, u, 1.0)
            glow(ctx, 640, 330, 500, GOLD, 0.12)
            for i, x in enumerate([200, 420, 860, 1080]):
                person_back(ctx, x, 700, 300, TOWN[(i + qi) % len(TOWN)], sit=1, bow=0.8, dark=0.55)
            r = ramp(u, 1.0, 3.0)
            person_back(ctx, 640, 720, 340, ABU_BAKR, sit=1, raise_hand=r, bow=0.3, dark=0.8)
            if r > 0.6:
                glow(ctx, 640 + 120, 720 - 340 * 0.5 - 200, 90, GOLD, 0.12 * r)
        vignette(ctx, 0.5)


for _q in range(4):
    make_question(_q)


# ================================================================ 7. Glad tidings (390-440)
@shot(15)
def s7_brighter(ctx, u, d):
    k = ramp(u, 2, 12)
    with Cam(ctx, 1.0 + 0.1 * k, 640, 380):
        circle_scene(ctx, u, light_i=1 + 2.5 * k, rot=4, bow=0.6, day=0.75)
    tint(ctx, C("#fff6dd"), 0.35 * k)
    vignette(ctx, 0.4)


@shot(20)
def s7_gates(ctx, u, d):
    sky(ctx, (C("#1a1430"), C("#5a3a5a"), C("#e8b070")), horizon=720)
    stars(ctx, u, 0.6, y_max=400)
    glow(ctx, 640, 720, 900, GOLD, 0.35)
    for i in range(8):
        a = math.radians(-70 + i * 20)
        x = 640 + math.sin(a) * 520
        y = 430 - math.cos(a) * 200
        s = 0.8 + 0.2 * math.cos(a)
        gw, gh = 70 * s, 150 * s
        o = ramp(u, 2 + i * 0.6, 4 + i * 0.6)
        glow(ctx, x, y, 140 * s, GOLD, 0.25 + 0.35 * o)
        ctx.move_to(x - gw / 2, y + gh / 2)
        ctx.line_to(x - gw / 2, y - gh / 2 + gw / 2)
        ctx.arc(x, y - gh / 2 + gw / 2, gw / 2, math.pi, 0)
        ctx.line_to(x + gw / 2, y + gh / 2)
        ctx.close_path()
        setc(ctx, mix(GOLD, (1, 1, 1), o))
        ctx.fill()
        for side in (-1, 1):
            lw = gw / 2 * (1 - o * 0.85)
            fill_rect(ctx, x + (0 if side > 0 else -gw / 2) + (gw / 2 - lw if side > 0 else 0),
                      y - gh / 2 + gw * 0.5, lw, gh - gw * 0.5, C("#c08a2a"), 0.9)
    clouds = [(200, 640), (520, 680), (860, 650), (1120, 690)]
    for cx, cy in clouds:
        for j in range(5):
            ellipse(ctx, cx + j * 50 - 100 + math.sin(u * 0.2 + j) * 10, cy, 90, 40, (1, 0.93, 0.85), 0.35)
    vignette(ctx, 0.4)


@shot(15)
def s7_tear(ctx, u, d):
    masjid_interior(ctx, u, day=0.7, floor_y=430, dark=0.75)
    glow(ctx, 640, 300, 600, GOLD, 0.3)
    person_back(ctx, 640, 760, 420, ABU_BAKR, sit=1, bow=0.9, shake=0.6 * ramp(u, 2, 4), dark=0.8)
    for k in range(3):
        t0 = 4 + k * 3.5
        p = ramp(u, t0, t0 + 1.4)
        if 0 < p < 1:
            tear(ctx, 560 + k * 15, lerp(420, 700, p * p), 7)
    vignette(ctx, 0.55)


# ================================================================ 8. Umar's heart (440-490)
@shot(18, "b")
def s8_umar_looks(ctx, u, d):
    with Cam(ctx, 1.0 + 0.03 * u / d, 640, 380):
        masjid_interior(ctx, u, day=0.4, floor_y=420, dark=0.7)
        person_back(ctx, 980, 560, 160, ABU_BAKR, sit=1, bow=0.8, dark=0.6)
        holy_light(ctx, 1100, 330, 12, u, 0.8)
        p = dict(POSES["jalsa"])
        p["head"] = 5 + math.sin(u * 0.4) * 4
        person_side(ctx, 330, 700, 360, p, UMAR, facing=1, silhouette=C("#101524"))
    tint(ctx, C("#1d2c55"), 0.3)
    vignette(ctx, 0.6)


@shot(32)
def s8_umar_room(ctx, u, d):
    with Cam(ctx, 1.0 + 0.04 * u / d, 640, 380):
        room(ctx, u, sky_pal=DUSK if u < 10 else NIGHT, lamp=1.0, dawn=0.0)
        lift = ramp(u, 20, 24)
        person_side(ctx, 260, 600, 240, pose_mix("sit_hug", "sit_up", lift), UMAR, facing=1, dark=0.75)
    tint(ctx, C("#1d2c55"), 0.15)
    vignette(ctx, 0.7)


# ================================================================ 9. Following in the dark (490-540)
@shot(15, "b")
def s9_follow(ctx, u, d):
    vx, vy = alley(ctx, u, night=1.0)
    k = ramp(u, 0, d)
    z = lerp(0.2, 0.8, k)
    x = lerp(620, vx, k)
    y = lerp(700, vy + 40, z)
    person_back(ctx, x, y, lerp(330, 40, z), ABU_BAKR, step=u * 4, silhouette=C("#0a0b14"))
    glow(ctx, vx, vy - 120, 300, C("#5a78c8"), 0.15)
    vignette(ctx, 0.7)


@shot(15)
def s9_peek(ctx, u, d):
    street_side(ctx, u, night=1.0, ground=580, seed=101, palms=True)
    fill_rect(ctx, 0, 0, 470, H, C("#15141e"))
    wall_texture(ctx, 0, 0, 470, H, C("#15141e"))
    lean = ramp(u, 2, 5) * (1 - ramp(u, 11, 13))
    p = dict(POSES["stand"])
    p["torso"] = 20 * lean
    p["head"] = 10 * lean
    person_side(ctx, 400 + 25 * lean, 690, 300, p, UMAR, facing=1, silhouette=C("#08080e"))
    fill_rect(ctx, 0, 0, 420, H, C("#15141e"))
    person_back(ctx, 1000 - u * 25, 600, 110, ABU_BAKR, step=u * 4, silhouette=C("#0b0b13"))
    vignette(ctx, 0.7)


@shot(20)
def s9_lonely_house(ctx, u, d):
    sky(ctx, NIGHT, horizon=560)
    stars(ctx, u, 1.0, y_max=480)
    moon(ctx, 1050, 120, 26)
    ground_band(ctx, 560, C("#141522"))
    house(ctx, 520, 580, 240, 150, MUD, win=(0.62, 0.3, 26, 26), lit=0.9 + 0.1 * math.sin(u * 6), door=True,
          night=0.85, seed=6)
    palm(ctx, 900, 580, 240, u, col=C("#0e0f1a"))
    w = ramp(u, 0, 12)
    if w < 1:
        person_side(ctx, lerp(150, 600, w), 640 - w * 50, lerp(160, 90, w), walk_pose(u * 4), ABU_BAKR,
                    silhouette=C("#0a0a12"))
    else:
        open_ = 1 - ramp(u, 13, 14.5)
        glow(ctx, 610, 550, 80, WARM, 0.5 * open_)
    vignette(ctx, 0.6)


# ================================================================ 10. The blind woman (540-600)
def tiny_room(ctx, u, lamp=1.0, dawn=0.0):
    room(ctx, u, sky_pal=NIGHT if dawn < 0.5 else MORNING, lamp=lamp, dawn=dawn, jug=True)


@shot(10, "b")
def s10_room(ctx, u, d):
    tiny_room(ctx, u)
    turn = math.sin(u * 0.6) * ramp(u, 3, 5)
    blind_woman(ctx, 820, 620, 300, u, hands="lap", turn=turn)
    vignette(ctx, 0.6)


@shot(10)
def s10_sweep(ctx, u, d):
    tiny_room(ctx, u)
    blind_woman(ctx, 950, 600, 240, u, hands="lap", turn=-0.6)
    p = dict(POSES["sweep"])
    sw = math.sin(u * 3.2)
    p["arm"] = 45 + 20 * sw
    p["arm2"] = 30 + 20 * sw
    x = 380 + u * 15
    info = person_side(ctx, x, 680, 260, p, ABU_BAKR, facing=1, dark=0.8)
    hx, hy = info["hand"]
    bx = hx + 40 + sw * 25
    capsule(ctx, (hx, hy), (bx, 680), 5, WOOD)
    ctx.set_line_width(2)
    for k in range(9):
        setc(ctx, C("#b8975c"))
        ctx.move_to(bx, 670)
        ctx.line_to(bx - 20 + k * 5, 690)
        ctx.stroke()
    dust(ctx, u, 25, (bx - 80, 600, 160, 90), (1, 0.85, 0.6), 0.5, speed=20)
    vignette(ctx, 0.6)


@shot(10)
def s10_water(ctx, u, d):
    closeup_bg(ctx, u)
    tilt = ramp(u, 1, 3) * (1 - ramp(u, 6.5, 7.5))
    ctx.save()
    ctx.translate(560, 260)
    ctx.rotate(tilt * 0.9)
    ellipse(ctx, 0, 0, 90, 110, C("#8a5530"))
    ellipse(ctx, 70, -80, 30, 14, C("#6b3f24"))
    ctx.restore()
    hand(ctx, 470, 320, 70, -0.2, SKIN_AB, ABU_BAKR.cloak, grip=0.6)
    if 0.6 < tilt:
        setc(ctx, C("#bcdff5"), 0.8)
        ctx.set_line_width(7)
        ctx.move_to(650, 230)
        ctx.curve_to(690, 260, 700, 360, 700, 470)
        ctx.stroke()
    ellipse(ctx, 700, 520, 70, 22, C("#6b4b2e"))
    fill_rect(ctx, 630, 470, 140, 50, C("#7d5a3a"))
    ellipse(ctx, 700, 470, 70, 18, C("#3e6a8a") if u > 3 else C("#2a1c10"))
    hand(ctx, 560, 560, 70, 0.1, SKIN_W, C("#4e4038"), grip=0.8, palm_up=True)
    hand(ctx, 840, 560, 70, math.pi - 0.1, SKIN_W, C("#4e4038"), grip=0.8, palm_up=True)


@shot(14)
def s10_dates(ctx, u, d):
    closeup_bg(ctx, u)
    pit_cycle(ctx, u, ABU_BAKR.cloak)


@shot(16)
def s10_smile(ctx, u, d):
    tiny_room(ctx, u, dawn=0.2)
    give = ramp(u, 0, 3)
    hands = "receive" if u < 7 else "dua"
    blind_woman(ctx, 760, 640, 360, u, hands=hands, smile=ramp(u, 3, 6))
    if hands == "receive":
        for i in range(3):
            date_fruit(ctx, 745 + i * 15, 568, 12, 0.3, split=0.2, pit=False)
    p = pose_mix("jalsa", "kneel_give", give * (1 - ramp(u, 4, 6)))
    person_side(ctx, 420, 690, 300, p, ABU_BAKR, facing=1, dark=0.7)
    vignette(ctx, 0.6)


# ================================================================ 11. Umar understands (600-630)
@shot(10, "b")
def s11_gap(ctx, u, d):
    with Cam(ctx, 1.0, 640 + math.sin(u * 0.7) * 8, 360 + math.sin(u * 0.5) * 5):
        tiny_room(ctx, u, dawn=0.3)
        blind_woman(ctx, 760, 620, 260, u, hands="dua", smile=1)
        person_side(ctx, 520, 650, 240, "jalsa", ABU_BAKR, facing=1, dark=0.7)
    gap = 260 + 40 * ramp(u, 0, 3)
    fill_rect(ctx, 0, 0, 640 - gap / 2, H, C("#1a120b"))
    fill_rect(ctx, 640 + gap / 2, 0, W, H, C("#1a120b"))
    for x in (640 - gap / 2 - 60, 640 + gap / 2 + 20):
        for k in range(4):
            fill_rect(ctx, x + k * 12, 0, 3, H, C("#2a1c10"))
    vignette(ctx, 0.5)


@shot(10)
def s11_umar_tear(ctx, u, d):
    street_side(ctx, u, night=0.6, ground=600, seed=111, pal=mix_pal(DAWN, NIGHT, 0.4))
    person_back(ctx, 640, 780, 520, UMAR, bow=0.9, dark=0.65)
    p = ramp(u, 3, 5)
    if 0 < p < 1:
        tear(ctx, 600, lerp(330, 720, p * p), 8)
    vignette(ctx, 0.6)


@shot(10)
def s11_walk_away(ctx, u, d):
    vx, vy = alley(ctx, u, night=0.4, end_glow=0.6)
    glow(ctx, vx, vy - 40, 400, GOLD, 0.5)
    k = ramp(u, 0, d)
    z = lerp(0.1, 0.75, k)
    person_back(ctx, lerp(640, vx, k), lerp(700, vy + 40, z), lerp(320, 60, z), UMAR, step=u * 3.5,
                dark=0.5)
    vignette(ctx, 0.5)


# ================================================================ 12. Time passes (630-660)
@shot(15, "b")
def s12_seasons(ctx, u, d):
    cyc = u * 0.8
    night = 0.5 + 0.5 * math.sin(cyc * 2)
    street_side(ctx, u, night=night, ground=560, seed=121, palms=True, lit_t=night)
    if 6 < u < 10:
        ctx.set_line_width(1.5)
        for i in range(140):
            x = (i * 97 + u * 900) % (W + 200) - 100
            y = (i * 53 + u * 1400) % H
            setc(ctx, (0.8, 0.85, 0.95), 0.4)
            ctx.move_to(x, y)
            ctx.line_to(x - 8, y + 24)
            ctx.stroke()
    if u > 10:
        dust(ctx, u, 80, (0, 300, W, 400), (0.9, 0.8, 0.6), 0.5, speed=60)
    black(ctx, 1 - ramp(u, 0, 3))
    vignette(ctx, 0.5)


@shot(7)
def s12_dim(ctx, u, d):
    sky(ctx, NIGHT, horizon=560)
    stars(ctx, u, 1.0, y_max=480)
    ground_band(ctx, 560, C("#141522"))
    lit = 0.9 * (1 - ramp(u, 0, d) * 0.8)
    house(ctx, 520, 580, 240, 150, MUD, win=(0.62, 0.3, 26, 26), lit=lit, door=True, night=0.85, seed=6)
    vignette(ctx, 0.6)


@shot(8)
def s12_empty(ctx, u, d):
    with Cam(ctx, 1.05, 640, 400):
        circle_scene(ctx, u, light_i=0.0, rot=2, bow=0.8, empty_abu=True, day=0.5, dark=0.8)
    tint(ctx, C("#1d2c55"), 0.2)
    vignette(ctx, 0.55)


# ================================================================ 13. The dates with pits (660-700)
@shot(8, "b")
def s13_enter(ctx, u, d):
    sky(ctx, DAWN, horizon=560, t=0.4, pal2=MORNING)
    ground_band(ctx, 560, SAND)
    house(ctx, 400, 600, 480, 300, MUD, door=True, seed=6)
    fill_rect(ctx, 544, 535, 40, 65, C("#2a1c10"))
    k = ramp(u, 0, 6)
    person_back(ctx, lerp(560, 564, k), lerp(720, 600, k), lerp(320, 90, k), UMAR, step=u * 4, a=1 - ramp(u, 6, 7))
    vignette(ctx, 0.4)


@shot(6)
def s13_sweep(ctx, u, d):
    tiny_room(ctx, u, dawn=0.6, lamp=0.5)
    blind_woman(ctx, 950, 600, 240, u, hands="lap", turn=-0.5)
    p = dict(POSES["sweep"])
    sw = math.sin(u * 3)
    p["arm"] = 45 + 20 * sw
    info = person_side(ctx, 420 + u * 12, 680, 270, p, UMAR, facing=1, dark=0.8)
    capsule(ctx, info["hand"], (info["hand"][0] + 40 + sw * 25, 680), 5, WOOD)
    vignette(ctx, 0.6)


@shot(10)
def s13_pit(ctx, u, d):
    closeup_bg(ctx, u, warm=0.6)
    close = ramp(u, 2.5, 4)
    hand(ctx, 640, 470, 95, math.pi / 2 + 0.2, SKIN_W, C("#4e4038"), grip=0.2 + 0.6 * close, palm_up=True)
    if u < 4:
        date_fruit(ctx, lerp(900, 650, ramp(u, 0, 2)), lerp(380, 470, ramp(u, 0, 2)), 30, 0.4)
    if u < 2.2:
        hand(ctx, lerp(1050, 820, ramp(u, 0, 2)), 360, 70, math.pi + 0.3, SKIN_AB, UMAR.cloak, grip=0.6)
    black(ctx, 0.35 * ramp(u, 4, 6))
    vignette(ctx, 0.7)


@shot(16)
def s13_weep(ctx, u, d):
    tiny_room(ctx, u, dawn=0.6, lamp=0.4)
    blind_woman(ctx, 780, 640, 340, u, hands="lap", cry=ramp(u, 0, 2))
    p = dict(POSES["bow_sit"])
    person_side(ctx, 430, 690, 300, p, UMAR, facing=1, dark=0.7)
    for k in range(2):
        pp = ramp(u, 3 + k * 6, 4.5 + k * 6)
        if 0 < pp < 1:
            tear(ctx, 470, lerp(470, 680, pp * pp), 7)
    tint(ctx, C("#1d2c55"), 0.15)
    vignette(ctx, 0.6)


# ================================================================ 14. Ending (700-720)
@shot(8)
def s14_umar_pits(ctx, u, d):
    closeup_bg(ctx, u, warm=1.2)
    pit_cycle(ctx, u, UMAR.cloak, period=5.0)
    tint(ctx, GOLD, 0.06)


@shot(5)
def s14_sunrise(ctx, u, d):
    tiny_room(ctx, u, dawn=1.0, lamp=0.2)
    blind_woman(ctx, 780, 640, 340, u, hands="lap", smile=0.6)
    person_side(ctx, 470, 690, 300, "kneel_give", UMAR, facing=1, dark=0.75)
    k = ramp(u, 0, d)
    glow(ctx, 575, 160, 900 * (0.5 + k), GOLD, 0.6 * k)
    tint(ctx, C("#fff1cf"), 0.5 * k)


@shot(7)
def s14_end(ctx, u, d):
    vgrad(ctx, 0, 0, W, H, [(0, C("#e6b35a")), (1, C("#b9802f"))])
    glow(ctx, 640, 360, 600, (1, 1, 0.9), 0.3)
    a = ramp(u, 0.3, 1.5)
    text_center(ctx, "Bëj mirë në fshehtësi.", W / 2, 330, 58, (1, 1, 1), a, bold=True)
    text_center(ctx, "Do good in secret.", W / 2, 410, 30, (1, 0.98, 0.92), a * 0.9)
    black(ctx, ramp(u, 5.5, 7))


TOTAL = sum(s[0] for s in SHOTS)
