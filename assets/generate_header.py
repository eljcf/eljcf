from pathlib import Path
import math
import random

from PIL import Image, ImageDraw

WIDTH = 1600
HEIGHT = 420
SCALE = 3
SEED = 8473
OUTPUT_DIR = Path(__file__).resolve().parent

THEMES = {
    "light": {
        "background": "#FCFBF8",
        "line": (24, 54, 44),
        "accent": (181, 67, 52),
    },
    "dark": {
        "background": "#0D1F19",
        "line": (183, 198, 186),
        "accent": (214, 106, 82),
    },
}


def flow_angle(x, y):
    nx = x / WIDTH
    ny = y / HEIGHT
    base = (
        0.08
        + 0.30 * math.sin(nx * 5.2 + ny * 3.4)
        + 0.17 * math.cos(ny * 8.2 - nx * 2.8)
    )

    dx = (x - WIDTH * 0.73) / (WIDTH * 0.24)
    dy = (y - HEIGHT * 0.50) / (HEIGHT * 0.88)
    influence = math.exp(-1.65 * (dx * dx + dy * dy))
    swirl = math.atan2(dy, dx) + math.pi / 2

    vx = (1 - influence) * math.cos(base) + influence * 0.92 * math.cos(swirl)
    vy = (1 - influence) * math.sin(base) + influence * 0.92 * math.sin(swirl)
    return math.atan2(vy, vx)


def trace_streamline(x, y, step=4.2, max_steps=360):
    points = []
    for _ in range(max_steps):
        if x > WIDTH + 30 or y < -50 or y > HEIGHT + 50:
            break
        points.append((round(x * SCALE), round(y * SCALE)))
        angle = flow_angle(x, y)
        x += math.cos(angle) * step
        y += math.sin(angle) * step
    return points


def generate(theme_name):
    theme = THEMES[theme_name]
    rng = random.Random(SEED)
    size = (WIDTH * SCALE, HEIGHT * SCALE)
    image = Image.new("RGB", size, theme["background"])
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    line_count = 290
    for index in range(line_count):
        start_x = -35 if index < 235 else rng.uniform(-20, WIDTH * 0.62)
        start_y = (index + 0.5) * HEIGHT / 235 if index < 235 else rng.uniform(-10, HEIGHT + 10)
        start_y += rng.uniform(-4, 4)
        points = trace_streamline(start_x, start_y)
        if len(points) < 3:
            continue

        is_accent = 145 < start_y < 270 and index % 3 == 0
        if is_accent:
            alpha = rng.randint(170, 220) if theme_name == "light" else rng.randint(180, 230)
            color = (*theme["accent"], alpha)
            width = SCALE + 1
        else:
            alpha = rng.randint(38, 82) if theme_name == "light" else rng.randint(36, 78)
            color = (*theme["line"], alpha)
            width = SCALE + 1 if rng.random() < 0.22 else SCALE

        draw.line(points, fill=color, width=width)

    image = Image.alpha_composite(image.convert("RGBA"), layer)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size[0] - 1, size[1] - 1),
        radius=22 * SCALE,
        fill=255,
    )
    image.putalpha(mask)
    image = image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    image.save(OUTPUT_DIR / f"header-{theme_name}.png", optimize=True)


if __name__ == "__main__":
    generate("light")
    generate("dark")
