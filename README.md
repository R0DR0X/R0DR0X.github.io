# Portfolio — Iván Rodrigo Pianto Antón

A bilingual (Spanish/English) personal portfolio generated from one content file.
The same content renders:

| Output | Path |
| --- | --- |
| Website, Spanish | `site/index.html` |
| Website, English | `site/en/index.html` |
| CV print source (ES / EN) | `site/cv/es.html`, `site/cv/en.html` |
| CV PDF, max 2 A4 pages (ES / EN) | `site/files/Ivan-Rodrigo-Pianto-Anton-CV-ES.pdf`, `...-CV-EN.pdf` |
| Portfolio PDF, A4 (ES / EN) | `site/files/Ivan-Rodrigo-Pianto-Anton-Portafolio-ES.pdf`, `...-Portfolio-EN.pdf` |

Everything is static HTML with inline CSS and JS. No external fonts, scripts, styles or images.

## Requirements

- Python 3 (standard library only, nothing to install).
- For PDFs: Google Chrome or Chromium on `PATH` (`google-chrome`, `google-chrome-stable`, `chromium` or `chromium-browser`).
- Optional: `pdfinfo` / `pdftotext` (poppler) for page counts in tests and for scanning PDFs with the name check.

## Build

```sh
python3 tools/build.py          # validate content, write the HTML pages
python3 tools/build.py --pdf    # also print the four PDFs into site/files/
```

Options: `--content FILE` (default `content/portfolio.json`) and `--out DIR` (default `site/`).

The build validates the content first. Every `{"es": ..., "en": ...}` object needs both non-empty strings;
otherwise it prints `content error: <json path> missing <lang>` (for example
`content error: projects[3].title missing en`), exits 1 and writes nothing.
With `--pdf` and no Chrome binary it prints `pdf error: no Chrome/Chromium binary found` and exits 1
after writing the HTML.

To preview the site locally, serve the folder so the language links (`en/`, `../`) resolve:

```sh
python3 -m http.server -d site 8000
```

## Tests

```sh
python3 -m unittest discover -s tests -v
```

Tests build into temporary directories, so they never touch `site/`. The PDF test is skipped when no Chrome binary is found.

## Checks

Name check (anonymization): scans text, HTML and PDF files for denylisted names, case-insensitive and whole-word.

```sh
python3 tools/check_names.py --denylist research/denylist.txt site
```

It prints `name found: <term> in <file>` per hit and exits 1, or `ok: no denylisted names` and exits 0.

Contrast check (WCAG AA for every color pair of the website palette):

```sh
python3 tools/contrast.py
```

## Content

All content lives in `content/portfolio.json`. Interface strings that are not content (section titles,
buttons, filter labels) live in the `UI` dictionary in `tools/build.py`, one entry per language.
The key stack terms and the two CV highlights per featured project are chosen in `KEY_STACK` and
`CV_HIGHLIGHTS` in the same file.

## Before publishing

Set `meta.siteUrl` in `content/portfolio.json` to the public base URL (for example `https://example.com`),
then rebuild. With a value, each page gets a canonical URL and reciprocal absolute
`<link rel="alternate" hreflang="es|en|x-default">` tags (`x-default` points to Spanish).
While it is empty, those tags are omitted.

## Privacy

`research/` holds private notes and the anonymization denylist. It is listed in `.gitignore`
and must never be committed or published.
