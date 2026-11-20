#!/usr/bin/env python3
"""Post-process the snake-and-commits SVG: white base, subtle card, floating particles.

Runs inside GitHub Actions on ubuntu-latest. Stdlib only.
"""
import math
import random
import re
import sys
from pathlib import Path

# matrix theme -> light "paper" palette (empty, l1..l4, head, snake, ramp1..3, label, frame)
PALETTE = {
    "#0a0f0a": "#ffffff",  # empty cell -> white
    "#0d3d1a": "#d8f3dc",  # contribution level 1
    "#12742f": "#95d5b2",  # contribution level 2
    "#1fb84e": "#52b788",  # contribution level 3
    "#39ff7a": "#2d6a4f",  # contribution level 4 / snake green
    "#d6ffe4": "#1b4332",  # snake head
    "#3fa060": "#6b7280",  # month labels / legend text
}

# Particle CSS: slow drifting and twinkling, pure CSS keyframes.
PARTICLE_CSS = """
    /* --- decorative particles (CSS only, GitHub-safe) --- */
    @keyframes ptf {
      0%   { transform: translateY(0px) translateX(0px); opacity: 0; }
      15%  { opacity: var(--o); }
      85%  { opacity: var(--o); }
      100% { transform: translateY(-26px) translateX(6px); opacity: 0; }
    }
    @keyframes ptw {
      0%, 100% { opacity: calc(var(--o) * 0.35); }
      50%      { opacity: var(--o); }
    }
    .pt { animation: ptf var(--d) ease-in-out var(--t) infinite, ptw calc(var(--d) * 0.6) ease-in-out var(--t) infinite; }
"""

CARD = (
    '<rect x="4" y="4" width="{w}" height="{h}" rx="16" '
    'fill="#ffffff" stroke="#e5e7eb" stroke-width="1.5" />'
)


def parse_viewbox(svg: str):
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if not m:
        raise SystemExit("no viewBox found")
    return float(m.group(1)), float(m.group(2))


def recolor(svg: str) -> str:
    for old, new in PALETTE.items():
        svg = re.sub(re.escape(old), new, svg, flags=re.IGNORECASE)
    return svg


def add_card(svg: str, w: float, h: float) -> str:
    # insert after the opening <svg ...> tag, before <style>, so card sits behind cells
    m = re.search(r'(<svg\b[^>]*>)', svg)
    if not m:
        raise SystemExit("no <svg> open tag")
    card = CARD.format(w=w - 8, h=h - 8)
    return svg[: m.end()] + "\n" + card + svg[m.end() :]


def add_particles(svg: str, w: float, h: float) -> str:
    rng = random.Random(20261120)
    n = 64
    circles = []
    for i in range(n):
        x = rng.uniform(8, w - 8)
        # bias particles toward the header band and the empty top rows
        y = rng.uniform(6, h - 6)
        r = rng.uniform(0.9, 2.3)
        o = rng.uniform(0.28, 0.62)
        d = rng.uniform(5, 11)
        t = -rng.uniform(0, 11)
        color = rng.choice(["#2d6a4f", "#52b788", "#6b7280"])
        circles.append(
            f'<circle class="pt" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" '
            f'fill="{color}" style="--o:{o:.2f};--d:{d:.1f}s;--t:{t:.1f}s" />'
        )
    group = '  <g aria-hidden="true">\n' + "\n".join("    " + c for c in circles) + "\n  </g>\n"
    # inject CSS before </style>
    svg = svg.replace("</style>", PARTICLE_CSS + "  </style>", 1)
    # inject circles before </svg>
    return svg.replace("</svg>", group + "</svg>", 1)


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: style_snake.py <input.svg> <output.svg>")
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    svg = src.read_text(encoding="utf-8")
    w, h = parse_viewbox(svg)
    svg = recolor(svg)
    svg = add_card(svg, w, h)
    svg = add_particles(svg, w, h)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(svg, encoding="utf-8")
    print(f"styled {src} -> {dst} ({len(svg)} bytes, {w:.0f}x{h:.0f})")


if __name__ == "__main__":
    main()
