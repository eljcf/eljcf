from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent

THEMES = {
    "light": {
        "primary": "#173C32",
        "secondary": "#718077",
        "construction": "#B8C2BA",
        "accent": "#B54A38",
    },
    "dark": {
        "primary": "#EEF0E9",
        "secondary": "#91A398",
        "construction": "#395249",
        "accent": "#D06A53",
    },
}


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


def hero_svg(theme_name):
    theme = THEMES[theme_name]
    frames = typing_frames()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 300" width="1600" role="img" aria-labelledby="title desc">
  <title id="title">Raz — 吴禹佟, AI Product Manager</title>
  <desc id="desc">An editorial composition with a geometrically constructed R monogram and a typewriter name animation.</desc>
  <defs>
    <clipPath id="english-clip"><rect x="70" y="88" width="268.8" height="78">{animate("width", frames, "english")}</rect></clipPath>
    <clipPath id="chinese-clip"><rect x="70" y="88" width="0" height="78">{animate("width", frames, "chinese")}</rect></clipPath>
    <style>
      .mono {{ font-family: "SFMono-Regular", Menlo, Consolas, monospace; }}
      .cjk {{ font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif; }}
      .cursor {{ animation: blink 1.05s step-end infinite; }}
      @keyframes blink {{ 0%,48% {{ opacity:1; }} 49%,100% {{ opacity:0; }} }}
    </style>
  </defs>
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

  <g fill="none" stroke="{theme['construction']}" stroke-width="1">
    <circle cx="1255" cy="105" r="76"/>
    <circle cx="1255" cy="105" r="45"/>
    <path d="M1080 105H1450M1160 30V270M1115 250H1405M1160 150H1395"/>
    <path d="M1160 55L1375 250M1160 250L1330 55" stroke-dasharray="3 7"/>
  </g>
  <g fill="none" stroke-linecap="square" stroke-linejoin="miter">
    <path d="M1160 250V55H1255" stroke="{theme['primary']}" stroke-width="5"/>
    <path d="M1255 55C1345 55 1345 150 1255 150H1160" stroke="{theme['accent']}" stroke-width="5"/>
    <path d="M1250 150L1375 250" stroke="{theme['primary']}" stroke-width="5"/>
  </g>
  <circle cx="1255" cy="150" r="5" fill="{theme['accent']}"/>
  <g class="mono" font-size="10" letter-spacing="1.5" fill="{theme['secondary']}">
    <text x="1450" y="110">R / 01</text>
    <text x="1375" y="270">FORM / FUNCTION</text>
  </g>
</svg>
'''


if __name__ == "__main__":
    for name in THEMES:
        (OUTPUT_DIR / f"hero-{name}.svg").write_text(hero_svg(name), encoding="utf-8")
