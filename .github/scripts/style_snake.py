from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from assets.generate_hero import pixel_text

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


def apply_contribution_year(svg, contribution_path):
    from datetime import date

    data = json.loads(contribution_path.read_text(encoding="utf-8"))
    calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [day for week in calendar["weeks"] for day in week["contributionDays"]]
    matches = list(re.finditer(r'<rect\b[^>]*class="c(?: c\d)?"[^>]*/>', svg))

    animated_cells = {}
    for match in matches:
        tag = match.group(0)
        class_match = re.search(r'class="c (c\d)"', tag)
        x_match = re.search(r'x="([\d.]+)"', tag)
        y_match = re.search(r'y="([\d.]+)"', tag)
        if class_match and x_match and y_match:
            animated_cells[(x_match.group(1), y_match.group(1))] = class_match.group(1)

    levels = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    cells = []
    for week_index, week in enumerate(calendar["weeks"]):
        for day in week["contributionDays"]:
            day_date = date.fromisoformat(day["date"])
            weekday = (day_date.weekday() + 1) % 7
            x = 2 + week_index * 16
            y = 2 + weekday * 16
            level = levels[day["contributionLevel"]]
            animation_class = animated_cells.get((str(x), str(y)))
            class_name = f"c {animation_class}" if animation_class else "c"
            cells.append(
                f'<rect class="{class_name}" x="{x}" y="{y}" rx="2" ry="2" style="fill:var(--c{level})"/>'
            )

    if not matches:
        raise SystemExit("contribution grid not found")
    svg = svg[: matches[0].start()] + "".join(cells) + svg[matches[-1].end() :]
    active_days = sum(day["contributionCount"] > 0 for day in days)
    print(f"Applied {days[0]['date']}..{days[-1]['date']}: {len(days)} cells, {active_days} active days, {calendar['totalContributions']} contributions")
    return svg


def main():
    source = Path(sys.argv[1])
    theme_name = sys.argv[2]
    theme = THEMES[theme_name]
    svg = source.read_text(encoding="utf-8")

    for old, new in theme["colors"].items():
        svg = re.sub(re.escape(old), new, svg, flags=re.IGNORECASE)

    if len(sys.argv) > 3:
        svg = apply_contribution_year(svg, Path(sys.argv[3]))

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

    spine_x = min_x + 16
    insert = f'''
<rect x="{min_x:g}" y="{new_y:g}" width="{width:g}" height="{new_height:g}" fill="{theme['surface']}"/>
<style>
  .profile-thread {{ stroke-dasharray: 9 15; animation: profile-drift 12s linear infinite; }}
  @keyframes profile-drift {{ to {{ stroke-dashoffset: -96; }} }}
</style>
<path class="profile-thread" d="M{spine_x:g} {new_y:g}V{min_y:g}" fill="none" stroke="{theme['secondary']}" stroke-width="1.5" stroke-opacity="0.65"/>
<circle cx="{spine_x:g}" cy="{min_y - 35:g}" r="4" fill="{theme['accent']}"/>
<g>{pixel_text("03 / CONTRIBUTION", int(min_x + 48), int(min_y - 42), 3 * width / 1600, theme['secondary'])}</g>
'''
    opening = re.search(r"<svg\b[^>]*>", svg)
    if not opening:
        raise SystemExit("SVG opening tag not found")
    svg = svg[: opening.end()] + insert + svg[opening.end() :]
    source.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
