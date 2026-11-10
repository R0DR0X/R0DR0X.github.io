#!/usr/bin/env python3
"""Animated inline SVG covers, one per project, for the "night blueprint" site.

    COVER_IDS        project ids from content/portfolio.json, in JSON order
    cover_svg(id, area) -> one <svg class="cover cover--<id>"> string (4:3)
    covers_css()        shared keyframes and animation classes

Colors come only from CSS custom properties set by the site (--cover-bg,
--cover-line, --cover-line-2, --cover-accent, --cover-glow). Element ids are
prefixed with "cv-<id>-" so many covers can share one document. Without the
CSS motion block every cover is a complete static picture.

Standard library only; output is deterministic (randomness is seeded by id).
"""
import math
import random
import re

COVER_IDS = (
    "erp-traceability",
    "ecommerce-platform",
    "ad-intelligence",
    "construction-platform",
    "road-intelligence",
    "flood-warning",
    "meeting-copilot",
    "agent-cockpit",
    "stamp-platform",
    "personal-finance",
    "personal-agent",
    "genmedia-mcp",
    "roblox-game",
    "exporter-web-bi",
    "company-website",
    "ad-tracker",
    "finance-case",
)

# Attribute shorthands. "@" is replaced by the per-cover id prefix.
L2 = 'stroke="var(--cover-line-2)"'
AC = 'stroke="var(--cover-accent)"'
FA = 'fill="var(--cover-accent)"'
FL = 'fill="var(--cover-line)"'
FB = 'fill="var(--cover-bg)"'
GL = 'filter="url(#@-g)"'
NL = 'pathLength="100"'
BT = 'stroke-linecap="butt"'


def _n(x):
    """Compact number: at most one decimal, no trailing zeros."""
    s = f"{x:.1f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def _d(k):
    """Positive stagger class for step k (0.5 s per step); step 0 has none."""
    return f" cv-d{k}" if k else ""


def _slug(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-") or "project"


def _dot(d, cls="", color=AC, width=5, glow=True, offset=None):
    """A round dot travelling along path d (stroke-dashoffset animation)."""
    off = f' stroke-dashoffset="{offset}"' if offset is not None else ""
    fx = f" {GL}" if glow else ""
    return (f'<path class="cv-run{(" " + cls) if cls else ""}" d="{d}" {NL} stroke-width="{width}" '
            f'stroke-dasharray=".1 99.9"{off} {color}{fx}/>')


def _ink(d, cls="", attrs=""):
    """A line that redraws itself over a faint blueprint ghost of the same path."""
    ghost = attrs.replace(GL, "").strip()
    return (f'<path d="{d}" {ghost} opacity=".22"/>'
            f'<path class="cv-draw{(" " + cls) if cls else ""}" d="{d}" {NL} {attrs}/>')


def _frame(slug, body, hx=200, hy=150):
    svg = (
        f'<svg class="cover cover--{slug}" viewBox="0 0 400 300" aria-hidden="true" focusable="false" '
        'preserveAspectRatio="xMidYMid slice"><defs>'
        '<pattern id="@-p" width="20" height="20" patternUnits="userSpaceOnUse">'
        '<path d="M20 0H0V20" fill="none" stroke="var(--cover-line)" stroke-width=".5"/></pattern>'
        '<radialGradient id="@-h"><stop offset="0" stop-color="var(--cover-glow)" stop-opacity=".26"/>'
        '<stop offset="1" stop-color="var(--cover-glow)" stop-opacity="0"/></radialGradient>'
        '<filter id="@-g" filterUnits="userSpaceOnUse" x="-200" y="-200" width="800" height="700">'
        '<feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/>'
        '<feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
        '<rect width="400" height="300" fill="var(--cover-bg)"/>'
        '<rect width="400" height="300" fill="url(#@-p)" opacity=".1"/>'
        f'<circle class="cv-halo" cx="{hx}" cy="{hy}" r="170" fill="url(#@-h)"/>'
        '<g class="cv-art" fill="none" stroke="var(--cover-line)" stroke-width="1.25" '
        f'stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>'
    )
    return svg.replace("@", f"cv-{slug}")


def _bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d
                 for a, b, c, d in zip(p0, p1, p2, p3))


# ---------------------------------------------------------------- covers


def _erp_traceability(rng):
    trace = "M82 128C116 74 170 74 202 126C232 80 294 80 323 134"
    return (
        f'<path class="cv-draw cv-slow" d="M22 240q12-7 24 0t24 0t24 0t24 0t24 0" {NL} {L2} opacity=".6"/>'
        '<path d="M36 204h92l-14 22H50zM82 204v-66M88 146l30 48H88z"/>'
        '<path d="M150 226H382" opacity=".5"/>'
        '<path d="M158 226v-52l22-14v14l22-14v14l22-14v66M232 226v-92h12v92"/>'
        f'<path d="M166 204h52" stroke-width="6" stroke-dasharray="6 6" {BT} {L2} opacity=".5"/>'
        f'<circle class="cv-blink cv-d3" cx="246" cy="122" r="4" {L2} opacity=".6"/>'
        f'<circle class="cv-blink cv-d6" cx="256" cy="108" r="6" {L2} opacity=".35"/>'
        '<path d="M270 202h106v24H270zM304 202v24M340 202v24M288 178h70v24M322 178v24"/>'
        f'<path d="M274 214h100M292 190h64M310 166h28" stroke-width="14" stroke-dasharray="1 4" {BT} opacity=".3"/>'
        f'<path d="M306 154h34v24h-34z" {AC}/>'
        f'<path d="{trace}" {L2} stroke-dasharray="2 6"/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="4.5" {FB} {AC}/>'
                  f'<circle class="cv-ping cv-n{i}" cx="{x}" cy="{y}" r="9" {AC} opacity=".5"/>'
                  for i, (x, y) in enumerate(((82, 128), (202, 126), (323, 134)), 1))
        + _dot(trace)
    )


def _ecommerce_platform(rng):
    xs, counts = (40, 100, 160, 220, 278), (1, 3, 3, 3, 1)
    layers = []
    for x, c in zip(xs, counts):
        ys = [150] if c == 1 else [88 + rng.randint(-10, 10), 150 + rng.randint(-8, 8), 212 + rng.randint(-10, 10)]
        layers.append([(x, y) for y in ys])

    def seg(p, q):
        m = (p[0] + q[0]) / 2
        return f"C{_n(m)} {p[1]} {_n(m)} {q[1]} {q[0]} {q[1]}"

    edges = []
    for a, b in zip(layers, layers[1:]):
        for i, p in enumerate(a):
            for j, q in enumerate(b):
                if len(a) == 1 or len(b) == 1 or i == j or (abs(i - j) == 1 and rng.random() < .55):
                    edges.append(f"M{p[0]} {p[1]}{seg(p, q)}")
    routes = []
    for lane in range(3):
        pts = [layer[0] if len(layer) == 1 else layer[lane] for layer in layers]
        routes.append(f"M{pts[0][0]} {pts[0][1]}" + "".join(seg(p, q) for p, q in zip(pts, pts[1:])) + "H318")
    nodes = "".join(f'<circle cx="{x}" cy="{y}" r="5" {FB}/>' for layer in layers for x, y in layer)
    return (
        f'<path d="{"".join(edges)}" {L2} opacity=".55"/>'
        f'<path d="M283 150H314" {AC}/>'
        f'<g stroke-width="1.5">{nodes}</g>'
        f'<circle class="cv-ping" cx="40" cy="150" r="10" {AC} opacity=".5"/>'
        '<path d="M320 136l28-13 28 13-28 13zM320 136v32l28 13 28-13v-32M348 149v32"/>'
        f'<path class="cv-blink cv-d4" d="M334 129.5l28 13v8" {AC}/>'
        + _dot(routes[1], "cv-n1")
        + _dot(routes[0], "cv-n3", L2, 4)
        + _dot(routes[2], "cv-n5", L2, 4)
    )


def _ad_intelligence(rng):
    tiles = []
    lit = set(rng.sample(range(1, 16), 6))
    for k in range(16):
        a = math.radians(22.5 * k + rng.uniform(-4, 4))
        r = rng.uniform(34, 104)
        x, y = 200 + r * math.cos(a) - 8, 150 + r * math.sin(a) - 5.5
        if k in lit:
            tiles.append(f'<rect class="cv-blink cv-d{k}" x="{_n(x)}" y="{_n(y)}" width="16" height="11" rx="2" '
                         f'{AC} {FA} fill-opacity=".25"/>')
        else:
            tiles.append(f'<rect x="{_n(x)}" y="{_n(y)}" width="16" height="11" rx="2" {L2} opacity=".35"/>')
    return (
        '<g opacity=".5"><circle cx="200" cy="150" r="40"/><circle cx="200" cy="150" r="80"/>'
        '<path d="M70 150H330M200 20V280" stroke-dasharray="2 5"/></g>'
        '<circle cx="200" cy="150" r="120" stroke-width="1.5"/>'
        + "".join(tiles)
        + '<g transform="translate(200 150)"><g class="cv-spin">'
        '<path d="M0 0H120A120 120 0 0 0 91.9-77.1z" fill="var(--cover-glow)" fill-opacity=".1" stroke="none"/>'
        '<path d="M0 0H120A120 120 0 0 0 115.9-31.1z" fill="var(--cover-glow)" fill-opacity=".14" stroke="none"/>'
        f'<path d="M0 0H120" {L2} stroke-width="1.5" {GL}/></g></g>'
        f'<circle cx="200" cy="150" r="3" {FA} {AC}/>'
    )


def _construction_platform(rng):
    return (
        _ink("M110 240V100H290V240", "", 'stroke-width="1.75"')
        + _ink("M110 195H290M110 150H290", "cv-d1")
        + _ink("M126 206h30v22h-30zM185 206h30v22h-30zM244 206h30v22h-30zM126 161h30v22h-30z"
               "M185 161h30v22h-30zM244 161h30v22h-30zM126 116h30v22h-30zM244 116h30v22h-30z", "cv-d2", L2)
        + _ink("M186 150v-8h8v-8h8v-8h8v-10M100 100h200", "cv-d3", L2) +
        '<path d="M90 240H310"/>'
        f'<path d="M92 247H308" stroke-width="10" stroke-dasharray="1 5" {BT} opacity=".3"/>'
        + _ink("M338 240V56M352 240V56M338 220l14-20-14-20 14-20-14-20 14-20-14-20 14-20-14-20"
               "M300 56H392M320 56l25-22 25 22M378 56v46", "cv-d4", f'{L2} stroke-width="1"') +
        f'<path d="M372 102h12v10h-12z" {AC}/>'
        f'<g {AC} stroke-width=".9"><path d="M80 100V240M110 264H290M84 100h20M84 150h20M84 195h20M84 240h20'
        'M110 246v22M290 246v22M200 260v8"/>'
        '<path d="M76 104l8-8M76 154l8-8M76 199l8-8M76 244l8-8M106 268l8-8M286 268l8-8M196 268l8-8"'
        ' stroke-width="1.5"/></g>'
        f'<path d="M300 92l6 8 6-8z" {AC}/>'
    )


def _road_intelligence(rng):
    main = "M-10 222C80 206 120 124 200 130S320 64 410 80"
    roads = (
        "M58 -10C88 80 150 150 140 310",
        "M238 310C246 222 300 182 410 192",
        "M200 130C232 100 250 40 262 -10",
    )
    return (
        f'<g {L2} opacity=".22"><path d="M40 60c40-30 110-20 120 20s-60 60-100 40-50-40-20-60z"/>'
        '<path d="M260 230c30-30 100-30 110 0s-40 50-80 40-50-20-30-40z"/>'
        '<path d="M290 250c10-10 40-10 50 0s-20 20-30 14-24-6-20-14z"/></g>'
        f'<path d="{main}" stroke-width="2"/>'
        f'<path d="{main}" stroke-width=".75" stroke-dasharray="4 6" {L2} opacity=".7"/>'
        + "".join(f'<path d="{d}" {L2}/>' for d in roads)
        + f'<path class="cv-blink cv-d4" d="M262 102C282 88 300 80 320 78" {AC} stroke-width="2"/>'
        f'<g {FB}><circle cx="200" cy="130" r="4"/><circle cx="115" cy="133" r="4"/><circle cx="296" cy="203" r="4"/></g>'
        f'<circle class="cv-ping" cx="290" cy="88" r="10" {AC} opacity=".6"/>'
        + _dot(main, "cv-slow", offset=-30)
        + _dot(main, "cv-n4", L2, 4)
        + _dot(roads[0], "cv-n2", L2, 4, False)
        + _dot(roads[1], "cv-slow cv-n6", AC, 4, False)
        + _dot(roads[2], "cv-n3", L2, 4, False)
    )


def _flood_warning(rng):
    p = [(40, 232), (90, 230), (115, 222), (140, 200), (165, 178), (190, 92), (220, 90),
         (250, 88), (270, 140), (300, 178), (330, 214), (350, 222), (370, 224)]
    d = f"M{p[0][0]} {p[0][1]}" + "".join(
        "C" + " ".join(f"{x} {y}" for x, y in p[i:i + 3]) for i in (1, 4, 7, 10))
    lo, hi = 0.0, 1.0
    for _ in range(30):  # rising edge of segment two crosses the threshold y=130
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _bezier(*p[3:7], mid)[1] > 130 else (lo, mid)
    cx, cy = _bezier(*p[3:7], lo)
    streaks = []
    for k in range(4):
        parts = []
        for _ in range(4):
            x, y = rng.randint(30, 380), rng.randint(14, 70)
            parts.append(f"M{x} {y}l-3 11")
        streaks.append(f'<path class="cv-fall cv-n{2 * k + 1}" d="{"".join(parts)}" {L2} opacity=".7"/>')
    return (
        "".join(streaks)
        + '<path d="M40 40V250H372" opacity=".6"/>'
        '<path d="M40 254H372" stroke-width="6" stroke-dasharray="1 32" opacity=".5"/>'
        f'<path d="{d}V250H40z" fill="var(--cover-glow)" fill-opacity=".08" stroke="none"/>'
        f'<path d="M40 196C120 194 160 170 220 160S320 190 372 200" {L2} stroke-dasharray="1 5" opacity=".6"/>'
        f'<path d="M40 130H372" {AC} stroke-dasharray="7 6"/>'
        + _ink(d, "", f'stroke-width="2" {GL}') +
        f'<circle cx="{_n(cx)}" cy="{_n(cy)}" r="4" {FA} {AC}/>'
        f'<circle class="cv-ping" cx="{_n(cx)}" cy="{_n(cy)}" r="11" {AC}/>'
    )


def _meeting_copilot(rng):
    groups = [[] for _ in range(6)]
    for i, x in enumerate(range(36, 228, 8)):
        env = math.sin(math.pi * (i + 1) / 25) ** .7
        h = max(6, round(env * rng.uniform(40, 120)))
        groups[i % 6].append(f"M{x} {150 - h // 2}v{h - h % 2}")
    bars = "".join(f'<path class="cv-breathe cv-n{k + 1}" d="{"".join(g)}" stroke-width="2"/>'
                   for k, g in enumerate(groups))
    nodes = ((282, 104), (334, 76), (300, 166), (362, 140), (334, 216), (272, 216))
    links = "M236 150L254 150L282 104L334 76L362 140L300 166L282 104M300 166L334 216L272 216L254 150M300 166L254 150"
    return (
        '<path d="M28 150H230" opacity=".25"/>' + bars
        + f'<path d="{links}" {L2} opacity=".7"/>'
        + "".join(f'<circle class="cv-blink cv-d{2 * i + 1}" cx="{x}" cy="{y}" r="5" {FB} {AC if i == 1 else ""}/>'
                  for i, (x, y) in enumerate(nodes))
        + f'<circle cx="254" cy="150" r="3" {FL}/>'
        + _dot("M236 150L254 150L282 104L334 76", "cv-n2")
    )


def _agent_cockpit(rng):
    lines = []
    for i in range(7):
        y = 96 + 16 * i
        w = rng.randint(22, 52)
        lines.append(f'<path class="cv-type cv-d{i + 1}" d="M86 {y}h{w}" {NL} {L2}/>')
    beam = "M160 150H246"
    return (
        '<rect x="60" y="60" width="96" height="180" rx="14" stroke-width="1.75"/>'
        '<path d="M96 72h24M96 228h24" opacity=".6"/>'
        + "".join(f'<path d="M74 {92 + 16 * i}l4 4-4 4" {AC if i == 6 else L2}/>' for i in range(7))
        + "".join(lines)
        + '<rect x="250" y="94" width="110" height="74" rx="4" stroke-width="1.75"/>'
        '<path d="M236 178h138l-10 12H246z"/>'
        f'<path d="M264 112h40M264 124h62M264 136h28M264 148h50" {L2} opacity=".6"/>'
        f'<path class="cv-blink" d="M318 112h12" {AC} stroke-width="2"/>'
        f'<path d="{beam}" {L2} stroke-dasharray="3 5"/>'
        + _dot(beam, "cv-quick")
        + f'<rect x="192" y="146" width="22" height="18" rx="3" {FB} {AC} stroke-width="1.5"/>'
        f'<path d="M196 146v-6a7 7 0 0 1 14 0v6M203 152v5" {AC} stroke-width="1.5"/>'
        f'<circle class="cv-ping" cx="203" cy="152" r="18" {AC} opacity=".5"/>'
    )


def _stamp_platform(rng):
    return (
        f'<g transform="rotate(8 190 150)" {L2} opacity=".35"><rect x="130" y="70" width="153" height="180" '
        'stroke-width="5" stroke-dasharray="0 9"/></g>'
        '<g transform="rotate(-6 170 150)">'
        f'<rect x="94" y="60" width="153" height="180" {FB} stroke-width="6" stroke-dasharray="0 9"/>'
        '<rect x="108" y="74" width="125" height="152" rx="1"/>'
        f'<circle cx="196" cy="114" r="14" {AC}/>'
        + _ink("M116 200l30-42 20 22 18-30 40 50") +
        f'<path d="M116 212h110" {L2} opacity=".6"/><path d="M118 84h20M206 84h18" {L2} stroke-width="2"/></g>'
        f'<g {AC} stroke-width="1.75">'
        + "".join(f'<path class="cv-blink cv-d{4 - i}" d="M300 {216 - 22 * i}l20-14 20 14"/>' for i in range(4))
        + '</g>'
        f'<circle cx="320" cy="98" r="6" {FA} {AC} {GL}/>'
        f'<circle class="cv-ping" cx="320" cy="98" r="16" {AC}/>'
        f'<circle class="cv-ping cv-n3" cx="320" cy="98" r="16" {AC}/>'
        '<path d="M296 236h48" opacity=".5"/>'
    )


def _personal_finance(rng):
    out = []
    for i, x in enumerate((44, 132, 220, 308)):
        cx = x + 24
        level = (62, 96, 40, 112)[i]
        color = AC if i == 3 else L2
        out.append(
            f'<path d="M{x} 60h48v34h-48zM{x} 60l24 18 24-18"/>'
            f'<rect x="{cx - 10}" y="118" width="20" height="124" rx="4" opacity=".7"/>'
            f'<path class="cv-rise cv-d{2 * i + 1}" d="M{cx} 236V{236 - level}" stroke-width="10" {BT} {color} opacity=".75"/>'
        )
    return (
        "".join(out)
        + '<path d="M30 254H370" opacity=".5"/>'
        f'<path d="M30 170H370M30 200H370" {L2} stroke-dasharray="2 6" opacity=".4"/>'
        f'<path d="M318 108h20" {AC} stroke-width="2"/>'
        f'<circle class="cv-ping" cx="332" cy="120" r="14" {AC} opacity=".6"/>'
    )


def _personal_agent(rng):
    return (
        '<path d="M52 58h146a12 12 0 0 1 12 12v30a12 12 0 0 1-12 12H76l-16 14v-14h-8a12 12 0 0 1-12-12V70a12 12 0 0 1 12-12z"/>'
        f'<path d="M58 78h110M58 92h80" {L2} opacity=".7"/>'
        f'<path d="M248 136H104a12 12 0 0 0-12 12v26a12 12 0 0 0 12 12h120l16 14v-14h8a12 12 0 0 0 12-12v-26a12 12 0 0 0-12-12z" {L2}/>'
        f'<path d="M110 156h108M110 170h70" opacity=".6"/>'
        '<path d="M54 214h58a12 12 0 0 1 12 12v8a12 12 0 0 1-12 12H54a12 12 0 0 1-12-12v-8a12 12 0 0 1 12-12z"/>'
        + "".join(f'<circle class="cv-blink cv-d{i + 1}" cx="{66 + 17 * i}" cy="230" r="3" {FL}/>' for i in range(3))
        + '<g transform="translate(318 150)">'
        f'<circle r="64" {L2} stroke-dasharray="2 6" opacity=".6"/>'
        '<circle r="44" stroke-width="1.5"/>'
        f'<circle r="38" stroke-width="5" stroke-dasharray="1 18.9" {L2} opacity=".7"/>'
        '<path d="M0 0L-14-14"/>'
        f'<g class="cv-spin cv-slow"><path d="M0 4V-32" {AC} stroke-width="1.5"/></g>'
        f'<g class="cv-spin"><circle cx="64" r="4.5" {FA} {AC} {GL}/></g>'
        f'<circle r="3" {FL}/></g>'
    )


def _genmedia_mcp(rng):
    frames = "".join(f'<use href="#@-{"abc"[k % 3]}" x="{8 + 80 * k}"/>' for k in range(9))
    return (
        '<defs>'
        f'<g id="@-a"><rect y="118" width="66" height="64" rx="3"/><path d="M8 170l16-20 10 12 10-16 16 24" {L2}/>'
        f'<circle cx="46" cy="136" r="6" {AC}/></g>'
        f'<g id="@-b"><rect y="118" width="66" height="64" rx="3"/><path d="M26 136v28l20-14z" {AC}/></g>'
        f'<g id="@-c"><rect y="118" width="66" height="64" rx="3"/><path d="M8 140q8-8 16 0t16 0t16 0M8 154q8-8 16 0t16 0t16 0'
        f'M8 168q8-8 16 0t16 0t16 0" {L2}/></g></defs>'
        '<g class="cv-slide">'
        '<path d="M0 104H720M0 196H720" stroke-width="1.5"/>'
        f'<path d="M0 111H720M0 189H720" stroke-width="6" stroke-dasharray="6 10" {BT} {L2} opacity=".7"/>'
        + frames + '</g>'
        f'<path class="cv-twinkle" d="M330 30q2 14 16 16-14 2-16 16-2-14-16-16 14-2 16-16z" {AC} {FA} fill-opacity=".3" {GL}/>'
        f'<path class="cv-twinkle cv-d6" d="M70 238q1.5 9 10 10-8.5 1-10 10-1.5-9-10-10 8.5-1 10-10z" {L2}/>'
        f'<circle class="cv-twinkle cv-d10" cx="352" cy="244" r="2.5" {FL}/>'
    )


def _roblox_game(rng):
    lane = "M200 80H290A70 70 0 0 1 290 220H110A70 70 0 0 1 110 80Z"
    return (
        '<path d="M110 58H290A92 92 0 0 1 290 242H110A92 92 0 0 1 110 58Z" stroke-width="1.5"/>'
        '<path d="M110 102H290A48 48 0 0 1 290 198H110A48 48 0 0 1 110 102Z" stroke-width="1.5"/>'
        f'<path d="{lane}" {L2} stroke-dasharray="6 9" opacity=".5"/>'
        '<path d="M110 52H290A98 98 0 0 1 290 248H110A98 98 0 0 1 110 52Z" stroke-width="4" stroke-dasharray="6 6" stroke-linecap="butt" opacity=".25"/>'
        f'<g {AC} stroke-width="6" stroke-dasharray="5 5" {BT}><path d="M197 58v44"/><path d="M203 58v44" stroke-dashoffset="5"/></g>'
        f'<path d="M170 150l10-8v16zM196 150l10-8v16zM222 150l10-8v16z" {L2} opacity=".6"/>'
        + _dot(lane, "", AC, 7, offset=-12)
        + _dot(lane, "cv-slow", L2, 6, offset=-40)
    )


def _exporter_web_bi(rng):
    o = (148, 212)
    dests = ((266, 92), (306, 140), (120, 96), (252, 196))
    arcs = []
    for i, (x, y) in enumerate(dests):
        mx, my = (o[0] + x) / 2, (o[1] + y) / 2 - 46
        color = AC if i == 0 else L2
        arcs.append(f'<path class="cv-draw{_d(2 * i)}" d="M{o[0]} {o[1]}Q{_n(mx)} {_n(my)} {x} {y}" {NL} {color} stroke-width="1.5"/>'
                    f'<circle class="cv-blink cv-d{2 * i + 1}" cx="{x}" cy="{y}" r="3.5" {FL}/>')
    return (
        '<circle cx="200" cy="150" r="112" stroke-width="1.5"/>'
        '<g opacity=".35"><ellipse cx="200" cy="150" rx="44" ry="112"/><ellipse cx="200" cy="150" rx="84" ry="112"/>'
        '<path d="M200 38V262M88 150H312M98 100H302M98 200H302M127 64H273M127 236H273"/></g>'
        f'<path d="M140 190c10-8 22-4 28 6s-4 26-14 30-22-10-14-36z" {L2} opacity=".5"/>'
        + "".join(arcs)
        + f'<circle cx="{o[0]}" cy="{o[1]}" r="4" {FA} {AC} {GL}/>'
        f'<circle class="cv-ping" cx="{o[0]}" cy="{o[1]}" r="12" {AC}/>'
        f'<circle cx="200" cy="150" r="134" {L2} stroke-dasharray="1 7" opacity=".5"/>'
    )


def _company_website(rng):
    bars = "".join(
        f'<path class="cv-rise cv-d{2 * i + 1}" d="M{214 + 26 * i} 232V{232 - h}" stroke-width="12" {BT} '
        f'{AC if i == 4 else L2} opacity=".75"/>'
        for i, h in enumerate((28, 46, 66, 88, 112)))
    return (
        '<rect x="50" y="42" width="300" height="214" rx="8" stroke-width="1.5"/>'
        '<path d="M50 68H350"/>'
        + "".join(f'<circle cx="{64 + 11 * i}" cy="55" r="3" {L2}/>' for i in range(3))
        + '<rect x="106" y="49" width="170" height="12" rx="6" opacity=".5"/>'
        f'<rect x="300" y="50" width="20" height="10" rx="5" {AC}/><rect x="322" y="50" width="20" height="10" rx="5" opacity=".5"/>'
        '<path d="M72 94h104M72 108h72" stroke-width="2"/>'
        f'<path d="M86 136h86M86 146h60M86 170h86M86 180h50M86 204h86M86 214h66" {L2} opacity=".6"/>'
        f'<circle cx="76" cy="141" r="5" {AC}/><path d="M73.5 142.5l2.5-3 2.5 3" {AC}/>'
        '<circle cx="76" cy="175" r="5" opacity=".6"/><circle cx="76" cy="209" r="5" opacity=".6"/>'
        '<path d="M200 236H330" opacity=".6"/>'
        + bars
        + f'<path class="cv-draw cv-d2" d="M206 196L236 178 262 160 288 140 316 108" {NL} {AC} stroke-width="1.5"/>'
        f'<path d="M306 108h10v10" {AC} stroke-width="1.5"/>'
    )


def _ad_tracker(rng):
    x0, y0, cw, rh, cols, rows = 50, 50, 36, 28, 8, 7
    grid = "".join(f"M{x0} {y0 + rh * r}h{cw * cols}" for r in range(rows + 1))
    grid += "".join(f"M{x0 + cw * c} {y0}v{rh * rows}" for c in range(cols + 1))
    colpaths = []
    for c in range(1, cols):
        parts = "".join(f"M{x0 + cw * c + 6} {y0 + rh * r + 14}h{rng.randint(12, 24)}" for r in range(1, rows))
        colpaths.append(f'<path class="cv-type cv-d{c}" d="{parts}" {NL} {L2} stroke-width="2"/>')
    return (
        f'<path d="M{x0} {y0 + 14}h{cw * cols}" stroke-width="28" {BT} opacity=".1"/>'
        f'<path d="{grid}" opacity=".5" stroke-width=".9"/>'
        f'<path d="M{x0} {y0}h{cw * cols}v{rh * rows}H{x0}z" stroke-width="1.5"/>'
        + "".join(f'<path d="M{x0 + cw * c + 8} {y0 + 14}h18" stroke-width="2"/>' for c in range(1, cols))
        + f'<path d="M{x0 + cw - 8} {y0 + rh + 14}V{y0 + rh * rows}" stroke-width="2" stroke-dasharray="0 {rh}" {AC}/>'
        + "".join(colpaths)
        + f'<rect class="cv-blink cv-d8" x="{x0 + cw * 5}" y="{y0 + rh * 4}" width="{cw}" height="{rh}" {AC} stroke-width="2" {GL}/>'
        f'<path d="M{x0 + cw * 5 + 6} {y0 + rh * 4 + 14}h20" {AC} stroke-width="2"/>'
    )


def _finance_case(rng):
    o = (60, 150)
    up = "M60 150C140 146 196 106 250 90S330 62 372 52"
    down = "M60 150C140 154 196 190 250 206S330 230 372 240"
    candles = []
    for i in range(7):
        x = 80 + 18 * i
        top, h = rng.randint(212, 226), rng.randint(10, 22)
        filled = 'fill="var(--cover-line-2)" fill-opacity=".35"' if i % 3 == 1 else ""
        candles.append(f'<path d="M{x} {top - 6}v{h + 12}"/><rect x="{x - 4}" y="{top}" width="8" height="{h}" {filled}/>')
    return (
        f'<path d="M60 150H372" stroke-dasharray="2 6" opacity=".35"/>'
        f'<path d="M60 40V262" {L2} stroke-dasharray="1 5" opacity=".4"/>'
        f'<path d="M250 90V206" {L2} stroke-dasharray="3 4" opacity=".5"/>'
        f'<g {L2} opacity=".55">{"".join(candles)}</g>'
        + _ink(up, "", f'stroke-width="2" {GL}')
        + _ink(down, "cv-d2", f'{AC} stroke-width="2" {GL}') +
        f'<circle cx="372" cy="52" r="4" {FL}/><circle cx="372" cy="240" r="4" {FA} {AC}/>'
        f'<path d="M{o[0]} {o[1] - 8}l8 8-8 8-8-8z" {FB} {AC} stroke-width="1.5"/>'
        f'<circle class="cv-ping" cx="{o[0]}" cy="{o[1]}" r="14" {AC}/>'
    )


# ------------------------------------------------------- generic by area


def _generic_software(rng):
    return (
        "".join(_ink(f"M200 {96 + 34 * i}l90 32-90 32-90-32z", _d(2 * i).strip(), AC if i == 0 else L2)
                for i in range(3))
        + _dot("M110 128l90 32 90-32-90-32z", "", AC)
    )


def _generic_ai(rng):
    pts = []
    for k in range(8):
        a, r = math.radians(45 * k + rng.uniform(-12, 12)), rng.uniform(60, 110)
        pts.append((round(200 + r * math.cos(a)), round(150 + r * .85 * math.sin(a))))
    ring = "M" + "L".join(f"{x} {y}" for x, y in pts) + "Z"
    spokes = "".join(f"M200 150L{x} {y}" for x, y in pts[::2])
    return (
        f'<path d="{ring}{spokes}" {L2} opacity=".6"/><circle cx="200" cy="150" r="6" {FA} {AC} {GL}/>'
        + "".join(f'<circle class="cv-blink cv-d{i + 1}" cx="{x}" cy="{y}" r="5" {FB}/>' for i, (x, y) in enumerate(pts))
        + _dot(ring)
    )


def _generic_engineering(rng):
    rings = []
    for i in range(5):
        rx, ry = 40 + 30 * i, 26 + 20 * i
        d = f"M{200 - rx} 150a{rx} {ry} 0 1 0 {2 * rx} 0a{rx} {ry} 0 1 0 {-2 * rx} 0"
        rings.append(_ink(d, _d(i).strip(), AC if i == 0 else L2))
    return "".join(rings)


def _generic_other(rng):
    return (
        "".join(f'<circle cx="200" cy="150" r="{36 + 34 * i}" {L2} opacity="{.8 - .2 * i:.1f}"/>' for i in range(3))
        + f'<g transform="translate(200 150)"><g class="cv-spin"><circle cx="104" r="5" {FA} {AC} {GL}/></g></g>'
        f'<circle cx="200" cy="150" r="4" {FL}/>'
    )


COVERS = {
    "erp-traceability": _erp_traceability,
    "ecommerce-platform": _ecommerce_platform,
    "ad-intelligence": _ad_intelligence,
    "construction-platform": _construction_platform,
    "road-intelligence": _road_intelligence,
    "flood-warning": _flood_warning,
    "meeting-copilot": _meeting_copilot,
    "agent-cockpit": _agent_cockpit,
    "stamp-platform": _stamp_platform,
    "personal-finance": _personal_finance,
    "personal-agent": _personal_agent,
    "genmedia-mcp": _genmedia_mcp,
    "roblox-game": _roblox_game,
    "exporter-web-bi": _exporter_web_bi,
    "company-website": _company_website,
    "ad-tracker": _ad_tracker,
    "finance-case": _finance_case,
}

GENERIC = {
    "software": _generic_software,
    "ai": _generic_ai,
    "engineering": _generic_engineering,
    "other": _generic_other,
}


def cover_svg(project_id, area):
    """Return the animated SVG cover for a project; unknown ids get an area cover."""
    slug = _slug(project_id)
    draw = COVERS.get(project_id) or GENERIC.get(area, _generic_other)
    return _frame(slug, draw(random.Random(slug)))


_CSS = """\
@media (prefers-reduced-motion: no-preference){
.cover .cv-halo,.cover .cv-art{transition:opacity .6s ease,transform .6s ease}
.cover .cv-halo{opacity:.7;transform-box:fill-box;transform-origin:center}
.cover .cv-art{opacity:.88}
.cover-host:hover .cover .cv-halo,.cover-host:focus-within .cover .cv-halo{opacity:1;transform:scale(1.15)}
.cover-host:hover .cover .cv-art,.cover-host:focus-within .cover .cv-art{opacity:1}
.cover .cv-draw{stroke-dasharray:100 100;animation:cv-draw 12s ease-in-out infinite both}
.cover .cv-type{stroke-dasharray:100 100;animation:cv-type 9s steps(8,end) infinite both}
.cover .cv-run{animation:cv-run 7s linear infinite}
.cover .cv-blink{animation:cv-blink 8s ease-in-out infinite both}
.cover .cv-spin{transform-origin:0 0;animation:cv-spin 8s linear infinite}
.cover .cv-rise{transform-box:fill-box;transform-origin:50% 100%;animation:cv-rise 9s ease-in-out infinite both}
.cover .cv-breathe{transform-box:fill-box;transform-origin:center;animation:cv-breathe 6s ease-in-out infinite}
.cover .cv-slide{animation:cv-slide 18s linear infinite}
.cover .cv-fall{animation:cv-fall 6s linear infinite}
.cover .cv-twinkle{transform-box:fill-box;transform-origin:center;animation:cv-twinkle 7s ease-in-out infinite both}
.cover .cv-ping{transform-box:fill-box;transform-origin:center;animation:cv-ping 6s ease-out infinite}
.cover .cv-slow{animation-duration:16s}
.cover .cv-quick{animation-duration:6s}
.cover .cv-d1{animation-delay:.5s}.cover .cv-d2{animation-delay:1s}.cover .cv-d3{animation-delay:1.5s}
.cover .cv-d4{animation-delay:2s}.cover .cv-d5{animation-delay:2.5s}.cover .cv-d6{animation-delay:3s}
.cover .cv-d7{animation-delay:3.5s}.cover .cv-d8{animation-delay:4s}.cover .cv-d9{animation-delay:4.5s}
.cover .cv-d10{animation-delay:5s}.cover .cv-d11{animation-delay:5.5s}.cover .cv-d12{animation-delay:6s}
.cover .cv-d13{animation-delay:6.5s}.cover .cv-d14{animation-delay:7s}.cover .cv-d15{animation-delay:7.5s}
.cover .cv-n1{animation-delay:-1s}.cover .cv-n2{animation-delay:-2s}.cover .cv-n3{animation-delay:-3s}
.cover .cv-n4{animation-delay:-4s}.cover .cv-n5{animation-delay:-5s}.cover .cv-n6{animation-delay:-6s}
.cover .cv-n7{animation-delay:-7s}
@keyframes cv-draw{0%,40%{stroke-dashoffset:0}62%,66%{stroke-dashoffset:-100}100%{stroke-dashoffset:-200}}
@keyframes cv-type{0%,20%{stroke-dashoffset:0}24%{stroke-dashoffset:100}72%,100%{stroke-dashoffset:0}}
@keyframes cv-run{from{stroke-dashoffset:0}to{stroke-dashoffset:-100}}
@keyframes cv-blink{0%{opacity:1}40%,90%{opacity:.25}100%{opacity:1}}
@keyframes cv-spin{to{transform:rotate(360deg)}}
@keyframes cv-rise{0%,20%{transform:scaleY(1)}45%{transform:scaleY(.2)}100%{transform:scaleY(1)}}
@keyframes cv-breathe{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.35)}}
@keyframes cv-slide{to{transform:translateX(-240px)}}
@keyframes cv-fall{0%{transform:translate(4px,-24px);opacity:0}15%,80%{opacity:.8}100%{transform:translate(-14px,60px);opacity:0}}
@keyframes cv-twinkle{0%,100%{transform:scale(1) rotate(0deg);opacity:1}50%{transform:scale(.45) rotate(45deg);opacity:.35}}
@keyframes cv-ping{0%{transform:scale(.5);opacity:.9}70%,100%{transform:scale(1.7);opacity:0}}
.cover-host:not(.is-inview) .cover *,html.motion-paused .cover *{animation-play-state:paused!important}
}
@media print{.cover,.cover *{animation:none!important;transition:none!important}}
"""


def covers_css():
    """Shared CSS for every cover: all motion sits behind prefers-reduced-motion."""
    return _CSS
