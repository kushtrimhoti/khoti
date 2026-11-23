"""Reusable sets: rooms, the masjid, streets, close-ups."""
import math
import random

import cairo

from engine import *  # noqa: F401,F403


def dust(ctx, u, n=40, box=(0, 0, W, H), c=(1, 0.9, 0.7), a=0.35, seed=7, speed=6):
    rnd = random.Random(seed)
    x0, y0, w, h = box
    for _ in range(n):
        px = x0 + (rnd.uniform(0, w) + u * rnd.uniform(-speed, speed)) % w
        py = y0 + (rnd.uniform(0, h) - u * rnd.uniform(1, speed)) % h
        r = rnd.uniform(0.8, 2.2)
        al = a * (0.5 + 0.5 * math.sin(u * rnd.uniform(0.5, 2) + rnd.uniform(0, 6)))
        ctx.set_source_rgba(c[0], c[1], c[2], al)
        ctx.arc(px, py, r, 0, 6.283)
        ctx.fill()


def straw_floor(ctx, y, h, col=STRAW, dark=1.0, seed=2):
    vgrad(ctx, -400, y, W + 800, h, [(0, shade(col, 0.55 * dark)), (1, shade(col, 0.9 * dark))])
    rnd = random.Random(seed)
    ctx.set_line_width(1)
    for _ in range(160):
        yy = y + rnd.uniform(0, h)
        xx = rnd.uniform(-200, W + 200)
        ln = rnd.uniform(15, 50) * (0.4 + (yy - y) / h)
        setc(ctx, shade(col, rnd.uniform(0.5, 1.15) * dark), 0.45)
        ctx.move_to(xx, yy)
        ctx.line_to(xx + ln, yy + rnd.uniform(-2, 2))
        ctx.stroke()


def wall_texture(ctx, x, y, w, h, col, seed=5, n=60):
    rnd = random.Random(seed)
    for _ in range(n):
        ellipse(ctx, rnd.uniform(x, x + w), rnd.uniform(y, y + h), rnd.uniform(10, 50), rnd.uniform(4, 16),
                shade(col, rnd.uniform(0.85, 1.12)), 0.25)


# ------------------------------------------------------------------ small house interior
def room(ctx, u, sky_pal=NIGHT, lamp=1.0, window=True, door_open=0.0, wall=C("#3a2c20"), dawn=0.0,
         jug=True, niche=True):
    """The interior from the reference picture: dark wall, niche lamp, small starry window."""
    fill_rect(ctx, -300, -300, W + 600, H + 600, wall)
    wall_texture(ctx, -100, 0, W + 200, 520, wall, seed=11, n=90)
    # left wall (door) and floor
    poly(ctx, [(-200, -50), (110, 40), (110, 560), (-200, 720)], shade(wall, 0.75))
    vgrad(ctx, -300, 520, W + 600, 300, [(0, shade(wall, 0.55)), (1, shade(wall, 0.4))])
    # straw mats
    poly(ctx, [(170, 540), (560, 540), (520, 700), (40, 720)], shade(STRAW, 0.55))
    poly(ctx, [(700, 540), (1150, 540), (1260, 720), (760, 700)], shade(STRAW, 0.5))
    ctx.set_line_width(1)
    rnd = random.Random(3)
    for _ in range(140):
        x = rnd.uniform(60, 1240)
        y = rnd.uniform(545, 715)
        setc(ctx, shade(STRAW, rnd.uniform(0.4, 0.8)), 0.5)
        ctx.move_to(x, y)
        ctx.line_to(x + rnd.uniform(10, 30), y + rnd.uniform(-2, 2))
        ctx.stroke()
    # door on the left wall
    poly(ctx, [(0, 130), (90, 150), (90, 520), (0, 560)], shade(WOOD, 0.65))
    if door_open > 0:
        poly(ctx, [(0, 130), (90 * door_open, 150), (90 * door_open, 520), (0, 560)], C("#c9a46a"), door_open)
        glow(ctx, 40, 380, 260, GOLD, 0.35 * door_open)
    for k in range(4):
        capsule(ctx, (k * 22 + 5, 140 + k * 5), (k * 22 + 5, 545 - k * 9), 1.5, shade(WOOD, 0.4))
    # window
    if window:
        wx, wy, ww, wh = 520, 90, 110, 130
        ctx.save()
        ctx.rectangle(wx, wy, ww, wh)
        ctx.clip()
        sky(ctx, sky_pal, horizon=wy + wh)
        stars(ctx, u, 1 - dawn, y_max=wy + wh, seed=21, n=25, x0=wx, x1=wx + ww)
        ctx.restore()
        ctx.set_line_width(5)
        setc(ctx, shade(wall, 0.5))
        ctx.rectangle(wx, wy, ww, wh)
        ctx.stroke()
        glow(ctx, wx + ww / 2, wy + wh / 2, 150, mix(C("#5a78c8"), GOLD, dawn), 0.15)
    # niche with lamp
    lamp_pos = (575, 370)
    if niche:
        nx, ny = 545, 305
        ctx.move_to(nx, ny + 75)
        ctx.line_to(nx, ny + 25)
        ctx.arc(nx + 30, ny + 25, 30, math.pi, 0)
        ctx.line_to(nx + 60, ny + 75)
        ctx.close_path()
        setc(ctx, shade(wall, 0.45))
        ctx.fill()
        oil_lamp(ctx, 568, 372, 1.0, u, lit=lamp)
    if jug:
        ellipse(ctx, 1080, 470, 55, 70, C("#7a4a2c"))
        ellipse(ctx, 1080, 405, 25, 10, C("#5e3720"))
        capsule(ctx, (1035, 430), (1025, 470), 7, C("#6b3f24"))
        glow(ctx, 1060, 455, 60, WARM, 0.12 * lamp)
    # warm lamplight wash
    glow(ctx, 575, 360, 520, WARM, 0.18 * lamp)
    return lamp_pos


def sleeper(ctx, x, ground, s, u, look=TOWN[0]):
    breath = math.sin(u * 1.1) * s * 0.01
    ctx.move_to(x - s * 0.55, ground)
    ctx.curve_to(x - s * 0.5, ground - s * 0.25 - breath, x + s * 0.3, ground - s * 0.3 - breath, x + s * 0.55, ground)
    ctx.close_path()
    setc(ctx, C("#8a7458"))
    ctx.fill()
    ellipse(ctx, x - s * 0.62, ground - s * 0.08, s * 0.14, s * 0.06, C("#d9d2c2"))
    ellipse(ctx, x - s * 0.55, ground - s * 0.17, s * 0.1, s * 0.09, look.skin)
    ellipse(ctx, x - s * 0.55, ground - s * 0.22, s * 0.12, s * 0.07, look.turban or C("#eee"))


# ------------------------------------------------------------------ masjid
def masjid_interior(ctx, u, day=0.0, dark=1.0, beams=None, light_x=None, light_y=None, light_i=0.0,
                    floor_y=470, pillars=True, wallc=None):
    """Simple early masjid: mud walls, palm-trunk pillars, palm-frond roof."""
    wallc = wallc or mix(C("#3b3024"), C("#a9875d"), day)
    fill_rect(ctx, -400, -400, W + 800, H + 800, shade(wallc, dark))
    wall_texture(ctx, -200, 0, W + 400, floor_y, shade(wallc, dark), seed=9, n=80)
    # roof of palm fronds
    vgrad(ctx, -400, -400, W + 800, 520, [(0, shade(C("#2a2016"), dark)), (1, shade(C("#2a2016"), dark), 0)])
    rnd = random.Random(4)
    ctx.set_line_width(3)
    for i in range(60):
        x = -300 + i * 32
        setc(ctx, shade(C("#4a3a22"), dark), 0.8)
        ctx.move_to(x, 0)
        ctx.line_to(x + rnd.uniform(-40, 40), 70)
        ctx.stroke()
    fill_rect(ctx, -400, 60, W + 800, 18, shade(WOOD, dark * 0.8))
    if beams is None:
        beams = day
    if beams > 0:
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        for i in range(7):
            bx = 80 + i * 190 + math.sin(i * 3) * 40
            g = cairo.LinearGradient(bx, 70, bx + 160, floor_y + 150)
            g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.22 * beams)
            g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0.0)
            ctx.set_source(g)
            ctx.move_to(bx, 70)
            ctx.line_to(bx + 26, 70)
            ctx.line_to(bx + 200, floor_y + 160)
            ctx.line_to(bx + 120, floor_y + 160)
            ctx.close_path()
            ctx.fill()
        ctx.restore()
        dust(ctx, u, 60, (0, 80, W, floor_y), (1, 0.92, 0.7), 0.45 * beams)
    straw_floor(ctx, floor_y, H - floor_y + 200, dark=dark * lerp(0.75, 1.0, day))
    if pillars:
        for i, px in enumerate([-60, 230, 640, 1050, 1340]):
            col = shade(C("#5a4026"), dark * lerp(0.8, 1.05, day))
            fill_rect(ctx, px - 18, 70, 36, floor_y - 60, col)
            for k in range(14):
                yy = 90 + k * (floor_y - 90) / 14
                fill_rect(ctx, px - 18, yy, 36, 3, shade(col, 0.7), 0.7)
            fill_rect(ctx, px + 8, 70, 10, floor_y - 60, shade(col, 0.75), 0.6)
    if light_x is not None:
        holy_light(ctx, light_x, light_y, 14, u, light_i)


CIRCLE = []  # (angle, look-index, is_abu_bakr, is_umar)
for i, ang in enumerate([200, 222, 244, 266, 290, 312, 334]):
    CIRCLE.append((ang, i % len(TOWN), ang == 312, ang == 222))


def circle_scene(ctx, u, light_i=1.0, rot=0.0, raise_hand=0.0, bow=0.6, empty_abu=False, day=0.6, dark=1.0,
                 shake=0.0):
    masjid_interior(ctx, u, day=day, dark=dark, floor_y=420)
    cx, cy, rx, ry = 640, 470, 400, 120
    lx, ly = 640, 330
    # far side of circle: small silhouettes beside the light
    far = []
    for ang in [20, 45, 135, 160, 70, 110]:
        a = math.radians(ang + rot)
        far.append((math.sin(a) * -1, cx + math.cos(a) * rx * 0.85, cy - abs(math.sin(a)) * ry * 0.9))
    for _, x, y in sorted(far, key=lambda p: p[2]):
        person_back(ctx, x, y, 95, TOWN[2], sit=1, silhouette=shade(C("#2a2219"), dark), bow=bow)
    holy_light(ctx, lx, ly, 15, u, light_i)
    glow(ctx, lx, ly + 60, 520, GOLD, 0.12 * light_i)
    near = []
    for ang, li, abu, um in CIRCLE:
        a = math.radians(ang + rot)
        x = cx + math.cos(a) * rx
        y = cy - math.sin(a) * ry + 60
        near.append((y, x, li, abu, um))
    for y, x, li, abu, um in sorted(near):
        if abu and empty_abu:
            glow(ctx, x, y - 40, 70, GOLD, 0.08)
            continue
        look = ABU_BAKR if abu else UMAR if um else TOWN[li]
        sc = 150 + (y - 470) * 0.9
        person_back(ctx, x, y, sc, look, sit=1, bow=0.2 if abu else bow, raise_hand=raise_hand if abu else 0,
                    dark=0.75 * dark, shake=shake if abu else 0)
    return lx, ly


# ------------------------------------------------------------------ exterior helpers
def masjid_ext(ctx, x, ground, w, h, night=0.0, door_glow=0.0):
    col = mix(MUD, MUD_NIGHT, night)
    fill_rect(ctx, x, ground - h, w, h, col)
    fill_rect(ctx, x, ground - h, w, 8, shade(col, 0.7))
    # palm-frond roof line
    ctx.set_line_width(2)
    for i in range(int(w / 9)):
        setc(ctx, shade(col, 0.6))
        ctx.move_to(x + i * 9, ground - h)
        ctx.line_to(x + i * 9 + 5, ground - h - 7)
        ctx.stroke()
    for i in range(3):
        dx = x + w * (0.25 + i * 0.25) - 18
        fill_rect(ctx, dx, ground - 62, 36, 62, shade(col, 0.4))
        if door_glow > 0:
            fill_rect(ctx, dx, ground - 62, 36, 62, WARM, door_glow)
            glow(ctx, dx + 18, ground - 30, 90, WARM, 0.4 * door_glow)
    # raised roof platform where the adhan is called
    fill_rect(ctx, x + w * 0.78, ground - h - 40, 60, 40, shade(col, 0.95))


def ground_band(ctx, y, c, h=400):
    fill_rect(ctx, -500, y, W + 1000, h, c)


def alley(ctx, u, night=0.0, end_glow=0.0, poor=True):
    """One-point perspective narrow street. Vanishing point at (640, 330)."""
    vx, vy = 640, 330
    skyc = mix_pal(MORNING, NIGHT, night)
    sky(ctx, skyc, horizon=330)
    if night > 0.5:
        stars(ctx, u, night, y_max=300, seed=8, n=60)
    wallL = mix(C("#a37f58"), MUD_NIGHT, night)
    wallR = shade(wallL, 0.8)
    groundc = mix(C("#c8a776"), C("#1b1c2a"), night)
    poly(ctx, [(-50, H + 50), (vx - 60, vy + 40), (vx + 60, vy + 40), (W + 50, H + 50)], groundc)
    poly(ctx, [(-50, -100), (vx - 60, vy - 110), (vx - 60, vy + 40), (-50, H + 50)], wallL)
    poly(ctx, [(W + 50, -100), (vx + 60, vy - 110), (vx + 60, vy + 40), (W + 50, H + 50)], wallR)
    # end wall with a corner opening on the right
    poly(ctx, [(vx - 60, vy - 110), (vx + 20, vy - 110), (vx + 20, vy + 40), (vx - 60, vy + 40)], shade(wallL, 0.9))
    fill_rect(ctx, vx + 20, vy - 60, 40, 100, shade(groundc, 0.7))
    if end_glow:
        glow(ctx, vx + 40, vy, 120, GOLD, end_glow)
    # cracks and doors (poorer street)
    rnd = random.Random(12)
    ctx.set_line_width(1.5)
    for side in (-1, 1):
        for k in range(5):
            t = 0.15 + k * 0.17
            xx = lerp(-50 if side < 0 else W + 50, vx + side * 60, t)
            top = lerp(-100, vy - 110, t)
            bot = lerp(H + 50, vy + 40, t)
            dh = (bot - top) * 0.45
            dw = 70 * (1 - t) + 6
            fill_rect(ctx, xx - dw / 2, bot - dh, dw, dh, shade(wallL if side < 0 else wallR, 0.55))
            setc(ctx, shade(wallL, 0.6), 0.6)
            ctx.move_to(xx + rnd.uniform(-30, 30), top + rnd.uniform(30, 120))
            ctx.line_to(xx + rnd.uniform(-30, 30), top + rnd.uniform(130, 220))
            ctx.stroke()
    return vx, vy


def street_side(ctx, u, night=0.0, pan=0.0, ground=560, lit_t=0.0, seed=31, pal=None, palms=True):
    pal = pal or mix_pal(MORNING, NIGHT, night)
    sky(ctx, pal, horizon=ground - 60)
    if night > 0.3:
        stars(ctx, u, night, y_max=ground - 200, seed=seed)
    ctx.save()
    ctx.translate(-pan * 0.4, 0)
    skyline(ctx, ground - 60, night=min(1, night + 0.2), seed=seed + 1, x0=-400, x1=W + 1400, scale=0.7,
            base=shade(MUD, 0.85))
    ctx.restore()
    ctx.save()
    ctx.translate(-pan, 0)
    skyline(ctx, ground, night=night, seed=seed, x0=-400, x1=W + 3000, scale=1.5, lit_t=lit_t)
    if palms:
        for px in range(-200, 3000, 640):
            palm(ctx, px + 300, ground + 5, 260, u, col=mix(C("#3d3a24"), C("#10121c"), night))
    ctx.restore()
    ground_band(ctx, ground, mix(SAND, C("#1d1e2c"), night))
    vgrad(ctx, -100, ground, W + 200, 200, [(0, (0, 0, 0), 0.0), (1, (0, 0, 0), 0.25)])


def mix_pal(p1, p2, t):
    return tuple(mix(a, b, t) for a, b in zip(p1, p2))


# ------------------------------------------------------------------ close-up hands and dates
SKIN_AB = C("#a7744f")
SKIN_W = C("#b88663")


def hand(ctx, x, y, s, ang, skin, sleeve, grip=0.0, palm_up=False):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    capsule(ctx, (-s * 1.6, 0), (-s * 0.6, 0), s * 0.9, sleeve)
    ellipse(ctx, 0, 0, s * 0.6, s * 0.45, skin)
    for k in range(4):
        fy = (-1.5 + k) * s * 0.2
        ln = s * (0.75 - abs(k - 1.5) * 0.08)
        bend = grip * 0.9
        p1 = (s * 0.45, fy)
        p2 = (s * 0.45 + ln * math.cos(bend), fy + ln * math.sin(bend) * (1 if palm_up else -0.4))
        capsule(ctx, p1, p2, s * 0.17, skin)
    capsule(ctx, (s * 0.1, s * 0.35), (s * 0.55, s * 0.55 - grip * s * 0.3), s * 0.2, shade(skin, 0.95))
    ctx.restore()


def date_fruit(ctx, x, y, s, ang=0.0, split=0.0, pit=True, pit_off=(0, 0)):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    dc = C("#5b2a14")
    if split <= 0.01:
        ellipse(ctx, 0, 0, s, s * 0.45, dc)
        ellipse(ctx, -s * 0.2, -s * 0.15, s * 0.5, s * 0.12, shade(dc, 1.5), 0.5)
    else:
        for side in (-1, 1):
            ellipse(ctx, 0, side * split * s * 0.4, s, s * 0.3, dc)
            ellipse(ctx, 0, side * split * s * 0.3, s * 0.8, s * 0.12, C("#a0612e"))
    if pit and split > 0.01:
        ellipse(ctx, pit_off[0], pit_off[1], s * 0.55, s * 0.14, C("#c9a67a"))
    ctx.restore()


def closeup_bg(ctx, u, warm=1.0):
    fill_rect(ctx, -100, -100, W + 200, H + 200, C("#2b1f15"))
    glow(ctx, 900, 120, 700, WARM, 0.25 * warm, add=True)
    straw_floor(ctx, 380, 400, dark=0.7)
    vignette(ctx, 0.6)


def pit_cycle(ctx, u, sleeve, skin=SKIN_AB, bowl_count=0, period=4.6, x=560, y=420):
    """Two hands take the pit out of a date, put the soft date on a plate."""
    k = int(u // period)
    p = (u % period) / period
    # plate of soft dates and bowl of pits
    ellipse(ctx, 940, 560, 170, 45, C("#7a5a3a"))
    ellipse(ctx, 940, 552, 150, 35, C("#8e6b47"))
    for i in range(min(9, k + 3)):
        date_fruit(ctx, 860 + (i % 5) * 38, 545 - (i // 5) * 20, 22, 0.2, split=0.25, pit=False)
    ellipse(ctx, 240, 600, 90, 28, C("#5e4430"))
    for i in range(min(14, k + bowl_count + 2)):
        ellipse(ctx, 200 + (i * 17) % 80, 592 - (i // 5) * 5, 10, 3.5, C("#c9a67a"))
    split = ramp(p, 0.15, 0.35) * (1 - ramp(p, 0.7, 0.85))
    pit_out = ramp(p, 0.35, 0.6)
    pit_off = (lerp(0, -40, pit_out), lerp(0, -70, pit_out))
    dx = lerp(0, 380, ramp(p, 0.8, 1.0))
    if p < 0.97:
        date_fruit(ctx, x + dx, y, 46, -0.15, split=split, pit=p < 0.62, pit_off=pit_off)
    if 0.6 <= p < 0.8:
        pp = ramp(p, 0.6, 0.8)
        ellipse(ctx, lerp(x - 40, 240, pp), lerp(y - 70, 590, pp) - math.sin(pp * math.pi) * 60, 26, 7,
                C("#c9a67a"))
    hand(ctx, x - 90 + dx * 0.6, y + 60, 70, -0.5, skin, sleeve, grip=0.5)
    hand(ctx, x + 80, y - 40 + pit_out * -40, 60, math.pi + 0.6, skin, sleeve, grip=0.3 + split * 0.4)
