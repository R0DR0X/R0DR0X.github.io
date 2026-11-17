# Portfolio — Iván Rodrigo Pianto Antón

A bilingual (Spanish/English) personal portfolio generated from one content file.
The same content renders:

| Output | Path |
| --- | --- |
| Website, Spanish | `site/index.html` |
| Website, English | `site/en/index.html` |
| Website artwork (copied from `assets/img/`) | `site/assets/img/*.webp`, `og.jpg` |
| Real screenshots (copied from `assets/img/real/`) | `site/assets/img/real/*.webp` |
| Mock screens (copied from `assets/img/mock/`) | `site/assets/img/mock/*.webp` |
| CV print source (ES / EN) | `site/cv/es.html`, `site/cv/en.html` |
| CV PDF, max 2 A4 pages (ES / EN) | `site/files/Ivan-Rodrigo-Pianto-Anton-CV-ES.pdf`, `...-CV-EN.pdf` |
| Portfolio PDF, A4 (ES / EN) | `site/files/Ivan-Rodrigo-Pianto-Anton-Portafolio-ES.pdf`, `...-Portfolio-EN.pdf` |

Everything is static HTML with inline CSS and JS. No external fonts, scripts, styles or libraries; the only
images are the local files listed in `assets/img/manifest.json`, `assets/img/real/manifest.json` and
`assets/img/mock/manifest.json`.

## Website

A single page in the escorpia.com design language: light by default with dark `.on-dark` sections, cyan
`#00D4FF` accents, mono chips, `<mark>` highlights, pills and rounded cards, system font stacks only.

- Header: section links, language switch, a theme toggle (light/dark, remembered in `localStorage`), the
  "Pausar animaciones" / "Pause animations" button and, on narrow screens, a menu button.
- Hero: a `<canvas>` sphere of skill nodes drawn with a hand-written 3D projection, steered by the pointer; its
  labels are the skill chips of the page and never cover the hero copy. With motion allowed the stage is pinned
  while the page scrolls: the copy scrolls away, then the sphere unrolls row by row into a flat grid, tilts into a
  floor and lights up the numbered tiles of the featured cases (labels from the chapter index; a lit tile opens its
  chapter). When paused the frame only follows the scroll; under reduced motion it is one still sphere and the hero
  is not pinned. The loop stops off screen and in hidden tabs.
- Featured work (`#work`): a scroll story with a CSS 3D laptop and phone. On wide screens the device is pinned
  between the text column and a chapter index: the lid opens, the screen changes per chapter (and per screenshot
  inside a chapter) and the phone joins for the projects that have one, beside the laptop with a clear gap (the
  laptop moves left and shrinks; a chapter without a phone centers the laptop alone). A project with a `terminal`
  in the content (freshia) puts the phone in front and the laptop smaller and set back, its screen an HTML terminal
  that the phone never covers. On narrow screens every chapter has its own device above the text; a chapter with a
  phone stacks it above the laptop, centered and larger, with a gap and the laptop at full size (freshia too: phone
  above, terminal laptop below). Each chapter is `article#case-<id>`.
- Real projects (`erp-traceability` → Escorpia Traza, `ecommerce-platform` → WiinComerce, `agent-cockpit` →
  freshia) carry a `product` entry in the content (name and optional public link), a one-line `impact` and
  `modules`: one problem → solution → saving block per module. A module may carry a `credit`
  (`text` with a `{link}` placeholder, `link`, `url`): the WiinComerce WhatsApp CRM credits vocero-crm by Kevin
  Belier (MIT), the repository it builds on. Every other project keeps its referential artwork
  and anonymized wording.
- Count-up figures, a stack marquee, project cards with the project's image (real screenshot, else mock screen,
  else the animated SVG cover) and an area filter (View Transitions
  when supported), method cards, skills and an experience timeline that draws with scroll.
- Without JavaScript or with `prefers-reduced-motion: reduce` every section is static and fully readable: the
  story shows each chapter next to its device, the marquee is a wrapped list and reveals are off. Every animation
  and transition lives inside `@media (prefers-reduced-motion: no-preference)`.
- With `meta.siteUrl` set, each page also gets Open Graph and Twitter card tags (image `assets/img/og.jpg`)
  and a JSON-LD `Person`.
- Printing the website (the portfolio PDF) switches to a light layout without devices, artwork or motion, with
  every project, module and highlight expanded.

### Real screenshots

`assets/img/real/manifest.json` lists the screenshots of the real projects:

```json
{ "erp-traceability": [ { "file": "erp-traceability-01-llegadas", "device": "laptop", "width": 1600, "height": 1000,
  "alt": { "es": "…", "en": "…" }, "area": "llegadas", "source": "…" } ] }
```

Laptop shots ship as `<file>-800.webp` and `<file>-1600.webp` (16:10), phone shots as `<file>-400.webp` and
`<file>-800.webp` (1:2); `width`/`height` describe the larger file. Each screenshot is shown once: the device
keeps the first shot and the shots no module uses, and each module shows the next unused shot of its `area`
(the pinned stage adds those back). The first screenshot loads eagerly, the rest lazily. Without the manifest
the real projects fall back to their referential artwork, so the build works before the screenshots exist.
Real screenshots carry no label.

### Mock screens

`assets/img/mock/manifest.json` uses the same schema and file names for every project without real screenshots
(`source` names the artboard). Its shots fill those story chapters and project cards with a small
"Vista ilustrativa" / "Illustrative view" label. Without the manifest those projects keep their referential
artwork (case image and SVG cover).

## Requirements

- Python 3 (standard library only, nothing to install).
- For PDFs: Google Chrome or Chromium on `PATH` (`google-chrome`, `google-chrome-stable`, `chromium` or `chromium-browser`).
- Optional: `pdfinfo` / `pdftotext` (poppler) for page counts in tests and for scanning PDFs with the name check.

## Build

```sh
python3 tools/build.py          # validate content, write the HTML pages
python3 tools/build.py --pdf    # also print the four PDFs into site/files/
```

Options: `--content FILE` (default `content/portfolio.json`), `--out DIR` (default `site/`) and
`--real-images DIR` (default `assets/img/real`, the folder of the real screenshots and their `manifest.json`) and
`--mock-images DIR` (default `assets/img/mock`, the folder of the mock screens and their `manifest.json`).

The build validates the content first. Every `{"es": ..., "en": ...}` object needs both non-empty strings;
otherwise it prints `content error: <json path> missing <lang>` (for example
`content error: projects[3].title missing en`), exits 1 and writes nothing.
The image manifest is checked too: `hero` and `hero-mobile` are required and every listed file must exist
(`content error: image manifest has no 'hero'`, `content error: image 'hero' file missing: hero-960.webp`).
Real-screenshot and mock-screen manifests are checked the same way
(`content error: real image 'agent-cockpit' file missing: agent-cockpit-01-chat-800.webp`,
`content error: mock image 'roblox-game' file missing: roblox-game-01-carrera-1600.webp`).
The build then copies every manifest image into `site/assets/img/`, every real screenshot into
`site/assets/img/real/` and every mock screen into `site/assets/img/mock/`.
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

Contrast check (WCAG AA for every color pair of the light and dark website palette and the print palette):

```sh
python3 tools/contrast.py
```

## Content

All content lives in `content/portfolio.json`. Interface strings that are not content (section titles,
buttons, filter labels) live in the `UI` dictionary in `tools/build.py`, one entry per language.
Story strings (chapter index, stage captions, module labels) live in `STORY_UI` in `tools/story_html.py`.
The key stack terms and the two CV highlights per featured project are chosen in `KEY_STACK` and
`CV_HIGHLIGHTS` in `tools/build.py`. Featured projects can set `short` (chapter index label); real projects set
`product`, `impact` and `modules` (`area`, `title`, `problem`, `solution`, `saving`, each text as `{es, en}`).
The stylesheet and scripts are split into `tools/site_css.py`, `tools/story_css.py`, `tools/page_css.py`,
`tools/site_js.py`, `tools/story_js.py` and `tools/sphere_js.py`.

## Publishing

The site is published at https://r0dr0x.github.io/ from the repository `R0DR0X/R0DR0X.github.io`.
On every push to `main`, `.github/workflows/pages.yml` runs the tests and deploys the committed `site/`
folder to GitHub Pages. The workflow does not build: rebuild locally with `python3 tools/build.py --pdf`,
run the name check, and commit `site/` together with the content change.

`meta.siteUrl` in `content/portfolio.json` holds the public base URL (`https://r0dr0x.github.io`); change it
and rebuild if the site moves. With a value, each page gets a canonical URL and reciprocal absolute
`<link rel="alternate" hreflang="es|en|x-default">` tags (`x-default` points to Spanish).
While it is empty, those tags are omitted.

## Privacy

`research/` holds private notes and the anonymization denylist. It is listed in `.gitignore`
and must never be committed or published.
