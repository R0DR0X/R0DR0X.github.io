#!/usr/bin/env python3
"""Render the bilingual portfolio website, CV print sources and PDFs.

One content source (content/portfolio.json) renders:
  site/index.html, site/en/index.html  portfolio website (es, en)
  site/cv/es.html, site/cv/en.html     CV print sources
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

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTENT = ROOT / "content" / "portfolio.json"
DEFAULT_OUT = ROOT / "site"
LANGS = ("es", "en")
GITHUB_BASE = "https://github.com/"
CHROME_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")

PDF_NAMES = {
    "cv": {"es": "Ivan-Rodrigo-Pianto-Anton-CV-ES.pdf", "en": "Ivan-Rodrigo-Pianto-Anton-CV-EN.pdf"},
    "portfolio": {"es": "Ivan-Rodrigo-Pianto-Anton-Portafolio-ES.pdf", "en": "Ivan-Rodrigo-Pianto-Anton-Portfolio-EN.pdf"},
}
PAGE_PATHS = {"es": "index.html", "en": "en/index.html"}
CV_PATHS = {"es": "cv/es.html", "en": "cv/en.html"}

# Key stack shown beside the name; every term must exist in content skills.
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

# Light palette (warm paper, ink, terracotta). tools/contrast.py checks PAIRS.
PALETTE = {
    "paper": "#f6f3ee",
    "rail": "#ede6da",
    "hover": "#e6dfd2",
    "ink": "#1d1b18",
    "muted": "#5c564d",
    "rule": "#d9d2c5",
    "control": "#7a705f",
    "accent": "#9a3b1b",
    "accent-strong": "#7d2f15",
    "on-accent": "#ffffff",
}
# (foreground, background, minimum ratio, role)
PAIRS = [
    ("ink", "paper", 4.5, "body text"),
    ("muted", "paper", 4.5, "secondary text"),
    ("accent", "paper", 4.5, "numbers, links, periods"),
    ("on-accent", "accent", 4.5, "primary button, pressed filter"),
    ("on-accent", "accent-strong", 4.5, "primary button hover"),
    ("ink", "rail", 4.5, "sidebar text"),
    ("muted", "rail", 4.5, "sidebar secondary text"),
    ("accent", "rail", 4.5, "sidebar links"),
    ("ink", "hover", 4.5, "hovered control text"),
    ("paper", "ink", 4.5, "skip link"),
    ("control", "paper", 3.0, "control borders"),
    ("control", "rail", 3.0, "sidebar control borders"),
    ("ink", "paper", 3.0, "focus outline"),
    ("accent", "paper", 3.0, "pressed filter boundary (focus ring is offset onto paper)"),
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
        "key_stack": "Stack principal",
        "languages": "Idiomas",
        "education": "Formación",
        "about": "Perfil",
        "numbers": "En cifras",
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
        "stack": "Stack",
        "methods": "Cómo trabajo",
        "skills": "Habilidades",
        "experience": "Experiencia",
        "current": "(actual)",
        "more": "Además",
        "contact": "Contacto",
        "contact_text": "¿Tienes una operación que necesita software? Escríbeme y cuéntame qué quieres resolver.",
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
        "key_stack": "Key stack",
        "languages": "Languages",
        "education": "Education",
        "about": "About",
        "numbers": "By the numbers",
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
        "stack": "Stack",
        "methods": "How I work",
        "skills": "Skills",
        "experience": "Experience",
        "current": "(current)",
        "more": "Also",
        "contact": "Contact",
        "contact_text": "Do you run an operation that needs software? Email me and tell me what you want to solve.",
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


# ---------------------------------------------------------------------- CSS

def css_vars():
    return "\n".join(f"    --{name}: {value};" for name, value in PALETTE.items())


SITE_CSS = """
  :root {
%VARS%
    --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, ui-serif, serif;
    --sans: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --rail-w: clamp(300px, 27vw, 360px);
  }
  * { box-sizing: border-box; }
  [hidden] { display: none !important; }
  html { scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }
  @media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    *, *::before, *::after { transition: none !important; animation: none !important; }
  }
  body { margin: 0; background: var(--paper); color: var(--ink); font: 1.0625rem/1.6 var(--sans); overflow-wrap: break-word; }
  h1, h2, h3 { font-family: var(--serif); font-weight: 500; color: var(--ink); }
  a { color: var(--accent); text-underline-offset: 3px; }
  a:hover { color: var(--accent-strong); }
  :focus-visible { outline: 3px solid var(--ink); outline-offset: 3px; border-radius: 3px; }
  main:focus { outline: none; }
  .plain { list-style: none; margin: 0; padding: 0; }
  .skip { position: absolute; left: -9999px; top: 8px; z-index: 10; display: inline-flex; align-items: center; min-height: 44px; padding: 0 1rem; background: var(--ink); color: var(--paper); font-weight: 600; }
  .skip:focus { left: 8px; color: var(--paper); }
  .sr-only { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }
  .label { margin: 0 0 .375rem; font: 600 .75rem/1.4 var(--sans); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
  .inline { list-style: none; margin: 0; padding: 0; }
  .inline li { display: inline; }
  .inline li:not(:last-child)::after { content: " · "; color: var(--muted); }

  /* Identity block: top on narrow screens, sticky sidebar on wide ones. */
  .rail { background: var(--rail); border-bottom: 1px solid var(--rule); padding: 1.25rem 1.25rem 1.75rem; }
  .rail-top { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: .5rem 1rem; }
  .stamp { margin: 0; font-size: .8125rem; color: var(--muted); }
  .lang ul { display: flex; gap: .25rem; }
  .lang a { display: inline-flex; align-items: center; min-height: 44px; padding: 0 .75rem; border: 1px solid var(--control); border-radius: 999px; color: var(--ink); font-size: .875rem; font-weight: 600; text-decoration: none; }
  .lang a:hover { background: var(--hover); }
  .lang a[aria-current="page"] { background: var(--ink); border-color: var(--ink); color: var(--paper); }
  .rail h1 { margin: 1.25rem 0 .5rem; font-size: clamp(1.875rem, 6vw, 2.375rem); line-height: 1.1; letter-spacing: -.01em; }
  .headline { margin: 0 0 .75rem; font-size: 1rem; line-height: 1.5; }
  .facts { font-size: .9375rem; color: var(--muted); }
  .facts li { display: flex; align-items: center; min-height: 32px; }
  .facts a { display: inline-flex; align-items: center; min-height: 44px; }
  .actions { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: 1rem; }
  .btn { display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: .5rem 1.125rem; border-radius: 999px; font: 600 .9375rem/1.25 var(--sans); text-decoration: none; text-align: center; }
  .btn.primary { background: var(--accent); color: var(--on-accent); }
  .btn.primary:hover { background: var(--accent-strong); color: var(--on-accent); }
  .btn.secondary { border: 1px solid var(--control); color: var(--ink); background: transparent; }
  .btn.secondary:hover { background: var(--hover); color: var(--ink); }
  .toc { margin-top: 1.25rem; padding-top: .5rem; border-top: 1px solid var(--rule); }
  .toc ul { display: flex; flex-wrap: wrap; gap: 0 .25rem; }
  .toc a { display: inline-flex; align-items: center; min-height: 44px; padding: 0 .5rem; color: var(--ink); font-size: .9375rem; text-decoration: none; }
  .toc a:hover { color: var(--accent-strong); text-decoration: underline; }
  .dossier { display: grid; gap: 1.25rem; margin-top: 1.25rem; padding-top: 1.25rem; border-top: 1px solid var(--rule); font-size: .9375rem; }
  .dossier p, .dossier ul { margin: 0; }
  .dossier .stacked li + li { margin-top: .25rem; }

  /* Main column */
  main { padding: 0 1.25rem; }
  main > section { padding: 2.75rem 0; border-top: 1px solid var(--rule); }
  main > section:first-child { border-top: 0; }
  h2 { font-size: clamp(1.625rem, 4.5vw, 2.125rem); line-height: 1.2; margin: 0 0 .5rem; }
  .note { margin: 0 0 1.75rem; color: var(--muted); max-width: 64ch; }
  .about { margin: .75rem 0 0; font-family: var(--serif); font-size: 1.25rem; line-height: 1.55; max-width: 60ch; }

  .stats { display: grid; grid-template-columns: 1fr; gap: 1px; margin-top: 1rem; background: var(--rule); border: 1px solid var(--rule); }
  .stats li { display: flex; flex-direction: column; gap: .5rem; padding: 1.25rem 1.25rem 1.375rem; background: var(--paper); }
  .stats .v { white-space: nowrap; overflow-wrap: normal; font: 600 clamp(2.25rem, 9vw, 3.25rem)/1 var(--sans); font-variant-numeric: tabular-nums lining-nums; letter-spacing: -.03em; color: var(--ink); }
  .stats .l { font-size: .9375rem; line-height: 1.45; color: var(--muted); }

  .case { display: grid; grid-template-columns: 1fr; gap: .25rem 2rem; padding: 2rem 0; border-top: 1px solid var(--rule); }
  .case:first-of-type { border-top: 0; padding-top: .5rem; }
  .num { font-family: var(--serif); font-size: 1.75rem; line-height: 1.2; color: var(--accent); font-variant-numeric: tabular-nums lining-nums; }
  .case h3 { margin: 0 0 .5rem; font-size: clamp(1.375rem, 4vw, 1.75rem); line-height: 1.2; }
  .meta { margin: 0 0 1rem; font-size: .9375rem; color: var(--muted); }
  .case .summary { margin: 0 0 1rem; max-width: 66ch; }
  .case ul.hl { margin: 0 0 1rem; padding-left: 1.25rem; max-width: 68ch; }
  .hl li { margin-bottom: .375rem; }
  .hl li::marker { color: var(--accent); }
  .stack { margin: 0; font-size: .875rem; color: var(--muted); max-width: 80ch; }
  .stack b { font: 600 .75rem var(--sans); letter-spacing: .08em; text-transform: uppercase; color: var(--ink); margin-right: .5rem; }

  .filters { display: flex; flex-wrap: wrap; gap: .5rem; margin-bottom: .75rem; }
  .chip { display: inline-flex; align-items: center; gap: .5rem; min-height: 44px; padding: 0 1rem; border: 1px solid var(--control); border-radius: 999px; background: transparent; color: var(--ink); font: .9375rem/1.2 var(--sans); cursor: pointer; }
  .chip .n { color: var(--muted); font-variant-numeric: tabular-nums; }
  .chip:hover { background: var(--hover); }
  .chip[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: var(--on-accent); font-weight: 600; }
  .chip[aria-pressed="true"] .n { color: var(--on-accent); }
  .count { margin: 0 0 1rem; font-size: .9375rem; color: var(--muted); }
  .empty { margin-bottom: 1rem; padding: 1.5rem; border: 1px dashed var(--control); }
  .empty p { margin: 0 0 1rem; }
  .empty .btn { border: 1px solid var(--control); background: transparent; color: var(--ink); cursor: pointer; }
  .index li.item { display: grid; grid-template-columns: 2.75rem minmax(0, 1fr); gap: .75rem; padding: 1rem 0; border-top: 1px solid var(--rule); }
  .index .n { font-family: var(--serif); font-size: 1.25rem; line-height: 1.4; color: var(--accent); font-variant-numeric: tabular-nums lining-nums; }
  .index h3 { margin: 0; font-family: var(--sans); font-size: 1.0625rem; font-weight: 650; line-height: 1.4; }
  .index h3 a { color: var(--ink); }
  .index h3 a:hover { color: var(--accent-strong); }
  .index .meta { margin: .125rem 0 0; font-size: .875rem; }
  .index .summary { margin: .5rem 0 0; font-size: .9375rem; max-width: 70ch; }
  .index ul.hl { margin: .375rem 0 0; padding-left: 1.125rem; font-size: .9375rem; max-width: 70ch; }
  .index .stack { margin-top: .375rem; }
  .index .go { display: inline-flex; align-items: center; min-height: 44px; font-size: .875rem; }

  .methods { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 16rem), 1fr)); gap: 1.5rem 2.5rem; margin-top: 1rem; }
  .methods li { border-top: 1px solid var(--rule); padding-top: .75rem; }
  .methods h3 { margin: 0 0 .375rem; font-size: 1.3125rem; line-height: 1.3; }
  .methods p { margin: 0; color: var(--muted); }

  .skills { margin: 1rem 0 0; }
  .skills > div { padding: .75rem 0; border-top: 1px solid var(--rule); }
  .skills dt { font-weight: 600; }
  .skills dd { margin: .125rem 0 0; color: var(--muted); }

  .timeline { margin-top: 1rem; }
  .timeline li { position: relative; padding: 0 0 1.75rem 1.75rem; }
  .timeline li::before { content: ""; position: absolute; left: 6px; top: .6rem; bottom: -.4rem; width: 2px; background: var(--rule); }
  .timeline li:last-child { padding-bottom: 0; }
  .timeline li:last-child::before { display: none; }
  .timeline .dot { position: absolute; left: 0; top: .35rem; width: 14px; height: 14px; border-radius: 50%; border: 2px solid var(--accent); background: var(--paper); }
  .timeline .dot.now { background: var(--accent); }
  .timeline .when { margin: 0; font-size: .9375rem; font-weight: 600; color: var(--accent); font-variant-numeric: tabular-nums; }
  .timeline h3 { margin: .125rem 0 0; font-size: 1.25rem; line-height: 1.3; }
  .timeline .org { margin: 0; color: var(--muted); }
  .timeline .body { margin: .375rem 0 0; max-width: 66ch; }

  .more { margin: 1rem 0 0; padding-left: 1.25rem; max-width: 70ch; }
  .more li { margin-bottom: .375rem; }
  .more li::marker { color: var(--accent); }

  footer.contact { padding: 2.75rem 1.25rem 3.5rem; border-top: 1px solid var(--rule); }
  footer.contact p { margin: 0 0 1.25rem; color: var(--muted); max-width: 60ch; }
  footer.contact .btn { overflow-wrap: anywhere; }

  @media (min-width: 480px) {
    .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  }

  @media (min-width: 720px) {
    .rail { padding: 1.75rem 2.5rem 2rem; }
    .dossier { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.5rem; }
    main, footer.contact { padding-left: 2.5rem; padding-right: 2.5rem; }
    .case { grid-template-columns: 4rem minmax(0, 1fr); }
    .timeline li { display: grid; grid-template-columns: 9rem minmax(0, 1fr); column-gap: 1.5rem; padding-left: 2rem; }
    .skills > div { display: grid; grid-template-columns: 13rem minmax(0, 1fr); gap: 1.5rem; }
    .skills dd { margin: 0; }
  }

  @media (min-width: 1080px) {
    .page { display: grid; grid-template-columns: var(--rail-w) minmax(0, 1fr); grid-template-rows: auto 1fr; }
    .rail { grid-column: 1; grid-row: 1 / span 2; position: sticky; top: 0; align-self: start; height: 100vh; overflow-y: auto; border-bottom: 0; border-right: 1px solid var(--rule); padding: 2rem 2rem 2.5rem; scrollbar-width: thin; }
    .dossier { grid-template-columns: 1fr; }
    main { grid-column: 2; padding: 1rem 4rem 0; max-width: 64rem; }
    footer.contact { grid-column: 2; padding: 2.75rem 4rem 4rem; max-width: 64rem; }
  }

  @media print {
    @page { size: A4; margin: 13mm 14mm 14mm; }
    html { font-size: 8.75pt; }
    body { background: #ffffff; color: #000000; line-height: 1.45; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .skip, .lang, .actions, .toc, #filters, .count, .empty, .go { display: none !important; }
    .index li.item[hidden] { display: grid !important; }
    .page { display: block; }
    main *, .rail *, footer.contact * { max-width: none !important; }
    .rail { position: static; height: auto; overflow: visible; background: none; border: 0; border-bottom: 1px solid var(--rule); padding: 0 0 3mm; }
    .rail-top { justify-content: flex-start; }
    .rail h1 { margin: 1mm 0 1mm; font-size: 2.4rem; }
    .headline { margin-bottom: 1mm; font-size: 1.1rem; }
    .facts { display: flex; flex-wrap: wrap; gap: 0 1.5em; }
    .facts li, .facts a { min-height: 0; }
    .dossier { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 5mm; margin-top: 3mm; padding-top: 3mm; }
    main, footer.contact { padding: 0; }
    main > section { padding: 4mm 0; }
    h2 { font-size: 1.65rem; margin-bottom: 1mm; break-after: avoid; }
    .note { margin-bottom: 2mm; break-inside: avoid; }
    .about { font-size: 1.15rem; }
    .stats { grid-template-columns: repeat(4, 1fr); margin-top: 2mm; }
    .stats li { padding: .5rem .75rem; background: #ffffff; }
    .stats .v { font-size: 2rem; }
    .stats .l { font-size: .875rem; }
    .case { grid-template-columns: 2.5rem minmax(0, 1fr); gap: 0 1rem; padding: 3mm 0; }
    .case:first-of-type { padding-top: 1mm; }
    .num { font-size: 1.5rem; }
    .case h3 { margin-bottom: .5mm; font-size: 1.35rem; }
    .meta { margin-bottom: 1.5mm; }
    .case .summary { margin-bottom: 1.5mm; }
    .case ul.hl { margin-bottom: 1.5mm; }
    .hl li { margin-bottom: .5mm; }
    .case, .index li.item, .methods li, .timeline li, .skills > div, .stats li, .more li { break-inside: avoid; page-break-inside: avoid; }
    h2, h3, .meta { break-after: avoid; page-break-after: avoid; }
    .index li.item { grid-template-columns: 2.5rem minmax(0, 1fr); gap: 0 1rem; padding: 2mm 0; }
    .index .summary { margin-top: 1mm; }
    .methods { grid-template-columns: repeat(3, 1fr); gap: 3mm 6mm; margin-top: 2mm; }
    .methods h3 { font-size: 1.15rem; }
    .timeline { margin-top: 2mm; }
    .timeline li { display: grid; grid-template-columns: 8rem minmax(0, 1fr); column-gap: 1rem; padding-bottom: 3mm; }
    .skills { margin-top: 2mm; }
    .skills > div { display: grid; grid-template-columns: 11rem minmax(0, 1fr); gap: 1rem; padding: 1.25mm 0; }
    .skills dd { margin: 0; }
    footer.contact { padding-top: 4mm; break-inside: avoid; }
    p, li { orphans: 3; widows: 3; }
    a { color: inherit; text-decoration: none; }
  }
"""

FILTER_JS = """
(function () {
  var group = document.getElementById('filters');
  if (!group) return;
  var chips = Array.prototype.slice.call(group.querySelectorAll('button[data-filter]'));
  var items = Array.prototype.slice.call(document.querySelectorAll('#index li[data-area]'));
  var count = document.getElementById('count');
  var empty = document.getElementById('empty');
  var emptyArea = document.getElementById('empty-area');
  function label(chip) { return chip.getAttribute('data-label'); }
  function apply(chip) {
    var area = chip.getAttribute('data-filter');
    var shown = 0;
    chips.forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
    items.forEach(function (item) {
      var match = area === 'all' || item.getAttribute('data-area') === area;
      item.hidden = !match;
      if (match) shown++;
    });
    var noun = shown === 1 ? count.getAttribute('data-one') : count.getAttribute('data-many');
    count.textContent = shown + ' ' + noun + ' · ' + label(chip);
    emptyArea.textContent = label(chip);
    empty.hidden = shown !== 0;
  }
  chips.forEach(function (chip) { chip.addEventListener('click', function () { apply(chip); }); });
  document.getElementById('reset').addEventListener('click', function () { apply(chips[0]); chips[0].focus(); });
  group.hidden = false;
  count.hidden = false;
})();
"""


# --------------------------------------------------------------- site page

def render_site(data, lang):
    ui = UI[lang]
    meta = data["meta"]
    other = "en" if lang == "es" else "es"
    prefix = "" if lang == "es" else "../"
    other_href = "en/" if lang == "es" else "../"
    projects = data["projects"]
    areas = {area["id"]: t(area["title"], lang) for area in data["areas"]}
    numbers = {p["id"]: i + 1 for i, p in enumerate(projects)}
    email = meta["email"]

    head_links = ""
    if meta.get("siteUrl", "").strip():
        urls = site_urls(meta["siteUrl"].strip())
        head_links = (
            f'<link rel="canonical" href="{e(urls[lang])}">\n'
            f'<link rel="alternate" hreflang="es" href="{e(urls["es"])}">\n'
            f'<link rel="alternate" hreflang="en" href="{e(urls["en"])}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{e(urls["es"])}">\n'
        )

    lang_links = []
    for code in LANGS:
        if code == lang:
            lang_links.append(f'<li><a href="./" hreflang="{code}" lang="{code}" aria-current="page">{e(ui["lang_name"][code])}</a></li>')
        else:
            lang_links.append(f'<li><a href="{other_href}" hreflang="{code}" lang="{code}">{e(ui["lang_name"][code])}</a></li>')

    toc = [("about", ui["about"]), ("work", ui["work"]), ("projects", ui["projects"]), ("methods", ui["methods"]),
           ("skills", ui["skills"]), ("experience", ui["experience"]), ("contact", ui["contact"])]

    rail = f"""<header class="rail">
  <div class="rail-top">
    <p class="stamp">{e(ui["updated"].format(date=meta["updated"]))}</p>
    <nav class="lang" aria-label="{e(ui["lang_nav"])}"><ul class="plain">{"".join(lang_links)}</ul></nav>
  </div>
  <h1>{e(meta["name"])}</h1>
  <p class="headline">{e(t(meta["headline"], lang))}</p>
  <ul class="plain facts">
    <li>{e(t(meta["location"], lang))}</li>
    <li><a href="mailto:{e(email)}">{e(email)}</a></li>
    <li><a href="{e(github_url(data))}">{e(github_label(data))}</a></li>
  </ul>
  <div class="actions">
    <a class="btn primary" href="mailto:{e(email)}">{e(ui["email_cta"])}</a>
    <a class="btn secondary" href="{prefix}files/{PDF_NAMES["cv"][lang]}">{e(ui["cv_pdf"])}</a>
    <a class="btn secondary" href="{prefix}files/{PDF_NAMES["portfolio"][lang]}">{e(ui["portfolio_pdf"])}</a>
  </div>
  <nav class="toc" aria-label="{e(ui["sections"])}">
    <ul class="plain">{"".join(f'<li><a href="#{sid}">{e(label)}</a></li>' for sid, label in toc)}</ul>
  </nav>
  <div class="dossier">
    <div>
      <h2 class="label">{e(ui["key_stack"])}</h2>
      <ul class="inline">{"".join(f"<li>{e(term)}</li>" for term in KEY_STACK)}</ul>
    </div>
    <div>
      <h2 class="label">{e(ui["languages"])}</h2>
      <ul class="plain stacked">{"".join(f"<li>{e(t(item, lang))}</li>" for item in data["languages"])}</ul>
    </div>
    <div>
      <h2 class="label">{e(ui["education"])}</h2>
      <ul class="plain stacked">{"".join(f"<li>{e(t(item, lang))}</li>" for item in data["education"])}</ul>
    </div>
  </div>
</header>"""

    stats = "".join(
        f'<li><span class="v">{e(stat["value"])}</span><span class="l">{e(t(stat["label"], lang))}</span></li>'
        for stat in data["stats"]
    )

    def stack_line(project):
        return f'<p class="stack"><b>{e(ui["stack"])}</b>{" · ".join(e(s) for s in project["stack"])}</p>'

    def highlights(project):
        return '<ul class="hl">' + "".join(f"<li>{e(t(h, lang))}</li>" for h in project["highlights"]) + "</ul>"

    cases = []
    for project in projects:
        if not project["featured"]:
            continue
        n = num(numbers[project["id"]])
        meta_line = " · ".join(e(t(project[k], lang)) for k in ("context", "role", "period"))
        cases.append(f"""<article class="case" id="case-{e(project["id"])}" aria-labelledby="case-{e(project["id"])}-h">
  <div class="num" aria-hidden="true">{n}</div>
  <div>
    <h3 id="case-{e(project["id"])}-h">{e(t(project["title"], lang))}</h3>
    <p class="meta">{meta_line}</p>
    <p class="summary">{e(t(project["summary"], lang))}</p>
    {highlights(project)}
    {stack_line(project)}
  </div>
</article>""")

    counts = {area_id: sum(1 for p in projects if p["area"] == area_id) for area_id in areas}
    chips = [f'<button type="button" class="chip" data-filter="all" data-label="{e(ui["filter_all"])}" aria-pressed="true">{e(ui["filter_all"])} <span class="n">{len(projects)}</span></button>']
    for area_id, title in areas.items():
        chips.append(f'<button type="button" class="chip" data-filter="{e(area_id)}" data-label="{e(title)}" aria-pressed="false">{e(title)} <span class="n">{counts[area_id]}</span></button>')

    items = []
    for project in projects:
        n = num(numbers[project["id"]])
        title = e(t(project["title"], lang))
        area = e(areas[project["area"]])
        if project["featured"]:
            body = (f'<h3><a href="#case-{e(project["id"])}">{title}</a></h3>'
                    f'<p class="meta">{area} · {e(t(project["context"], lang))} · {e(t(project["period"], lang))}</p>'
                    f'<a class="go" href="#case-{e(project["id"])}">{e(ui["see_case"].format(n=n))}</a>')
        else:
            meta_line = " · ".join(e(t(project[k], lang)) for k in ("context", "role", "period"))
            body = (f'<h3>{title}</h3><p class="meta">{area} · {meta_line}</p>'
                    f'<p class="summary">{e(t(project["summary"], lang))}</p>{highlights(project)}{stack_line(project)}')
        items.append(f'<li class="item" data-area="{e(project["area"])}"><span class="n" aria-hidden="true">{n}</span><div>{body}</div></li>')

    methods = "".join(
        f'<li><h3>{e(t(m["title"], lang))}</h3><p>{e(t(m["body"], lang))}</p></li>' for m in data["methods"]
    )
    skills = "".join(
        f'<div><dt>{e(t(g["title"], lang))}</dt><dd><ul class="inline">'
        + "".join(f"<li>{e(t(item, lang))}</li>" for item in g["items"])
        + "</ul></dd></div>"
        for g in data["skills"]
    )
    timeline = []
    for job in data["experience"]:
        current = is_current(job["period"])
        state = f' <span class="sr-only">{e(ui["current"])}</span>' if current else ""
        timeline.append(f"""<li>
  <span class="dot{' now' if current else ''}" aria-hidden="true"></span>
  <p class="when">{e(t(job["period"], lang))}{state}</p>
  <div>
    <h3>{e(t(job["role"], lang))}</h3>
    <p class="org">{e(t(job["org"], lang))}</p>
    <p class="body">{e(t(job["body"], lang))}</p>
  </div>
</li>""")
    more = "".join(f"<li>{e(t(item, lang))}</li>" for item in data["more"])

    description = e(t(meta["headline"], lang))
    empty_text = e(ui["empty"]).replace("{area}", '<span id="empty-area"></span>')
    count_text = f'{len(projects)} {ui["count_many"]} · {ui["filter_all"]}'
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{e(ui["title"].format(name=meta["name"]))}</title>
<meta name="description" content="{description}">
{head_links}<style>{SITE_CSS.replace("%VARS%", css_vars())}</style>
</head>
<body>
<a class="skip" href="#main">{e(ui["skip"])}</a>
<div class="page">
{rail}
<main id="main" tabindex="-1">
<section id="about" aria-labelledby="about-h">
  <h2 id="about-h">{e(ui["about"])}</h2>
  <p class="about">{e(t(data["about"], lang))}</p>
</section>
<section id="numbers" aria-labelledby="numbers-h">
  <h2 id="numbers-h">{e(ui["numbers"])}</h2>
  <ul class="plain stats">{stats}</ul>
</section>
<section id="work" aria-labelledby="work-h">
  <h2 id="work-h">{e(ui["work"])}</h2>
  <p class="note">{e(ui["work_note"])}</p>
  {"".join(cases)}
</section>
<section id="projects" aria-labelledby="projects-h">
  <h2 id="projects-h">{e(ui["projects"])}</h2>
  <p class="note">{e(ui["projects_note"].format(n=len(projects), a=len(areas)))}</p>
  <div class="filters" id="filters" role="group" aria-label="{e(ui["filter_label"])}" hidden>{"".join(chips)}</div>
  <p class="count" id="count" role="status" hidden data-one="{e(ui["count_one"])}" data-many="{e(ui["count_many"])}">{e(count_text)}</p>
  <div class="empty" id="empty" hidden>
    <p>{empty_text}</p>
    <button type="button" class="btn" id="reset">{e(ui["reset"])}</button>
  </div>
  <ol class="plain index" id="index">{"".join(items)}</ol>
</section>
<section id="methods" aria-labelledby="methods-h">
  <h2 id="methods-h">{e(ui["methods"])}</h2>
  <ul class="plain methods">{methods}</ul>
</section>
<section id="skills" aria-labelledby="skills-h">
  <h2 id="skills-h">{e(ui["skills"])}</h2>
  <dl class="skills">{skills}</dl>
</section>
<section id="experience" aria-labelledby="experience-h">
  <h2 id="experience-h">{e(ui["experience"])}</h2>
  <ol class="plain timeline">{"".join(timeline)}</ol>
</section>
<section id="more" aria-labelledby="more-h">
  <h2 id="more-h">{e(ui["more"])}</h2>
  <ul class="more">{more}</ul>
</section>
</main>
<footer class="contact" id="contact" aria-labelledby="contact-h">
  <h2 id="contact-h">{e(ui["contact"])}</h2>
  <p>{e(ui["contact_text"])} {e(t(meta["location"], lang))}.</p>
  <div class="actions">
    <a class="btn primary" href="mailto:{e(email)}">{e(email)}</a>
    <a class="btn secondary" href="{e(github_url(data))}">{e(github_label(data))}</a>
  </div>
</footer>
</div>
<script>{FILTER_JS}</script>
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

def render_all(data):
    files = {}
    for lang in LANGS:
        files[PAGE_PATHS[lang]] = render_site(data, lang)
        files[CV_PATHS[lang]] = render_cv(data, lang)
    return files


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
        files = render_all(data)
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

    if args.pdf:
        error = build_pdfs(args.out)
        if error:
            print(f"pdf error: {error}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
