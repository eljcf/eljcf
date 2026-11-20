from datetime import date
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from assets.generate_hero import pixel_text

THEMES = {
    "light": {
        "surface": "#F2F3EE",
        "empty": "#D7DED6",
        "active": "#173C32",
        "secondary": "#6F7F74",
        "accent": "#B54A38",
    },
    "dark": {
        "surface": "#10231C",
        "empty": "#1B3429",
        "active": "#C3D2C4",
        "secondary": "#91A398",
        "accent": "#D06A53",
    },
}


def build_grid(data):
    calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    cells = {}
    for week_index, week in enumerate(calendar["weeks"]):
        for day in week["contributionDays"]:
            current = date.fromisoformat(day["date"])
            weekday = (current.weekday() + 1) % 7
            position = (week_index, weekday)
            cells[position] = {
                "date": day["date"],
                "active": day["contributionCount"] > 0,
                "x": 2 + week_index * 16,
                "y": 2 + weekday * 16,
            }
    return cells, calendar["totalContributions"]


def dfs_route(cells):
    start = next(iter(cells))
    visited = set()
    route = []

    def visit(node):
        visited.add(node)
        route.append(node)
        week, weekday = node
        neighbors = [(week + 1, weekday), (week, weekday + 1), (week - 1, weekday), (week, weekday - 1)]
        for neighbor in neighbors:
            if neighbor in cells and neighbor not in visited:
                visit(neighbor)
                route.append(node)

    visit(start)
    return route


def generate(data, theme_name):
    cells, total_contributions = build_grid(data)
    route = dfs_route(cells)
    theme = THEMES[theme_name]
    step_seconds = 0.065
    duration = (len(route) - 1) * step_seconds
    first_visit = {}
    for index, position in enumerate(route):
        first_visit.setdefault(position, index)

    grid = []
    for position, cell in cells.items():
        color = theme["active"] if cell["active"] else theme["empty"]
        disappearance = ""
        if cell["active"]:
            visit_time = first_visit[position] * step_seconds
            disappearance = f'<animate attributeName="opacity" from="1" to="0" begin="{visit_time:.3f}s" dur="0.08s" fill="freeze"/>'
        grid.append(
            f'<rect x="{cell["x"]}" y="{cell["y"]}" width="12" height="12" rx="2" fill="{color}">{disappearance}</rect>'
        )

    route_path = " ".join(
        ("M" if index == 0 else "L") + f'{cells[position]["x"] + 6} {cells[position]["y"] + 6}'
        for index, position in enumerate(route)
    )
    snake = []
    for index in range(6):
        snake.append(f'''<rect x="-5" y="-5" width="10" height="10" rx="2" fill="{theme['accent']}">
  <animateMotion path="{route_path}" dur="{duration:.3f}s" begin="{-index * step_seconds:.3f}s" fill="freeze" rotate="0"/>
</rect>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-16 -96 880 256" width="880" height="256" role="img" aria-label="2026 contribution DFS snake">
<rect x="-16" y="-96" width="880" height="256" fill="{theme['surface']}"/>
<path d="M0 -96V-32" fill="none" stroke="{theme['secondary']}" stroke-width="1.5" stroke-opacity="0.65"/>
<circle cx="0" cy="-67" r="4" fill="{theme['accent']}"/>
<g>{pixel_text("03 / CONTRIBUTION", 32, -78, 1.65, theme['secondary'])}</g>
<g shape-rendering="geometricPrecision">{''.join(grid)}</g>
<g>{''.join(snake)}</g>
</svg>
''', len(cells), sum(cell["active"] for cell in cells.values()), total_contributions, len(route)


def main():
    source = Path(sys.argv[1])
    theme_name = sys.argv[2]
    destination = Path(sys.argv[3])
    data = json.loads(source.read_text(encoding="utf-8"))
    svg, cells, active, contributions, route_length = generate(data, theme_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(svg, encoding="utf-8")
    print(f"{destination}: {cells} cells, {active} active days, {contributions} contributions, DFS route {route_length} steps")


if __name__ == "__main__":
    main()
