"""Generiše proceduralne pejzaže korištene na stranici i snima ih u folder img/.
Varijanta B: AVIF i WebP, dimenzije prilagođene prikazu, dvije veličine naslovne slike.
Potrebno: Python 3, numpy, Pillow (za AVIF Pillow 11.2+ ili pillow-avif-plugin).
Pokretanje iz foldera stranice: python izvor/napravi_slike_b.py"""
import numpy as np
from PIL import Image, ImageFilter
import os

rng = np.random.default_rng(42)


def fractal_noise(h, w, octaves=6, seed=0):
    r = np.random.default_rng(seed)
    out = np.zeros((h, w))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        sh, sw = max(2, h // (2 ** (octaves - o + 1))), max(2, w // (2 ** (octaves - o + 1)))
        base = r.random((sh, sw))
        img = Image.fromarray((base * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        out += amp * (np.asarray(img) / 255.0)
        total += amp
        amp *= 0.55
    return out / total


def ridge(w, seed, base, amp, rough):
    r = np.random.default_rng(seed)
    x = np.linspace(0, 1, w)
    y = np.full(w, base, dtype=float)
    for k in range(1, 9):
        y += amp / k * np.sin(2 * np.pi * (k * x * r.uniform(0.6, 1.4) + r.random()))
    y += rough * (fractal_noise(1, w, 5, seed)[0] - 0.5)
    return y


def landscape(w, h, seed, sky_top, sky_bot, layers, water=None):
    yy = np.linspace(0, 1, h)[:, None]
    img = np.zeros((h, w, 3))
    for c in range(3):
        img[..., c] = sky_top[c] * (1 - yy) + sky_bot[c] * yy
    clouds = fractal_noise(h, w, 7, seed + 100)
    cmask = np.clip((clouds - 0.55) * 3, 0, 1) * (1 - yy) ** 1.5
    img = img * (1 - cmask[..., None] * 0.6) + 255 * cmask[..., None] * 0.6
    tex = fractal_noise(h, w, 7, seed + 7)
    for i, (col, base, amp, rough) in enumerate(layers):
        ry = ridge(w, seed + i, base, amp, rough) * h
        mask = (np.arange(h)[:, None] > ry[None, :])
        shade = 0.75 + 0.5 * (tex - 0.5)
        layer = np.stack([col[c] * shade for c in range(3)], -1)
        img[mask] = layer[mask]
    if water is not None:
        wl = int(water * h)
        refl = img[wl - (h - wl):wl][::-1].copy() if 2 * wl > h else img[:h - wl][::-1].copy()
        refl = refl[: h - wl]
        ripple = fractal_noise(h - wl, w, 6, seed + 55)
        img[wl:] = refl * 0.65 + np.array([30, 60, 90]) * 0.35 + (ripple[..., None] - 0.5) * 30
    noise = rng.normal(0, 5, img.shape)
    img = np.clip(img + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(img).filter(ImageFilter.GaussianBlur(0.6))

scenes = [
    dict(name="hero", w=2400, h=1200, seed=1, sky_top=(70, 120, 190), sky_bot=(235, 200, 160),
         layers=[((120, 130, 160), 0.42, 0.08, 0.10), ((70, 95, 90), 0.55, 0.06, 0.08),
                 ((35, 60, 45), 0.66, 0.04, 0.05)], water=0.74),
    dict(name="kartica1", w=1200, h=800, seed=11, sky_top=(40, 90, 170), sky_bot=(200, 220, 240),
         layers=[((150, 150, 170), 0.35, 0.12, 0.12), ((60, 100, 60), 0.6, 0.05, 0.06)]),
    dict(name="kartica2", w=1200, h=800, seed=12, sky_top=(250, 140, 90), sky_bot=(250, 210, 150),
         layers=[((110, 70, 90), 0.5, 0.07, 0.07), ((50, 40, 60), 0.68, 0.04, 0.05)], water=0.8),
    dict(name="kartica3", w=1200, h=800, seed=13, sky_top=(90, 150, 210), sky_bot=(220, 235, 245),
         layers=[((230, 235, 245), 0.3, 0.15, 0.10), ((90, 110, 130), 0.55, 0.07, 0.08),
                 ((40, 70, 50), 0.72, 0.03, 0.04)]),
    dict(name="kartica4", w=1200, h=800, seed=14, sky_top=(30, 40, 90), sky_bot=(160, 110, 160),
         layers=[((60, 50, 80), 0.55, 0.06, 0.06), ((25, 25, 40), 0.7, 0.03, 0.03)], water=0.82),
    dict(name="kartica5", w=1200, h=800, seed=15, sky_top=(120, 170, 220), sky_bot=(245, 240, 220),
         layers=[((170, 160, 110), 0.6, 0.03, 0.05), ((110, 140, 70), 0.75, 0.02, 0.03)]),
    dict(name="kartica6", w=1200, h=800, seed=16, sky_top=(60, 110, 160), sky_bot=(180, 210, 220),
         layers=[((80, 120, 100), 0.45, 0.10, 0.10), ((30, 80, 50), 0.62, 0.06, 0.08)], water=0.78),
]


os.makedirs("img", exist_ok=True)
for s in scenes:
    im = landscape(s["w"], s["h"], s["seed"], s["sky_top"], s["sky_bot"], s["layers"], s.get("water")).convert("RGB")
    if s["name"] == "hero":
        for w in (1600, 800):                                  # dvije veličine za srcset
            r = im.resize((w, w // 2), Image.LANCZOS)
            r.save(f"img/hero-{w}.avif", "AVIF", quality=60, speed=6)
            r.save(f"img/hero-{w}.webp", "WEBP", quality=75)
    else:
        im.resize((600, 400), Image.LANCZOS).save(f"img/{s['name']}.webp", "WEBP", quality=75)
    print(s["name"], "gotovo")
