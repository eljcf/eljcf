from pathlib import Path
import math
import random

WIDTH = 1600
HEIGHT = 430
SEED = 8473
OUTPUT_DIR = Path(__file__).resolve().parent

THEMES = {
    "light": {
        "background": "#FAF7F1",
        "primary": "#173C32",
        "secondary": "#718077",
        "line": "#315C4C",
        "accent": "#B54A38",
        "faint": "#DCD8CF",
    },
    "dark": {
        "background": "#0D211A",
        "primary": "#EEF0E9",
        "secondary": "#91A398",
        "line": "#8FA79A",
        "accent": "#D06A53",
        "faint": "#29443A",
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


def trace(x, y, step=4.5, max_steps=260):
    points = []
    for _ in range(max_steps):
        if x > WIDTH + 40 or x < 570 or y < -60 or y > HEIGHT + 60:
            break
        points.append((x, y))
        angle = flow_angle(x, y)
        x += math.cos(angle) * step
        y += math.sin(angle) * step
    return points


def path_data(points):
    return " ".join(("M" if index == 0 else "L") + f"{x:.1f} {y:.1f}" for index, (x, y) in enumerate(points))


def typing_frames():
    frames = [(0.0, 0.0), (0.04, 0.0)]
    for index in range(1, 9):
        frames.append((0.04 + index * 0.02, index * 37.2))
    frames.append((0.34, 297.6))
    for index in range(7, -1, -1):
        frames.append((0.34 + (8 - index) * 0.015, index * 37.2))
    frames.append((0.50, 0.0))
    for index in range(1, 6):
        frames.append((0.50 + index * 0.035, index * 62.0))
    frames.append((0.82, 310.0))
    for index in range(4, -1, -1):
        frames.append((0.82 + (5 - index) * 0.025, index * 62.0))
    frames.append((1.0, 0.0))
    return frames


def animation_values(frames, phase):
    selected = []
    if phase == "english":
        selected = [(time, width) for time, width in frames if time <= 0.50]
        selected.append((1.0, 0.0))
    elif phase == "chinese":
        selected = [(0.0, 0.0), (0.49, 0.0)]
        selected.extend((time, width) for time, width in frames if time >= 0.50)
    else:
        selected = frames
    times = ";".join(f"{time:.3f}" for time, _ in selected)
    widths = ";".join(f"{width:.1f}" for _, width in selected)
    return times, widths


def animate(attribute, frames, phase):
    times, values = animation_values(frames, phase)
    return f'<animate attributeName="{attribute}" values="{values}" keyTimes="{times}" calcMode="discrete" dur="17s" repeatCount="indefinite"/>'


def line_art():
    rng = random.Random(SEED)
    paths = []
    for index in range(180):
        start_x = 590 if index < 120 else rng.uniform(600, 1120)
        start_y = (index + 0.5) * HEIGHT / 120 if index < 120 else rng.uniform(-20, HEIGHT + 20)
        start_y += rng.uniform(-5, 5)
        points = trace(start_x, start_y)
        if len(points) < 4:
            continue
        accent = 145 < start_y < 285 and index % 4 == 0
        paths.append({
            "d": path_data(points),
            "accent": accent,
            "opacity": rng.uniform(0.36, 0.68) if accent else rng.uniform(0.10, 0.26),
            "width": 1.15 if accent else rng.choice([0.65, 0.8, 1.0]),
        })
    return paths


def hero_svg(theme_name, paths):
    theme = THEMES[theme_name]
    frames = typing_frames()
    en_times, en_widths = animation_values(frames, "english")
    zh_times, zh_widths = animation_values(frames, "chinese")
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
    <clipPath id="frame"><rect width="1600" height="430" rx="18"/></clipPath>
    <clipPath id="english-clip"><rect x="88" y="125" width="0" height="90">{animate("width", frames, "english")}</rect></clipPath>
    <clipPath id="chinese-clip"><rect x="88" y="125" width="0" height="90">{animate("width", frames, "chinese")}</rect></clipPath>
    <style>
      .mono {{ font-family: "SFMono-Regular", Menlo, Consolas, monospace; }}
      .cjk {{ font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif; }}
      .sans {{ font-family: "Avenir Next", "Helvetica Neue", Arial, sans-serif; }}
      .cursor {{ animation: blink 1.05s step-end infinite; }}
      @keyframes blink {{ 0%,48% {{ opacity:1; }} 49%,100% {{ opacity:0; }} }}
    </style>
  </defs>
  <rect width="1600" height="430" rx="18" fill="{theme['background']}"/>
  <g clip-path="url(#frame)">{''.join(lines)}</g>
  <line x1="88" y1="91" x2="1512" y2="91" stroke="{theme['faint']}" stroke-width="1"/>
  <g class="mono" font-size="12" letter-spacing="2.2">
    <text x="88" y="62" fill="{theme['secondary']}">AI PRODUCT MANAGER</text>
    <text x="1512" y="62" text-anchor="end" fill="{theme['secondary']}">RAZ / 2026</text>
  </g>
  <g font-size="62" font-weight="500">
    <text class="mono" x="88" y="190" fill="{theme['primary']}" clip-path="url(#english-clip)">I'm Raz.</text>
    <text class="cjk" x="88" y="190" fill="{theme['primary']}" clip-path="url(#chinese-clip)">我叫吴禹佟</text>
  </g>
  <rect class="cursor" x="88" y="143" width="4" height="55" fill="{theme['accent']}">{animate("x", frames, "cursor")}</rect>
  <text class="mono" x="91" y="259" fill="{theme['secondary']}" font-size="15" letter-spacing="1.2">RAG · Agents · Developer Tools</text>
  <rect x="88" y="315" width="26" height="3" fill="{theme['accent']}"/>
</svg>
'''


def button_svg(theme_name):
    theme = THEMES[theme_name]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 64" width="250" role="img" aria-label="View resume">
  <path d="M8 1H242V7H249V57H243V63H7V58H1V7H8Z" fill="{theme['background']}" stroke="{theme['primary']}" stroke-width="2"/>
  <rect x="8" y="8" width="6" height="6" fill="{theme['accent']}"/>
  <text x="28" y="39" fill="{theme['primary']}" font-family="SFMono-Regular, Menlo, Consolas, monospace" font-size="15" font-weight="600" letter-spacing="1.4">VIEW RESUME</text>
  <path d="M213 39V24H228M213 39L228 24M213 32V39H220" fill="none" stroke="{theme['accent']}" stroke-width="2"/>
</svg>
'''


if __name__ == "__main__":
    paths = line_art()
    for name in THEMES:
        (OUTPUT_DIR / f"hero-{name}.svg").write_text(hero_svg(name, paths), encoding="utf-8")
        (OUTPUT_DIR / f"resume-{name}.svg").write_text(button_svg(name), encoding="utf-8")
