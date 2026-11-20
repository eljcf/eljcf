from pathlib import Path
import math
import random

WIDTH = 1600
HEIGHT = 300
SEED = 8473
OUTPUT_DIR = Path(__file__).resolve().parent

THEMES = {
    "light": {
        "primary": "#173C32",
        "secondary": "#718077",
        "line": "#315C4C",
        "accent": "#B54A38",
    },
    "dark": {
        "primary": "#EEF0E9",
        "secondary": "#91A398",
        "line": "#8FA79A",
        "accent": "#D06A53",
    },
}


def flow_angle(x, y):
    nx = x / WIDTH
    ny = y / HEIGHT
    base = 0.08 + 0.34 * math.sin(nx * 5.6 + ny * 3.2) + 0.16 * math.cos(ny * 8.4 - nx * 2.6)
    dx = (x - WIDTH * 0.79) / (WIDTH * 0.20)
    dy = (y - HEIGHT * 0.50) / (HEIGHT * 0.90)
    influence = math.exp(-1.7 * (dx * dx + dy * dy))
    swirl = math.atan2(dy, dx) + math.pi / 2
    vx = (1 - influence) * math.cos(base) + influence * 0.95 * math.cos(swirl)
    vy = (1 - influence) * math.sin(base) + influence * 0.95 * math.sin(swirl)
    return math.atan2(vy, vx)


def trace(x, y, step=4.5, max_steps=360):
    points = []
    for _ in range(max_steps):
        if x > WIDTH + 40 or x < -40 or y < -60 or y > HEIGHT + 60:
            break
        points.append((x, y))
        angle = flow_angle(x, y)
        x += math.cos(angle) * step
        y += math.sin(angle) * step
    return points


def path_data(points):
    return " ".join(("M" if index == 0 else "L") + f"{x:.1f} {y:.1f}" for index, (x, y) in enumerate(points))


def typing_frames():
    english_width = 8 * 33.6
    chinese_width = 5 * 56.0
    frames = [(0.0, english_width), (0.20, english_width)]
    for index in range(7, -1, -1):
        frames.append((0.20 + (8 - index) * 0.015, index * 33.6))
    frames.append((0.34, 0.0))
    for index in range(1, 6):
        frames.append((0.34 + index * 0.032, index * 56.0))
    frames.append((0.72, chinese_width))
    for index in range(4, -1, -1):
        frames.append((0.72 + (5 - index) * 0.015, index * 56.0))
    frames.append((0.86, 0.0))
    for index in range(1, 9):
        frames.append((0.86 + index * 0.015, index * 33.6))
    frames.append((1.0, english_width))
    return frames


def animation_values(frames, phase):
    selected = []
    for time, width in frames:
        if phase == "english":
            value = width if time < 0.34 or time >= 0.86 else 0.0
        elif phase == "chinese":
            value = width if 0.34 <= time < 0.86 else 0.0
        else:
            value = width + 70.0
        selected.append((time, value))
    times = ";".join(f"{time:.3f}" for time, _ in selected)
    values = ";".join(f"{value:.1f}" for _, value in selected)
    return times, values


def animate(attribute, frames, phase):
    times, values = animation_values(frames, phase)
    return f'<animate attributeName="{attribute}" values="{values}" keyTimes="{times}" calcMode="discrete" dur="16s" repeatCount="indefinite"/>'


def line_art():
    rng = random.Random(SEED)
    paths = []
    for index in range(180):
        start_x = -30 if index < 130 else rng.uniform(-20, 1050)
        start_y = (index + 0.5) * HEIGHT / 130 if index < 130 else rng.uniform(-20, HEIGHT + 20)
        start_y += rng.uniform(-5, 5)
        points = trace(start_x, start_y)
        if len(points) < 4:
            continue
        accent = 95 < start_y < 205 and index % 4 == 0
        paths.append({
            "d": path_data(points),
            "accent": accent,
            "opacity": rng.uniform(0.32, 0.58) if accent else rng.uniform(0.10, 0.25),
            "width": 1.05 if accent else rng.choice([0.65, 0.8, 1.0]),
        })
    return paths


def hero_svg(theme_name, paths):
    theme = THEMES[theme_name]
    frames = typing_frames()
    lines = []
    for path in paths:
        color = theme["accent"] if path["accent"] else theme["line"]
        lines.append(
            f'<path d="{path["d"]}" fill="none" stroke="{color}" stroke-opacity="{path["opacity"]:.2f}" stroke-width="{path["width"]}"/>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" role="img" aria-labelledby="title desc">
  <title id="title">Raz — 吴禹佟, AI Product Manager</title>
  <desc id="desc">A generative flow-field composition in deep green and maple red, with a typewriter name animation.</desc>
  <defs>
    <clipPath id="frame"><rect width="1600" height="300"/></clipPath>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="white" stop-opacity="0"/>
      <stop offset="0.28" stop-color="white" stop-opacity="0"/>
      <stop offset="0.55" stop-color="white" stop-opacity="0.7"/>
      <stop offset="1" stop-color="white" stop-opacity="1"/>
    </linearGradient>
    <mask id="line-fade" maskUnits="userSpaceOnUse" x="0" y="0" width="1600" height="300"><rect width="1600" height="300" fill="url(#fade)"/></mask>
    <clipPath id="english-clip"><rect x="70" y="88" width="268.8" height="78">{animate("width", frames, "english")}</rect></clipPath>
    <clipPath id="chinese-clip"><rect x="70" y="88" width="0" height="78">{animate("width", frames, "chinese")}</rect></clipPath>
    <style>
      .mono {{ font-family: "SFMono-Regular", Menlo, Consolas, monospace; }}
      .cjk {{ font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif; }}
      .cursor {{ animation: blink 1.05s step-end infinite; }}
      @keyframes blink {{ 0%,48% {{ opacity:1; }} 49%,100% {{ opacity:0; }} }}
    </style>
  </defs>
  <g clip-path="url(#frame)" mask="url(#line-fade)">{''.join(lines)}</g>
  <g class="mono" font-size="11" letter-spacing="2.0">
    <text x="70" y="48" fill="{theme['secondary']}">AI PRODUCT MANAGER</text>
    <text x="1530" y="48" text-anchor="end" fill="{theme['secondary']}">RAZ / 2026</text>
  </g>
  <g font-size="56" font-weight="500">
    <text class="mono" x="70" y="145" fill="{theme['primary']}" clip-path="url(#english-clip)">I'm Raz.</text>
    <text class="cjk" x="70" y="145" fill="{theme['primary']}" clip-path="url(#chinese-clip)">我叫吴禹佟</text>
  </g>
  <rect class="cursor" x="338.8" y="105" width="3" height="48" fill="{theme['accent']}">{animate("x", frames, "cursor")}</rect>
  <text class="mono" x="72" y="207" fill="{theme['secondary']}" font-size="14" letter-spacing="1.1">RAG · Agents · Developer Tools</text>
</svg>
'''


if __name__ == "__main__":
    paths = line_art()
    for name in THEMES:
        (OUTPUT_DIR / f"hero-{name}.svg").write_text(hero_svg(name, paths), encoding="utf-8")
