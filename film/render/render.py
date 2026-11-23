"""Render frames: python3 render.py video START END OUT.mp4 | sheet OUT.png"""
import subprocess
import sys

import cairo

from engine import FPS, H, W, black, ease
from scenes import SHOTS, TOTAL

XF = 0.8   # crossfade length (s)
DIP = 1.2  # dip-to-black length (s)

STARTS = []
_t = 0.0
for _d, _f, _tr in SHOTS:
    STARTS.append(_t)
    _t += _d


def draw_shot(i, t):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(s)
    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()
    d, fn, _ = SHOTS[i]
    fn(ctx, t - STARTS[i], d)
    return s


def frame(t):
    i = max(k for k in range(len(SHOTS)) if STARTS[k] <= t or k == 0)
    surf = draw_shot(i, t)
    ctx = cairo.Context(surf)
    # transitions at the start of shot i and of shot i+1
    for j in (i, i + 1):
        if j <= 0 or j >= len(SHOTS):
            continue
        b = STARTS[j]
        if SHOTS[j][2] == "x" and abs(t - b) < XF / 2:
            a = ease((t - (b - XF / 2)) / XF)
            other = draw_shot(j - 1 if j == i else j, t)
            # shot j fades in over shot j-1
            if j == i:
                base, top, al = other, surf, a
            else:
                base, top, al = surf, other, a
            out = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
            c2 = cairo.Context(out)
            c2.set_source_surface(base)
            c2.paint()
            c2.set_source_surface(top)
            c2.paint_with_alpha(al)
            return out
        if SHOTS[j][2] == "b" and abs(t - b) < DIP / 2:
            black(ctx, 1 - abs(t - b) / (DIP / 2))
    if t < 1.5:
        black(ctx, 1 - t / 1.5)
    return surf


def video(start, end, out):
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for n in range(int(round(start * FPS)), int(round(end * FPS))):
        s = frame(n / FPS)
        s.flush()
        p.stdin.write(bytes(s.get_data()))
    p.stdin.close()
    p.wait()


def sheet(out, cols=6, scale=0.25):
    times = [STARTS[i] + SHOTS[i][0] * 0.6 for i in range(len(SHOTS))]
    rows = (len(times) + cols - 1) // cols
    tw, th = int(W * scale), int(H * scale)
    big = cairo.ImageSurface(cairo.FORMAT_ARGB32, tw * cols, th * rows)
    c = cairo.Context(big)
    for k, t in enumerate(times):
        s = frame(t)
        c.save()
        c.translate((k % cols) * tw, (k // cols) * th)
        c.scale(scale, scale)
        c.set_source_surface(s)
        c.paint()
        c.restore()
        c.set_source_rgb(1, 1, 0)
        c.select_font_face("Inter")
        c.set_font_size(14)
        c.move_to((k % cols) * tw + 4, (k // cols) * th + 16)
        c.show_text(f"{k} {SHOTS[k][1].__name__} {t:.0f}s")
    big.write_to_png(out)


if __name__ == "__main__":
    if sys.argv[1] == "video":
        video(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
    elif sys.argv[1] == "sheet":
        sheet(sys.argv[2])
    elif sys.argv[1] == "info":
        print("total", TOTAL, "shots", len(SHOTS))
        for i, (d, f, tr) in enumerate(SHOTS):
            print(i, f"{STARTS[i]:6.1f}", d, tr, f.__name__)
    elif sys.argv[1] == "png":
        frame(float(sys.argv[2])).write_to_png(sys.argv[3])
