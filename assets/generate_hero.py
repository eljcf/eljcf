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
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
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
  .spine { stroke-dasharray: 3 10; animation: route 14s linear infinite; }
  @keyframes route { to { stroke-dashoffset: -52; } }
'''


def pixel_text(text, x, y, scale, color):
    rects = []
    cursor = x
    for char in text:
        glyph = PIXEL_GLYPHS[char]
        for row, line in enumerate(glyph):
            for column, bit in enumerate(line):
                if bit == "1":
                    rects.append(f'<rect x="{cursor + column * scale}" y="{y + row * scale}" width="{scale}" height="{scale}" fill="{color}"/>')
        cursor += 6 * scale
    return "".join(rects)


def typing_timeline():
    sentences = [
        {"count": 12, "width": 36.0, "type": 0.075, "delete": 0.045},
        {"count": 8, "width": 34.0, "type": 0.09, "delete": 0.05},
        {"count": 31, "width": 12.0, "type": 0.05, "delete": 0.028},
    ]
    frames = [(0.0, 0.0)]
    windows = []
    time = 0.0
    for sentence in sentences:
        start = time
        for index in range(1, sentence["count"] + 1):
            time += sentence["type"]
            frames.append((time, index * sentence["width"]))
        time += 0.48
        frames.append((time, sentence["count"] * sentence["width"]))
        for index in range(sentence["count"] - 1, -1, -1):
            time += sentence["delete"]
            frames.append((time, index * sentence["width"]))
        windows.append((start, time))
        time += 0.22
        frames.append((time, 0.0))
    final_start = time + 0.25
    total = final_start + 1.5
    return frames, windows, final_start, total


def clip_animation(frames, total):
    times = ";".join(f"{time / total:.5f}" for time, _ in frames)
    widths = ";".join(f"{width:.1f}" for _, width in frames)
    return f'<animate attributeName="width" values="{widths}" keyTimes="{times}" calcMode="discrete" dur="{total:.2f}s" fill="freeze"/>'


def visibility(start, end):
    return f'<animate attributeName="opacity" to="1" begin="{start:.2f}s" dur="0.01s" fill="freeze"/><animate attributeName="opacity" to="0" begin="{end:.2f}s" dur="0.01s" fill="freeze"/>'


def spine(height, theme, node_y):
    return f'''<path class="spine" d="M34 0V{height}" fill="none" stroke="{theme['construction']}" stroke-width="1.5"/>
  <circle cx="34" cy="{node_y}" r="4" fill="{theme['accent']}"/>'''


def monogram(theme):
    return f'''
  <g fill="none" stroke="{theme['construction']}" stroke-width="1">
    <circle cx="1255" cy="105" r="76"/><circle cx="1255" cy="105" r="45"/>
    <path d="M1080 105H1450M1160 30V270M1115 250H1405M1160 150H1395"/>
  </g>
  <g fill="none" stroke-linecap="square">
    <path d="M1160 250V55H1255" stroke="{theme['primary']}" stroke-width="5"/>
    <path d="M1255 55C1345 55 1345 150 1255 150H1160" stroke="{theme['accent']}" stroke-width="5"/>
    <path d="M1250 150L1375 250" stroke="{theme['primary']}" stroke-width="5"/>
  </g>
  <circle cx="1255" cy="150" r="5" fill="{theme['accent']}"/>
'''


def cursor(y, height, frames, total, window, color):
    x_values = ";".join(f"{70 + width:.1f}" for _, width in frames)
    times = ";".join(f"{time / total:.5f}" for time, _ in frames)
    return f'''<rect x="70" y="{y}" width="2" height="{height}" fill="{color}" opacity="0">
    <animate attributeName="x" values="{x_values}" keyTimes="{times}" calcMode="discrete" dur="{total:.2f}s" fill="freeze"/>{visibility(*window)}
  </rect>'''


def hero_svg(theme_name):
    theme = THEMES[theme_name]
    frames, windows, final_start, total = typing_timeline()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 360" width="1600" role="img" aria-label="Hello world. I'm Raz. Product Manager for AGI.">
  <defs>
    <style>{STYLE}</style>
    <clipPath id="typing-clip"><rect x="70" y="72" width="0" height="115">{clip_animation(frames, total)}</rect></clipPath>
  </defs>
  <rect width="1600" height="360" fill="{theme['surface']}"/>
  <g class="mono" font-size="11" letter-spacing="2.0" fill="{theme['secondary']}">
    <text x="1530" y="45" text-anchor="end">RAZ / 2026</text>
  </g>
  <g clip-path="url(#typing-clip)">
    <g opacity="0">{pixel_text("Hello world.", 70, 90, 6, theme['primary'])}{visibility(*windows[0])}</g>
    <text class="serif" x="66" y="165" fill="{theme['accent']}" font-size="58" font-style="italic" opacity="0">I'm Raz.{visibility(*windows[1])}</text>
    <text class="mono" x="70" y="150" fill="{theme['primary']}" font-size="20" opacity="0">&lt;p&gt;Product Manager for AGI.&lt;/p&gt;{visibility(*windows[2])}</text>
  </g>
  {cursor(96, 32, frames, total, windows[0], theme['accent'])}
  {cursor(125, 38, frames, total, windows[1], theme['accent'])}
  {cursor(132, 21, frames, total, windows[2], theme['accent'])}
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="{final_start:.2f}s" dur="1.2s" fill="freeze"/>
    <g>{pixel_text("Hello world.", 70, 72, 6, theme['primary'])}</g>
    <text class="serif" x="66" y="198" fill="{theme['accent']}" font-size="58" font-style="italic">I'm Raz.</text>
    <text class="mono" x="70" y="253" fill="{theme['primary']}" font-size="20">&lt;p&gt;Product Manager for AGI.&lt;/p&gt;</text>
    <rect x="70" y="286" width="254" height="50" fill="{theme['primary']}"/>
    <rect x="70" y="286" width="6" height="50" fill="{theme['accent']}"/>
    <text class="mono" x="100" y="318" fill="{theme['surface']}" font-size="14" font-weight="600" letter-spacing="1.5">VIEW RESUME ↗</text>
  </g>
  {monogram(theme)}
  {spine(360, theme, 330)}
</svg>
'''


def work_svg(theme_name):
    theme = THEMES[theme_name]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 300" width="1600" role="img" aria-label="Public repository: Gemini-exporter">
  <defs><style>{STYLE}</style></defs><rect width="1600" height="300" fill="{theme['surface']}"/>
  {spine(300, theme, 48)}
  <g>{pixel_text("01 / SELECTED WORK", 70, 34, 3, theme['secondary'])}</g>
  <rect x="70" y="85" width="1450" height="175" fill="{theme['surface_alt']}" stroke="{theme['construction']}" stroke-width="1.5"/>
  <rect x="70" y="85" width="5" height="175" fill="{theme['accent']}"/>
  <text class="mono" x="105" y="119" fill="{theme['secondary']}" font-size="10" letter-spacing="1.5">PUBLIC REPOSITORY / 01</text>
  <text class="mono" x="1480" y="119" text-anchor="end" fill="{theme['secondary']}" font-size="10" letter-spacing="1.5">GITHUB ↗</text>
  <text class="serif" x="101" y="170" fill="{theme['primary']}" font-size="39">Gemini-exporter</text>
  <text x="105" y="207" fill="{theme['secondary']}" font-family="PingFang SC, Microsoft YaHei, sans-serif" font-size="17">完整导出 Gemini 超长对话，并在新对话中恢复上下文。</text>
  <text class="mono" x="105" y="239" fill="{theme['primary']}" font-size="13">JavaScript · Chrome Extension MV3 · DOM API</text>
</svg>
'''


def tech_svg(theme_name):
    theme = THEMES[theme_name]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 230" width="1600" role="img" aria-label="Tech stack">
  <defs><style>{STYLE}</style></defs><rect width="1600" height="230" fill="{theme['surface_alt']}"/>
  {spine(230, theme, 48)}
  <g>{pixel_text("02 / TECH STACK", 70, 34, 3, theme['secondary'])}</g>
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
        for panel, renderer in {"hero": hero_svg, "work": work_svg, "tech": tech_svg}.items():
            (OUTPUT_DIR / f"{panel}-{name}.svg").write_text(renderer(name), encoding="utf-8")
