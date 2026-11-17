"""Featured-work story: real screenshots, chapters, devices and modules.

Real screenshots (S5, contract in odd/tasks/portafolio-escorpia.md L7) live in
assets/img/real/ with a manifest.json:
  {"<project id>": [{"file", "device": "laptop"|"phone", "width", "height",
                      "alt": {"es", "en"}, "area", "source"}]}
Laptop shots ship as <file>-800.webp and <file>-1600.webp, phone shots as
<file>-400.webp and <file>-800.webp; width/height describe the large variant.
Only projects with a "product" in the content use them. Without a manifest
every chapter falls back to its referential artwork.
"""
import json
import shutil
from html import escape

from covers import cover_svg

VARIANTS = {"laptop": (800, 1600), "phone": (400, 800)}
SIZES = {"laptop": "(min-width: 62.5rem) 34rem, 92vw", "phone": "(min-width: 62.5rem) 10rem, 30vw"}
THUMB_SIZES = {"laptop": "(min-width: 62.5rem) 26rem, 92vw", "phone": "6.25rem"}
REAL_PATH = "assets/img/real/"


def e(text):
    return escape(text, quote=True)


def t(value, lang):
    return value[lang] if isinstance(value, dict) else value


def variant_files(shot):
    return [f'{shot["file"]}-{w}.webp' for w in VARIANTS[shot["device"]]]


def load_real(real_dir, projects):
    """Real shots per real project id; {} when there is no manifest.

    Raises ValueError with a readable message when the manifest is invalid
    or one of its files is missing.
    """
    path = real_dir / "manifest.json"
    if not path.is_file():
        return {}
    manifest = json.loads(path.read_text(encoding="utf-8"))
    real_ids = [p["id"] for p in projects if p.get("product")]
    real = {}
    for pid in real_ids:
        shots = manifest.get(pid) or []
        for i, shot in enumerate(shots):
            where = f"real image {pid}[{i}]"
            if shot.get("device") not in VARIANTS:
                raise ValueError(f"{where} has unknown device {shot.get('device')!r}")
            for key in ("file", "width", "height", "alt"):
                if not shot.get(key):
                    raise ValueError(f"{where} has no {key}")
            for lang in ("es", "en"):
                if not str(shot["alt"].get(lang, "")).strip():
                    raise ValueError(f"{where}.alt missing {lang}")
            for name in variant_files(shot):
                if not (real_dir / name).is_file():
                    raise ValueError(f"real image {pid!r} file missing: {name}")
        if shots:
            real[pid] = shots
    return real


def copy_real(real, real_dir, out):
    """Copy every real screenshot into out/assets/img/real/."""
    if not real:
        return
    target = out / "assets" / "img" / "real"
    target.mkdir(parents=True, exist_ok=True)
    for shots in real.values():
        for shot in shots:
            for name in variant_files(shot):
                shutil.copyfile(real_dir / name, target / name)


class Eager:
    """The first real screenshot of the page loads eagerly; the rest are lazy."""

    def __init__(self):
        self.used = False

    def take(self):
        first, self.used = not self.used, True
        return first


def real_img(shot, lang, prefix, sizes, eager):
    small, large = VARIANTS[shot["device"]]
    width, height = int(shot["width"]), int(shot["height"])
    files = [f"{prefix}{REAL_PATH}{name}" for name in variant_files(shot)]
    srcset = f"{files[0]} {small}w, {files[1]} {large}w"
    lazy = "" if eager.take() else ' loading="lazy"'
    return (f'<img src="{files[0]}" srcset="{srcset}" sizes="{sizes}" width="{width}" height="{height}" '
            f'alt="{e(t(shot["alt"], lang))}"{lazy} decoding="async">')


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


def device(lap, phone=None, dev_id=""):
    """The CSS 3D laptop (plus the phone when given) around screen markup."""
    cls = "dev has-phone ph-on" if phone else "dev"
    ident = f' id="{dev_id}"' if dev_id else ""
    phone_html = f"{PHONE_OPEN}{phone or ''}</div></div></div>" if (phone is not None or dev_id) else ""
    return (f'<div class="{cls}"{ident}><div class="dev-in"><div class="scene"><div class="floor"></div>'
            f'<div class="lap">{LAP_PARTS}{lap}</div></div></div></div>{phone_html}</div></div></div>')


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
