"""Drawing primitives for the Abu Bakr short film (pycairo, 1280x720)."""
import math
import random

import cairo

W, H = 1280, 720
FPS = 24


# ---------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ramp(u, a, b):
    """0 before a, 1 after b, smooth in between."""
    if b <= a:
        return 1.0 if u >= a else 0.0
    return ease((u - a) / (b - a))


def C(h, a=None):
    h = h.lstrip("#")
    c = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return c if a is None else c + (a,)


def mix(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def shade(c, k):
    """k<1 darker, k>1 lighter."""
    if k <= 1:
        return tuple(x * k for x in c)
    return tuple(x + (1 - x) * (k - 1) for x in c)


def setc(ctx, c, a=1.0):
    ctx.set_source_rgba(c[0], c[1], c[2], a)


def new_frame():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    return s, cairo.Context(s)


class Cam:
    """Camera: zoom around a world point (cx, cy) placed at screen centre."""

    def __init__(self, ctx, zoom=1.0, cx=W / 2, cy=H / 2, rot=0.0):
        self.ctx, self.z, self.cx, self.cy, self.rot = ctx, zoom, cx, cy, rot

    def __enter__(self):
        c = self.ctx
        c.save()
        c.translate(W / 2, H / 2)
        if self.rot:
            c.rotate(self.rot)
        c.scale(self.z, self.z)
        c.translate(-self.cx, -self.cy)
        return c

    def __exit__(self, *a):
        self.ctx.restore()


def fill_rect(ctx, x, y, w, h, c, a=1.0):
    setc(ctx, c, a)
    ctx.rectangle(x, y, w, h)
    ctx.fill()


def vgrad(ctx, x, y, w, h, stops):
    g = cairo.LinearGradient(0, y, 0, y + h)
    for off, c, *al in stops:
        g.add_color_stop_rgba(off, c[0], c[1], c[2], al[0] if al else 1.0)
    ctx.set_source(g)
    ctx.rectangle(x, y, w, h)
    ctx.fill()


def glow(ctx, x, y, r, c, a=1.0, add=True, core=0.0):
    ctx.save()
    if add:
        ctx.set_operator(cairo.OPERATOR_ADD)
    g = cairo.RadialGradient(x, y, r * core, x, y, r)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], a)
    g.add_color_stop_rgba(0.35, c[0], c[1], c[2], a * 0.45)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


def ellipse(ctx, x, y, rx, ry, c=None, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    if c is not None:
        setc(ctx, c, a)
        ctx.fill()


def capsule(ctx, p1, p2, w, c, a=1.0):
    setc(ctx, c, a)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(*p1)
    ctx.line_to(*p2)
    ctx.stroke()


def poly(ctx, pts, c, a=1.0):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    setc(ctx, c, a)
    ctx.fill()


def vignette(ctx, strength=0.55):
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, W * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, strength)
    ctx.set_source(g)
    ctx.paint()


def black(ctx, a):
    if a > 0:
        ctx.set_source_rgba(0, 0, 0, clamp(a))
        ctx.paint()


def tint(ctx, c, a):
    if a > 0:
        ctx.set_source_rgba(c[0], c[1], c[2], a)
        ctx.paint()


# ---------------------------------------------------------------- palettes
NIGHT = (C("#060b1c"), C("#0e1d42"), C("#1f3563"))
DAWN = (C("#14214a"), C("#5b4a7a"), C("#e8a06a"))
MORNING = (C("#7fb2d9"), C("#d9c9a8"), C("#f6d9a0"))
DAY = (C("#6fa8d6"), C("#bcd6e6"), C("#f3e2bb"))
DUSK = (C("#2a2b55"), C("#a35a5a"), C("#f0a35e"))

MUD = C("#b48a5e")
MUD_DARK = C("#7d5a3a")
MUD_NIGHT = C("#2c2a3c")
SAND = C("#d9b98a")
STRAW = C("#b8975c")
WOOD = C("#5a3b22")
GOLD = C("#ffd27a")
WARM = C("#ffb35c")
HOLY = C("#fff4d6")


def sky(ctx, pal, horizon=H * 0.75, t=1.0, pal2=None):
    top, mid, bot = pal
    if pal2:
        top, mid, bot = (mix(a, b, t) for a, b in zip(pal, pal2))
    g = cairo.LinearGradient(0, -200, 0, horizon)
    g.add_color_stop_rgb(0, *top)
    g.add_color_stop_rgb(0.6, *mid)
    g.add_color_stop_rgb(1, *bot)
    ctx.set_source(g)
    ctx.rectangle(-2000, -2000, W + 4000, H + 4000)
    ctx.fill()


_STARS = None


def stars(ctx, time, alpha=1.0, y_max=H * 0.7, seed=3, n=170, x0=-200, x1=W + 200):
    if alpha <= 0.01:
        return
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(-150, y_max) ** 1.0
        r = rnd.choice([0.7, 0.9, 1.1, 1.5, 2.0])
        ph = rnd.uniform(0, 6.28)
        tw = 0.6 + 0.4 * math.sin(time * rnd.uniform(1.0, 3.0) + ph)
        a = alpha * tw * (1 - y / (y_max + 200)) * 0.95
        ctx.set_source_rgba(1, 1, 0.92, clamp(a))
        ctx.arc(x, y, r, 0, 6.283)
        ctx.fill()
        if r >= 1.5:
            glow(ctx, x, y, r * 5, (0.8, 0.85, 1.0), a * 0.25)


def moon(ctx, x, y, r, a=1.0):
    glow(ctx, x, y, r * 5, (0.7, 0.8, 1.0), 0.18 * a)
    ellipse(ctx, x, y, r, r, C("#f2eed8"), a)
    ellipse(ctx, x + r * 0.35, y - r * 0.15, r * 0.9, r * 0.9, C("#0e1d42"), a * 0.0)


# ---------------------------------------------------------------- architecture
def house(ctx, x, ground, w, h, col, win=None, lit=0.0, door=False, night=0.0, seed=0):
    rnd = random.Random(seed)
    col = mix(col, MUD_NIGHT, night)
    side = shade(col, 0.78)
    # body with slightly uneven parapet
    ctx.move_to(x, ground)
    ctx.line_to(x, ground - h)
    steps = max(2, int(w / 18))
    for i in range(steps + 1):
        px = x + w * i / steps
        ctx.line_to(px, ground - h - rnd.uniform(0, 5) - (4 if i in (0, steps) else 0))
    ctx.line_to(x + w, ground)
    ctx.close_path()
    setc(ctx, col)
    ctx.fill()
    fill_rect(ctx, x + w * 0.82, ground - h, w * 0.18, h, side, 0.55)
    # roof beams poking out
    for i in range(int(w / 40)):
        bx = x + 14 + i * 40
        fill_rect(ctx, bx, ground - h + 10, 6, 6, shade(col, 0.45))
    if door:
        dw, dh = min(34, w * 0.3), min(60, h * 0.55)
        dx = x + w * 0.3
        fill_rect(ctx, dx, ground - dh, dw, dh, shade(WOOD, 1 - night * 0.6))
    if win:
        wx, wy, ww, wh = x + win[0] * w, ground - h + win[1] * h, win[2], win[3]
        fill_rect(ctx, wx, wy, ww, wh, shade(col, 0.35))
        if lit > 0:
            fill_rect(ctx, wx, wy, ww, wh, WARM, lit)
            glow(ctx, wx + ww / 2, wy + wh / 2, 60, WARM, 0.5 * lit)


def skyline(ctx, ground, night=0.0, seed=1, x0=-300, x1=W + 300, scale=1.0, lit_t=None, base=MUD):
    rnd = random.Random(seed)
    x = x0
    i = 0
    while x < x1:
        w = rnd.uniform(60, 150) * scale
        h = rnd.uniform(50, 120) * scale
        lit = 0.0
        win = None
        if rnd.random() < 0.6:
            win = (rnd.uniform(0.2, 0.6), rnd.uniform(0.25, 0.5), 9 * scale, 11 * scale)
            if lit_t is not None and rnd.random() < 0.5:
                lit = clamp(lit_t * rnd.uniform(0.5, 1.0))
        house(ctx, x, ground, w, h, shade(base, rnd.uniform(0.85, 1.1)), win=win, lit=lit,
              night=night, seed=seed * 100 + i)
        x += w - rnd.uniform(0, 12)
        i += 1


def palm(ctx, x, ground, h, t=0.0, col=None, sway=1.0):
    col = col or C("#3d3a24")
    lean = math.sin(t * 0.8 + x * 0.01) * 6 * sway
    top = (x + h * 0.12 + lean, ground - h)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(10):
        f0, f1 = k / 10, (k + 1) / 10
        p0 = (lerp(x, top[0], f0) + math.sin(f0 * 3) * 8, lerp(ground, top[1], f0))
        p1 = (lerp(x, top[0], f1) + math.sin(f1 * 3) * 8, lerp(ground, top[1], f1))
        capsule(ctx, p0, p1, lerp(h * 0.07, h * 0.045, f0), shade(col, 0.9 + 0.1 * (k % 2)))
    leaf = shade(col, 1.25)
    for j in range(9):
        ang = -math.pi / 2 + (j - 4) * 0.42 + math.sin(t * 1.3 + j) * 0.05 * sway
        L = h * (0.42 + 0.06 * math.sin(j * 7))
        droop = 0.5 + 0.15 * abs(j - 4)
        ex = top[0] + math.cos(ang) * L
        ey = top[1] + math.sin(ang) * L * 0.6 + L * droop * 0.5
        mx = top[0] + math.cos(ang) * L * 0.5
        my = top[1] + math.sin(ang) * L * 0.55 - L * 0.08
        ctx.move_to(*top)
        ctx.curve_to(mx, my - h * 0.03, mx, my + h * 0.02, ex, ey)
        ctx.curve_to(mx, my + h * 0.06, mx, my + h * 0.05, *top)
        setc(ctx, leaf)
        ctx.fill()


# ---------------------------------------------------------------- light of the Prophet ﷺ
def holy_light(ctx, x, y, r, time, intensity=1.0):
    """A small soft light. Never a figure."""
    if intensity <= 0:
        return
    pulse = 1 + 0.06 * math.sin(time * 1.6)
    glow(ctx, x, y, r * 9 * pulse, GOLD, 0.22 * intensity)
    glow(ctx, x, y, r * 4.5 * pulse, HOLY, 0.45 * intensity)
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_ADD)
    for i in range(10):
        a = time * 0.08 + i * math.pi / 5
        g = cairo.RadialGradient(x, y, r, x, y, r * 7 * pulse)
        g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.035 * intensity)
        g.add_color_stop_rgba(1, 1, 0.95, 0.8, 0)
        ctx.set_source(g)
        ctx.move_to(x, y)
        ctx.arc(x, y, r * 7 * pulse, a - 0.05, a + 0.05)
        ctx.close_path()
        ctx.fill()
    ctx.restore()
    glow(ctx, x, y, r * 1.8, (1, 0.98, 0.9), 0.6 * intensity, core=0.3)
    ellipse(ctx, x, y, r * 0.7, r * 0.7, (1, 1, 0.97), 0.95 * min(1, intensity))


def oil_lamp(ctx, x, y, s, time, lit=1.0, seed=0):
    ellipse(ctx, x, y, 14 * s, 6 * s, C("#8a5a32"))
    ellipse(ctx, x + 12 * s, y - 2 * s, 6 * s, 3 * s, C("#8a5a32"))
    ellipse(ctx, x, y - 3 * s, 8 * s, 2.5 * s, C("#3a2414"))
    if lit <= 0:
        return
    fl = 1 + 0.15 * math.sin(time * 13 + seed) + 0.08 * math.sin(time * 29 + seed * 2)
    fx, fy = x + 16 * s, y - 5 * s
    glow(ctx, fx, fy - 6 * s, 120 * s * fl, WARM, 0.35 * lit)
    glow(ctx, fx, fy - 6 * s, 30 * s * fl, GOLD, 0.6 * lit)
    ctx.move_to(fx, fy)
    ctx.curve_to(fx - 4 * s, fy - 5 * s, fx - 1 * s, fy - 12 * s * fl, fx + math.sin(time * 9) * s, fy - 16 * s * fl)
    ctx.curve_to(fx + 2 * s, fy - 10 * s, fx + 4 * s, fy - 5 * s, fx, fy)
    setc(ctx, C("#fff1b0"), lit)
    ctx.fill()


def lantern(ctx, x, y, s, time, seed=0):
    capsule(ctx, (x, y - 14 * s), (x, y - 4 * s), 1.5 * s, C("#2a1c10"))
    ctx.rectangle(x - 6 * s, y - 4 * s, 12 * s, 14 * s)
    setc(ctx, C("#ffd88a"))
    ctx.fill()
    fl = 1 + 0.12 * math.sin(time * 11 + seed)
    glow(ctx, x, y + 3 * s, 70 * s * fl, WARM, 0.45)
    glow(ctx, x, y + 3 * s, 18 * s, GOLD, 0.7)


# ---------------------------------------------------------------- people
# A pose is a dict of joint angles in degrees. Angles of limbs are measured
# from "straight down"; positive means toward the facing direction.
POSES = {
    "stand": dict(torso=0, th1=0, sh1=0, th2=0, sh2=0, arm=8, el=0, arm2=-6, el2=0, head=0),
    "qiyam": dict(torso=0, th1=0, sh1=0, th2=0, sh2=0, arm=20, el=95, arm2=15, el2=100, head=12),
    "ruku": dict(torso=90, th1=0, sh1=0, th2=0, sh2=0, arm=-35, el=0, arm2=-30, el2=0, head=0),
    "sujud": dict(torso=132, th1=12, sh1=-90, th2=12, sh2=-90, arm=95, el=10, arm2=90, el2=12, head=5),
    "jalsa": dict(torso=-2, th1=90, sh1=-88, th2=90, sh2=-88, arm=15, el=70, arm2=10, el2=72, head=8),
    "sit_hug": dict(torso=-12, th1=145, sh1=15, th2=140, sh2=10, arm=55, el=70, arm2=50, el2=75, head=25),
    "sit_up": dict(torso=-12, th1=145, sh1=15, th2=140, sh2=10, arm=55, el=70, arm2=50, el2=75, head=-15),
    "sweep": dict(torso=28, th1=8, sh1=0, th2=-8, sh2=0, arm=45, el=15, arm2=30, el2=20, head=10),
    "kneel_give": dict(torso=10, th1=90, sh1=-88, th2=90, sh2=-88, arm=70, el=20, arm2=40, el2=60, head=15),
    "bow_sit": dict(torso=18, th1=90, sh1=-88, th2=90, sh2=-88, arm=25, el=60, arm2=20, el2=65, head=35),
    "carry": dict(torso=0, th1=0, sh1=0, th2=0, sh2=0, arm=170, el=-20, arm2=-6, el2=0, head=0),
}


def pose_mix(a, b, t):
    pa = POSES[a] if isinstance(a, str) else a
    pb = POSES[b] if isinstance(b, str) else b
    t = ease(t)
    return {k: lerp(pa[k], pb[k], t) for k in pa}


def walk_pose(phase, base="stand", amp=1.0):
    p = dict(POSES[base])
    s = math.sin(phase)
    p["th1"] = 24 * s * amp
    p["th2"] = -24 * s * amp
    p["sh1"] = p["th1"] - max(0, -s) * 30 * amp
    p["sh2"] = p["th2"] - max(0, s) * 30 * amp
    p["arm"] = -18 * s * amp + 4
    p["arm2"] = 18 * s * amp + 4
    p["el"] = 12
    p["el2"] = 12
    p["torso"] = 4
    return p


def _dir(angle_deg, f):
    a = math.radians(angle_deg)
    return (math.sin(a) * f, math.cos(a))


class Look:
    def __init__(self, robe, cloak=None, turban=None, skin=None, feet=None, tail=False, scarf=None):
        self.robe = robe
        self.cloak = cloak
        self.turban = turban
        self.skin = skin or C("#8a5f42")
        self.feet = feet or C("#3a2a1c")
        self.tail = tail
        self.scarf = scarf  # women: head covering colour


# characters (shown from behind / side / silhouette, faces never drawn)
ABU_BAKR = Look(C("#d8c7a3"), C("#7a5232"), C("#efe9dc"), tail=True)
UMAR = Look(C("#b9b3a6"), C("#5c5f66"), C("#2c3550"), tail=True)
BILAL = Look(C("#e9e2d2"), C("#8a7350"), C("#f3efe6"), skin=C("#4a3022"))
TOWN = [
    Look(C("#e6dcc6"), None, C("#f1ece2")),
    Look(C("#cbb995"), C("#6e5a3e"), C("#d9cfbb")),
    Look(C("#a9a08e"), None, C("#3d3a35")),
    Look(C("#d7c9a9"), C("#4f4636"), C("#ece4d2")),
    Look(C("#bfae8a"), None, C("#6b4b2e")),
    Look(C("#e2d6bd"), C("#80684a"), C("#c9bfa9")),
]
WOMAN_FAR = Look(C("#3b3330"), None, None, scarf=C("#3b3330"))


def _darken_look(look, k):
    return Look(shade(look.robe, k), shade(look.cloak, k) if look.cloak else None,
                shade(look.turban, k) if look.turban else None, shade(look.skin, k),
                shade(look.feet, k), look.tail, shade(look.scarf, k) if look.scarf else None)


def person_side(ctx, x, ground, s, pose, look, facing=1, dark=1.0, silhouette=None, a=1.0, props=None):
    """Side-view figure. s = standing height in px. Returns dict of key points."""
    P = POSES[pose] if isinstance(pose, str) else pose
    f = facing
    th, sh, to = 0.26 * s, 0.25 * s, 0.31 * s
    ua, fa = 0.17 * s, 0.16 * s
    hr = 0.072 * s
    tw, lw, aw = 0.18 * s, 0.125 * s, 0.07 * s

    hip = (0.0, 0.0)

    def add(p, l, ang, up=False):
        d = _dir(ang, f)
        return (p[0] + d[0] * l, p[1] + (-d[1] if up else d[1]) * l)

    k1 = add(hip, th, P["th1"])
    a1 = add(k1, sh, P["sh1"])
    k2 = add(hip, th, P["th2"])
    a2 = add(k2, sh, P["sh2"])
    neck = add(hip, to, P["torso"], up=True)
    head = add(neck, hr * 1.25, P["torso"] + P["head"], up=True)
    shoulder = add(hip, to * 0.85, P["torso"], up=True)
    e1 = add(shoulder, ua, P["arm"])
    h1 = add(e1, fa, P["arm"] + P["el"])
    e2 = add(shoulder, ua, P["arm2"])
    h2 = add(e2, fa, P["arm2"] + P["el2"])

    pts = [k1, a1, k2, a2, head, h1, h2, neck]
    low = max(p[1] + (hr if p is head else lw * 0.5) for p in pts)
    ox, oy = x, ground - low

    def T(p):
        return (ox + p[0], oy + p[1])

    lk = look
    if silhouette is not None:
        lk = Look(silhouette, silhouette, silhouette, silhouette, silhouette, look.tail,
                  silhouette if look.scarf else None)
    elif dark != 1.0:
        lk = _darken_look(look, dark)
    far = _darken_look(lk, 0.72) if silhouette is None else lk

    ctx.push_group()
    # far arm & leg
    capsule(ctx, T(hip), T(k2), lw * 1.05, far.robe)
    capsule(ctx, T(k2), T(a2), lw * 0.95, far.robe)
    ellipse(ctx, T(a2)[0] + f * lw * 0.25, T(a2)[1] + lw * 0.2, lw * 0.5, lw * 0.25, far.feet)
    capsule(ctx, T(shoulder), T(e2), aw, far.cloak or far.robe)
    capsule(ctx, T(e2), T(h2), aw * 0.9, far.cloak or far.robe)
    ellipse(ctx, *T(h2), aw * 0.5, aw * 0.5, far.skin)
    # thobe skirt when upright
    upright = clamp(1 - (abs(P["th1"]) + abs(P["th2"])) / 80) * clamp(1 - abs(P["torso"]) / 40)
    if upright > 0.05:
        mid = ((a1[0] + a2[0]) / 2, max(a1[1], a2[1]) - lw * 0.3)
        spread = abs(a1[0] - a2[0]) * 0.5
        flare = tw * 0.62 + spread
        poly(ctx, [T((-tw * 0.5, -lw * 0.2)), T((tw * 0.5, -lw * 0.2)),
                   T((mid[0] + flare, mid[1])), T((mid[0] - flare, mid[1]))], lk.robe, upright)
    # near leg
    capsule(ctx, T(hip), T(k1), lw * 1.1, lk.robe)
    capsule(ctx, T(k1), T(a1), lw, lk.robe)
    ellipse(ctx, T(a1)[0] + f * lw * 0.25, T(a1)[1] + lw * 0.2, lw * 0.5, lw * 0.25, lk.feet)
    # torso + cloak
    capsule(ctx, T(hip), T(neck), tw, lk.robe)
    if lk.cloak:
        back = _dir(P["torso"] + 90, f)
        off = (-back[0] * tw * 0.12, back[1] * tw * 0.12)
        capsule(ctx, T((hip[0] + off[0], hip[1] + off[1] + lw * 0.3)), T((neck[0] + off[0], neck[1] + off[1])),
                tw * 1.08, lk.cloak)
        capsule(ctx, T(hip), T(neck), tw * 0.55, lk.robe)
    # head (no face drawn)
    hx, hy = T(head)
    ellipse(ctx, hx, hy, hr, hr * 1.08, lk.skin)
    if lk.scarf:
        ellipse(ctx, hx, hy - hr * 0.05, hr * 1.25, hr * 1.3, lk.scarf)
        capsule(ctx, (hx, hy), T(shoulder), hr * 2.0, lk.scarf)
    if lk.turban:
        ctx.save()
        ctx.translate(hx, hy)
        ctx.rotate(math.radians(P["torso"] + P["head"]) * f)
        ellipse(ctx, -f * hr * 0.1, -hr * 0.45, hr * 1.18, hr * 0.78, lk.turban)
        ellipse(ctx, -f * hr * 0.05, -hr * 0.62, hr * 0.85, hr * 0.5, shade(lk.turban, 1.12))
        if lk.tail:
            capsule(ctx, (-f * hr * 0.8, -hr * 0.2), (-f * hr * 1.1, hr * 1.4), hr * 0.42, lk.turban)
        ctx.restore()
    # near arm
    capsule(ctx, T(shoulder), T(e1), aw * 1.05, lk.cloak or lk.robe)
    capsule(ctx, T(e1), T(h1), aw, lk.robe)
    ellipse(ctx, *T(h1), aw * 0.55, aw * 0.55, lk.skin)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(a)
    return {"hand": T(h1), "hand2": T(h2), "head": (hx, hy), "hip": T(hip), "hr": hr}


def person_back(ctx, x, ground, s, look, sit=0.0, sway=0.0, bob=0.0, raise_hand=0.0, bow=0.0,
                dark=1.0, silhouette=None, a=1.0, shake=0.0, step=None):
    """Figure seen from behind (no face). sit 0..1, raise_hand 0..1 (right arm), bow 0..1."""
    lk = look
    if silhouette is not None:
        lk = Look(silhouette, silhouette, silhouette, silhouette, silhouette, look.tail,
                  silhouette if look.scarf else None)
    elif dark != 1.0:
        lk = _darken_look(look, dark)
    ctx.push_group()
    ctx.save()
    ctx.translate(x, ground - bob * s * 0.02)
    ctx.rotate(math.radians(sway))
    bw = 0.36 * s
    hgt = lerp(0.82 * s, 0.5 * s, sit)
    shoulder_y = -hgt
    if step is not None and sit < 0.5:
        # legs / feet stepping below the hem
        for side, ph in ((-1, 0), (1, math.pi)):
            lift = max(0, math.sin(step + ph)) * s * 0.03
            ellipse(ctx, side * bw * 0.18, -lift, bw * 0.12, s * 0.025, lk.feet)
    # body
    body_bottom_w = lerp(bw * 0.95, bw * 1.5, sit)
    ctx.move_to(-body_bottom_w / 2, -s * 0.02)
    ctx.curve_to(-bw * 0.6, shoulder_y * 0.45, -bw * 0.62, shoulder_y + s * 0.02, -bw * 0.3, shoulder_y - s * 0.015)
    ctx.curve_to(-bw * 0.1, shoulder_y - s * 0.03, bw * 0.1, shoulder_y - s * 0.03, bw * 0.3, shoulder_y - s * 0.015)
    ctx.curve_to(bw * 0.62, shoulder_y + s * 0.02, bw * 0.6, shoulder_y * 0.45, body_bottom_w / 2, -s * 0.02)
    ctx.close_path()
    setc(ctx, lk.cloak or lk.robe)
    ctx.fill()
    if lk.cloak:
        # robe visible at the hem
        ctx.move_to(-body_bottom_w * 0.42, -s * 0.02)
        ctx.line_to(body_bottom_w * 0.42, -s * 0.02)
        ctx.line_to(body_bottom_w * 0.36, -s * 0.08)
        ctx.line_to(-body_bottom_w * 0.36, -s * 0.08)
        ctx.close_path()
        setc(ctx, lk.robe)
        ctx.fill()
        # cloak fold line
        setc(ctx, shade(lk.cloak, 0.8))
        ctx.set_line_width(s * 0.008)
        ctx.move_to(0, shoulder_y + s * 0.04)
        ctx.line_to(sway * 0.3, -s * 0.05)
        ctx.stroke()
    # raised right arm
    if raise_hand > 0.01:
        sh = (bw * 0.38, shoulder_y + s * 0.03)
        ang = math.radians(lerp(10, 165, ease(raise_hand)))
        el = (sh[0] + math.sin(ang) * s * 0.15, sh[1] + math.cos(ang) * s * 0.15)
        ang2 = ang + math.radians(lerp(0, 15, raise_hand))
        hd = (el[0] + math.sin(ang2) * s * 0.14, el[1] + math.cos(ang2) * s * 0.14)
        capsule(ctx, sh, el, s * 0.06, lk.cloak or lk.robe)
        capsule(ctx, el, hd, s * 0.05, lk.robe)
        ellipse(ctx, hd[0], hd[1], s * 0.03, s * 0.03, lk.skin)
    # head
    hr = 0.085 * s
    hy = shoulder_y - hr * 0.75 + bow * hr * 0.9 + math.sin(shake * 40) * shake * 1.5
    capsule(ctx, (0, shoulder_y + s * 0.01), (0, hy), hr * 1.0, lk.skin)
    ellipse(ctx, 0, hy, hr, hr * 1.05 * (1 - bow * 0.15), lk.skin)
    if lk.scarf:
        ellipse(ctx, 0, hy, hr * 1.3, hr * 1.3, lk.scarf)
        capsule(ctx, (0, hy), (0, shoulder_y + s * 0.1), hr * 2.2, lk.scarf)
    if lk.turban:
        ellipse(ctx, 0, hy - hr * 0.35 + bow * hr * 0.2, hr * 1.2, hr * 0.85, lk.turban)
        ellipse(ctx, 0, hy - hr * 0.55 + bow * hr * 0.2, hr * 0.85, hr * 0.5, shade(lk.turban, 1.12))
        if lk.tail:
            capsule(ctx, (hr * 0.1, hy + hr * 0.2), (hr * 0.15 + sway, shoulder_y + s * 0.12), hr * 0.5,
                    shade(lk.turban, 0.92))
    ctx.restore()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(a)
    return {"head": (x, ground - hgt - hr)}


def blind_woman(ctx, x, ground, s, time, hands="lap", smile=0.0, turn=0.0, cry=0.0, a=1.0, dark=1.0):
    """Old blind woman, front view, seated on a mat. Eyes closed."""
    dress = shade(C("#4e4038"), dark)
    scarf = shade(C("#2f2a2a"), dark)
    skin = shade(C("#b07a58"), dark)
    ctx.push_group()
    ctx.save()
    ctx.translate(x, ground)
    breath = math.sin(time * 1.4) * s * 0.004
    # body (seated dome)
    ctx.move_to(-s * 0.42, 0)
    ctx.curve_to(-s * 0.42, -s * 0.35, -s * 0.25, -s * 0.52 - breath, 0, -s * 0.53 - breath)
    ctx.curve_to(s * 0.25, -s * 0.52 - breath, s * 0.42, -s * 0.35, s * 0.42, 0)
    ctx.close_path()
    setc(ctx, dress)
    ctx.fill()
    # patches
    fill_rect(ctx, -s * 0.25, -s * 0.2, s * 0.09, s * 0.08, shade(dress, 1.25))
    fill_rect(ctx, s * 0.12, -s * 0.33, s * 0.07, s * 0.07, shade(dress, 0.8))
    # head with scarf
    hx = turn * s * 0.03
    hy = -s * 0.62
    ellipse(ctx, hx, hy + s * 0.02, s * 0.15, s * 0.17, scarf)
    capsule(ctx, (hx, hy + s * 0.05), (hx, -s * 0.45), s * 0.22, scarf)
    ellipse(ctx, hx + turn * s * 0.015, hy + s * 0.025, s * 0.088, s * 0.105, skin)
    # face: closed eyes, mouth
    ex = hx + turn * s * 0.02
    setc(ctx, shade(skin, 0.45))
    ctx.set_line_width(max(1.0, s * 0.006))
    for side in (-1, 1):
        ctx.arc(ex + side * s * 0.032, hy + s * 0.012, s * 0.018, 0.25, math.pi - 0.25)
        ctx.stroke()
    my = hy + s * 0.07
    ctx.move_to(ex - s * 0.025, my)
    ctx.curve_to(ex - s * 0.01, my + s * 0.02 * smile - s * 0.01 * (1 - smile),
                 ex + s * 0.01, my + s * 0.02 * smile - s * 0.01 * (1 - smile), ex + s * 0.025, my)
    ctx.stroke()
    # wrinkles
    setc(ctx, shade(skin, 0.75))
    ctx.set_line_width(max(0.8, s * 0.003))
    ctx.move_to(ex - s * 0.03, hy - s * 0.04)
    ctx.line_to(ex + s * 0.03, hy - s * 0.04)
    ctx.stroke()
    if cry > 0:
        for side in (-1, 1):
            ty = hy + s * 0.03 + ((time * 0.6 + side * 0.3) % 1) * s * 0.06
            ellipse(ctx, ex + side * s * 0.035, ty, s * 0.006, s * 0.009, (0.85, 0.92, 1.0), cry)
    # hands
    if hands == "lap":
        for side in (-1, 1):
            ellipse(ctx, side * s * 0.08, -s * 0.12, s * 0.05, s * 0.032, skin)
    elif hands == "receive":
        ellipse(ctx, -s * 0.045, -s * 0.2, s * 0.05, s * 0.03, skin)
        ellipse(ctx, s * 0.045, -s * 0.2, s * 0.05, s * 0.03, skin)
    elif hands == "dua":
        for side in (-1, 1):
            capsule(ctx, (side * s * 0.15, -s * 0.3), (side * s * 0.07, -s * 0.38), s * 0.06, dress)
            ellipse(ctx, side * s * 0.055, -s * 0.42, s * 0.04, s * 0.06, skin)
    ctx.restore()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(a)
    return {"lap": (x, ground - s * 0.2)}


def goat(ctx, x, ground, s, time, facing=1):
    f = facing
    col = C("#e9e2d4")
    leg = C("#6b5a48")
    bob = math.sin(time * 8) * s * 0.01
    for i, lx in enumerate((-0.3, -0.18, 0.18, 0.3)):
        sw = math.sin(time * 8 + i * 1.6) * s * 0.05
        capsule(ctx, (x + f * lx * s, ground - s * 0.35), (x + f * lx * s + sw, ground), s * 0.05, leg)
    ellipse(ctx, x, ground - s * 0.45 + bob, s * 0.4, s * 0.17, col)
    hx, hy = x + f * s * 0.42, ground - s * 0.62 + bob
    capsule(ctx, (x + f * s * 0.3, ground - s * 0.5 + bob), (hx, hy), s * 0.12, col)
    ellipse(ctx, hx + f * s * 0.06, hy + s * 0.02, s * 0.11, s * 0.07, col)
    capsule(ctx, (hx, hy - s * 0.05), (hx - f * s * 0.08, hy - s * 0.18), s * 0.03, C("#8a7a66"))
    ellipse(ctx, hx - f * s * 0.05, hy + s * 0.03, s * 0.06, s * 0.025, shade(col, 0.85))
    capsule(ctx, (x - f * s * 0.38, ground - s * 0.52 + bob), (x - f * s * 0.45, ground - s * 0.6 + bob),
            s * 0.05, col)


def tear(ctx, x, y, s, a=1.0):
    ctx.move_to(x, y - s)
    ctx.curve_to(x + s * 0.7, y, x + s * 0.6, y + s * 0.8, x, y + s * 0.8)
    ctx.curve_to(x - s * 0.6, y + s * 0.8, x - s * 0.7, y, x, y - s)
    setc(ctx, (0.85, 0.93, 1.0), a)
    ctx.fill()
    glow(ctx, x, y, s * 3, (0.7, 0.85, 1.0), 0.4 * a)


def text_center(ctx, s, x, y, size, c=(1, 1, 1), a=1.0, font="Noto Serif", bold=False):
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    ext = ctx.text_extents(s)
    ctx.move_to(x - ext.width / 2 - ext.x_bearing, y - ext.height / 2 - ext.y_bearing)
    setc(ctx, c, a)
    ctx.show_text(s)
