#!/usr/bin/env python3
"""Render the bilingual portfolio website, CV print sources and PDFs.

One content source (content/portfolio.json) renders:
  site/index.html, site/en/index.html  portfolio website (es, en)
  site/cv/es.html, site/cv/en.html     CV print sources
  site/assets/img/*                    artwork listed in assets/img/manifest.json
  site/files/*.pdf                     with --pdf, printed by headless Chrome

Standard library only. Content is validated before anything is written.
"""
import argparse
import json
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

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTENT = ROOT / "content" / "portfolio.json"
DEFAULT_OUT = ROOT / "site"
ASSETS = ROOT / "assets" / "img"
MANIFEST = ASSETS / "manifest.json"
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

# "Night blueprint" screen palette plus the light print palette (print-*).
# tools/contrast.py checks every pair in PAIRS.
PALETTE = {
    "bg": "#0a0e13",
    "surface": "#10161e",
    "surface-2": "#151d27",
    "hair": "#1f2b38",
    "control": "#5a7086",
    "text": "#e8eef5",
    "muted": "#9aabbd",
    "cyan": "#39d0c8",
    "sea": "#7ee0c3",
    "amber": "#ff8a4c",
    "amber-hover": "#ffa775",
    "violet": "#b7a6ff",
    "on-accent": "#0a0e13",
    "cover-bg": "#0c1219",
    "steel": "#7d9bb3",
    "print-paper": "#ffffff",
    "print-ink": "#16191d",
    "print-muted": "#4a525c",
    "print-accent": "#0b6964",
    "print-rule": "#d5dbe1",
}
# Accent per project area (tags, covers, spotlight).
AREA_ACCENT = {"software": "amber", "ai": "violet", "engineering": "cyan", "other": "sea"}
# (foreground, background, minimum ratio, role)
PAIRS = [
    ("text", "bg", 4.5, "body text"),
    ("text", "surface", 4.5, "card text"),
    ("text", "surface-2", 4.5, "hovered control text"),
    ("muted", "bg", 4.5, "secondary text"),
    ("muted", "surface", 4.5, "card secondary text"),
    ("muted", "surface-2", 4.5, "secondary text on raised surfaces"),
    ("cyan", "bg", 4.5, "links, kickers, numbers"),
    ("cyan", "surface", 4.5, "links on cards"),
    ("sea", "bg", 4.5, "skill group titles"),
    ("sea", "surface", 4.5, "area tag (other) on cards"),
    ("amber", "bg", 4.5, "area tag (software)"),
    ("amber", "surface", 4.5, "area tag (software) on cards"),
    ("violet", "bg", 4.5, "area tag (ai)"),
    ("violet", "surface", 4.5, "area tag (ai) on cards"),
    ("on-accent", "amber", 4.5, "primary button"),
    ("on-accent", "amber-hover", 4.5, "primary button hover"),
    ("on-accent", "cyan", 4.5, "pressed filter"),
    ("bg", "text", 4.5, "current language, skip link"),
    ("control", "bg", 3.0, "control borders"),
    ("control", "surface", 3.0, "control borders on cards"),
    ("control", "surface-2", 3.0, "control borders on raised surfaces"),
    ("sea", "bg", 3.0, "focus ring"),
    ("sea", "surface", 3.0, "focus ring on cards"),
    ("cyan", "bg", 3.0, "pressed filter boundary"),
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
        "explore": "Explorar",
        "key_stack": "Stack principal",
        "languages": "Idiomas",
        "education": "Formación",
        "about": "Perfil",
        "numbers": "En cifras",
        "stack_title": "Stack en uso",
        "stack_note": "Tecnologías que aparecen en los proyectos de este portafolio.",
        "work": "Casos destacados",
        "work_note": "Ocho proyectos con el detalle completo. Los nombres de clientes y empresas están anonimizados.",
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
        "explore": "Explore",
        "key_stack": "Key stack",
        "languages": "Languages",
        "education": "Education",
        "about": "About",
        "numbers": "By the numbers",
        "stack_title": "Stack in use",
        "stack_note": "Technologies used across the projects in this portfolio.",
        "work": "Featured work",
        "work_note": "Eight projects in full detail. Client and company names are anonymized.",
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


def unique_cover(project, suffix):
    """A second copy of a cover with its own element ids."""
    slug = project["id"]
    return cover_svg(slug, project["area"]).replace(f"cv-{slug}-", f"cv-{slug}-{suffix}-")


FAVICON = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
           "<rect width='64' height='64' rx='14' fill='#0a0e13'/>"
           "<path d='M10 46c10-4 14-18 24-20s14 10 20 4' fill='none' stroke='#39d0c8' stroke-width='4' stroke-linecap='round'/>"
           "<path d='M10 32c8-3 12-12 20-13' fill='none' stroke='#7ee0c3' stroke-width='3' stroke-linecap='round' opacity='.6'/>"
           "<circle cx='47' cy='23' r='5' fill='#ff8a4c'/></svg>")


def data_uri_svg(svg):
    return "data:image/svg+xml," + quote(svg, safe=" =':/,.-")


# ---------------------------------------------------------------------- CSS

def css_vars():
    return "\n".join(f"    --{name}: {value};" for name, value in PALETTE.items())


SITE_CSS = """
  :root {
%VARS%
    --sans: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --mono: ui-monospace, "SF Mono", "Cascadia Code", "JetBrains Mono", Menlo, Consolas, "Liberation Mono", monospace;
    --radius: 18px;
    --header-h: 4rem;
    --ease: cubic-bezier(.2, .7, .2, 1);
    --grain: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  }
  *, *::before, *::after { box-sizing: border-box; }
  [hidden] { display: none !important; }
  html { -webkit-text-size-adjust: 100%; scroll-padding-top: calc(var(--header-h) + 1rem); background: var(--bg); color-scheme: dark; }
  body { margin: 0; background: var(--bg); color: var(--text); font: 400 clamp(1.0625rem, 1rem + .25vw, 1.125rem)/1.65 var(--sans); overflow-wrap: break-word; -webkit-font-smoothing: antialiased; }
  body::after { content: ""; position: fixed; inset: 0; z-index: 90; pointer-events: none; background-image: var(--grain); opacity: .045; }
  h1, h2, h3 { color: var(--text); }
  a { color: var(--cyan); text-underline-offset: .2em; text-decoration-thickness: 1px; }
  a:hover { color: var(--sea); }
  :focus-visible { outline: 2px solid var(--sea); outline-offset: 3px; border-radius: 6px; }
  main:focus { outline: none; }
  img, svg, canvas { display: block; max-width: 100%; }
  .wrap { width: min(100% - 2.5rem, 76rem); margin-inline: auto; }
  .plain { list-style: none; margin: 0; padding: 0; }
  .sr-only { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }
  .print-only { display: none; }
  .skip { position: absolute; left: -9999px; top: 8px; z-index: 100; display: inline-flex; align-items: center; min-height: 44px; padding: 0 1rem; border-radius: 8px; background: var(--text); color: var(--bg); font-weight: 700; }
  .skip:focus { left: 8px; color: var(--bg); }

  /* Header */
  .site-header { position: sticky; top: 0; z-index: 50; height: var(--header-h); margin-bottom: calc(-1 * var(--header-h)); background: rgba(10, 14, 19, .66); -webkit-backdrop-filter: blur(14px) saturate(1.4); backdrop-filter: blur(14px) saturate(1.4); border-bottom: 1px solid rgba(31, 43, 56, .8); }
  .bar { position: relative; height: 100%; display: flex; align-items: center; gap: .5rem; }
  .mark { display: inline-flex; align-items: center; gap: .625rem; min-height: 44px; margin-right: auto; color: var(--text); font-weight: 700; letter-spacing: -.01em; text-decoration: none; white-space: nowrap; }
  .mark:hover { color: var(--text); }
  .mark-glyph { display: grid; place-items: center; width: 2.25rem; height: 2.25rem; border: 1px solid var(--control); border-radius: 10px; font: 700 .8125rem/1 var(--mono); color: var(--sea); }
  .mark-name { display: none; }
  .site-nav ul { display: flex; gap: .125rem; }
  .site-nav a { display: inline-flex; align-items: center; min-height: 44px; padding: 0 .75rem; border-radius: 8px; color: var(--muted); font-size: .9375rem; text-decoration: none; }
  .site-nav a:hover { color: var(--text); }
  .site-nav a.is-active { color: var(--text); box-shadow: inset 0 -2px 0 var(--cyan); border-radius: 0; }
  .tools { display: flex; align-items: center; gap: .375rem; }
  .lang ul { display: flex; }
  .lang a { display: inline-grid; place-items: center; min-width: 44px; min-height: 44px; border: 1px solid var(--control); color: var(--text); font: 600 .8125rem/1 var(--mono); letter-spacing: .06em; text-decoration: none; }
  .lang li:first-child a { border-radius: 999px 0 0 999px; }
  .lang li:last-child a { border-radius: 0 999px 999px 0; border-left: 0; }
  .lang a:hover { background: var(--surface-2); color: var(--text); }
  .lang a[aria-current="page"] { background: var(--text); border-color: var(--text); color: var(--bg); }
  .icon-btn { display: inline-flex; align-items: center; justify-content: center; gap: .5rem; min-width: 44px; min-height: 44px; padding: 0 .75rem; border: 1px solid var(--control); border-radius: 999px; background: transparent; color: var(--text); font: 500 .875rem/1 var(--sans); cursor: pointer; }
  .icon-btn:hover { background: var(--surface-2); }
  .icon-btn svg { width: 16px; height: 16px; flex: none; }
  .pause .i-play, .pause.is-paused .i-pause { display: none; }
  .pause.is-paused .i-play { display: block; }
  .progress { display: none; position: absolute; left: 0; right: 0; bottom: -1px; height: 2px; transform-origin: 0 50%; transform: scaleX(0); background: linear-gradient(90deg, var(--cyan), var(--sea) 70%, var(--amber)); }
  @media (min-width: 40rem) { .mark-name { display: inline; } }
  @media (max-width: 83.99rem) { .pause-label { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; } .pause { padding: 0; } }
  @media (max-width: 67.99rem) {
    .site-nav { position: absolute; top: 100%; left: -1.25rem; right: -1.25rem; padding: .25rem 1.25rem; background: var(--bg); border-bottom: 1px solid var(--hair); box-shadow: 0 24px 48px rgba(0, 0, 0, .5); overflow-x: auto; }
    html.js .site-nav { display: none; padding: .5rem 1.25rem 1.25rem; }
    html.js .site-header.menu-open .site-nav { display: block; }
    html.js .site-nav ul { flex-direction: column; }
    html.js .site-nav a { min-height: 52px; color: var(--text); font-size: 1.25rem; font-weight: 600; }
    html.js .site-nav a.is-active { box-shadow: inset 2px 0 0 var(--cyan); }
  }
  @media (min-width: 68rem) { .menu { display: none !important; } }

  /* Hero */
  .hero { position: relative; isolation: isolate; display: grid; align-items: center; min-height: clamp(36rem, 100svh, 72rem); overflow: clip; }
  .hero-media { position: absolute; inset: 0; z-index: -1; background: var(--bg); }
  .hero-art, .hero-art img, .flow, .hero-scrim { position: absolute; inset: 0; width: 100%; height: 100%; }
  .hero-art img { object-fit: cover; object-position: 70% 50%; }
  .flow { mix-blend-mode: screen; pointer-events: none; }
  .hero-scrim { background: linear-gradient(90deg, rgba(10, 14, 19, .95) 0%, rgba(10, 14, 19, .86) 34%, rgba(10, 14, 19, .32) 64%, rgba(10, 14, 19, 0) 100%), linear-gradient(0deg, var(--bg) 0%, rgba(10, 14, 19, 0) 26%); }
  .hero-inner { position: relative; padding: calc(var(--header-h) + 3rem) 0 6rem; }
  .hero-copy { max-width: 64rem; }
  .kicker { display: flex; align-items: center; gap: .75rem; margin: 0 0 1.25rem; font: 500 .8125rem/1.4 var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--cyan); }
  .kicker::before { content: ""; width: 2rem; height: 1px; background: currentColor; }
  .name { margin: 0 0 1.5rem; font: 800 clamp(2.6rem, 1rem + 6.6vw, 6.5rem)/.95 var(--sans); letter-spacing: -.045em; text-wrap: balance; overflow-wrap: normal; }
  .name .w { display: inline-block; }
  .headline { margin: 0 0 1rem; max-width: 34ch; font-size: clamp(1.125rem, 1rem + .7vw, 1.5rem); font-weight: 650; line-height: 1.35; letter-spacing: -.01em; }
  .lede { margin: 0 0 1.25rem; max-width: 54ch; color: var(--muted); }
  .loc { display: flex; align-items: center; gap: .5rem; margin: 0 0 2rem; font: 500 .875rem/1.4 var(--mono); color: var(--muted); }
  .loc svg { width: 14px; height: 14px; color: var(--amber); }
  .cta { display: flex; flex-wrap: wrap; gap: .625rem; }
  .btn { display: inline-flex; align-items: center; justify-content: center; gap: .5rem; min-height: 48px; padding: .75rem 1.375rem; border: 1px solid transparent; border-radius: 999px; font: 650 1rem/1.2 var(--sans); text-align: center; text-decoration: none; cursor: pointer; }
  .btn.primary { background: var(--amber); color: var(--on-accent); box-shadow: 0 10px 40px -12px rgba(255, 138, 76, .55); }
  .btn.primary:hover { background: var(--amber-hover); color: var(--on-accent); }
  .btn.ghost { border-color: var(--control); background: rgba(10, 14, 19, .6); color: var(--text); -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px); }
  .btn.ghost:hover { background: var(--surface-2); color: var(--text); }
  .cue { position: absolute; left: 50%; bottom: 1.25rem; display: none; flex-direction: column; align-items: center; gap: .5rem; min-width: 44px; padding: .25rem .5rem; transform: translateX(-50%); color: var(--muted); font: 500 .75rem/1 var(--mono); letter-spacing: .16em; text-transform: uppercase; text-decoration: none; }
  .cue:hover { color: var(--text); }
  .cue-line { position: relative; width: 1px; height: 40px; overflow: hidden; background: linear-gradient(var(--control), transparent); }
  .cue-line::after { content: ""; position: absolute; left: -1px; top: 0; width: 3px; height: 12px; border-radius: 2px; background: var(--sea); }
  @media (min-width: 48rem) and (min-height: 40rem) { .cue { display: flex; } }
  @media (orientation: portrait) and (max-width: 64rem) {
    .hero { align-items: start; }
    .hero-art img { object-position: 50% 100%; }
    .hero-scrim { background: linear-gradient(180deg, rgba(10, 14, 19, .9) 0%, rgba(10, 14, 19, .82) 50%, rgba(10, 14, 19, .35) 78%, var(--bg) 100%); }
    .hero-inner { padding-top: calc(var(--header-h) + 2rem); }
  }

  /* Sections */
  .sec { position: relative; isolation: isolate; padding: clamp(4.5rem, 3rem + 6vw, 8rem) 0; }
  .sec + .sec { border-top: 1px solid var(--hair); }
  .glow::before { content: ""; position: absolute; z-index: -1; inset: 0; pointer-events: none; background: radial-gradient(40rem 26rem at 12% 8%, rgba(57, 208, 200, .07), transparent 70%), radial-gradient(34rem 24rem at 92% 60%, rgba(255, 138, 76, .045), transparent 70%); }
  .sec-head { margin-bottom: clamp(2.5rem, 2rem + 2vw, 4rem); }
  .sec-title { margin: 0; font: 800 clamp(2.25rem, 1.3rem + 4.2vw, 4.75rem)/1 var(--sans); letter-spacing: -.04em; text-wrap: balance; }
  .note { margin: 1.25rem 0 0; max-width: 58ch; color: var(--muted); }
  .tag { display: inline-flex; align-items: center; gap: .5rem; font: 600 .75rem/1.3 var(--mono); letter-spacing: .1em; text-transform: uppercase; color: var(--area, var(--sea)); }
  .tag::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: currentColor; box-shadow: 0 0 10px currentColor; }
  .chips { display: flex; flex-wrap: wrap; gap: .375rem; }
  .chips li { padding: .3rem .625rem; border: 1px solid var(--hair); border-radius: 6px; background: rgba(21, 29, 39, .6); font: 500 .8125rem/1.3 var(--mono); color: var(--muted); }

  /* About */
  .about-grid { display: grid; gap: 2.5rem; }
  .about-text { margin: 0; max-width: 34ch; font-size: clamp(1.375rem, 1rem + 1.6vw, 2.25rem); font-weight: 600; line-height: 1.3; letter-spacing: -.02em; }
  .facts { display: grid; gap: 1.75rem; margin: 0; }
  .facts dt { margin-bottom: .5rem; font: 600 .75rem/1.3 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--sea); }
  .facts dd { margin: 0; color: var(--muted); }
  .facts dd li + li { margin-top: .25rem; }
  @media (min-width: 60rem) { .about-grid { grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr); gap: 4rem; align-items: start; } }

  /* Stats */
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 15rem), 1fr)); border-top: 1px solid var(--hair); }
  .stat { position: relative; padding: 2rem 1.5rem 2rem 0; border-bottom: 1px solid var(--hair); }
  .stat::before { content: ""; position: absolute; top: -1px; left: 0; width: 3rem; height: 2px; background: var(--cyan); box-shadow: 0 0 14px var(--cyan); }
  .stat .v { margin: 0 0 .75rem; font: 700 clamp(2.75rem, 1.5rem + 3.4vw, 4.5rem)/1 var(--mono); letter-spacing: -.06em; font-variant-numeric: tabular-nums; white-space: nowrap; overflow-wrap: normal; }
  .stat .l { margin: 0; max-width: 28ch; color: var(--muted); }
  @media (min-width: 72rem) { .stats { grid-template-columns: repeat(4, minmax(0, 1fr)); } }

  /* Stack marquee (static wrapped list unless motion is allowed) */
  .stack-sec { padding: clamp(3.5rem, 3rem + 3vw, 5.5rem) 0; border-top: 1px solid var(--hair); background: linear-gradient(180deg, var(--surface), var(--bg)); }
  .stack-sec .sec-head { margin-bottom: 2rem; }
  .stack-sec .sec-title { font-size: clamp(1.75rem, 1.2rem + 2.4vw, 3rem); }
  .mq { display: grid; gap: .75rem; padding-inline: max(1.25rem, (100% - 76rem) / 2); }
  .mq-row { display: flex; }
  .mq-track { display: flex; flex-wrap: wrap; gap: .625rem; }
  .mq-track[aria-hidden="true"] { display: none; }
  .mq-track li { padding: .625rem 1.125rem; border: 1px solid var(--hair); border-radius: 999px; background: var(--surface); font: 500 clamp(.9375rem, .85rem + .35vw, 1.125rem)/1.2 var(--mono); white-space: nowrap; }
  .mq-row.rev li { color: var(--muted); }

  /* Featured cases */
  .case { display: grid; gap: 2rem; padding: clamp(2.5rem, 2rem + 3vw, 5rem) 0; border-top: 1px solid var(--hair); }
  .case:first-of-type { border-top: 0; padding-top: 0; }
  .case-top { display: flex; align-items: baseline; gap: 1rem; margin: 0 0 1rem; }
  .case-num { font: 700 clamp(2.5rem, 2rem + 2vw, 3.75rem)/1 var(--mono); letter-spacing: -.06em; color: var(--area, var(--cyan)); }
  .case h3 { margin: 0 0 .75rem; font: 750 clamp(1.625rem, 1.2rem + 1.8vw, 2.5rem)/1.1 var(--sans); letter-spacing: -.03em; text-wrap: balance; }
  .meta { margin: 0 0 1.25rem; font: 500 .875rem/1.5 var(--mono); color: var(--muted); }
  .summary { margin: 0 0 1.25rem; }
  .hl { margin: 0 0 1.5rem; padding: 0; list-style: none; }
  .hl li { position: relative; margin-bottom: .625rem; padding-left: 1.5rem; }
  .hl li::before { content: ""; position: absolute; left: 0; top: .72em; width: .75rem; height: 1px; background: var(--area, var(--cyan)); }
  .stack-label { margin: 0 0 .5rem; font: 600 .75rem/1.3 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
  .case-media { position: relative; border-radius: var(--radius); }
  .case-text { min-width: 0; }
  .case-media:focus-within { outline: 2px solid var(--sea); outline-offset: 4px; }
  .media-clip { position: relative; aspect-ratio: 4 / 3; overflow: hidden; border-radius: var(--radius); border: 1px solid var(--hair); background: var(--surface); --cover-bg: #000000; --cover-line: var(--sea); --cover-line-2: var(--cyan); --cover-accent: var(--area); --cover-glow: var(--area); }
  .zoom, .zoom img, .media-clip .cover, .duo { position: absolute; inset: 0; width: 100%; height: 100%; }
  .zoom img { object-fit: cover; }
  .media-clip .cover { opacity: .42; mix-blend-mode: screen; }
  .duo { background: linear-gradient(155deg, color-mix(in srgb, var(--area) 20%, transparent), transparent 46%), linear-gradient(0deg, rgba(10, 14, 19, .6), transparent 45%); }
  .media-clip::after { content: ""; position: absolute; inset: 0; background-image: var(--grain); opacity: .08; pointer-events: none; }
  .fig { position: absolute; left: 1rem; bottom: .875rem; z-index: 1; font: 600 .75rem/1 var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--text); }
  @media (min-width: 60rem) {
    .case { grid-template-columns: minmax(0, 1fr) minmax(0, 1.08fr); gap: clamp(2.5rem, 1rem + 4vw, 5rem); align-items: start; }
    .case-media { position: sticky; top: calc(var(--header-h) + 2rem); }
    .case:nth-of-type(odd) .case-media { order: -1; }
  }
  @media (max-width: 59.99rem) { .case-media { order: -1; } }

  /* All projects */
  .filters { display: flex; flex-wrap: wrap; gap: .5rem; margin-bottom: 1rem; }
  .chip { display: inline-flex; align-items: center; gap: .5rem; min-height: 44px; padding: 0 1rem; border: 1px solid var(--control); border-radius: 999px; background: transparent; color: var(--text); font: 500 .9375rem/1.2 var(--sans); cursor: pointer; }
  .chip .n { font-family: var(--mono); font-size: .8125rem; color: var(--muted); }
  .chip:hover { background: var(--surface-2); }
  .chip[aria-pressed="true"] { border-color: var(--cyan); background: var(--cyan); color: var(--on-accent); font-weight: 650; }
  .chip[aria-pressed="true"] .n { color: var(--on-accent); }
  .count { margin: 0 0 1.5rem; font: 500 .875rem/1.4 var(--mono); color: var(--muted); }
  .empty { margin-bottom: 1.5rem; padding: 1.5rem; border: 1px dashed var(--control); border-radius: var(--radius); }
  .empty p { margin: 0 0 1rem; }
  .empty .btn { border-color: var(--control); background: transparent; color: var(--text); }
  .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 20rem), 1fr)); gap: 1.25rem; }
  .card { position: relative; display: flex; flex-direction: column; border: 1px solid var(--hair); border-radius: var(--radius); background: var(--surface); }
  .card::before { content: ""; position: absolute; inset: 0; z-index: 0; border-radius: inherit; pointer-events: none; opacity: 0; background: radial-gradient(22rem circle at var(--mx, 50%) var(--my, 0%), color-mix(in srgb, var(--area) 13%, transparent), transparent 65%); }
  .card:hover { border-color: color-mix(in srgb, var(--area) 45%, var(--hair)); }
  .card-cover { position: relative; aspect-ratio: 4 / 3; overflow: hidden; border-radius: calc(var(--radius) - 1px) calc(var(--radius) - 1px) 0 0; border-bottom: 1px solid var(--hair); --cover-bg: var(--cover-bg); --cover-line: var(--steel); --cover-line-2: var(--sea); --cover-accent: var(--area); --cover-glow: var(--area); }
  .card-cover .cover { width: 100%; height: 100%; }
  .card-body { position: relative; z-index: 1; display: flex; flex: 1; flex-direction: column; padding: 1.25rem 1.375rem 1.375rem; }
  .card-top { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin: 0 0 .75rem; }
  .card-top .n { font: 700 1.125rem/1 var(--mono); color: var(--text); }
  .card h3 { margin: 0 0 .375rem; font: 700 1.25rem/1.25 var(--sans); letter-spacing: -.015em; }
  .card h3 a { color: var(--text); text-decoration: none; }
  .card h3 a:hover { color: var(--cyan); text-decoration: underline; }
  .card .meta { margin-bottom: .75rem; font-size: .8125rem; }
  .card .summary { margin-bottom: 1rem; font-size: 1rem; color: var(--muted); }
  .card details { margin-top: auto; border-top: 1px solid var(--hair); }
  .card summary { display: flex; align-items: center; justify-content: space-between; min-height: 44px; font: 600 .8125rem/1.3 var(--mono); letter-spacing: .06em; text-transform: uppercase; color: var(--cyan); cursor: pointer; list-style: none; }
  .card summary::-webkit-details-marker { display: none; }
  .card summary::after { content: "+"; font-size: 1.25rem; line-height: 1; color: var(--text); }
  .card details[open] summary::after { content: "−"; }
  .card .hl { margin: .5rem 0 1rem; font-size: .9375rem; }
  .go { display: inline-flex; align-items: center; min-height: 44px; margin-top: .25rem; font: 600 .875rem/1.2 var(--mono); }

  /* Methods, skills */
  .methods { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 20rem), 1fr)); gap: 0 2.5rem; }
  .method { padding: 1.75rem 0; border-top: 1px solid var(--hair); }
  .m-num { font: 600 .875rem/1 var(--mono); color: var(--cyan); }
  .method h3 { margin: .875rem 0 .5rem; font: 700 1.375rem/1.25 var(--sans); letter-spacing: -.02em; }
  .method p { margin: 0; color: var(--muted); }
  .skills { margin: 0; }
  .skill { display: grid; gap: .875rem; padding: 1.5rem 0; border-top: 1px solid var(--hair); }
  .skill dt { font: 600 .8125rem/1.4 var(--mono); letter-spacing: .1em; text-transform: uppercase; color: var(--sea); }
  .skill dd { margin: 0; }
  .skill .chips li { color: var(--text); }
  @media (min-width: 48rem) { .skill { grid-template-columns: 15rem minmax(0, 1fr); gap: 2rem; } }

  /* Experience timeline */
  .tl { position: relative; padding-left: 2.5rem; }
  .tl-line { position: absolute; left: .5rem; top: .5rem; bottom: .5rem; width: 2px; background: var(--hair); }
  .tl-line span { position: absolute; inset: 0; transform-origin: 50% 0; background: linear-gradient(var(--cyan), var(--sea)); box-shadow: 0 0 12px rgba(57, 208, 200, .5); }
  .timeline li { position: relative; padding-bottom: 3rem; }
  .timeline li:last-child { padding-bottom: 0; }
  .tl-dot { position: absolute; left: calc(-2.5rem + .5rem + 1px - 9px); top: .3rem; width: 18px; height: 18px; border: 2px solid var(--control); border-radius: 50%; background: var(--bg); }
  .tl-dot i { position: absolute; inset: 3px; border-radius: 50%; background: var(--cyan); box-shadow: 0 0 14px var(--cyan); }
  .tl-dot.now i { background: var(--amber); box-shadow: 0 0 14px var(--amber); }
  .when { margin: 0 0 .375rem; font: 600 .875rem/1.4 var(--mono); color: var(--cyan); }
  .timeline h3 { margin: 0; font: 700 1.375rem/1.25 var(--sans); letter-spacing: -.02em; }
  .org { margin: .25rem 0 0; color: var(--muted); }
  .timeline .body { margin: .625rem 0 0; max-width: 62ch; }
  @media (min-width: 48rem) { .timeline li { display: grid; grid-template-columns: 11rem minmax(0, 1fr); gap: 2rem; } }

  /* More */
  .more { display: grid; gap: 0 2.5rem; grid-template-columns: repeat(auto-fill, minmax(min(100%, 26rem), 1fr)); }
  .more li { position: relative; padding: 1.125rem 0 1.125rem 2rem; border-top: 1px solid var(--hair); }
  .more li::before { content: "+"; position: absolute; left: 0; top: 1.125rem; font: 700 1rem/1.65 var(--mono); color: var(--amber); }

  /* Contact */
  .contact { padding-bottom: clamp(5rem, 4rem + 5vw, 9rem); }
  .contact::before { content: ""; position: absolute; z-index: -1; inset: 0; pointer-events: none; background: radial-gradient(46rem 30rem at 50% 100%, rgba(57, 208, 200, .1), transparent 70%); }
  .contact-title { margin: 0 0 1.5rem; max-width: 14ch; font: 800 clamp(2.75rem, 1.2rem + 6.4vw, 6.75rem)/.95 var(--sans); letter-spacing: -.045em; text-wrap: balance; }
  .contact-text { margin: 0 0 2.5rem; max-width: 52ch; color: var(--muted); font-size: 1.125rem; }
  .glow-btn { position: relative; isolation: isolate; display: inline-flex; max-width: 100%; padding: 2px; overflow: hidden; border-radius: 999px; background: linear-gradient(90deg, var(--cyan), var(--sea), var(--amber)); box-shadow: 0 0 56px -10px rgba(57, 208, 200, .55); text-decoration: none; }
  .glow-btn::before { content: ""; position: absolute; z-index: -1; left: 50%; top: 50%; width: 130%; aspect-ratio: 1; translate: -50% -50%; background: conic-gradient(from 0deg, var(--cyan), var(--sea), var(--amber), var(--violet), var(--cyan)); }
  .glow-btn > span { display: inline-flex; align-items: center; gap: .75rem; min-height: 60px; min-width: 0; padding: 1rem 1.75rem; border-radius: 999px; background: var(--bg); color: var(--text); font: 700 clamp(1rem, .85rem + .7vw, 1.5rem)/1.2 var(--sans); letter-spacing: -.01em; overflow-wrap: anywhere; }
  .glow-btn:hover > span { background: var(--surface); }
  .glow-btn:hover { color: var(--text); }
  .contact-links { display: flex; flex-wrap: wrap; gap: .25rem 1.5rem; margin-top: 2rem; }
  .contact-links a { display: inline-flex; align-items: center; min-height: 44px; font: 500 .9375rem/1.3 var(--mono); }

  .site-footer { padding: 2rem 0 2.5rem; border-top: 1px solid var(--hair); font: 500 .8125rem/1.6 var(--mono); color: var(--muted); }
  .site-footer .wrap { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: .5rem 2rem; }
  .site-footer p { margin: 0; }
  .site-footer a { display: inline-flex; align-items: center; min-height: 44px; }

  @media (hover: hover) and (pointer: fine) { .card:hover::before { opacity: 1; } }

  /* Motion: only with no reduced-motion preference; html.motion-paused stops it. */
  @media (prefers-reduced-motion: no-preference) {
    html { scroll-behavior: smooth; }
    .name .w { animation: word-in .64s var(--ease) both; animation-delay: calc(var(--i) * 80ms); }
    .hero-copy > :not(.name) { animation: fade-up .6s var(--ease) both; animation-delay: .24s; }
    .cue-line::after { animation: cue 2.4s var(--ease) infinite; }
    .btn, .chip, .icon-btn, .lang a, .card, .site-nav a { transition: background-color .2s, border-color .2s, color .2s; }
    .card::before { transition: opacity .35s; }
    .magnetic { transition: transform .3s var(--ease), background-color .2s, border-color .2s, color .2s; }
    .zoom { transition: transform .9s var(--ease); }
    @media (hover: hover) and (pointer: fine) { .case-media:hover .zoom { transform: scale(1.045); } }
    .glow-btn::before { animation: spin 6s linear infinite; }
    .mq { overflow: hidden; padding-inline: 0; -webkit-mask-image: linear-gradient(90deg, transparent, #000 7%, #000 93%, transparent); mask-image: linear-gradient(90deg, transparent, #000 7%, #000 93%, transparent); }
    .mq-row { width: max-content; }
    .mq-track, .mq-track[aria-hidden="true"] { display: flex; flex-wrap: nowrap; padding-right: .625rem; animation: marquee var(--dur, 90s) linear infinite; }
    .mq-row.rev .mq-track { animation-direction: reverse; }
    .mq:hover .mq-track, .mq:focus-within .mq-track, html.motion-paused .mq-track { animation-play-state: paused; }
    html.motion-paused .name .w, html.motion-paused .hero-copy > *, html.motion-paused .cue-line::after, html.motion-paused .glow-btn::before { animation: none; }
    @supports ((animation-timeline: scroll()) and (animation-range: 0% 100%)) {
      .progress { display: block; animation: grow-x linear both; animation-timeline: scroll(root block); }
    }
    @supports ((animation-timeline: view()) and (animation-range: 0% 100%)) {
      html.js:not(.motion-paused) .reveal { animation: rise linear both; animation-timeline: view(); animation-range: cover calc(var(--i, 0) * 40px) cover calc(240px + var(--i, 0) * 40px); }
      html.js:not(.motion-paused) .media-clip { animation: unclip linear both; animation-timeline: view(); animation-range: cover 0% cover 42%; }
      html.js:not(.motion-paused) .zoom img { animation: settle linear both; animation-timeline: view(); animation-range: cover 0% cover 50%; }
      .tl { view-timeline: --tl block; }
      html.js:not(.motion-paused) .tl-line span { animation: grow-y linear both; animation-timeline: --tl; animation-range: entry 10% entry 100%; }
      html.js:not(.motion-paused) .tl-dot i { animation: dot-on linear both; animation-timeline: view(); animation-range: cover 120px cover 220px; }
    }
    @supports not ((animation-timeline: view()) and (animation-range: 0% 100%)) {
      html.js:not(.motion-paused) .reveal:not(.is-in) { opacity: 0; transform: translateY(32px); }
      html.js .reveal { transition: opacity .8s var(--ease), transform .8s var(--ease); transition-delay: calc(var(--i, 0) * 70ms); }
      html.js:not(.motion-paused) .media-clip:not(.is-in) { clip-path: inset(12% 12% 12% 12% round var(--radius)); }
      html.js .media-clip { transition: clip-path 1.1s var(--ease); }
      html.js:not(.motion-paused) .tl:not(.is-in) .tl-line span { transform: scaleY(0); }
      html.js .tl-line span { transition: transform 1.6s var(--ease); }
      html.js:not(.motion-paused) .timeline li:not(.is-in) .tl-dot i { opacity: 0; transform: scale(.3); }
      html.js .tl-dot i { transition: opacity .6s, transform .6s var(--ease); }
    }
    @keyframes word-in { from { opacity: 0; transform: translateY(.42em); } to { opacity: 1; transform: none; } }
    @keyframes fade-up { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
    @keyframes rise { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: none; } }
    @keyframes unclip { from { clip-path: inset(12% 12% 12% 12% round var(--radius)); } to { clip-path: inset(0 round var(--radius)); } }
    @keyframes settle { from { transform: scale(1.16); } to { transform: scale(1); } }
    @keyframes grow-x { to { transform: scaleX(1); } }
    @keyframes grow-y { from { transform: scaleY(0); } to { transform: scaleY(1); } }
    @keyframes dot-on { from { opacity: 0; transform: scale(.3); } to { opacity: 1; transform: none; } }
    @keyframes cue { 0% { transform: translateY(-12px); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateY(40px); opacity: 0; } }
    @keyframes spin { to { transform: rotate(1turn); } }
    @keyframes marquee { to { transform: translateX(-100%); } }
    ::view-transition-group(*) { animation-duration: .38s; animation-timing-function: var(--ease); }
  }

  @media print {
    @page { size: A4; margin: 13mm 14mm 14mm; }
    :root { --bg: var(--print-paper); --surface: var(--print-paper); --surface-2: var(--print-paper); --text: var(--print-ink); --muted: var(--print-muted); --hair: var(--print-rule); --cyan: var(--print-accent); --sea: var(--print-accent); --amber: var(--print-accent); --violet: var(--print-accent); --area: var(--print-accent); }
    *, *::before, *::after { animation: none !important; transition: none !important; box-shadow: none !important; text-shadow: none !important; }
    html { font-size: 8.75pt; color-scheme: light; background: #ffffff; }
    body { background: #ffffff; color: var(--text); line-height: 1.45; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    body::after, .skip, .site-header, .hero-media, .cue, .cta, .stack-sec, .filters, .count, .empty, .case-media, .card-cover, .go, .glow-btn, .tl-line, .tl-dot, .site-footer .top, .card.is-featured .summary, .card.is-featured details { display: none !important; }
    .reveal, .media-clip, .name .w, .hero-copy > * { opacity: 1 !important; transform: none !important; clip-path: none !important; }
    .card[hidden] { display: block !important; }
    .print-only { display: block; }
    .wrap { width: auto; margin: 0; }
    a { color: inherit; text-decoration: none; }
    .hero { display: block; min-height: 0; overflow: visible; padding: 0 0 3mm; border-bottom: 1px solid var(--hair); }
    .hero-inner { padding: 0; }
    .hero-copy { max-width: none; }
    .kicker { margin-bottom: 1.5mm; font-size: .8rem; break-after: avoid; page-break-after: avoid; }
    .kicker::before { display: none; }
    .name { margin: 0 0 1mm; font-size: 2.6rem; letter-spacing: -.02em; }
    .headline { margin-bottom: 1mm; max-width: none; font-size: 1.15rem; }
    .lede { margin-bottom: 1mm; max-width: none; color: var(--text); }
    .loc { margin: 0; }
    .sec { padding: 4mm 0; }
    .sec + .sec { border-top: 1px solid var(--hair); }
    .glow::before, .contact::before { display: none; }
    .sec-head { margin-bottom: 2mm; break-after: avoid; }
    .sec-title { font-size: 1.65rem; letter-spacing: -.01em; }
    .note { margin-top: 1mm; max-width: none; }
    .about-grid { grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr); gap: 6mm; }
    .about-text { max-width: none; font-size: 1.1rem; font-weight: 500; }
    .facts { gap: 2mm; }
    .stats { grid-template-columns: repeat(4, minmax(0, 1fr)); }
    .stat { padding: 2mm 3mm 2mm 0; }
    .stat::before { display: none; }
    .stat .v { margin-bottom: 1mm; font-size: 1.8rem; }
    .stat .v .tally { display: none; }
    .stat .v .sr-only { position: static; width: auto; height: auto; margin: 0; overflow: visible; clip: auto; white-space: nowrap; }
    .case { display: block; padding: 3mm 0; }
    .case:first-of-type { padding-top: 0; }
    .case-top { margin-bottom: 1mm; }
    .case-num { font-size: 1.5rem; }
    .case h3 { margin-bottom: .5mm; font-size: 1.35rem; }
    .meta { margin-bottom: 1.5mm; font-size: .85rem; }
    .summary { margin-bottom: 1.5mm; }
    .hl { margin-bottom: 1.5mm; }
    .hl li { margin-bottom: .5mm; padding-left: 1.1rem; }
    .chips { display: block; }
    .chips li { display: inline; padding: 0; border: 0; background: none; font-size: .8rem; }
    .chips li:not(:last-child)::after { content: " · "; }
    .stack-label { display: inline; margin-right: .5em; }
    .cards { display: block; }
    .card { display: block; padding: 2mm 0; border: 0; border-top: 1px solid var(--hair); border-radius: 0; background: none; }
    .card::before { display: none; }
    .card-body { padding: 0; }
    .card-top { justify-content: flex-start; margin-bottom: .5mm; }
    .card h3 { font-size: 1.1rem; }
    .card .meta { margin-bottom: .5mm; }
    .card .summary { margin-bottom: .5mm; color: var(--text); font-size: 1rem; }
    .card details { border: 0; }
    .card details > summary { display: none; }
    details::details-content { content-visibility: visible; display: block; }
    .card .hl { margin: .5mm 0; font-size: 1rem; }
    .methods { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0 6mm; }
    .method { padding: 2mm 0; }
    .method h3 { margin: 1mm 0; font-size: 1.15rem; }
    .skill { grid-template-columns: 11rem minmax(0, 1fr); gap: 1rem; padding: 1.25mm 0; }
    .tl { padding-left: 0; }
    .timeline li { display: grid; grid-template-columns: 8rem minmax(0, 1fr); gap: 1rem; padding-bottom: 3mm; }
    .timeline h3 { font-size: 1.15rem; }
    .more { display: block; }
    .more li { padding: .75mm 0 .75mm 1.25rem; border: 0; }
    .more li::before { top: .75mm; line-height: 1.45; }
    .contact { padding: 4mm 0 0; break-inside: avoid; }
    .contact-title { max-width: none; margin-bottom: 1mm; font-size: 1.65rem; letter-spacing: -.01em; }
    .contact-text { margin-bottom: 1mm; font-size: 1rem; }
    .contact-links { margin-top: 0; }
    .contact-links a { min-height: 0; }
    .site-footer { padding: 2mm 0 0; border: 0; }
    .case, .card, .method, .timeline li, .skill, .stat, .more li { break-inside: avoid; page-break-inside: avoid; }
    h2, h3, .meta, .case-top, .card-top { break-after: avoid; page-break-after: avoid; }
    p, li { orphans: 3; widows: 3; }
  }
"""

HEAD_JS = ("(function(r){r.classList.add('js');try{if(localStorage.getItem('motion')==='paused')"
           "r.classList.add('motion-paused')}catch(e){}})(document.documentElement);")

SITE_JS = r"""
(function () {
  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)');
  var hasIO = 'IntersectionObserver' in window;
  var viewTL = !!(window.CSS && CSS.supports && CSS.supports('(animation-timeline: view()) and (animation-range: 0% 100%)'));
  function paused() { return root.classList.contains('motion-paused'); }
  function still() { return reduce.matches || paused(); }
  function each(sel, fn) { Array.prototype.forEach.call(document.querySelectorAll(sel), fn); }
  function onReduce(fn) { if (reduce.addEventListener) reduce.addEventListener('change', fn); else if (reduce.addListener) reduce.addListener(fn); }

  // Global pause (WCAG 2.2.2): remembered, keyboard operable, label toggles.
  var toggle = document.getElementById('motion-toggle');
  if (toggle) {
    var label = toggle.querySelector('.pause-label');
    var sync = function () {
      label.textContent = toggle.getAttribute(paused() ? 'data-resume' : 'data-pause');
      toggle.classList.toggle('is-paused', paused());
    };
    sync();
    toggle.hidden = false;
    toggle.addEventListener('click', function () {
      var on = !paused();
      root.classList.toggle('motion-paused', on);
      try { localStorage.setItem('motion', on ? 'paused' : 'running'); } catch (e) {}
      sync();
      document.dispatchEvent(new CustomEvent('motionchange'));
    });
  }

  // Mobile menu: disclosure button.
  var header = document.getElementById('site-header');
  var menu = document.getElementById('menu-toggle');
  var nav = document.getElementById('site-nav');
  if (header && menu && nav) {
    var setMenu = function (open, refocus) {
      header.classList.toggle('menu-open', open);
      menu.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (!open && refocus) menu.focus();
    };
    var isOpen = function () { return menu.getAttribute('aria-expanded') === 'true'; };
    menu.hidden = false;
    menu.addEventListener('click', function () { setMenu(!isOpen()); });
    nav.addEventListener('click', function (ev) { if (ev.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape' && isOpen()) setMenu(false, true); });
    document.addEventListener('click', function (ev) { if (isOpen() && !header.contains(ev.target)) setMenu(false); });
  }

  // Highlight the section in view.
  if (hasIO && nav) {
    var links = {};
    each('#site-nav a[href^="#"]', function (a) { links[a.getAttribute('href').slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        Object.keys(links).forEach(function (id) { links[id].classList.toggle('is-active', id === en.target.id); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    each('main > section[id]', function (s) { spy.observe(s); });
  }

  // Reveal fallback where view() timelines are missing; always ends visible.
  var revealSel = '.reveal, .media-clip, .tl, .timeline li';
  function showAll() { each(revealSel, function (el) { el.classList.add('is-in'); }); }
  if (!viewTL) {
    if (hasIO) {
      var rio = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('is-in'); rio.unobserve(en.target); } });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.04 });
      each(revealSel, function (el) { rio.observe(el); });
    } else showAll();
  }

  // Covers animate only while visible.
  if (hasIO) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { en.target.classList.toggle('is-inview', en.isIntersecting); });
    }, { rootMargin: '80px 0px' });
    each('.cover-host', function (el) { cio.observe(el); });
  } else each('.cover-host', function (el) { el.classList.add('is-inview'); });

  // Count-up of the stats (the final value stays in the DOM for assistive tech).
  var counters = [];
  each('.tally[data-value]', function (el) {
    var m = el.getAttribute('data-value').match(/^([^\d]*)([\d,.]+)(.*)$/);
    if (!m) return;
    var digits = m[2].replace(/,/g, '');
    counters.push({ el: el, pre: m[1], n: parseFloat(digits), dec: (digits.split('.')[1] || '').length, comma: m[2].indexOf(',') >= 0, post: m[3], done: false });
  });
  function fmt(c, v) {
    var s = v.toFixed(c.dec);
    if (c.comma) s = s.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return c.pre + s + c.post;
  }
  function finish(c) { c.done = true; c.el.textContent = c.el.getAttribute('data-value'); }
  function count(c) {
    if (c.done) return;
    c.done = true;
    if (still()) { finish(c); return; }
    var start = null;
    var tick = function (now) {
      if (start === null) start = now;
      var k = Math.min(1, (now - start) / 1400);
      c.el.textContent = fmt(c, c.n * (1 - Math.pow(1 - k, 3)));
      if (k < 1 && !still()) requestAnimationFrame(tick); else finish(c);
    };
    requestAnimationFrame(tick);
  }
  if (counters.length && hasIO && !still()) {
    counters.forEach(function (c) { c.el.textContent = fmt(c, 0); });
    var sio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        counters.forEach(function (c) { if (c.el === en.target) count(c); });
        sio.unobserve(en.target);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (c) { sio.observe(c.el); });
    var settle = function () { if (still()) counters.forEach(finish); };
    document.addEventListener('motionchange', settle);
    onReduce(settle);
  }

  // Magnetic buttons and card spotlight: fine pointers only.
  if (fine.matches) {
    each('.magnetic', function (el) {
      el.addEventListener('pointermove', function (ev) {
        if (still()) return;
        var r = el.getBoundingClientRect();
        var x = (ev.clientX - r.left) / r.width - 0.5, y = (ev.clientY - r.top) / r.height - 0.5;
        el.style.transform = 'translate(' + (x * 12).toFixed(1) + 'px,' + (y * 8).toFixed(1) + 'px)';
      });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
    each('.card', function (el) {
      el.addEventListener('pointermove', function (ev) {
        var r = el.getBoundingClientRect();
        el.style.setProperty('--mx', (ev.clientX - r.left).toFixed(0) + 'px');
        el.style.setProperty('--my', (ev.clientY - r.top).toFixed(0) + 'px');
      });
    });
  }

  // Area filter (progressive: every project is visible without JS).
  var group = document.getElementById('filters');
  if (group) {
    var chips = Array.prototype.slice.call(group.querySelectorAll('button[data-filter]'));
    var items = Array.prototype.slice.call(document.querySelectorAll('#index li[data-area]'));
    var countEl = document.getElementById('count');
    var empty = document.getElementById('empty');
    var emptyArea = document.getElementById('empty-area');
    var apply = function (chip) {
      var area = chip.getAttribute('data-filter');
      var shown = 0;
      chips.forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
      items.forEach(function (item) {
        var match = area === 'all' || item.getAttribute('data-area') === area;
        item.hidden = !match;
        if (match) shown++;
      });
      var noun = shown === 1 ? countEl.getAttribute('data-one') : countEl.getAttribute('data-many');
      countEl.textContent = shown + ' ' + noun + ' · ' + chip.getAttribute('data-label');
      emptyArea.textContent = chip.getAttribute('data-label');
      empty.hidden = shown !== 0;
    };
    var choose = function (chip, then) {
      if (document.startViewTransition && !still()) {
        var vt = document.startViewTransition(function () { apply(chip); });
        if (then) vt.finished.then(then, then);
      } else { apply(chip); if (then) then(); }
    };
    chips.forEach(function (chip) { chip.addEventListener('click', function () { choose(chip); }); });
    document.getElementById('reset').addEventListener('click', function () { choose(chips[0], function () { chips[0].focus(); }); });
    group.hidden = false;
    countEl.hidden = false;
  }

  // Print: open every detail and settle every animated state.
  window.addEventListener('beforeprint', function () {
    each('.card details', function (d) { if (!d.open) { d.open = true; d.setAttribute('data-print-open', ''); } });
    counters.forEach(finish);
    showAll();
  });
  window.addEventListener('afterprint', function () {
    each('details[data-print-open]', function (d) { d.open = false; d.removeAttribute('data-print-open'); });
  });

  // Hero flow field: drifting contour lines over the artwork.
  var canvas = document.getElementById('flow');
  var ctx = canvas && canvas.getContext && canvas.getContext('2d');
  if (!ctx) return;
  var hero = canvas.closest('.hero') || canvas.parentNode;
  var W = 0, H = 0, parts = [], raf = 0, last = 0, clock = 0, onScreen = true, ptr = null;
  var HUES = ['57,208,200', '126,224,195', '57,208,200'], SPARK = '255,138,76';
  function spawn(p) {
    p.x = Math.random() * W; p.y = Math.random() * H; p.age = 0; p.life = 90 + Math.random() * 260;
    p.spark = Math.random() < 0.012;
    p.c = p.spark ? SPARK : HUES[(Math.random() * 3) | 0];
    p.v = 0.45 + Math.random() * 0.8; p.w = p.spark ? 1.6 : (Math.random() < 0.6 ? 0.7 : 1.2);
    return p;
  }
  function angle(x, y) {
    return Math.sin(x * 0.0018 + clock * 0.00012) * 1.8 + Math.cos(y * 0.0023 - clock * 0.0001) * 1.5 + Math.sin((x - y) * 0.0009 + clock * 0.00006) * 1.1;
  }
  function resize() {
    var r = hero.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = Math.max(1, Math.round(r.width)); H = Math.max(1, Math.round(r.height));
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var n = Math.min(420, Math.round(W * H / 2800));
    parts = [];
    for (var i = 0; i < n; i++) { var p = spawn({}); p.age = Math.random() * p.life; parts.push(p); }
  }
  function step(dt, fade, gain) {
    if (fade) {
      ctx.globalCompositeOperation = 'destination-out';
      ctx.fillStyle = 'rgba(0,0,0,' + Math.min(0.3, 0.05 * dt).toFixed(3) + ')';
      ctx.fillRect(0, 0, W, H);
    }
    // Segments are batched per color, alpha step and width: a few strokes per frame.
    var batches = {};
    for (var i = 0; i < parts.length; i++) {
      var p = parts[i], a = angle(p.x, p.y), vx = Math.cos(a), vy = Math.sin(a);
      if (ptr) {
        var dx = p.x - ptr.x, dy = p.y - ptr.y, d = Math.sqrt(dx * dx + dy * dy);
        if (d < 180 && d > 0.5) { var f = (1 - d / 180) * 1.2; vx -= dy / d * f; vy += dx / d * f; }
      }
      var nx = p.x + vx * p.v * dt * 1.4, ny = p.y + vy * p.v * dt * 1.4;
      var level = Math.round(Math.sin(Math.PI * Math.min(1, p.age / p.life)) * 6);
      if (level > 0) {
        var key = p.c + '|' + level + '|' + p.w;
        (batches[key] || (batches[key] = [])).push(p.x, p.y, nx, ny);
      }
      p.x = nx; p.y = ny; p.age += dt;
      if (p.age > p.life || nx < -10 || ny < -10 || nx > W + 10 || ny > H + 10) spawn(p);
    }
    ctx.globalCompositeOperation = 'lighter';
    ctx.lineCap = 'round';
    Object.keys(batches).forEach(function (key) {
      var k = key.split('|'), seg = batches[key], spark = k[0] === SPARK;
      ctx.strokeStyle = 'rgba(' + k[0] + ',' + (k[1] / 6 * (spark ? 0.95 : 0.5) * gain).toFixed(3) + ')';
      ctx.lineWidth = +k[2];
      ctx.beginPath();
      for (var j = 0; j < seg.length; j += 4) { ctx.moveTo(seg[j], seg[j + 1]); ctx.lineTo(seg[j + 2], seg[j + 3]); }
      ctx.stroke();
    });
    ctx.globalCompositeOperation = 'source-over';
  }
  function stillFrame() {
    ctx.clearRect(0, 0, W, H);
    clock = 4000;
    for (var s = 0; s < 60; s++) step(1, false, 0.45);
  }
  function running() { return onScreen && !document.hidden && !still(); }
  function frame(now) {
    raf = 0;
    if (!running()) return;
    raf = requestAnimationFrame(frame);
    if (W < 720 && last && now - last < 32) return;  // ~30 fps on small screens
    var dt = last ? Math.min(3, (now - last) / 16.67) : 1;
    last = now; clock += dt * 16.67;
    step(dt, true, 1);
  }
  function update() {
    if (running()) { if (!raf) { last = 0; raf = requestAnimationFrame(frame); } return; }
    if (raf) { cancelAnimationFrame(raf); raf = 0; }
    if (reduce.matches) stillFrame();
  }
  resize();
  if (still()) stillFrame();
  update();
  var timer = 0;
  window.addEventListener('resize', function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      var r = hero.getBoundingClientRect();
      if (Math.round(r.width) === W && Math.abs(Math.round(r.height) - H) < 160) return;
      resize();
      if (!running()) stillFrame();
    }, 160);
  });
  if (hasIO) new IntersectionObserver(function (en) { onScreen = en[0].isIntersecting; update(); }).observe(hero);
  document.addEventListener('visibilitychange', update);
  document.addEventListener('motionchange', update);
  onReduce(update);
  if (fine.matches) {
    hero.addEventListener('pointermove', function (ev) { var r = hero.getBoundingClientRect(); ptr = { x: ev.clientX - r.left, y: ev.clientY - r.top }; });
    hero.addEventListener('pointerleave', function () { ptr = null; });
  }
})();
"""

ICONS = {
    "pause": '<svg class="i-pause" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M5 3v10M11 3v10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "play": '<svg class="i-play" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M5 3l8 5-8 5z" fill="currentColor"/></svg>',
    "menu": '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    "pin": '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M8 15s5-4.6 5-8.5A5 5 0 0 0 3 6.5C3 10.4 8 15 8 15z" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="6.5" r="1.8" fill="currentColor"/></svg>',
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


def render_site(data, lang, manifest):
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
      <button type="button" class="icon-btn pause" id="motion-toggle" data-pause="{e(ui["pause"])}" data-resume="{e(ui["resume"])}" hidden>{ICONS["pause"]}{ICONS["play"]}<span class="pause-label">{e(ui["pause"])}</span></button>
      <button type="button" class="icon-btn menu" id="menu-toggle" aria-expanded="false" aria-controls="site-nav" hidden>{ICONS["menu"]}<span class="sr-only">{e(ui["menu"])}</span></button>
    </div>
  </div>
  <div class="progress" aria-hidden="true"></div>
</header>"""

    # Hero: the picture is the LCP element; the canvas draws over it.
    wide, tall = manifest["hero"], manifest["hero-mobile"]
    big = variants(wide)[-1]
    big_tall = variants(tall)[0]
    words = " ".join(f'<span class="w" style="--i:{i}">{e(word)}</span>' for i, word in enumerate(meta["name"].split()))
    hero = f"""<section id="top" class="hero" aria-labelledby="hero-name">
  <div class="hero-media" aria-hidden="true">
    <picture class="hero-art">
      <source media="(orientation: portrait) and (max-width: 64rem)" srcset="{srcset(tall, prefix)}" sizes="100vw" width="{big_tall["width"]}" height="{big_tall["height"]}">
      <source srcset="{srcset(wide, prefix)}" sizes="100vw" width="{big["width"]}" height="{big["height"]}">
      <img src="{prefix}assets/img/{big["file"]}" width="{big["width"]}" height="{big["height"]}" alt="" fetchpriority="high">
    </picture>
    <canvas id="flow" class="flow" aria-hidden="true"></canvas>
    <div class="hero-scrim"></div>
  </div>
  <div class="hero-inner wrap">
    <div class="hero-copy">
      <p class="kicker">{e(ui["hero_kicker"].format(date=meta["updated"]))}</p>
      <h1 class="name" id="hero-name">{words}</h1>
      <p class="headline">{e(t(meta["headline"], lang))}</p>
      <p class="lede">{e(lede)}</p>
      <p class="loc">{ICONS["pin"]}<span class="sr-only">{e(ui["location"])}:</span> {e(t(meta["location"], lang))}</p>
      <p class="print-only">{e(email)} · {e(github_label(data))}</p>
      <div class="cta">
        <a class="btn primary magnetic" href="mailto:{e(email)}">{e(ui["email_cta"])}</a>
        <a class="btn ghost magnetic" href="{cv_href}">{e(ui["cv_pdf"])}</a>
        <a class="btn ghost magnetic" href="{pdf_href}">{e(ui["portfolio_pdf"])}</a>
      </div>
    </div>
  </div>
  <a class="cue" href="#about"><span class="cue-line" aria-hidden="true"></span>{e(ui["explore"])}</a>
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
        rows.append(f'<div class="mq-row{" rev" if k else ""}"><ul class="plain mq-track">{items}</ul>'
                    f'<ul class="plain mq-track" aria-hidden="true">{items}</ul></div>')
    marquee_dur = max(40, round(len(terms) * 1.6))

    cases = []
    for project in projects:
        if not project["featured"]:
            continue
        pid = e(project["id"])
        n = num(numbers[project["id"]])
        meta_line = " · ".join(e(t(project[k], lang)) for k in ("context", "role", "period"))
        art = manifest.get(f"case-{project['id']}")
        image = ""
        if art:
            large = variants(art)[-1]
            image = (f'<div class="zoom"><img src="{prefix}assets/img/{large["file"]}" srcset="{srcset(art, prefix)}" '
                     f'sizes="(min-width: 60rem) 40rem, 100vw" width="{large["width"]}" height="{large["height"]}" '
                     'alt="" loading="lazy" decoding="async"></div>')
        cases.append(f"""<article class="case" id="case-{pid}" aria-labelledby="case-{pid}-h" style="{area_style(project["area"])}">
  <div class="case-text reveal">
    <p class="case-top"><span class="case-num" aria-hidden="true">{n}</span><span class="tag">{e(areas[project["area"]])}</span></p>
    <h3 id="case-{pid}-h">{e(t(project["title"], lang))}</h3>
    <p class="meta">{meta_line}</p>
    <p class="summary">{e(t(project["summary"], lang))}</p>
    {highlights(project)}
    <p class="stack-label">{e(ui["stack"])}</p>{chips(project["stack"])}
  </div>
  <div class="case-media" aria-hidden="true">
    <div class="cover-host media-clip">{image}{unique_cover(project, "case")}<span class="duo"></span><span class="fig">Fig. {n}</span></div>
  </div>
</article>""")

    counts = {area_id: sum(1 for p in projects if p["area"] == area_id) for area_id in areas}
    filter_chips = [f'<button type="button" class="chip" data-filter="all" data-label="{e(ui["filter_all"])}" aria-pressed="true">{e(ui["filter_all"])} <span class="n">{len(projects)}</span></button>']
    for area_id, title in areas.items():
        filter_chips.append(f'<button type="button" class="chip" data-filter="{e(area_id)}" data-label="{e(title)}" aria-pressed="false">{e(title)} <span class="n">{counts[area_id]}</span></button>')

    cards = []
    for i, project in enumerate(projects):
        pid = e(project["id"])
        n = num(numbers[project["id"]])
        title = e(t(project["title"], lang))
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
            f'<details><summary>{e(ui["details"])}</summary>{highlights(project)}'
            f'<p class="stack-label">{e(ui["stack"])}</p>{chips(project["stack"])}</details>{go}</div></li>'
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
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="{PALETTE["bg"]}">
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
<section id="about" class="sec glow" aria-labelledby="about-h">
  <div class="wrap">
    <div class="sec-head reveal">{kicker(1)}<h2 class="sec-title" id="about-h">{e(ui["about"])}</h2></div>
    <div class="about-grid">
      <p class="about-text reveal">{e(about_rest or about)}</p>
      <dl class="facts reveal">{facts}</dl>
    </div>
  </div>
</section>
<section id="numbers" class="sec" aria-labelledby="numbers-h">
  <div class="wrap">
    <div class="sec-head reveal">{kicker(2)}<h2 class="sec-title" id="numbers-h">{e(ui["numbers"])}</h2></div>
    <ul class="plain stats">{stats}</ul>
  </div>
</section>
<section id="stack" class="stack-sec" aria-labelledby="stack-h">
  <div class="wrap sec-head">{kicker(3)}<h2 class="sec-title" id="stack-h">{e(ui["stack_title"])}</h2><p class="note">{e(ui["stack_note"])}</p></div>
  <div class="mq" style="--dur: {marquee_dur}s">{"".join(rows)}</div>
</section>
<section id="work" class="sec glow" aria-labelledby="work-h">
  <div class="wrap">
    <div class="sec-head reveal">{kicker(4)}<h2 class="sec-title" id="work-h">{e(ui["work"])}</h2><p class="note">{e(ui["work_note"])}</p></div>
    {"".join(cases)}
  </div>
</section>
<section id="projects" class="sec" aria-labelledby="projects-h">
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
<section id="methods" class="sec glow" aria-labelledby="methods-h">
  <div class="wrap">
    <div class="sec-head reveal">{kicker(6)}<h2 class="sec-title" id="methods-h">{e(ui["methods"])}</h2></div>
    <ol class="plain methods">{methods}</ol>
  </div>
</section>
<section id="skills" class="sec" aria-labelledby="skills-h">
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
<section id="more" class="sec" aria-labelledby="more-h">
  <div class="wrap">
    <div class="sec-head reveal">{kicker(9)}<h2 class="sec-title" id="more-h">{e(ui["more"])}</h2></div>
    <ul class="plain more">{more}</ul>
  </div>
</section>
<section id="contact" class="sec contact" aria-labelledby="contact-h">
  <div class="wrap">
    <p class="kicker">{num(10)} · {e(ui["contact"])}</p>
    <h2 class="contact-title" id="contact-h">{e(ui["contact_big"])}</h2>
    <p class="contact-text">{e(ui["contact_text"])} {e(t(meta["location"], lang))}.</p>
    <a class="glow-btn" href="mailto:{e(email)}"><span>{e(ui["email_cta"])} · {e(email)}</span></a>
    <ul class="plain contact-links">
      <li><a href="mailto:{e(email)}">{e(email)}</a></li>
      <li><a href="{e(github_url(data))}">{e(github_label(data))}</a></li>
      <li><a href="{cv_href}">{e(ui["cv_pdf"])}</a></li>
      <li><a href="{pdf_href}">{e(ui["portfolio_pdf"])}</a></li>
    </ul>
  </div>
</section>
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>{e(meta["name"])} · {e(ui["updated"].format(date=meta["updated"]))}</p>
    <p>{e(ui["made"])}</p>
    <a class="top" href="#top">{e(ui["top"])} ↑</a>
  </div>
</footer>
<script>{SITE_JS}</script>
</body>
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

def render_all(data, manifest):
    files = {}
    for lang in LANGS:
        files[PAGE_PATHS[lang]] = render_site(data, lang, manifest)
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
    args = parser.parse_args(argv)

    try:
        data = json.loads(args.content.read_text(encoding="utf-8"))
        validate(data)
        check_references(data)
        try:
            manifest = load_manifest()
        except (OSError, json.JSONDecodeError) as exc:
            raise ContentError(f"cannot read {MANIFEST}: {exc}") from exc
        files = render_all(data, manifest)
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
    print(f"wrote {args.out / 'assets' / 'img'}")

    if args.pdf:
        error = build_pdfs(args.out)
        if error:
            print(f"pdf error: {error}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
