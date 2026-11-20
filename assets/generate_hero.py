from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent

THEMES = {
    "light": {
        "surface": "#F2F3EE",
        "surface_alt": "#EBF0EA",
        "primary": "#173C32",
        "secondary": "#6F7F74",
        "construction": "#B8C2BA",
        "accent": "#B54A38",
    },
    "dark": {
        "surface": "#10231C",
        "surface_alt": "#14291F",
        "primary": "#EEF0E9",
        "secondary": "#91A398",
        "construction": "#395249",
        "accent": "#D06A53",
    },
}

PIXEL_GLYPHS = {
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "e": ["00000", "01110", "10001", "11111", "10000", "01110", "00000"],
    "l": ["01100", "00100", "00100", "00100", "00100", "01110", "00000"],
    "o": ["00000", "01110", "10001", "10001", "10001", "01110", "00000"],
    "w": ["00000", "10001", "10001", "10101", "10101", "10101", "01010"],
    "r": ["00000", "10110", "11001", "10000", "10000", "10000", "00000"],
    "d": ["00001", "00001", "01101", "10011", "10001", "10011", "01101"],
    ".": ["00000", "00000", "00000", "00000", "00000", "00110", "00110"],
    " ": ["00000"] * 7,
}

STYLE = '''
  .mono { font-family: "SFMono-Regular", Menlo, Consolas, monospace; }
  .serif { font-family: Georgia, "Times New Roman", serif; }
  .thread { stroke-dasharray: 9 15; animation: drift 12s linear infinite; }
  .reveal-two { animation: reveal-two 4s ease both; }
  .reveal-three { animation: reveal-three 4s ease both; }
  @keyframes drift { to { stroke-dashoffset: -96; } }
  @keyframes reveal-two { 0%,18% { opacity:0; } 36%,100% { opacity:1; } }
  @keyframes reveal-three { 0%,48% { opacity:0; } 68%,100% { opacity:1; } }
'''


def pixel_text(text, x, y, scale, color):
    rects = []
    cursor = x
    for char in text:
        glyph = PIXEL_GLYPHS[char]
        for row, line in enumerate(glyph):
            for column, bit in enumerate(line):
                if bit == "1":
                    rects.append(
                        f'<rect x="{cursor + column * scale}" y="{y + row * scale}" width="{scale}" height="{scale}" fill="{color}"/>'
                    )
        cursor += 6 * scale
    return "".join(rects)


def thread(path, color, opacity=0.72):
    return f'<path class="thread" d="{path}" fill="none" stroke="{color}" stroke-width="2" stroke-opacity="{opacity}"/>'


def monogram(theme):
    return f'''
  <g fill="none" stroke="{theme['construction']}" stroke-width="1">
    <circle cx="1255" cy="105" r="76"/><circle cx="1255" cy="105" r="45"/>
    <path d="M1080 105H1450M1160 30V270M1115 250H1405M1160 150H1395"/>
    <path d="M1160 55L1375 250M1160 250L1330 55" stroke-dasharray="3 7"/>
  </g>
  <g fill="none" stroke-linecap="square" stroke-linejoin="miter">
    <path d="M1160 250V55H1255" stroke="{theme['primary']}" stroke-width="5"/>
    <path d="M1255 55C1345 55 1345 150 1255 150H1160" stroke="{theme['accent']}" stroke-width="5"/>
    <path d="M1250 150L1375 250" stroke="{theme['primary']}" stroke-width="5"/>
  </g>
  <circle cx="1255" cy="150" r="5" fill="{theme['accent']}"/>
'''


def hero_svg(theme_name):
    theme = THEMES[theme_name]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 360" width="1600" role="img" aria-label="Hello world. I'm Raz. Product Manager for AGI.">
  <defs><style>{STYLE}</style></defs>
  <rect width="1600" height="360" fill="{theme['surface']}"/>
  <g class="mono" font-size="11" letter-spacing="2.0" fill="{theme['secondary']}">
    <text x="70" y="45">AI PRODUCT MANAGER</text>
    <text x="1530" y="45" text-anchor="end">RAZ / 2026</text>
  </g>
  <g>{pixel_text("Hello world.", 70, 72, 6, theme['primary'])}</g>
  <text class="serif reveal-two" x="66" y="198" fill="{theme['accent']}" font-size="58" font-style="italic">I'm Raz.</text>
  <text class="mono reveal-three" x="70" y="253" fill="{theme['primary']}" font-size="20">&lt;p&gt;Product Manager for AGI.&lt;/p&gt;</text>
  {monogram(theme)}
  {thread("M1255 150 C1450 195 1310 285 1480 360", theme['accent'])}
</svg>
'''


def resume_svg(theme_name):
    theme = THEMES[theme_name]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 86" width="1600" role="img" aria-label="View resume">
  <defs><style>{STYLE}</style></defs>
  <rect width="1600" height="86" fill="{theme['surface']}"/>
  {thread("M1480 0V86", theme['accent'])}
  <rect x="70" y="38" width="8" height="8" fill="{theme['accent']}"/>
  <text class="mono" x="96" y="49" fill="{theme['primary']}" font-size="14" letter-spacing="1.7">VIEW RESUME ↗</text>
</svg>
'''


def work_svg(theme_name):
    theme = THEMES[theme_name]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 280" width="1600" role="img" aria-label="Selected work: Gemini-exporter">
  <defs><style>{STYLE}</style></defs>
  <rect width="1600" height="280" fill="{theme['surface']}"/>
  {thread("M1480 0 C1480 95 1390 75 1370 155 C1345 225 460 185 120 280", theme['accent'], 0.5)}
  <text class="mono" x="70" y="54" fill="{theme['secondary']}" font-size="11" letter-spacing="1.8">01 / SELECTED WORK</text>
  <text class="serif" x="66" y="126" fill="{theme['primary']}" font-size="46">Gemini-exporter</text>
  <text x="70" y="170" fill="{theme['secondary']}" font-family="PingFang SC, Microsoft YaHei, sans-serif" font-size="18">完整导出 Gemini 超长对话，并在新对话中恢复上下文。</text>
  <text class="mono" x="70" y="211" fill="{theme['primary']}" font-size="14">JavaScript · Chrome Extension MV3 · DOM API</text>
</svg>
'''


def tech_svg(theme_name):
    theme = THEMES[theme_name]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 250" width="1600" role="img" aria-label="Tech stack">
  <defs><style>{STYLE}</style></defs>
  <rect width="1600" height="250" fill="{theme['surface_alt']}"/>
  {thread("M120 0 C120 85 255 60 315 140 C380 220 1330 135 1480 250", theme['accent'], 0.5)}
  <text class="mono" x="70" y="54" fill="{theme['secondary']}" font-size="11" letter-spacing="1.8">02 / TECH STACK</text>
  <g class="mono" font-size="11" letter-spacing="1.5" fill="{theme['secondary']}">
    <text x="70" y="116">PRODUCT</text><text x="70" y="174">BUILD</text>
  </g>
  <g font-family="Avenir Next, Helvetica Neue, Arial, sans-serif" font-size="21" fill="{theme['primary']}">
    <text x="230" y="117">AI Product · RAG · Agent Systems</text>
    <text x="230" y="175">JavaScript · Chrome Extension · DOM API</text>
  </g>
</svg>
'''


if __name__ == "__main__":
    for name in THEMES:
        for panel, renderer in {
            "hero": hero_svg,
            "resume": resume_svg,
            "work": work_svg,
            "tech": tech_svg,
        }.items():
            (OUTPUT_DIR / f"{panel}-{name}.svg").write_text(renderer(name), encoding="utf-8")
