from pathlib import Path
import re
import sys

THEMES = {
    "light": {
        "surface": "#F2F3EE",
        "primary": "#173C32",
        "secondary": "#6F7F74",
        "accent": "#B54A38",
        "colors": {
            "#ebedf0": "#E1E6E0",
            "#9be9a8": "#CBD8CC",
            "#40c463": "#9FB8A6",
            "#30a14e": "#668D77",
            "#216e39": "#173C32",
            "#1b1f23": "#B54A38",
            "purple": "#B54A38",
        },
    },
    "dark": {
        "surface": "#10231C",
        "primary": "#EEF0E9",
        "secondary": "#91A398",
        "accent": "#D06A53",
        "colors": {
            "#161b22": "#1B3429",
            "#01311f": "#28473A",
            "#034525": "#3E6752",
            "#0f6d31": "#73947E",
            "#00c647": "#C3D2C4",
            "#1b1f23": "#D06A53",
            "purple": "#D06A53",
        },
    },
}


def main():
    source = Path(sys.argv[1])
    theme_name = sys.argv[2]
    theme = THEMES[theme_name]
    svg = source.read_text(encoding="utf-8")

    for old, new in theme["colors"].items():
        svg = re.sub(re.escape(old), new, svg, flags=re.IGNORECASE)

    match = re.search(r'viewBox="(-?[\d.]+) (-?[\d.]+) ([\d.]+) ([\d.]+)"', svg)
    if not match:
        raise SystemExit("viewBox not found")
    min_x, min_y, width, height = (float(value) for value in match.groups())
    header_height = 64.0
    new_y = min_y - header_height
    new_height = height + header_height
    svg = re.sub(
        r'viewBox="[^"]+"',
        f'viewBox="{min_x:g} {new_y:g} {width:g} {new_height:g}"',
        svg,
        count=1,
    )
    svg = re.sub(r'height="[\d.]+"', f'height="{new_height:g}"', svg, count=1)

    thread_x = min_x + width * 0.925
    insert = f'''
<rect x="{min_x:g}" y="{new_y:g}" width="{width:g}" height="{new_height:g}" fill="{theme['surface']}"/>
<style>
  .profile-thread {{ stroke-dasharray: 9 15; animation: profile-drift 12s linear infinite; }}
  @keyframes profile-drift {{ to {{ stroke-dashoffset: -96; }} }}
</style>
<text x="{min_x + 32:g}" y="{min_y - 28:g}" fill="{theme['secondary']}" font-family="SFMono-Regular, Menlo, Consolas, monospace" font-size="11" letter-spacing="1.8">03 / CONTRIBUTION</text>
<path class="profile-thread" d="M{thread_x:g} {new_y:g}V{min_y:g}" fill="none" stroke="{theme['accent']}" stroke-width="2" stroke-opacity="0.65"/>
'''
    opening = re.search(r"<svg\b[^>]*>", svg)
    if not opening:
        raise SystemExit("SVG opening tag not found")
    svg = svg[: opening.end()] + insert + svg[opening.end() :]
    source.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
