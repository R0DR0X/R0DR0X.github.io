#!/usr/bin/env python3
"""Render the bilingual portfolio website, CV print sources and PDFs.

One content source (content/portfolio.json) renders:
  site/index.html, site/en/index.html  portfolio website (es, en)
  site/cv/es.html, site/cv/en.html     CV print sources
  site/assets/img/*                    artwork listed in assets/img/manifest.json
  site/assets/img/real/*               real screenshots listed in assets/img/real/manifest.json
  site/files/*.pdf                     with --pdf, printed by headless Chrome

Standard library only. Content is validated before anything is written.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path
from urllib.parse import quote

sys.dont_write_bytecode = True  # keep tools/ free of __pycache__
sys.path.insert(0, str(Path(__file__).resolve().parent))
from covers import cover_svg, covers_css  # noqa: E402
from page_css import MOTION_CSS, PRINT_CSS, SECTIONS_CSS  # noqa: E402
from site_css import SITE_CSS as BASE_CSS  # noqa: E402
from site_js import BASE_JS, HEAD_JS  # noqa: E402
from sphere_js import SPHERE_JS  # noqa: E402
from story import copy_real, load_real  # noqa: E402
from story_css import STORY_CSS  # noqa: E402
from story_html import render_story  # noqa: E402
from story_js import STORY_JS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTENT = ROOT / "content" / "portfolio.json"
DEFAULT_OUT = ROOT / "site"
ASSETS = ROOT / "assets" / "img"
MANIFEST = ASSETS / "manifest.json"
REAL_DIR = ASSETS / "real"
LANGS = ("es", "en")
GITHUB_BASE = "https://github.com/"
CHROME_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")

PDF_NAMES = {
    "cv": {"es": "Ivan-Rodrigo-Pianto-Anton-CV-ES.pdf", "en": "Ivan-Rodrigo-Pianto-Anton-CV-EN.pdf"},
    "portfolio": {"es": "Ivan-Rodrigo-Pianto-Anton-Portafolio-ES.pdf", "en": "Ivan-Rodrigo-Pianto-Anton-Portfolio-EN.pdf"},
}
PAGE_PATHS = {"es": "index.html", "en": "en/index.html"}
CV_PATHS = {"es": "cv/es.html", "en": "cv/en.html"}
REQUIRED_IMAGES = ("hero", "hero-mobile")

# Key stack shown in the profile; every term must exist in content skills.
KEY_STACK = ["TypeScript", "Python", "Next.js 16", "NestJS", "FastAPI", "PostgreSQL"]

# The two strongest highlights per featured project for the CV (indexes into highlights).
CV_HIGHLIGHTS = {
    "erp-traceability": [1, 5],
    "ecommerce-platform": [0, 1],
    "ad-intelligence": [0, 1],
    "construction-platform": [0, 2],
    "road-intelligence": [1, 2],
    "flood-warning": [0, 2],
    "meeting-copilot": [0, 1],
    "agent-cockpit": [1, 3],
}

# escorpia.com palette (light page, dark .on-dark sections and dark theme),
# cover colors and the light print palette (print-*).
# tools/contrast.py checks every pair in PAIRS.
PALETTE = {
    "bg": "#040812",
    "bg-alt": "#08111d",
    "surface": "#111e31",
    "primary": "#00d4ff",
    "primary-light": "#47e8ff",
    "text-soft": "#c6d1dd",
    "white": "#ffffff",
    "paper": "#ffffff",
    "mist": "#f2f7fa",
    "line": "#dce6ee",
    "muted": "#44546a",
    "link": "#04607a",
    "control": "#768598",
    "cyan": "#39d0c8",
    "sea": "#7ee0c3",
    "amber": "#ff8a4c",
    "violet": "#b7a6ff",
    "steel": "#7d9bb3",
    "cover-bg": "#0c1219",
    "print-paper": "#ffffff",
    "print-ink": "#16191d",
    "print-muted": "#4a525c",
    "print-accent": "#0b6964",
    "print-rule": "#d5dbe1",
}
# Accent per project area (tag dots and animated covers on dark artwork).
AREA_ACCENT = {"software": "amber", "ai": "violet", "engineering": "cyan", "other": "sea"}
# (foreground, background, minimum ratio, role)
PAIRS = [
    ("bg", "paper", 4.5, "body text, light theme"),
    ("bg", "mist", 4.5, "body text on mist sections"),
    ("muted", "paper", 4.5, "secondary text, light theme"),
    ("muted", "mist", 4.5, "secondary text on mist sections"),
    ("link", "paper", 4.5, "links, light theme"),
    ("link", "mist", 4.5, "links on mist sections"),
    ("white", "bg", 4.5, "body text on dark sections"),
    ("white", "surface", 4.5, "card text on dark sections"),
    ("text-soft", "bg", 4.5, "secondary text on dark sections"),
    ("text-soft", "surface", 4.5, "secondary text on dark cards"),
    ("text-soft", "bg-alt", 4.5, "secondary text on dark mist"),
    ("primary-light", "bg", 4.5, "links, kickers and chapter numbers on dark"),
    ("primary-light", "surface", 4.5, "links on dark cards"),
    ("primary-light", "bg-alt", 4.5, "links on dark mist"),
    ("bg", "primary", 4.5, "primary button, chapter number badge"),
    ("bg", "primary-light", 4.5, "primary button hover, pressed states"),
    ("paper", "bg", 4.5, "current language and pressed filter, light theme"),
    ("bg", "white", 4.5, "current language and pressed filter, dark theme"),
    ("control", "paper", 3.0, "control borders, light theme"),
    ("control", "mist", 3.0, "control borders on mist sections"),
    ("control", "bg", 3.0, "control borders on dark sections"),
    ("control", "surface", 3.0, "control borders on dark cards"),
    ("bg", "paper", 3.0, "focus ring, light theme"),
    ("primary-light", "bg", 3.0, "focus ring on dark sections"),
    ("primary-light", "surface", 3.0, "focus ring on dark cards"),
    ("print-ink", "print-paper", 4.5, "print body text"),
    ("print-muted", "print-paper", 4.5, "print secondary text"),
    ("print-accent", "print-paper", 4.5, "print numbers and tags"),
]

UI = {
    "es": {
        "title": "{name} — Portafolio",
        "skip": "Saltar al contenido",
        "lang_nav": "Idioma",
        "lang_name": {"es": "Español", "en": "English"},
        "updated": "Actualizado {date}",
        "location": "Ubicación",
        "email_cta": "Escríbeme",
        "cv_pdf": "CV (PDF)",
        "portfolio_pdf": "Portafolio (PDF)",
        "sections": "Secciones",
        "nav": {"work": "Casos", "projects": "Proyectos", "methods": "Método", "experience": "Experiencia", "contact": "Contacto"},
        "menu": "Menú",
        "pause": "Pausar animaciones",
        "resume": "Reanudar animaciones",
        "hero_kicker": "Portafolio · {date}",
        "theme": "Tema oscuro",
        "hero_pill": "proyectos destacados · {loc}",
        "hero_hint": "Cada nodo es una habilidad. Mueve el puntero para girar la órbita.",
        "key_stack": "Stack principal",
        "languages": "Idiomas",
        "education": "Formación",
        "about": "Perfil",
        "numbers": "En cifras",
        "stack_title": "Stack en uso",
        "stack_note": "Tecnologías que aparecen en los proyectos de este portafolio.",
        "projects": "Todos los proyectos",
        "projects_note": "{n} proyectos en {a} áreas, numerados como en los casos destacados.",
        "filter_label": "Filtrar proyectos por área",
        "filter_all": "Todos",
        "count_one": "proyecto",
        "count_many": "proyectos",
        "empty": "No hay proyectos en «{area}».",
        "reset": "Mostrar todos los proyectos",
        "see_case": "Ver caso {n}",
        "details": "Logros y stack",
        "stack": "Stack",
        "methods": "Cómo trabajo",
        "skills": "Habilidades",
        "experience": "Experiencia",
        "current": "(actual)",
        "more": "Además",
        "contact": "Contacto",
        "contact_big": "¿Construimos algo juntos?",
        "contact_text": "¿Tienes una operación que necesita software? Escríbeme y cuéntame qué quieres resolver.",
        "made": "Hecho a mano con HTML, CSS y JavaScript, sin librerías.",
        "top": "Volver arriba",
        "og_locale": "es_PE",
        "cv_title": "{name} — CV",
        "cv_headings": ["Perfil", "Experiencia", "Proyectos destacados", "Habilidades", "Educación", "Idiomas"],
        "cv_figures": "Cifras clave",
    },
    "en": {
        "title": "{name} — Portfolio",
        "skip": "Skip to content",
        "lang_nav": "Language",
        "lang_name": {"es": "Español", "en": "English"},
        "updated": "Updated {date}",
        "location": "Location",
        "email_cta": "Email me",
        "cv_pdf": "CV (PDF)",
        "portfolio_pdf": "Portfolio (PDF)",
        "sections": "Sections",
        "nav": {"work": "Work", "projects": "Projects", "methods": "Method", "experience": "Experience", "contact": "Contact"},
        "menu": "Menu",
        "pause": "Pause animations",
        "resume": "Resume animations",
        "hero_kicker": "Portfolio · {date}",
        "theme": "Dark theme",
        "hero_pill": "featured projects · {loc}",
        "hero_hint": "Each node is a skill. Move the pointer to steer the orbit.",
        "key_stack": "Key stack",
        "languages": "Languages",
        "education": "Education",
        "about": "About",
        "numbers": "By the numbers",
        "stack_title": "Stack in use",
        "stack_note": "Technologies used across the projects in this portfolio.",
        "projects": "All projects",
        "projects_note": "{n} projects across {a} areas, numbered as in the featured work.",
        "filter_label": "Filter projects by area",
        "filter_all": "All",
        "count_one": "project",
        "count_many": "projects",
        "empty": "No projects in “{area}”.",
        "reset": "Show all projects",
        "see_case": "See case {n}",
        "details": "Highlights and stack",
        "stack": "Stack",
        "methods": "How I work",
        "skills": "Skills",
        "experience": "Experience",
        "current": "(current)",
        "more": "Also",
        "contact": "Contact",
        "contact_big": "Let’s build something together.",
        "contact_text": "Do you run an operation that needs software? Email me and tell me what you want to solve.",
        "made": "Handmade with HTML, CSS and JavaScript, no libraries.",
        "top": "Back to top",
        "og_locale": "en_US",
        "cv_title": "{name} — CV",
        "cv_headings": ["Profile", "Experience", "Selected projects", "Skills", "Education", "Languages"],
        "cv_figures": "Key figures",
    },
}


class ContentError(Exception):
    pass


# ---------------------------------------------------------------- validation

def is_bilingual(node):
    return isinstance(node, dict) and set(node) <= set(LANGS)


def validate(node, path=""):
    """Raise ContentError for the first {"es","en"} object missing a language."""
    if is_bilingual(node):
        for lang in LANGS:
            value = node.get(lang)
            if not isinstance(value, str) or not value.strip():
                raise ContentError(f"{path} missing {lang}")
    elif isinstance(node, dict):
        for key, value in node.items():
            validate(value, f"{path}.{key}" if path else key)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            validate(value, f"{path}[{i}]")


def check_references(data):
    terms = {item for group in data["skills"] for item in group["items"] if isinstance(item, str)}
    for term in KEY_STACK:
        if term not in terms:
            raise ContentError(f"key stack term {term!r} not in skills")
    areas = {area["id"] for area in data["areas"]}
    for i, project in enumerate(data["projects"]):
        if project["area"] not in areas:
            raise ContentError(f"projects[{i}].area unknown {project['area']}")
        picks = CV_HIGHLIGHTS.get(project["id"], [0, 1])
        if project["featured"] and max(picks) >= len(project["highlights"]):
            raise ContentError(f"projects[{i}].highlights has no item {max(picks)}")


def load_manifest(path=MANIFEST):
    """Image manifest; every listed file must exist next to it."""
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for key in REQUIRED_IMAGES:
        if key not in manifest:
            raise ContentError(f"image manifest has no {key!r}")
    for key, entry in manifest.items():
        for variant in entry["variants"]:
            if not (path.parent / variant["file"]).is_file():
                raise ContentError(f"image {key!r} file missing: {variant['file']}")
    return manifest


# ------------------------------------------------------------------- helpers

def t(value, lang):
    """Text of a bilingual object, or the value itself for plain strings."""
    return value[lang] if isinstance(value, dict) else value


def e(text):
    return escape(text, quote=True)


def num(i):
    return f"{i:02d}"


def is_current(period):
    return period["en"].endswith("present")


def github_url(data):
    return GITHUB_BASE + data["meta"]["github"]


def github_label(data):
    return "github.com/" + data["meta"]["github"]


def site_urls(site_url):
    base = site_url.rstrip("/")
    return {"es": base + "/", "en": base + "/en/"}


def first_sentence(text):
    """First sentence (with its period) and the rest of a paragraph."""
    head, sep, rest = text.partition(". ")
    return (head + "." if sep else head), rest.strip()


def stack_terms(projects):
    """Unique stack terms in order of first appearance."""
    seen = []
    for project in projects:
        for term in project["stack"]:
            if term not in seen:
                seen.append(term)
    return seen


def variants(entry):
    return sorted(entry["variants"], key=lambda v: v["width"])


def srcset(entry, prefix):
    return ", ".join(f'{prefix}assets/img/{v["file"]} {v["width"]}w' for v in variants(entry))


FAVICON = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
           "<rect width='64' height='64' rx='14' fill='#040812'/>"
           "<ellipse cx='32' cy='32' rx='23' ry='9' fill='none' stroke='#47e8ff' stroke-width='3' transform='rotate(-28 32 32)'/>"
           "<circle cx='32' cy='32' r='8' fill='#00d4ff'/><circle cx='51' cy='21' r='3.5' fill='#ffffff'/></svg>")


def data_uri_svg(svg):
    return "data:image/svg+xml," + quote(svg, safe=" =':/,.-")


# ---------------------------------------------------------------------- CSS

def css_vars():
    return "\n".join(f"    --{name}: {value};" for name, value in PALETTE.items())


def compact_css(css):
    """Drop comments and indentation; the rules themselves are untouched."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return "\n".join(line.strip() for line in css.splitlines() if line.strip())


def compact_js(js):
    """Drop indentation, blank lines and whole-line // comments (no ASI change)."""
    lines = (line.strip() for line in js.splitlines())
    return "\n".join(line for line in lines if line and not line.startswith("//"))


SITE_CSS = compact_css(BASE_CSS + STORY_CSS + SECTIONS_CSS + MOTION_CSS + PRINT_CSS)
# Separate scripts: an error in one never stops the others. Story runs first so
# the cover observer in BASE_JS also sees the stage clones.
SITE_JS = "".join(f"<script>{compact_js(js)}</script>\n" for js in (STORY_JS, BASE_JS, SPHERE_JS))


ICONS = {
    "pause": '<svg class="i-pause" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M5 3v10M11 3v10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "play": '<svg class="i-play" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M5 3l8 5-8 5z" fill="currentColor"/></svg>',
    "menu": '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    "moon": '<svg class="i-moon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>',
    "sun": '<svg class="i-sun" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></g></svg>',
}


# --------------------------------------------------------------- site page

def head_meta(data, lang, manifest):
    """Canonical, hreflang, Open Graph, Twitter and JSON-LD (only with meta.siteUrl)."""
    meta = data["meta"]
    site_url = meta.get("siteUrl", "").strip()
    if not site_url:
        return "", ""
    ui = UI[lang]
    urls = site_urls(site_url)
    title = ui["title"].format(name=meta["name"])
    description, _ = first_sentence(t(data["about"], lang))
    other = "en" if lang == "es" else "es"
    tags = [
        f'<link rel="canonical" href="{e(urls[lang])}">',
        f'<link rel="alternate" hreflang="es" href="{e(urls["es"])}">',
        f'<link rel="alternate" hreflang="en" href="{e(urls["en"])}">',
        f'<link rel="alternate" hreflang="x-default" href="{e(urls["es"])}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(description)}">',
        f'<meta property="og:url" content="{e(urls[lang])}">',
        f'<meta property="og:site_name" content="{e(meta["name"])}">',
        f'<meta property="og:locale" content="{UI[lang]["og_locale"]}">',
        f'<meta property="og:locale:alternate" content="{UI[other]["og_locale"]}">',
    ]
    og = manifest.get("og")
    if og:
        image = og["variants"][0]
        tags += [
            f'<meta property="og:image" content="{e(urls["es"] + "assets/img/" + image["file"])}">',
            f'<meta property="og:image:width" content="{image["width"]}">',
            f'<meta property="og:image:height" content="{image["height"]}">',
        ]
    tags.append('<meta name="twitter:card" content="summary_large_image">')
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": meta["name"],
        "jobTitle": t(meta["headline"], lang),
        "url": urls[lang],
        "sameAs": [github_url(data)],
    }
    ld = json.dumps(person, ensure_ascii=False).replace("</", "<\\/")
    return "\n".join(tags) + "\n", f'<script type="application/ld+json">{ld}</script>\n'


def render_site(data, lang, manifest, real=None):
    real = real or {}
    ui = UI[lang]
    meta = data["meta"]
    other_href = "en/" if lang == "es" else "../"
    prefix = "" if lang == "es" else "../"
    projects = data["projects"]
    areas = {area["id"]: t(area["title"], lang) for area in data["areas"]}
    numbers = {p["id"]: i + 1 for i, p in enumerate(projects)}
    email = meta["email"]
    about = t(data["about"], lang)
    lede, about_rest = first_sentence(about)
    cv_href = f'{prefix}files/{PDF_NAMES["cv"][lang]}'
    pdf_href = f'{prefix}files/{PDF_NAMES["portfolio"][lang]}'

    def area_style(area_id):
        return f'--area: var(--{AREA_ACCENT.get(area_id, "sea")})'

    def chips(items):
        return '<ul class="plain chips">' + "".join(f"<li>{e(t(i, lang))}</li>" for i in items) + "</ul>"

    def highlights(project):
        return '<ul class="hl">' + "".join(f"<li>{e(t(h, lang))}</li>" for h in project["highlights"]) + "</ul>"

    def details(project):
        # Featured highlights live in their story chapter; their card keeps the stack.
        if project["featured"]:
            return f'<details><summary>{e(ui["stack"])}</summary>{chips(project["stack"])}</details>'
        return (f'<details><summary>{e(ui["details"])}</summary>{highlights(project)}'
                f'<p class="stack-label">{e(ui["stack"])}</p>{chips(project["stack"])}</details>')

    def kicker(n):
        return f'<p class="kicker" aria-hidden="true">{num(n)}</p>'

    social, json_ld = head_meta(data, lang, manifest)

    # Header
    lang_links = []
    for code in LANGS:
        current = ' aria-current="page"' if code == lang else ""
        href = "./" if code == lang else other_href
        lang_links.append(f'<li><a href="{href}" hreflang="{code}" lang="{code}"{current}>'
                          f'<span aria-hidden="true">{code.upper()}</span><span class="sr-only">{e(ui["lang_name"][code])}</span></a></li>')
    nav = "".join(f'<li><a href="#{sid}">{e(label)}</a></li>' for sid, label in ui["nav"].items())
    initials = "".join(word[0] for word in meta["name"].split()[:2])
    header = f"""<header class="site-header" id="site-header">
  <div class="bar wrap">
    <a class="mark" href="#top"><span class="mark-glyph" aria-hidden="true">{e(initials)}</span><span class="mark-name">{e(meta["name"])}</span></a>
    <nav class="site-nav" id="site-nav" aria-label="{e(ui["sections"])}"><ul class="plain">{nav}</ul></nav>
    <div class="tools">
      <nav class="lang" aria-label="{e(ui["lang_nav"])}"><ul class="plain">{"".join(lang_links)}</ul></nav>
      <button type="button" class="icon-btn theme" id="theme-toggle" aria-pressed="false" aria-label="{e(ui["theme"])}" hidden>{ICONS["moon"]}{ICONS["sun"]}</button>
      <button type="button" class="icon-btn pause" id="motion-toggle" data-pause="{e(ui["pause"])}" data-resume="{e(ui["resume"])}" hidden>{ICONS["pause"]}{ICONS["play"]}<span class="pause-label">{e(ui["pause"])}</span></button>
      <button type="button" class="icon-btn menu" id="menu-toggle" aria-expanded="false" aria-controls="site-nav" hidden>{ICONS["menu"]}<span class="sr-only">{e(ui["menu"])}</span></button>
    </div>
  </div>
  <div class="progress" aria-hidden="true"></div>
</header>"""

    # Hero: dark stage with the canvas sphere of skills (no raster image).
    split = max(1, len(meta["name"].split()) // 2)
    words = meta["name"].split()
    name_html = f'{e(" ".join(words[:split]))} <mark>{e(" ".join(words[split:]))}</mark>'
    featured_n = sum(1 for p in projects if p["featured"])
    hero = f"""<section id="top" class="hero on-dark" aria-labelledby="hero-name">
  <div class="hero-glow" aria-hidden="true"></div>
  <canvas id="orbit" aria-hidden="true" data-labels="#skills .chips li"></canvas>
  <div class="wrap">
    <div class="hero-copy">
      <p class="pill"><b>{featured_n}</b>{e(ui["hero_pill"].format(loc=t(meta["location"], lang)))}</p>
      <h1 class="name" id="hero-name">{name_html}</h1>
      <p class="headline">{e(t(meta["headline"], lang))}</p>
      <p class="lede">{e(lede)}</p>
      <p class="print-only">{e(email)} · {e(github_label(data))}</p>
      <div class="cta">
        <a class="btn primary" href="mailto:{e(email)}">{e(ui["email_cta"])}</a>
        <a class="btn ghost" href="{cv_href}">{e(ui["cv_pdf"])}</a>
        <a class="btn ghost" href="{pdf_href}">{e(ui["portfolio_pdf"])}</a>
      </div>
      <p class="hint">{e(ui["hero_hint"])}</p>
    </div>
  </div>
</section>"""

    facts = (f'<div><dt>{e(ui["key_stack"])}</dt><dd>{", ".join(e(term) for term in KEY_STACK)}</dd></div>'
             f'<div><dt>{e(ui["languages"])}</dt><dd><ul class="plain">{"".join(f"<li>{e(t(i, lang))}</li>" for i in data["languages"])}</ul></dd></div>'
             f'<div><dt>{e(ui["education"])}</dt><dd><ul class="plain">{"".join(f"<li>{e(t(i, lang))}</li>" for i in data["education"])}</ul></dd></div>')

    stats = "".join(
        f'<li class="stat reveal" style="--i:{i}"><p class="v"><span class="sr-only">{e(s["value"])}</span>'
        f'<span class="tally" aria-hidden="true" data-value="{e(s["value"])}">{e(s["value"])}</span></p>'
        f'<p class="l">{e(t(s["label"], lang))}</p></li>'
        for i, s in enumerate(data["stats"])
    )

    terms = stack_terms(projects)
    rows = []
    for k, row in enumerate((terms[0::2], terms[1::2])):
        items = "".join(f"<li>{e(term)}</li>" for term in row)
        rows.append(f'<div class="mq-row{" rev" if k else ""}"><ul class="plain mq-track">{items}</ul></div>')
    marquee_dur = max(40, round(len(terms) * 1.6))

    work = render_story(data, lang, prefix, manifest, real, areas, numbers, area_style, kicker)

    counts = {area_id: sum(1 for p in projects if p["area"] == area_id) for area_id in areas}
    filter_chips = [f'<button type="button" class="chip" data-filter="all" data-label="{e(ui["filter_all"])}" aria-pressed="true">{e(ui["filter_all"])} <span class="n">{len(projects)}</span></button>']
    for area_id, title in areas.items():
        filter_chips.append(f'<button type="button" class="chip" data-filter="{e(area_id)}" data-label="{e(title)}" aria-pressed="false">{e(title)} <span class="n">{counts[area_id]}</span></button>')

    cards = []
    for i, project in enumerate(projects):
        pid = e(project["id"])
        n = num(numbers[project["id"]])
        title = e(t(project["title"], lang))
        if project.get("product"):
            title = f'{e(project["product"]["name"])} · {title}'
        featured = project["featured"]
        heading = f'<a href="#case-{pid}">{title}</a>' if featured else title
        go = f'<a class="go" href="#case-{pid}">{e(ui["see_case"].format(n=n))} →</a>' if featured else ""
        cards.append(
            f'<li class="card reveal{" is-featured" if featured else ""}" data-area="{e(project["area"])}" '
            f'style="{area_style(project["area"])}; --i:{i % 3}; view-transition-name: card-{pid}">'
            f'<div class="cover-host card-cover" aria-hidden="true">{cover_svg(project["id"], project["area"])}</div>'
            f'<div class="card-body"><p class="card-top"><span class="n" aria-hidden="true">{n}</span><span class="tag">{e(areas[project["area"]])}</span></p>'
            f'<h3>{heading}</h3>'
            f'<p class="meta">{e(t(project["context"], lang))} · {e(t(project["period"], lang))}</p>'
            f'<p class="summary">{e(t(project["summary"], lang))}</p>'
            f'{details(project)}{go}</div></li>'
        )

    methods = "".join(
        f'<li class="method reveal" style="--i:{i % 3}"><span class="m-num" aria-hidden="true">{num(i + 1)}</span>'
        f'<h3>{e(t(m["title"], lang))}</h3><p>{e(t(m["body"], lang))}</p></li>'
        for i, m in enumerate(data["methods"])
    )
    skills = "".join(
        f'<div class="skill reveal"><dt>{e(t(g["title"], lang))}</dt><dd>{chips(g["items"])}</dd></div>'
        for g in data["skills"]
    )
    timeline = []
    for job in data["experience"]:
        current = is_current(job["period"])
        state = f' <span class="sr-only">{e(ui["current"])}</span>' if current else ""
        timeline.append(f"""<li>
  <span class="tl-dot{' now' if current else ''}" aria-hidden="true"><i></i></span>
  <p class="when">{e(t(job["period"], lang))}{state}</p>
  <div>
    <h3>{e(t(job["role"], lang))}</h3>
    <p class="org">{e(t(job["org"], lang))}</p>
    <p class="body">{e(t(job["body"], lang))}</p>
  </div>
</li>""")
    more = "".join(f'<li class="reveal" style="--i:{i % 2}">{e(t(item, lang))}</li>' for i, item in enumerate(data["more"]))

    empty_text = e(ui["empty"]).replace("{area}", '<span id="empty-area"></span>')
    count_text = f'{len(projects)} {ui["count_many"]} · {ui["filter_all"]}'
    css = SITE_CSS.replace("%VARS%", css_vars()) + covers_css()
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="{PALETTE["paper"]}">
<title>{e(ui["title"].format(name=meta["name"]))}</title>
<meta name="description" content="{e(lede)}">
<link rel="icon" href="{e(data_uri_svg(FAVICON))}">
{social}<script>{HEAD_JS}</script>
<style>{css}</style>
{json_ld}</head>
<body>
<a class="skip" href="#main">{e(ui["skip"])}</a>
{header}
<main id="main" tabindex="-1">
{hero}
<section id="about" class="sec" aria-labelledby="about-h">
  <div class="wrap">
    <div class="sec-head reveal">{kicker(1)}<h2 class="sec-title" id="about-h">{e(ui["about"])}</h2></div>
    <div class="about-grid">
      <p class="about-text reveal">{e(about_rest or about)}</p>
      <dl class="facts reveal">{facts}</dl>
    </div>
  </div>
</section>
<section id="numbers" class="sec mist" aria-labelledby="numbers-h">
  <div class="wrap">
    <div class="sec-head reveal">{kicker(2)}<h2 class="sec-title" id="numbers-h">{e(ui["numbers"])}</h2></div>
    <ul class="plain stats">{stats}</ul>
  </div>
</section>
<section id="stack" class="stack-sec" aria-labelledby="stack-h">
  <div class="wrap sec-head">{kicker(3)}<h2 class="sec-title" id="stack-h">{e(ui["stack_title"])}</h2><p class="note">{e(ui["stack_note"])}</p></div>
  <div class="mq" style="--dur: {marquee_dur}s">{"".join(rows)}</div>
</section>
{work}
<section id="projects" class="sec mist" aria-labelledby="projects-h">
  <div class="wrap">
    <div class="sec-head reveal">{kicker(5)}<h2 class="sec-title" id="projects-h">{e(ui["projects"])}</h2><p class="note">{e(ui["projects_note"].format(n=len(projects), a=len(areas)))}</p></div>
    <div class="filters" id="filters" role="group" aria-label="{e(ui["filter_label"])}" hidden>{"".join(filter_chips)}</div>
    <p class="count" id="count" role="status" hidden data-one="{e(ui["count_one"])}" data-many="{e(ui["count_many"])}">{e(count_text)}</p>
    <div class="empty" id="empty" hidden>
      <p>{empty_text}</p>
      <button type="button" class="btn" id="reset">{e(ui["reset"])}</button>
    </div>
    <ol class="plain cards" id="index">{"".join(cards)}</ol>
  </div>
</section>
<section id="methods" class="sec" aria-labelledby="methods-h">
  <div class="wrap">
    <div class="sec-head reveal">{kicker(6)}<h2 class="sec-title" id="methods-h">{e(ui["methods"])}</h2></div>
    <ol class="plain methods">{methods}</ol>
  </div>
</section>
<section id="skills" class="sec mist" aria-labelledby="skills-h">
  <div class="wrap">
    <div class="sec-head reveal">{kicker(7)}<h2 class="sec-title" id="skills-h">{e(ui["skills"])}</h2></div>
    <dl class="skills">{skills}</dl>
  </div>
</section>
<section id="experience" class="sec" aria-labelledby="experience-h">
  <div class="wrap">
    <div class="sec-head reveal">{kicker(8)}<h2 class="sec-title" id="experience-h">{e(ui["experience"])}</h2></div>
    <div class="tl"><div class="tl-line" aria-hidden="true"><span></span></div><ol class="plain timeline">{"".join(timeline)}</ol></div>
  </div>
</section>
<section id="more" class="sec mist" aria-labelledby="more-h">
  <div class="wrap">
    <div class="sec-head reveal">{kicker(9)}<h2 class="sec-title" id="more-h">{e(ui["more"])}</h2></div>
    <ul class="plain more">{more}</ul>
  </div>
</section>
<section id="contact" class="sec contact" aria-labelledby="contact-h">
  <div class="wrap"><div class="cta-card on-dark">
    <p class="kicker">{num(10)} · {e(ui["contact"])}</p>
    <h2 class="contact-title" id="contact-h">{e(ui["contact_big"])}</h2>
    <p class="contact-text">{e(ui["contact_text"])} {e(t(meta["location"], lang))}.</p>
    <a class="btn primary" href="mailto:{e(email)}">{e(ui["email_cta"])}</a>
    <ul class="plain contact-links">
      <li><a href="mailto:{e(email)}">{e(email)}</a></li>
      <li><a href="{e(github_url(data))}">{e(github_label(data))}</a></li>
      <li><a href="{cv_href}">{e(ui["cv_pdf"])}</a></li>
      <li><a href="{pdf_href}">{e(ui["portfolio_pdf"])}</a></li>
    </ul>
  </div></div>
</section>
</main>
<footer class="site-footer on-dark">
  <div class="wrap">
    <p>{e(meta["name"])} · {e(ui["updated"].format(date=meta["updated"]))}</p>
    <p>{e(ui["made"])}</p>
    <a class="top" href="#top">{e(ui["top"])} ↑</a>
  </div>
</footer>
{SITE_JS}</body>
</html>
"""


# ------------------------------------------------------------------- CV page

CV_CSS = """
  @page { size: A4; margin: 14mm; }
  * { box-sizing: border-box; }
  html { font-size: 10pt; }
  body { margin: 0; background: #ffffff; color: #1d1b18; font-family: Arial, "Liberation Sans", Helvetica, system-ui, sans-serif; line-height: 1.38; }
  @media screen { body { max-width: 182mm; margin: 2rem auto; padding: 0 1rem; } }
  a { color: inherit; text-decoration: none; }
  h1 { margin: 0; font-size: 2rem; line-height: 1.15; }
  .headline { margin: .15rem 0 .2rem; font-size: 1.1rem; }
  .contact { margin: 0 0 .6rem; color: #3f3a33; }
  h2 { margin: .9rem 0 .35rem; padding-bottom: .15rem; border-bottom: .75pt solid #9a3b1b; font-size: 1.15rem; text-transform: uppercase; letter-spacing: .04em; color: #9a3b1b; break-after: avoid; }
  h3 { margin: .45rem 0 0; font-size: 1.02rem; break-after: avoid; }
  p { margin: .15rem 0; }
  ul { margin: .15rem 0 0; padding-left: 1.1rem; }
  li { margin: .05rem 0; }
  .sub { color: #3f3a33; }
  .entry { break-inside: avoid; }
  .skills p { margin: .12rem 0; }
"""


def render_cv(data, lang):
    ui = UI[lang]
    meta = data["meta"]
    h = ui["cv_headings"]
    email = meta["email"]
    figures = "; ".join(f'{e(s["value"])} {e(t(s["label"], lang))}' for s in data["stats"])

    jobs = "".join(
        f'<div class="entry"><h3>{e(t(job["role"], lang))} — {e(t(job["org"], lang))}</h3>'
        f'<p class="sub">{e(t(job["period"], lang))}</p><p>{e(t(job["body"], lang))}</p></div>'
        for job in data["experience"]
    )
    projects = []
    for project in data["projects"]:
        if not project["featured"]:
            continue
        picks = CV_HIGHLIGHTS.get(project["id"], [0, 1])
        bullets = "".join(f"<li>{e(t(project['highlights'][i], lang))}</li>" for i in picks)
        projects.append(
            f'<div class="entry"><h3>{e(t(project["title"], lang))}</h3>'
            f'<p class="sub">{e(t(project["context"], lang))} · {e(t(project["period"], lang))}</p>'
            f"<ul>{bullets}</ul></div>"
        )
    skills = "".join(
        f'<p><strong>{e(t(g["title"], lang))}:</strong> {", ".join(e(t(item, lang)) for item in g["items"])}</p>'
        for g in data["skills"]
    )
    education = "".join(f"<li>{e(t(item, lang))}</li>" for item in data["education"])
    languages = "".join(f"<li>{e(t(item, lang))}</li>" for item in data["languages"])

    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(ui["cv_title"].format(name=meta["name"]))}</title>
<style>{CV_CSS}</style>
</head>
<body>
<header>
  <h1>{e(meta["name"])}</h1>
  <p class="headline">{e(t(meta["headline"], lang))}</p>
  <p class="contact">{e(t(meta["location"], lang))} · <a href="mailto:{e(email)}">{e(email)}</a> · <a href="{e(github_url(data))}">{e(github_label(data))}</a></p>
</header>
<main>
<section>
  <h2>{e(h[0])}</h2>
  <p>{e(t(data["about"], lang))}</p>
  <p><strong>{e(ui["key_stack"])}:</strong> {", ".join(e(term) for term in KEY_STACK)}</p>
  <p><strong>{e(ui["cv_figures"])}:</strong> {figures}.</p>
</section>
<section>
  <h2>{e(h[1])}</h2>
  {jobs}
</section>
<section>
  <h2>{e(h[2])}</h2>
  {"".join(projects)}
</section>
<section class="skills">
  <h2>{e(h[3])}</h2>
  {skills}
</section>
<section>
  <h2>{e(h[4])}</h2>
  <ul>{education}</ul>
</section>
<section>
  <h2>{e(h[5])}</h2>
  <ul>{languages}</ul>
</section>
</main>
</body>
</html>
"""


# --------------------------------------------------------------------- build

def render_all(data, manifest, real=None):
    files = {}
    for lang in LANGS:
        files[PAGE_PATHS[lang]] = render_site(data, lang, manifest, real)
        files[CV_PATHS[lang]] = render_cv(data, lang)
    return files


def copy_images(manifest, out):
    """Copy every manifest image into out/assets/img/."""
    target = out / "assets" / "img"
    target.mkdir(parents=True, exist_ok=True)
    for entry in manifest.values():
        for variant in entry["variants"]:
            shutil.copyfile(ASSETS / variant["file"], target / variant["file"])


def find_chrome():
    for name in CHROME_NAMES:
        path = shutil.which(name)
        if path:
            return path
    return None


def print_pdf(chrome, source, target):
    with tempfile.TemporaryDirectory(prefix="portfolio-chrome-") as profile:
        result = subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
             f"--user-data-dir={profile}", "--no-pdf-header-footer", f"--print-to-pdf={target}",
             source.resolve().as_uri()],
            capture_output=True, text=True, timeout=180,
        )
    return result.returncode == 0 and target.is_file() and target.stat().st_size > 0


def build_pdfs(out):
    chrome = find_chrome()
    if not chrome:
        return "no Chrome/Chromium binary found"
    files_dir = out / "files"
    files_dir.mkdir(parents=True, exist_ok=True)
    jobs = []
    for lang in LANGS:
        jobs.append((out / CV_PATHS[lang], files_dir / PDF_NAMES["cv"][lang]))
        jobs.append((out / PAGE_PATHS[lang], files_dir / PDF_NAMES["portfolio"][lang]))
    for source, target in jobs:
        if not print_pdf(chrome, source, target):
            return f"Chrome could not print {target.name}"
        print(f"wrote {target}")
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--content", type=Path, default=DEFAULT_CONTENT, help="content JSON (default: content/portfolio.json)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output directory (default: site/)")
    parser.add_argument("--pdf", action="store_true", help="also print the CV and portfolio PDFs with headless Chrome")
    parser.add_argument("--real-images", type=Path, default=REAL_DIR,
                        help="folder with the real screenshots and their manifest.json (default: assets/img/real); "
                             "without a manifest the real projects show their referential artwork")
    args = parser.parse_args(argv)

    try:
        data = json.loads(args.content.read_text(encoding="utf-8"))
        validate(data)
        check_references(data)
        try:
            manifest = load_manifest()
        except (OSError, json.JSONDecodeError) as exc:
            raise ContentError(f"cannot read {MANIFEST}: {exc}") from exc
        try:
            real = load_real(args.real_images, data["projects"])
        except (OSError, json.JSONDecodeError) as exc:
            raise ContentError(f"cannot read {args.real_images / 'manifest.json'}: {exc}") from exc
        except ValueError as exc:
            raise ContentError(str(exc)) from exc
        files = render_all(data, manifest, real)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"content error: cannot read {args.content}: {exc}", file=sys.stderr)
        return 1
    except ContentError as exc:
        print(f"content error: {exc}", file=sys.stderr)
        return 1
    except (KeyError, TypeError, AttributeError) as exc:
        print(f"content error: invalid structure ({exc!r})", file=sys.stderr)
        return 1

    for rel, html in files.items():
        path = args.out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        print(f"wrote {path}")
    copy_images(manifest, args.out)
    copy_real(real, args.real_images, args.out)
    print(f"wrote {args.out / 'assets' / 'img'}")

    if args.pdf:
        error = build_pdfs(args.out)
        if error:
            print(f"pdf error: {error}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
