"""Behavior tests for tools/covers.py (animated SVG project covers).

The module is imported straight from tools/; nothing is written to disk.
"""
import importlib.util
import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "portfolio.json"


def load_covers():
    spec = importlib.util.spec_from_file_location("covers", ROOT / "tools" / "covers.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


covers = load_covers()
PROJECTS = json.loads(CONTENT.read_text(encoding="utf-8"))["projects"]
AREAS = {p["id"]: p["area"] for p in PROJECTS}

FORBIDDEN_TAGS = {"text", "script", "image", "foreignObject", "style", "iframe", "a", "audio", "video"}
COLOR_ATTRS = {"fill", "stroke", "stop-color", "flood-color", "lighting-color", "color"}
ALLOWED_COLOR = re.compile(r"^(none|currentColor|var\(--cover-(bg|line|line-2|accent|glow)\)|url\(#[\w-]+\))$")
LITERAL_COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch)\(", re.I)
ANIMATED_PROPS = {"transform", "opacity", "stroke-dashoffset"}
PRM_OPEN = "@media (prefers-reduced-motion: no-preference)"


def block_at(css, start):
    """Return (end_index, inner_text) of the {...} block that opens after start."""
    i = css.index("{", start)
    depth = 0
    for j in range(i, len(css)):
        if css[j] == "{":
            depth += 1
        elif css[j] == "}":
            depth -= 1
            if depth == 0:
                return j + 1, css[i + 1:j]
    raise AssertionError("unbalanced braces")


def media_blocks(css, query):
    out, pos = [], 0
    while True:
        k = css.find(query, pos)
        if k < 0:
            return out
        end, inner = block_at(css, k)
        out.append((k, end, inner))
        pos = end


def strip_blocks(css, spans):
    for start, end, _ in sorted(spans, reverse=True):
        css = css[:start] + css[end:]
    return css


def seconds(token):
    return float(token[:-2]) / 1000 if token.endswith("ms") else float(token[:-1])


class CoverIdsTest(unittest.TestCase):
    def test_ids_match_content_projects_in_order(self):
        self.assertEqual(covers.COVER_IDS, tuple(p["id"] for p in PROJECTS))
        self.assertEqual(len(covers.COVER_IDS), 17)


class CoverSvgTest(unittest.TestCase):
    def each(self):
        for pid in covers.COVER_IDS:
            yield pid, covers.cover_svg(pid, AREAS[pid])

    def test_single_well_formed_svg_with_required_root_attributes(self):
        for pid, svg in self.each():
            with self.subTest(pid=pid):
                self.assertTrue(svg.startswith("<svg ") and svg.endswith("</svg>"))
                self.assertEqual(svg.count("<svg"), 1)
                root = ET.fromstring(svg)
                self.assertEqual(root.tag, "svg")
                self.assertEqual(root.get("class"), f"cover cover--{pid}")
                self.assertEqual(root.get("viewBox"), "0 0 400 300")
                self.assertEqual(root.get("aria-hidden"), "true")
                self.assertEqual(root.get("focusable"), "false")
                self.assertEqual(root.get("preserveAspectRatio"), "xMidYMid slice")

    def test_no_forbidden_elements_attributes_colors_or_external_refs(self):
        for pid, svg in self.each():
            with self.subTest(pid=pid):
                self.assertNotRegex(svg, LITERAL_COLOR)
                self.assertNotIn("http", svg)
                self.assertNotIn("//", svg)
                for el in ET.fromstring(svg).iter():
                    self.assertNotIn(el.tag, FORBIDDEN_TAGS)
                    for name, value in el.attrib.items():
                        self.assertFalse(name.lower().startswith("on"), name)
                        self.assertNotEqual(name, "style")
                        if name in COLOR_ATTRS:
                            self.assertRegex(value, ALLOWED_COLOR, f"{el.tag} {name}={value}")
                        if name.endswith("href"):
                            self.assertTrue(value.startswith("#"), value)
                        for ref in re.findall(r"url\(([^)]*)\)", value):
                            self.assertTrue(ref.startswith("#"), ref)

    def test_size_limit_and_determinism(self):
        for pid, svg in self.each():
            with self.subTest(pid=pid):
                self.assertLessEqual(len(svg.encode("utf-8")), 4096)
                self.assertEqual(svg, covers.cover_svg(pid, AREAS[pid]))

    def test_covers_are_distinct_and_animated(self):
        seen = set()
        for pid, svg in self.each():
            with self.subTest(pid=pid):
                self.assertNotIn(svg, seen)
                seen.add(svg)
                self.assertRegex(svg, r'class="[^"]*\bcv-(draw|run|blink|spin|rise|breathe|slide|fall|twinkle|type|ping)\b')

    def test_dash_animated_elements_are_normalized(self):
        for pid, svg in self.each():
            for el in ET.fromstring(svg).iter():
                classes = (el.get("class") or "").split()
                if {"cv-draw", "cv-run", "cv-type"} & set(classes):
                    with self.subTest(pid=pid, tag=el.tag, classes=classes):
                        self.assertEqual(el.get("pathLength"), "100")

    def test_element_ids_unique_across_all_covers(self):
        doc = "<root>" + "".join(svg for _, svg in self.each()) + "</root>"
        ids = [el.get("id") for el in ET.fromstring(doc).iter() if el.get("id")]
        self.assertTrue(ids)
        self.assertEqual(len(ids), len(set(ids)))
        for pid, svg in self.each():
            for el in ET.fromstring(svg).iter():
                if el.get("id"):
                    self.assertTrue(el.get("id").startswith(f"cv-{pid}-"), el.get("id"))

    def test_internal_references_resolve(self):
        for pid, svg in self.each():
            ids = {el.get("id") for el in ET.fromstring(svg).iter()}
            for ref in re.findall(r"url\(#([\w-]+)\)", svg):
                self.assertIn(ref, ids, pid)

    def test_unknown_id_returns_generic_area_cover(self):
        for area in ("software", "ai", "engineering", "other", "nope"):
            with self.subTest(area=area):
                svg = covers.cover_svg("brand-new <project>", area)
                root = ET.fromstring(svg)
                self.assertEqual(root.tag, "svg")
                self.assertEqual(root.get("viewBox"), "0 0 400 300")
                self.assertTrue(root.get("class").startswith("cover cover--"))
                self.assertNotIn("<project>", svg)
                self.assertLessEqual(len(svg.encode("utf-8")), 4096)
                self.assertEqual(svg, covers.cover_svg("brand-new <project>", area))
        self.assertNotEqual(covers.cover_svg("x", "ai"), covers.cover_svg("x", "engineering"))


class CoversCssTest(unittest.TestCase):
    def setUp(self):
        self.css = covers.covers_css()
        self.motion = media_blocks(self.css, PRM_OPEN)
        self.prints = media_blocks(self.css, "@media print")

    def test_all_motion_lives_in_reduced_motion_block(self):
        self.assertEqual(len(self.motion), 1)
        rest = strip_blocks(self.css, self.motion + self.prints)
        for word in ("animation", "@keyframes", "transition"):
            self.assertNotIn(word, rest)
        self.assertIn("@keyframes", self.motion[0][2])

    def test_only_transform_opacity_and_dashoffset_are_animated(self):
        inner = self.motion[0][2]
        for start in [m.start() for m in re.finditer(r"@keyframes", inner)]:
            _, body = block_at(inner, start)
            props = set(re.findall(r"([a-z-]+)\s*:", body))
            self.assertTrue(props <= ANIMATED_PROPS, props)
        for value in re.findall(r"transition\s*:\s*([^;}]+)", inner):
            for part in value.split(","):
                self.assertIn(part.split()[0], ANIMATED_PROPS)

    def test_looping_animations_are_gentle(self):
        inner = self.motion[0][2]
        for value in re.findall(r"animation\s*:\s*([^;}]+)", inner):
            if "infinite" in value:
                duration = seconds(re.search(r"\b\d+(?:\.\d+)?m?s\b", value).group(0))
                self.assertTrue(6 <= duration <= 20, value)
        for value in re.findall(r"animation-duration\s*:\s*([^;}]+)", inner):
            self.assertTrue(6 <= seconds(value.strip()) <= 20, value)

    def test_play_control_selectors(self):
        inner = self.motion[0][2]
        self.assertIn(".cover-host:not(.is-inview)", inner)
        self.assertIn("html.motion-paused", inner)
        self.assertIn("animation-play-state:paused", inner.replace(" ", ""))
        self.assertIn(".cover-host:hover", inner)
        self.assertIn(".cover-host:focus-within", inner)

    def test_print_stops_animation(self):
        self.assertEqual(len(self.prints), 1)
        self.assertIn("animation:none", self.prints[0][2].replace(" ", ""))

    def test_every_cover_class_is_styled(self):
        used = set()
        for pid in covers.COVER_IDS:
            used |= set(re.findall(r"\bcv-[a-z0-9]+\b", " ".join(
                el.get("class") or "" for el in ET.fromstring(covers.cover_svg(pid, AREAS[pid])).iter())))
        for cls in used:
            self.assertIn("." + cls, self.css, cls)


if __name__ == "__main__":
    unittest.main()
