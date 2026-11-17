"""HTML of the featured-work story section (section#work).

One article.case.chapter per featured project, in content order, with its
text, its problem -> solution -> saving modules (real projects) and its own
device; plus the chapter index and the pinned stage used on wide screens.
"""
from covers import cover_svg
from story import SIZES, THUMB_SIZES, Eager, art_img, assign_shots, device, e, mock_label, real_img, t, terminal

STORY_UI = {
    "es": {
        "title": ("Ocho proyectos, ", "un capítulo", " cada uno"),
        "lead_fx": "Desplázate para abrir el portátil: cada capítulo cambia la pantalla y cuenta el contexto, el rol y los resultados.",
        "lead_static": "Cada capítulo muestra la pantalla del proyecto y cuenta el contexto, el rol y los resultados.",
        "note_real": "{names} aparecen con su nombre y sus capturas reales; los demás proyectos usan imágenes referenciales y sus clientes siguen anonimizados.",
        "note_ref": "{names} aparecen con su nombre real; las pantallas son imágenes referenciales y los clientes externos siguen anonimizados.",
        "and": " y ",
        "index": "Índice de capítulos",
        "chapters": "Capítulos",
        "more": "Más proyectos",
        "start": "Inicio",
        "opening": "Abriendo el portátil",
        "chapter": "Capítulo",
        "boot": "{n} capítulos · desplázate",
        "ref": "Imagen referencial",
        "mock": "Vista ilustrativa",
        "modules": "Problema → solución → ahorro",
        "problem": "Problema",
        "solution": "Solución",
        "saving": "Ahorro",
        "tech": "Logros técnicos y stack",
        "stack": "Stack",
    },
    "en": {
        "title": ("Eight projects, ", "one chapter", " each"),
        "lead_fx": "Scroll to open the laptop: each chapter swaps the screen and tells the context, the role and the results.",
        "lead_static": "Each chapter shows the project's screen and tells the context, the role and the results.",
        "note_real": "{names} appear with their real names and real screenshots; the other projects use reference images and their clients stay anonymized.",
        "note_ref": "{names} appear with their real names; the screens are reference images and external clients stay anonymized.",
        "and": " and ",
        "index": "Chapter index",
        "chapters": "Chapters",
        "more": "More projects",
        "start": "Start",
        "opening": "Opening the laptop",
        "chapter": "Chapter",
        "boot": "{n} chapters · scroll",
        "ref": "Reference image",
        "mock": "Illustrative view",
        "modules": "Problem → solution → saving",
        "problem": "Problem",
        "solution": "Solution",
        "saving": "Saving",
        "tech": "Technical highlights and stack",
        "stack": "Stack",
    },
}


def join_names(names, glue):
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + glue + names[-1]


def chips(items, lang):
    return '<ul class="plain chips">' + "".join(f"<li>{e(t(i, lang))}</li>" for i in items) + "</ul>"


def on_device(shots, device, assigned):
    """The device keeps its first shot plus every shot no module shows;
    the stage script adds the module thumbnails back on wide screens."""
    own = [i for i, x in enumerate(shots) if x["device"] == device]
    return [shots[i] for k, i in enumerate(own) if k == 0 or i not in assigned]


def screens(project, lang, prefix, manifest, shots, eager, s, assigned):
    """Laptop and phone screen markup; phone is None when there is none.

    Shots are real or mock (mock ones carry the illustrative label); a
    project with a terminal (S14) shows only that terminal on the laptop.
    """
    art = manifest.get(f"case-{project['id']}")
    laps = on_device(shots, "laptop", assigned)
    phones = on_device(shots, "phone", assigned)

    def shot_list(group, device):
        return "".join(f'<div class="shot{" on" if i == 0 else ""}">{real_img(x, lang, prefix, SIZES[device], eager)}'
                       f'{mock_label(x, s["mock"])}</div>' for i, x in enumerate(group))

    if project.get("terminal"):
        lap = terminal(project["terminal"], lang)
    elif laps:
        lap = shot_list(laps, "laptop")
    else:
        cover = cover_svg(project["id"], project["area"]).replace(f"cv-{project['id']}-", f"cv-{project['id']}-case-")
        image = art_img(art, prefix, SIZES["laptop"]) if art else ""
        lap = f'<div class="shot ref on cover-host">{image}{cover}<span class="slot">{e(s["ref"])}</span></div>'
    phone = None
    if phones:
        phone = shot_list(phones, "phone")
    elif project.get("product") and not shots and art:
        phone = f'<div class="shot ref on">{art_img(art, prefix, SIZES["phone"], smallest=True)}<span class="slot">{e(s["ref"])}</span></div>'
    return f'<div class="shots">{lap}</div>', (None if phone is None else f'<div class="shots">{phone}</div>')


def modules(project, lang, prefix, shots, eager, s, picks):
    if not project.get("modules"):
        return ""
    items = []
    for i, (module, pick) in enumerate(zip(project["modules"], picks)):
        thumb = ""
        if pick is not None:
            shot = shots[pick]
            cls = "mod-shot ph" if shot["device"] == "phone" else "mod-shot"
            thumb = f'<figure class="{cls}">{real_img(shot, lang, prefix, THUMB_SIZES[shot["device"]], eager)}</figure>'
        rows = "".join(f'<div class="{cls}"><dt>{e(s[key])}</dt><dd>{e(t(module[key], lang))}</dd></div>'
                       for key, cls in (("problem", "pb"), ("solution", "so"), ("saving", "sv")))
        items.append(f'<li class="mod" data-area="{e(module.get("area", ""))}"><div class="mod-top"><span class="mod-n" aria-hidden="true">{i + 1:02d}</span>'
                     f'<h4>{e(t(module["title"], lang))}</h4></div>{thumb}<dl>{rows}</dl></li>')
    head_id = f'mods-{project["id"]}'
    return (f'<section class="mods" aria-labelledby="{head_id}"><p class="mods-h" id="{head_id}"><span class="dot"></span>{e(s["modules"])}</p>'
            f'<ol class="plain mod-list">{"".join(items)}</ol></section>')


def chapter(project, i, ctx):
    lang, s, prefix = ctx["lang"], ctx["s"], ctx["prefix"]
    pid = e(project["id"])
    shots = ctx["real"].get(project["id"]) or ctx["mock"].get(project["id"], [])
    picks = assign_shots(project, shots)
    lap, phone = screens(project, lang, prefix, ctx["manifest"], shots, ctx["eager"], s, {i for i in picks if i is not None})
    product = project.get("product")
    title = f'<span class="ttl">{e(t(project["title"], lang))}</span>'
    if product:
        title = f'<span class="prod"><mark>{e(product["name"])}</mark></span><span class="sr-only">: </span>' + title
    extra = ""
    if project.get("impact"):
        extra += f'<p class="impact"><span class="dot"></span><span>{e(t(project["impact"], lang))}</span></p>'
    if product and product.get("url"):
        extra += f'<p><a class="ch-link" href="{e(product["url"])}">{e(t(product["link"], lang))} <span aria-hidden="true">↗</span></a></p>'
    hl = '<ul class="hl">' + "".join(f"<li>{e(t(h, lang))}</li>" for h in project["highlights"]) + "</ul>"
    tech = f'{hl}<p class="stack-label">{e(s["stack"])}</p>{chips(project["stack"], lang)}'
    if project.get("modules"):
        tech = f'<details><summary>{e(s["tech"])}</summary>{tech}</details>'
    meta = (f'<p class="ch-meta"><span class="pill">{e(t(project["context"], lang))}</span>'
            f'<span class="pill"><strong>{e(t(project["role"], lang))}</strong></span></p>')
    return (f'<article class="case chapter" id="case-{pid}" aria-labelledby="case-{pid}-h" style="{ctx["area_style"](project["area"])}">'
            f'<div class="ch-text"><p class="ch-kicker"><span class="num">{ctx["numbers"][project["id"]]:02d}</span>'
            f'{e(ctx["areas"][project["area"]])} · {e(t(project["period"], lang))}</p>'
            f'<h3 id="case-{pid}-h" tabindex="-1">{title}</h3>{meta}'
            f'<p class="ch-sum">{e(t(project["summary"], lang))}</p>{extra}'
            f'{modules(project, lang, prefix, shots, ctx["eager"], s, picks)}{tech}</div>'
            f'<div class="dev-cell" aria-hidden="true">{device(lap, phone, front=bool(project.get("terminal")))}</div></article>')


def render_story(data, lang, prefix, manifest, real, areas, numbers, area_style, kicker, mock=None):
    s = STORY_UI[lang]
    featured = [p for p in data["projects"] if p["featured"]]
    ctx = {"lang": lang, "s": s, "prefix": prefix, "manifest": manifest, "real": real, "mock": mock or {}, "eager": Eager(),
           "areas": areas, "numbers": numbers, "area_style": area_style}
    chapters = "".join(chapter(p, i, ctx) for i, p in enumerate(featured))
    names = join_names([p["product"]["name"] for p in featured if p.get("product")], s["and"])
    note = (s["note_real"] if real else s["note_ref"]).format(names=names)
    links = "".join(f'<li><a href="#case-{e(p["id"])}" data-i="{i}"><span class="n">{numbers[p["id"]]:02d}</span>'
                    f'<span class="l">{e(t(p.get("short", p["title"]), lang))}</span><i class="bar"></i></a></li>'
                    for i, p in enumerate(featured))
    rest = len(data["projects"]) - len(featured)
    links += f'<li class="more"><a href="#projects"><span class="n">+{rest}</span><span>{e(s["more"])}</span></a></li>'
    boot = (f'<div class="layer"><div class="shot boot"><div><i>IR</i><b>{e(data["meta"]["name"])}</b>'
            f'<small>{e(s["boot"].format(n=len(featured)))}</small><span class="ld"></span></div></div></div>')
    stage = (f'<div class="stage" aria-hidden="true">{device(boot, None, "stage-dev")}'
             f'<p class="stage-cap" data-start="{e(s["start"])}" data-open="{e(s["opening"])}" data-ch="{e(s["chapter"])}">'
             f'<b>{e(s["start"])}</b><span class="nm">{e(s["opening"])}</span><span class="track"><i></i></span></p></div>')
    a, b, c = s["title"]
    return f"""<section id="work" class="story on-dark" aria-labelledby="work-h">
  <div class="wrap"><div class="story-grid">
    <header class="story-head">{kicker(4)}<h2 class="sec-title" id="work-h">{e(a)}<mark>{e(b)}</mark>{e(c)}</h2>
      <p class="note"><span class="lead-fx">{e(s["lead_fx"])}</span><span class="lead-static">{e(s["lead_static"])}</span></p>
      <p class="hint">{e(note)}</p></header>
    <nav class="chap-index" aria-label="{e(s["index"])}"><p class="ci-title">{e(s["chapters"])}</p><ol class="plain">{links}</ol></nav>
    {stage}
    <div class="chapters">{chapters}</div>
  </div></div>
</section>"""
