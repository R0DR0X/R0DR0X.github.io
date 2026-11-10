"""Behavior tests for tools/build.py, tools/check_names.py and tools/contrast.py.

Every build runs into a fresh temp directory through --out/--content, so the
real site/ is never touched.
"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "tools" / "build.py"
CHECK_NAMES = ROOT / "tools" / "check_names.py"
CONTRAST = ROOT / "tools" / "contrast.py"
CONTENT = ROOT / "content" / "portfolio.json"

PAGES = {"es": "index.html", "en": os.path.join("en", "index.html")}
CVS = {"es": os.path.join("cv", "es.html"), "en": os.path.join("cv", "en.html")}
PDFS = [
    "Ivan-Rodrigo-Pianto-Anton-CV-ES.pdf",
    "Ivan-Rodrigo-Pianto-Anton-CV-EN.pdf",
    "Ivan-Rodrigo-Pianto-Anton-Portafolio-ES.pdf",
    "Ivan-Rodrigo-Pianto-Anton-Portfolio-EN.pdf",
]
CV_HEADINGS = {
    "es": ["Perfil", "Experiencia", "Proyectos destacados", "Habilidades", "Educación", "Idiomas"],
    "en": ["Profile", "Experience", "Selected projects", "Skills", "Education", "Languages"],
}
ALLOWED_HTTP_ANCHORS = {"https://github.com/R0DR0X"}
# Rioplatense voseo forms that must never appear in the neutral "tú" Spanish copy.
VOSEO = re.compile(
    r"(?i)\b(escribime|contame|mirá|tenés|querés|podés|sabés|hacé|vení|decime|buscá|elegí|vos)\b"
)
CHROME_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")


def run(args, env=None):
    return subprocess.run(
        [sys.executable, *map(str, args)],
        capture_output=True, text=True, env=env, timeout=600,
    )


def run_build(out, content=CONTENT, *extra, env=None):
    return run([BUILD, "--out", out, "--content", content, *extra], env=env)


def load_content():
    return json.loads(CONTENT.read_text(encoding="utf-8"))


def write_content(directory, data):
    path = Path(directory) / "content.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


class Page(HTMLParser):
    """Collects tags, visible text, and text/tags per enclosing <section id>."""

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.tags = []
        self.chunks = []
        self.sections = []
        self.section_text = {}
        self.section_tags = {}
        self.h2 = []
        self._in_h2 = False
        self._skip = 0
        self.feed(source)
        self.text = "\n".join(self.chunks)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag in ("script", "style"):
            self._skip += 1
        if tag == "section":
            self.sections.append(attrs.get("id"))
        if tag == "h2":
            self._in_h2 = True
            self.h2.append("")
        self.tags.append((tag, attrs))
        for sid in self.sections:
            self.section_tags.setdefault(sid, []).append((tag, attrs))

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1
        if tag == "section" and self.sections:
            self.sections.pop()
        if tag == "h2":
            self._in_h2 = False

    def handle_data(self, data):
        if self._skip:
            return
        self.chunks.append(data)
        if self._in_h2:
            self.h2[-1] += data
        for sid in self.sections:
            self.section_text[sid] = self.section_text.get(sid, "") + "\n" + data


class SiteBuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="portfolio-test-")
        cls.out = Path(cls.tmp) / "site"
        cls.result = run_build(cls.out)
        cls.data = load_content()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def source(self, rel):
        return (self.out / rel).read_text(encoding="utf-8")

    def page(self, lang):
        return Page(self.source(PAGES[lang]))

    def cv(self, lang):
        return Page(self.source(CVS[lang]))

    def test_build_succeeds_silently_on_stderr(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.assertEqual(self.result.stderr, "")
        for rel in [*PAGES.values(), *CVS.values()]:
            self.assertTrue((self.out / rel).is_file(), rel)

    # 1. Language of each page and its project titles.
    def test_pages_carry_their_language_and_titles(self):
        for lang, other in (("es", "en"), ("en", "es")):
            page = self.page(lang)
            self.assertEqual(page.lang, lang)
            for project in self.data["projects"]:
                self.assertIn(project["title"][lang], page.text, project["id"])
                if project["title"][other] != project["title"][lang]:
                    self.assertNotIn(project["title"][other], page.text, project["id"])

    # 2. Stats, methods, skill groups, index and featured cases.
    def test_pages_render_every_section_of_their_language(self):
        featured = [p for p in self.data["projects"] if p["featured"]]
        self.assertEqual(len(self.data["projects"]), 17)
        self.assertEqual(len(featured), 8)
        for lang in ("es", "en"):
            page = self.page(lang)
            for stat in self.data["stats"]:
                self.assertIn(stat["value"], page.section_text["numbers"])
                self.assertIn(stat["label"][lang], page.section_text["numbers"])
            for method in self.data["methods"]:
                self.assertIn(method["title"][lang], page.section_text["methods"])
            for group in self.data["skills"]:
                self.assertIn(group["title"][lang], page.section_text["skills"])

            index_items = [a for t, a in page.section_tags["projects"] if t == "li" and "data-area" in a]
            self.assertEqual(len(index_items), 17)
            self.assertFalse(any("hidden" in a for a in index_items), "projects hidden without JS")
            for project in self.data["projects"]:
                self.assertIn(project["title"][lang], page.section_text["projects"])

            cases = [a for t, a in page.section_tags["work"]
                     if t == "article" and "case" in a.get("class", "").split()]
            self.assertEqual(len(cases), 8)
            for project in featured:
                self.assertIn(project["title"][lang], page.section_text["work"])
            for project in self.data["projects"]:
                if not project["featured"]:
                    self.assertNotIn(project["title"][lang], page.section_text["work"])

    def test_area_filter_is_accessible_and_progressive(self):
        for lang in ("es", "en"):
            page = self.page(lang)
            tags = page.section_tags["projects"]
            groups = [a for t, a in tags if a.get("id") == "filters"]
            self.assertEqual(len(groups), 1)
            self.assertEqual(groups[0].get("role"), "group")
            self.assertIn("hidden", groups[0], "filter must stay hidden until JS runs")
            buttons = [a for t, a in tags if t == "button" and "data-filter" in a]
            self.assertEqual(len(buttons), len(self.data["areas"]) + 1)
            self.assertEqual([b["aria-pressed"] for b in buttons], ["true"] + ["false"] * len(self.data["areas"]))
            self.assertTrue(any(a.get("role") == "status" for t, a in tags))
            self.assertTrue(any(a.get("id") == "empty" and "hidden" in a for t, a in tags))
            self.assertTrue(any(t == "button" and a.get("id") == "reset" for t, a in tags))

    # 3. Language switch and hreflang alternates.
    def test_language_switch_links_to_the_other_page(self):
        for lang, other in (("es", "en"), ("en", "es")):
            rel = PAGES[lang]
            page = self.page(lang)
            links = {a["hreflang"]: a for t, a in page.tags if t == "a" and "hreflang" in a}
            self.assertEqual(set(links), {"es", "en"})
            target = links[other]
            self.assertEqual(target.get("lang"), other)
            resolved = os.path.normpath(os.path.join(os.path.dirname(rel), target["href"]))
            if target["href"].endswith("/"):
                resolved = os.path.normpath(os.path.join(resolved, "index.html"))
            self.assertEqual(resolved, os.path.normpath(PAGES[other]))
            self.assertNotIn("aria-current", target)
            self.assertEqual(links[lang].get("aria-current"), "page")
            self.assertEqual(links[lang].get("lang"), lang)

    def test_pdf_actions_link_to_the_language_files(self):
        expected = {
            "es": {"files/Ivan-Rodrigo-Pianto-Anton-CV-ES.pdf", "files/Ivan-Rodrigo-Pianto-Anton-Portafolio-ES.pdf"},
            "en": {"files/Ivan-Rodrigo-Pianto-Anton-CV-EN.pdf", "files/Ivan-Rodrigo-Pianto-Anton-Portfolio-EN.pdf"},
        }
        for lang in ("es", "en"):
            rel = PAGES[lang]
            hrefs = {
                os.path.normpath(os.path.join(os.path.dirname(rel), a["href"]))
                for t, a in self.page(lang).tags if t == "a" and a.get("href", "").endswith(".pdf")
            }
            self.assertEqual(hrefs, expected[lang])

    def test_spanish_copy_avoids_voseo(self):
        for rel in (PAGES["es"], CVS["es"]):
            self.assertIsNone(VOSEO.search(Page(self.source(rel)).text), rel)

    def test_no_alternates_or_canonical_without_site_url(self):
        data = copy.deepcopy(self.data)
        data["meta"]["siteUrl"] = ""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = run_build(out, write_content(tmp, data))
            self.assertEqual(result.returncode, 0, result.stderr)
            for lang in ("es", "en"):
                tags = Page((out / PAGES[lang]).read_text(encoding="utf-8")).tags
                rels = [a.get("rel") for t, a in tags if t == "link"]
                self.assertNotIn("alternate", rels)
                self.assertNotIn("canonical", rels)

    def test_reciprocal_absolute_alternates_with_site_url(self):
        data = copy.deepcopy(self.data)
        data["meta"]["siteUrl"] = "https://example.com/portfolio"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = run_build(out, write_content(tmp, data))
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = {
                "es": "https://example.com/portfolio/",
                "en": "https://example.com/portfolio/en/",
                "x-default": "https://example.com/portfolio/",
            }
            for lang in ("es", "en"):
                tags = Page((out / PAGES[lang]).read_text(encoding="utf-8")).tags
                alternates = {a["hreflang"]: a["href"] for t, a in tags if t == "link" and a.get("rel") == "alternate"}
                self.assertEqual(alternates, expected)
                canonical = [a["href"] for t, a in tags if t == "link" and a.get("rel") == "canonical"]
                self.assertEqual(canonical, [expected[lang]])

    # 4. No external resource loads; outbound anchors are allow-listed.
    def test_no_external_resources_and_allowed_anchors_only(self):
        external = re.compile(r"^\s*(https?:)?//", re.I)
        for rel in [*PAGES.values(), *CVS.values()]:
            source = self.source(rel)
            page = Page(source)
            self.assertNotRegex(source, r"(?i)\bsrc\s*=\s*[\"']?\s*(https?:)?//")
            self.assertNotRegex(source, r"(?i)url\(\s*[\"']?\s*(https?:)?//")
            self.assertNotIn("@import", source)
            for tag, attrs in page.tags:
                if tag in ("script", "img", "iframe", "video", "audio", "source", "embed"):
                    self.assertNotIn("src", attrs, f"{rel}: {tag} loads a file")
                if tag == "link" and attrs.get("rel") not in ("canonical", "alternate"):
                    self.assertFalse(external.match(attrs.get("href", "")), f"{rel}: {attrs}")
                if tag == "a":
                    href = attrs.get("href", "")
                    if href.startswith("mailto:") or href in ALLOWED_HTTP_ANCHORS:
                        continue
                    self.assertFalse(external.match(href), f"{rel}: outbound {href}")
                    self.assertIsNone(re.match(r"^[a-z][a-z0-9+.-]*:", href, re.I), f"{rel}: scheme {href}")

    # 6. CV print sources.
    def test_cv_pages_have_standard_headings_and_experience(self):
        for lang in ("es", "en"):
            cv = self.cv(lang)
            self.assertEqual(cv.lang, lang)
            self.assertEqual([h.strip() for h in cv.h2], CV_HEADINGS[lang])
            for job in self.data["experience"]:
                self.assertIn(job["role"][lang], cv.text)
                self.assertIn(job["org"][lang], cv.text)
                self.assertIn(job["period"][lang], cv.text)
            for tag, _ in cv.tags:
                self.assertNotIn(tag, ("table", "img", "aside", "svg"))


class ContentValidationTest(unittest.TestCase):
    # 5. A missing or empty translation stops the build before any write.
    def assert_rejected(self, mutate, expected_stderr, create_out=True):
        data = load_content()
        mutate(data)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            if create_out:
                out.mkdir()
            result = run_build(out, write_content(tmp, data))
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stderr, expected_stderr)
            self.assertEqual(result.stdout, "")
            if create_out:
                self.assertEqual(os.listdir(out), [])
            else:
                self.assertFalse(out.exists())

    def test_missing_en_string(self):
        self.assert_rejected(
            lambda d: d["projects"][3]["title"].pop("en"),
            "content error: projects[3].title missing en\n",
        )

    def test_empty_en_string_in_list_item(self):
        def mutate(d):
            d["skills"][3]["items"][0]["en"] = ""
        self.assert_rejected(mutate, "content error: skills[3].items[0] missing en\n", create_out=False)

    def test_missing_es_string(self):
        self.assert_rejected(
            lambda d: d["meta"]["headline"].pop("es"),
            "content error: meta.headline missing es\n",
        )


class PdfTest(unittest.TestCase):
    def test_pdf_without_chrome_fails_after_writing_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty_bin = Path(tmp) / "bin"
            empty_bin.mkdir()
            out = Path(tmp) / "out"
            env = dict(os.environ, PATH=str(empty_bin))
            result = run_build(out, CONTENT, "--pdf", env=env)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stderr, "pdf error: no Chrome/Chromium binary found\n")
            for rel in [*PAGES.values(), *CVS.values()]:
                self.assertTrue((out / rel).is_file(), rel)
            self.assertFalse((out / "files").exists())

    # 7. Real PDFs through headless Chrome.
    @unittest.skipUnless(any(shutil.which(n) for n in CHROME_NAMES), "no Chrome/Chromium binary")
    def test_pdf_outputs_and_cv_page_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = run_build(out, CONTENT, "--pdf")
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in PDFS:
                path = out / "files" / name
                self.assertTrue(path.is_file(), name)
                self.assertEqual(path.read_bytes()[:5], b"%PDF-")
                pages, (width, height) = pdf_info(path)
                self.assertAlmostEqual(width, 595.3, delta=2, msg=name)
                self.assertAlmostEqual(height, 841.9, delta=2, msg=name)
                if "-CV-" in name:
                    self.assertLessEqual(pages, 2, name)
                else:
                    self.assertGreaterEqual(pages, 2, name)
            if shutil.which("pdftotext"):
                denylist = Path(tmp) / "deny.txt"
                denylist.write_text("Pianto\n", encoding="utf-8")
                found = run([CHECK_NAMES, "--denylist", denylist, out / "files" / PDFS[0]])
                self.assertEqual(found.returncode, 1)
                self.assertEqual(found.stdout, f"name found: Pianto in {out / 'files' / PDFS[0]}\n")


def pdf_info(path):
    if shutil.which("pdfinfo"):
        info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, check=True).stdout
        pages = int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))
        size = re.search(r"^Page size:\s+([\d.]+) x ([\d.]+) pts", info, re.M)
        return pages, (float(size.group(1)), float(size.group(2)))
    raw = path.read_bytes()
    box = re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)", raw)
    return len(re.findall(rb"/Type\s*/Page(?!s)", raw)), (float(box.group(1)), float(box.group(2)))


class CheckNamesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="names-test-"))
        self.denylist = self.tmp / "denylist.txt"
        self.denylist.write_text("# fixture\nAcme Foods\n\nZeta\n", encoding="utf-8")
        self.docs = self.tmp / "docs"
        (self.docs / "nested").mkdir(parents=True)
        self.hit = self.docs / "nested" / "page.html"
        self.hit.write_text("<p>Built for ACME&nbsp;foods in Lima</p>", encoding="utf-8")
        self.clean = self.docs / "notes.txt"
        self.clean.write_text("Zetaline and zetas are not names.", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_reports_each_hit_and_fails(self):
        result = run([CHECK_NAMES, "--denylist", self.denylist, self.docs])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, f"name found: Acme Foods in {self.hit}\n")

    def test_word_boundary_and_clean_exit(self):
        result = run([CHECK_NAMES, "--denylist", self.denylist, self.clean])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "ok: no denylisted names\n")


class ContrastTest(unittest.TestCase):
    def test_every_palette_pair_meets_wcag_aa(self):
        result = run([CONTRAST])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("all pairs pass", result.stdout)


if __name__ == "__main__":
    unittest.main()
