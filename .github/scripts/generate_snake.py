#!/usr/bin/env python3
"""Render eljcf's contribution graph with dahan8473/snake-and-commits.

The game solver and cell-state renderer are adapted from v1 (commit c55d1f1):
https://github.com/dahan8473/snake-and-commits/blob/v1/generate.py

Local additions are limited to calendar-year JSON input, profile colors, and
the 03 pixel header. The reference action itself only accepts a GitHub user and
fetches a rolling 365-day window, so it cannot preserve the natural-year grid.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.request
from bisect import bisect_right
from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from assets.generate_hero import pixel_text

CELL, GAP = 11, 3
PITCH = CELL + GAP
MX, MTOP, MBOT = 16, 26, 30
STEPS_PER_SEC = 10
PAUSE_STEPS = 26
BASE_LEN = 3
HEADER_HEIGHT = 64

LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
         "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
MONTHS = ["", "jan", "feb", "mar", "apr", "may", "jun",
          "jul", "aug", "sep", "oct", "nov", "dec"]

# All non-empty contribution levels intentionally share one color.
THEMES = {
    "light": dict(
        surface="#F2F3EE",
        levels=["#D7DED6", "#173C32", "#173C32", "#173C32", "#173C32"],
        snake="#B54A38", head="#D06A53",
        ramp=[(1, "#B54A38"), (4, "#B54A38"), (10, "#9D4132"), (21, "#82372C")],
        text="#6F7F74", frame_bg="#F2F3EE", frame_border="#D7DED6",
    ),
    "dark": dict(
        surface="#10231C",
        levels=["#1B3429", "#C3D2C4", "#C3D2C4", "#C3D2C4", "#C3D2C4"],
        snake="#D06A53", head="#E58A73",
        ramp=[(1, "#D06A53"), (4, "#D06A53"), (10, "#B55743"), (21, "#934534")],
        text="#91A398", frame_bg="#10231C", frame_border="#1B3429",
    ),
}


def token():
    for key in ("GH_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(key):
            return os.environ[key]
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
    except FileNotFoundError:
        return ""


def fetch_weeks(user, tok):
    now = datetime.now(timezone.utc)
    frm = (now - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    query = """
    query($login:String!,$from:DateTime!){user(login:$login){contributionsCollection(from:$from){
      contributionCalendar{weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": user, "from": frm}}).encode(),
        headers={"Authorization": f"Bearer {tok}", "User-Agent": user},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    if data.get("errors"):
        sys.exit(f"GitHub API error: {data['errors']}")
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]


def load_weeks(source):
    data = json.loads(Path(source).read_text(encoding="utf-8"))
    if data.get("errors"):
        sys.exit(f"GitHub API error: {data['errors']}")
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]


def solve(grid, cap=999):
    """Real Snake rules: the head never enters an occupied cell; BFS to the nearest
    (sparse-first) commit cell avoiding the body; chase the tail when boxed in.
    Returns route, eats, growth steps, final length, uneaten count."""
    ncols = len(grid)

    def neighbors(cr):
        c, r = cr
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nc, nr = c + dc, r + dr
            if 0 <= nc < ncols and 0 <= nr < len(grid[nc]):
                yield (nc, nr)

    def bfs(start_, goal, blocked):
        if start_ == goal:
            return [start_]
        qq, seen = deque([(start_, [start_])]), {start_}
        while qq:
            cur, path = qq.popleft()
            for nb in neighbors(cur):
                if nb in seen or (nb in blocked and nb != goal):
                    continue
                if nb == goal:
                    return path + [nb]
                seen.add(nb)
                qq.append((nb, path + [nb]))
        return None

    remaining = {(c, r) for c in range(ncols) for r in range(len(grid[c])) if grid[c][r] > 0}
    start = min(remaining, key=lambda cr: cr[0] * 10 + abs(cr[1] - 3)) if remaining else (0, 3)
    body = deque([start])
    occupied = {start}
    route, eats, growth = [start], [], []

    def allowed():
        return BASE_LEN + len(growth)

    def eat(cell):
        remaining.discard(cell)
        eats.append((len(route) - 1, cell))
        if BASE_LEN + len(growth) < cap:
            growth.append(len(route) - 1)

    def step_to(cell):
        route.append(cell)
        body.append(cell)
        occupied.add(cell)
        if cell in remaining:
            eat(cell)
        while len(body) > allowed():
            occupied.discard(body.popleft())

    if start in remaining:
        eat(start)

    def safe(cell):
        if len(body) < 8:
            return True
        grows = cell in remaining
        occ = set(occupied)
        occ.add(cell)
        b0 = body[0]
        if not grows and len(body) + 1 > allowed():
            occ.discard(body[0])
            b0 = body[1] if len(body) > 1 else cell
        return bfs(cell, b0, occ - {b0, cell}) is not None

    stuck = 0
    while remaining and len(route) < 4000:
        head = body[-1]
        blocked = occupied - {head}
        path = None
        for cand in sorted(remaining, key=lambda cr: grid[cr[0]][cr[1]] * 8 +
                           abs(cr[0] - head[0]) + abs(cr[1] - head[1]))[:24]:
            p = bfs(head, cand, blocked)
            if p and len(p) > 1:
                path = p
                break
        if path:
            aborted = False
            for cell in path[1:]:
                if not safe(cell):
                    aborted = True
                    break
                step_to(cell)
            if not aborted:
                stuck = 0
                continue
        stuck += 1
        if stuck > 400:
            break
        head = body[-1]
        blocked = occupied - {head}
        tail = body[0]
        tp = bfs(head, tail, blocked - {tail})
        nxt = None
        if tp and len(tp) > 1 and tp[1] not in occupied and safe(tp[1]):
            nxt = tp[1]
        else:
            free = [nb for nb in neighbors(head) if nb not in occupied]
            pool = [nb for nb in free if safe(nb)] or free
            if pool:
                nxt = max(pool, key=lambda cr: sum(1 for n in neighbors(cr) if n not in occupied))
        if nxt is None:
            break
        step_to(nxt)
    return route, eats, growth, BASE_LEN + len(growth), len(remaining)


def render(grid, counts, months, route, eats, growth, theme, opts):
    t = THEMES[theme]
    ncols = len(grid)
    n = len(route)
    total = n + PAUSE_STEPS
    dur = total / STEPS_PER_SEC

    def pct(s):
        return round(s / total * 100, 3)

    def xy(c, r):
        return MX + c * PITCH, MTOP + r * PITCH

    def length_at(s):
        return BASE_LEN + bisect_right(growth, s)

    intervals, open_iv, prev = {}, {}, set()
    for s in range(n):
        bod = set(route[max(0, s - length_at(s) + 1): s + 1])
        for cell in bod - prev:
            open_iv[cell] = s
        for cell in prev - bod:
            intervals.setdefault(cell, []).append((open_iv.pop(cell), s))
        prev = bod
    for cell, st in open_iv.items():
        intervals.setdefault(cell, []).append((st, total))

    eaten_step = {cell: s for s, cell in eats}
    css, body = [], []
    for c in range(ncols):
        for r in range(len(grid[c])):
            x, y = xy(c, r)
            base = t["levels"][grid[c][r]]
            ivs = intervals.get((c, r), [])
            cls = f"c{c}_{r}"
            body.append(f'<rect class="{cls}" data-grid-cell="true" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{base}"/>')
            if not ivs:
                continue
            stops = [(0.0, base)]
            for a, b in ivs:
                post = base if (c, r) not in eaten_step or eaten_step[(c, r)] > b else t["levels"][0]
                pa = pct(a)
                stops += [(max(pa - .05, 0), None), (pa, t["head"])]
                for age, col in t["ramp"]:
                    if a + age < b:
                        stops.append((pct(a + age), col))
                if b < total:
                    pb = pct(b)
                    stops += [(max(pb - .05, 0), None), (pb, post)]
            frames, last = [], base
            for p, col in stops:
                col = last if col is None else col
                frames.append(f"{p}% {{ fill:{col}; }}")
                last = col
            frames.append(f"100% {{ fill:{last}; }}")
            css.append(f"@keyframes k{cls} {{ {' '.join(frames)} }}\n.{cls} {{ animation:k{cls} {dur:.1f}s linear infinite; }}")

    for c, label in months:
        x, _ = xy(c, 0)
        body.append(f'<text class="lab" x="{x}" y="14">{label}</text>')

    lx = MX + ncols * PITCH - GAP - 5 * (CELL + 3) - 62
    ly = MTOP + 7 * PITCH + 8
    body.append(f'<text class="lab" x="{lx-30}" y="{ly+9}">less</text>')
    for i in range(5):
        body.append(f'<rect x="{lx+i*(CELL+3)}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{t["levels"][i]}"/>')
    body.append(f'<text class="lab" x="{lx+5*(CELL+3)+8}" y="{ly+9}">more</text>')

    if opts.counter:
        total_commits = sum(counts[c][r] for _, (c, r) in eats)
        states, val = [(0, 0)], 0
        for s, (c, r) in eats:
            val += counts[c][r]
            states.append((s, val))
        body.append(f'<text class="lab" x="{MX}" y="{ly+9}">$ commits eaten:</text>')
        for i, (s, v) in enumerate(states):
            a = pct(s)
            b = pct(states[i + 1][0]) if i + 1 < len(states) else 100.0
            if b <= a:
                continue
            fr = (f"0% {{ opacity:0; }} {a}% {{ opacity:1; }} {b}% {{ opacity:0; }} 100% {{ opacity:0; }}"
                  if b < 100 else f"0% {{ opacity:0; }} {a}% {{ opacity:1; }} 100% {{ opacity:1; }}")
            css.append(f"@keyframes m{i} {{ {fr} }}\n.m{i} {{ animation:m{i} {dur:.1f}s steps(1,end) infinite; }}")
            body.append(f'<text class="cnt m{i}" opacity="0" x="{MX+102}" y="{ly+9}">{v}/{total_commits}</text>')

    w = MX * 2 + ncols * PITCH - GAP
    h = MTOP + 7 * PITCH - GAP + MBOT
    frame_open = frame_close = ""
    if opts.frame:
        frame_open = f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="12" fill="{t["frame_bg"]}" stroke="{t["frame_border"]}"/>'
        frame_close = f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="12" fill="none" stroke="{t["frame_border"]}"/>'
    mono = "ui-monospace,'SF Mono',Menlo,Consolas,monospace"
    header = f'''<rect x="0" y="{-HEADER_HEIGHT}" width="{w}" height="{h + HEADER_HEIGHT}" fill="{t['surface']}"/>
  <path d="M0 {-HEADER_HEIGHT}V0" fill="none" stroke="{t['text']}" stroke-width="1.5" stroke-opacity="0.65"/>
  <circle cx="0" cy="-35" r="4" fill="{t['snake']}"/>
  <g>{pixel_text("03 / CONTRIBUTION", 32, -42, 1.65, t['text'])}</g>'''
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {-HEADER_HEIGHT} {w} {h + HEADER_HEIGHT}" width="{w}" height="{h + HEADER_HEIGHT}" role="img" aria-label="Calendar-year contribution BFS snake">
  {header}
  <style>
    .lab {{ font-family:{mono}; font-size:9.5px; fill:{t['text']}; }}
    .cnt {{ font-family:{mono}; font-size:9.5px; fill:{t['snake']}; }}
    @media (prefers-reduced-motion) {{ * {{ animation:none !important; }} }}
    {chr(10).join(css)}
  </style>
  {frame_open}
  {chr(10).join('  ' + b for b in body)}
  {frame_close}
</svg>
"""


def main():
    parser = argparse.ArgumentParser(description="Turn a GitHub contribution graph into a Snake game (animated SVG).")
    parser.add_argument("--input", help="ContributionCalendar JSON; preserves its exact date range")
    parser.add_argument("--user", default=os.environ.get("GH_USER") or os.environ.get("GITHUB_REPOSITORY_OWNER"),
                        help="GitHub username for the reference rolling-365-day fetch")
    parser.add_argument("--output", default="dist/snake.svg", help="output svg path")
    parser.add_argument("--theme", default="light", choices=list(THEMES), help="color theme")
    parser.add_argument("--frame", action="store_true", help="draw a rounded window frame")
    parser.add_argument("--no-counter", dest="counter", action="store_false", help="hide the commits-eaten counter")
    parser.set_defaults(counter=True)
    opts = parser.parse_args()

    if opts.input:
        weeks = load_weeks(opts.input)
    else:
        if not opts.user:
            sys.exit("error: --input or --user is required")
        tok = token()
        if not tok:
            sys.exit("error: no token found. set GH_TOKEN (or GITHUB_TOKEN).")
        weeks = fetch_weeks(opts.user, tok)

    grid = [[LEVEL[d["contributionLevel"]] for d in w["contributionDays"]] for w in weeks]
    counts = [[d["contributionCount"] for d in w["contributionDays"]] for w in weeks]
    months, seen = [], None
    for c, week in enumerate(weeks):
        month = int(week["contributionDays"][0]["date"].split("-")[1])
        if month != seen:
            months.append((c, MONTHS[month]))
            seen = month
    if months and months[0][0] == 0 and len(months) > 1 and months[1][0] <= 2:
        months = months[1:]

    for cap in (48, 40, 34, 28, 24, 20, 16, 12):
        route, eats, growth, maxlen, left = solve(grid, cap)
        if left == 0:
            break

    output = Path(opts.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(grid, counts, months, route, eats, growth, opts.theme, opts), encoding="utf-8")
    cells = sum(len(column) for column in grid)
    food = sum(value > 0 for column in grid for value in column)
    print(f"wrote {output} — {cells} cells, {len(eats)}/{food} cells eaten, "
          f"BFS route {len(route)} steps, snake grew to {maxlen}, {left} left over")


if __name__ == "__main__":
    main()
