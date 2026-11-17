"""Featured-work story: real screenshots, chapters, devices and modules.

Real screenshots (S5, contract in odd/tasks/portafolio-escorpia.md L7) live in
assets/img/real/ with a manifest.json:
  {"<project id>": [{"file", "device": "laptop"|"phone", "width", "height",
                      "alt": {"es", "en"}, "area", "source"}]}
Laptop shots ship as <file>-800.webp and <file>-1600.webp, phone shots as
<file>-400.webp and <file>-800.webp; width/height describe the large variant.
Only projects with a "product" in the content use them. Without a manifest
every chapter falls back to its referential artwork.

Mock screens (S13, contract in L11) live in assets/img/mock/ with the same
manifest schema; they fill every project without real shots (story chapters
and project cards) and carry a small "illustrative view" label. Without a mock
manifest those projects keep their referential artwork.
"""
import json
import shutil
from html import escape

VARIANTS = {"laptop": (800, 1600), "phone": (400, 800)}
SIZES = {"laptop": "(min-width: 62.5rem) 34rem, 92vw", "phone": "(min-width: 62.5rem) 10rem, (min-width: 30rem) 13.5rem, 45vw"}
THUMB_SIZES = {"laptop": "(min-width: 62.5rem) 26rem, 92vw", "phone": "6.25rem"}


def e(text):
    return escape(text, quote=True)


def t(value, lang):
    return value[lang] if isinstance(value, dict) else value


def variant_files(shot):
    return [f'{shot["file"]}-{w}.webp' for w in VARIANTS[shot["device"]]]


def load_shots(shot_dir, ids, kind):
    """Shots per project id in ids, tagged with their kind; {} without manifest.

    Raises ValueError with a readable message when the manifest is invalid
    or one of its files is missing.
    """
    path = shot_dir / "manifest.json"
    if not path.is_file():
        return {}
    manifest = json.loads(path.read_text(encoding="utf-8"))
    found = {}
    for pid in ids:
        shots = manifest.get(pid) or []
        for i, shot in enumerate(shots):
            where = f"{kind} image {pid}[{i}]"
            if shot.get("device") not in VARIANTS:
                raise ValueError(f"{where} has unknown device {shot.get('device')!r}")
            for key in ("file", "width", "height", "alt"):
                if not shot.get(key):
                    raise ValueError(f"{where} has no {key}")
            for lang in ("es", "en"):
                if not str(shot["alt"].get(lang, "")).strip():
                    raise ValueError(f"{where}.alt missing {lang}")
            for name in variant_files(shot):
                if not (shot_dir / name).is_file():
                    raise ValueError(f"{kind} image {pid!r} file missing: {name}")
        if shots:
            found[pid] = [dict(shot, kind=kind) for shot in shots]
    return found


def load_real(real_dir, projects):
    """Real shots of the projects with a "product" (S5)."""
    return load_shots(real_dir, [p["id"] for p in projects if p.get("product")], "real")


def load_mock(mock_dir, projects, real):
    """Mock shots of every project without real shots (S13)."""
    return load_shots(mock_dir, [p["id"] for p in projects if p["id"] not in real], "mock")


def copy_shots(shots, src_dir, out, kind):
    """Copy every listed shot into out/assets/img/<kind>/."""
    if not shots:
        return
    target = out / "assets" / "img" / kind
    target.mkdir(parents=True, exist_ok=True)
    for group in shots.values():
        for shot in group:
            for name in variant_files(shot):
                shutil.copyfile(src_dir / name, target / name)


class Eager:
    """The first real screenshot of the page loads eagerly; the rest are lazy."""

    def __init__(self):
        self.used = False

    def take(self):
        first, self.used = not self.used, True
        return first


def real_img(shot, lang, prefix, sizes, eager=None):
    """A real or mock shot: srcset of both variants, size, alt; lazy unless eager."""
    small, large = VARIANTS[shot["device"]]
    width, height = int(shot["width"]), int(shot["height"])
    files = [f"{prefix}assets/img/{shot.get('kind', 'real')}/{name}" for name in variant_files(shot)]
    srcset = f"{files[0]} {small}w, {files[1]} {large}w"
    lazy = "" if eager and eager.take() else ' loading="lazy"'
    return (f'<img src="{files[0]}" srcset="{srcset}" sizes="{sizes}" width="{width}" height="{height}" '
            f'alt="{e(t(shot["alt"], lang))}"{lazy} decoding="async">')


def mock_label(shot, label):
    """The discreet "illustrative view" label of mock shots; real shots have none."""
    return f'<span class="slot">{e(label)}</span>' if shot.get("kind") == "mock" else ""


def art_img(art, prefix, sizes, smallest=False):
    """Referential artwork (decorative, alt="") from the image manifest."""
    ordered = sorted(art["variants"], key=lambda v: v["width"])
    pick = ordered[0] if smallest else ordered[-1]
    srcset = ", ".join(f'{prefix}assets/img/{v["file"]} {v["width"]}w' for v in ordered)
    return (f'<img src="{prefix}assets/img/{pick["file"]}" srcset="{srcset}" sizes="{sizes}" '
            f'width="{pick["width"]}" height="{pick["height"]}" alt="" loading="lazy" decoding="async">')


LAP_PARTS = ('<div class="base"><div class="b-bot"></div><div class="b-side l"></div><div class="b-side r"></div>'
             '<div class="kb"></div><div class="pad"></div><div class="b-front"></div></div>'
             '<div class="lid"><div class="lid-top"></div><div class="lid-back"></div><div class="lid-front"><div class="screen">')
PHONE_OPEN = ('<div class="phone"><div class="ph-edge l"></div><div class="ph-edge r"></div><div class="ph-back"></div>'
              '<div class="ph-front"><span class="notch"></span><div class="screen">')


def device(lap, phone=None, dev_id="", front=False):
    """The CSS 3D laptop (plus the phone when given) around screen markup.

    has-phone sets laptop and phone side by side; ph-lead (S14) puts the
    phone in front and the laptop smaller and set back behind it.
    """
    cls = "dev has-phone ph-on" if phone else "dev"
    if front and phone:
        cls += " ph-lead"
    ident = f' id="{dev_id}"' if dev_id else ""
    phone_html = f"{PHONE_OPEN}{phone or ''}</div></div></div>" if (phone is not None or dev_id) else ""
    return (f'<div class="{cls}"{ident}><div class="dev-in"><div class="scene"><div class="floor"></div>'
            f'<div class="lap">{LAP_PARTS}{lap}</div></div></div></div>{phone_html}</div></div></div>')


def terminal(term, lang):
    """A crisp HTML terminal for the laptop screen (S14): title bar plus lines."""
    lines = "".join(f'<span class="t-{e(line["k"])}">{e(t(line["t"], lang))}</span>' for line in term["lines"])
    return (f'<div class="shot on term"><p class="t-bar"><i></i><i></i><i></i><span>{e(t(term["title"], lang))}</span></p>'
            f'<p class="t-body">{lines}</p></div>')


def assign_shots(project, shots):
    """Pair each module with the next unused screenshot of the same area."""
    used, picks = set(), []
    for module in project.get("modules", []):
        pick = None
        for i, shot in enumerate(shots):
            if i not in used and shot.get("area") == module.get("area"):
                pick = i
                used.add(i)
                break
        picks.append(pick)
    return picks
