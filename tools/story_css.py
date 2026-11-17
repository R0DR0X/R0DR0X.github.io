"""Stylesheet of the featured-work story: pinned CSS 3D laptop + phone.

Ported from design/portafolio-escorpia/03-historia-scroll.html. The device is
designed at 760x600 and scaled with --k. Without JS (or with reduced motion)
every chapter shows its own device next to its text; `html.fx` on wide screens
pins one shared stage between the text column and the chapter index.
No animation or transition here: the scroll scene is driven by inline styles.
"""

STORY_CSS = """
/* story */
.story{position:relative;isolation:isolate;padding:clamp(4.5rem,3rem + 5vw,6.5rem) 0;--hair-dark:rgba(255,255,255,.1)}
.story::before{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;background:radial-gradient(900px 600px at 72% 8%,rgba(0,212,255,.13),transparent 70%),radial-gradient(700px 500px at 10% 60%,rgba(0,212,255,.06),transparent 70%)}
.story-head{max-width:42rem;margin:0 0 1.75rem}
.story-head .note{color:var(--text-soft)}
.story-head .hint{margin-top:1.25rem}
.chap-index{margin:0 0 1.5rem}
.ci-title{margin:0 0 .75rem;font:600 .75rem/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--primary-light)}
.chap-index ol{display:flex;flex-wrap:wrap;gap:.5rem}
.chap-index a{position:relative;overflow:hidden;display:flex;align-items:center;gap:.5rem;min-height:44px;padding:.5rem .875rem;border:1px solid var(--hair-dark);border-radius:999px;background:rgba(17,30,49,.75);color:var(--text-soft);font-size:.875rem;line-height:1.25;text-decoration:none}
.chap-index a .n{font:700 .75rem/1 var(--mono);color:var(--primary-light)}
.chap-index a:hover{border-color:rgba(71,232,255,.55);color:var(--white)}
.chap-index a[aria-current]{border-color:var(--primary);background:rgba(0,212,255,.13);color:var(--white)}
.chap-index a .bar{position:absolute;left:0;bottom:0;width:100%;height:2px;background:var(--primary);transform:scaleX(var(--p,0));transform-origin:left}
.chap-index .more a{border-style:dashed}
.stage{display:none}
.chapter{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:3.5rem;align-items:start;padding:4rem 0;border-top:1px solid var(--hair-dark)}
.dev-cell{order:2;min-width:0;position:sticky;top:calc(var(--hh) + 1rem)}
.ch-kicker{display:flex;flex-wrap:wrap;align-items:center;gap:.625rem;margin:0 0 .875rem;font:600 .75rem/1.3 var(--mono);letter-spacing:.07em;text-transform:uppercase;color:var(--primary-light)}
.ch-kicker .num{display:inline-grid;place-items:center;min-width:34px;height:26px;padding:0 8px;border-radius:8px;background:var(--primary);color:var(--bg)}
.chapter h3{font:800 clamp(1.5rem,1.2rem + 1vw,1.95rem)/1.15 var(--sans);letter-spacing:-.03em}
.chapter h3:focus{outline:none}
.chapter h3:focus-visible{outline:2px solid var(--primary-light)}
.prod{display:block;margin-bottom:.25rem;font-size:clamp(1.875rem,1.4rem + 1.6vw,2.6rem);line-height:1.05;letter-spacing:-.04em}
.prod mark{--highlight:rgba(0,212,255,.45)}
.ttl{display:block}
.prod + .ttl{font-size:clamp(1.0625rem,1rem + .35vw,1.25rem);font-weight:650;letter-spacing:-.015em;color:var(--text-soft)}
.ch-meta{display:flex;flex-wrap:wrap;gap:.5rem;margin:1rem 0 0}
.ch-meta .pill{padding:.375rem .75rem;font-size:.8125rem}
.ch-meta .pill strong{color:var(--white);font-weight:600}
.ch-sum{margin:1rem 0 0;color:var(--c-text)}
.impact{display:flex;gap:.625rem;align-items:baseline;margin:1rem 0 0;padding:.75rem .875rem;border:1px solid rgba(71,232,255,.35);border-radius:12px;background:rgba(0,212,255,.08);color:var(--white);font-weight:600;font-size:.9375rem}
.impact .dot{transform:translateY(-1px)}
.ch-link{display:inline-flex;align-items:center;gap:.375rem;min-height:44px;margin-top:.5rem;font:600 .875rem/1.2 var(--mono)}
.ch-text .hl{margin:1rem 0 1.125rem;font-size:.9375rem}
.ch-text .hl li::before{border-color:var(--primary-light)}
.ch-text details{margin:1rem 0;border-top:1px solid var(--hair-dark);border-bottom:1px solid var(--hair-dark)}
.ch-text summary{display:flex;align-items:center;justify-content:space-between;min-height:44px;font:600 .8125rem/1.3 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--primary-light);cursor:pointer;list-style:none}
.ch-text summary::-webkit-details-marker{display:none}
.ch-text summary::after{content:"+";font-size:1.25rem;line-height:1;color:var(--white)}
.ch-text details[open] summary::after{content:"\\2212"}
.ch-text .chips li{background:var(--surface);border-color:var(--hair-dark);font-size:.6875rem}
.ch-text .stack-label{color:var(--text-soft)}
/* problem -> solution -> saving */
.mods{margin-top:1.75rem}
.mods-h{display:flex;align-items:center;gap:.625rem;margin:0 0 .875rem;font:600 .75rem/1.3 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--primary-light)}
.mod-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,19rem),1fr));gap:.75rem}
.mod{display:flow-root;padding:1rem 1.125rem 1.125rem;border:1px solid var(--hair-dark);border-radius:14px;background:rgba(17,30,49,.72)}
.mod-top{display:flex;align-items:baseline;gap:.625rem;margin:0 0 .75rem}
.mod-n{flex:none;padding:.25rem .375rem;border-radius:6px;background:var(--primary);color:var(--bg);font:700 .75rem/1 var(--mono)}
.mod h4{margin:0;font:750 1.0625rem/1.3 var(--sans);letter-spacing:-.01em;color:var(--white)}
.mod dl{display:grid;gap:.625rem;margin:0}
.mod dt{font:600 .6875rem/1.2 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--text-soft)}
.mod dd{margin:.1875rem 0 0;font-size:.9375rem;line-height:1.5;color:var(--c-text)}
.mod .sv{padding:.5rem .75rem;border-left:3px solid var(--primary);border-radius:0 8px 8px 0;background:rgba(0,212,255,.08)}
.mod .sv dt{color:var(--primary-light)}
.mod .sv dd{color:var(--white);font-weight:600}
.mod-shot{margin:0 0 .75rem;overflow:hidden;border:1px solid var(--hair-dark);border-radius:10px;background:#02050b}
.mod-shot img{width:100%;height:auto}
.mod-shot.ph{float:right;width:6.25rem;margin:0 0 .5rem .75rem;border-radius:14px}
/* device: designed at 760x600 and scaled with --k */
.dev{position:relative;width:calc(760px * var(--k));height:calc(600px * var(--k));margin:0 auto;overflow:hidden}
.dev-in{position:absolute;left:0;top:0;width:760px;height:600px;transform:scale(var(--k));transform-origin:0 0}
.scene{position:absolute;inset:0;perspective:1700px;perspective-origin:50% 18%;transform-style:preserve-3d}
.floor{position:absolute;left:50%;top:350px;width:640px;height:220px;margin-left:-320px;pointer-events:none;background:radial-gradient(closest-side,rgba(0,212,255,.26),rgba(0,212,255,.06) 60%,transparent)}
.lap{position:absolute;left:132px;top:404px;width:520px;height:0;transform-style:preserve-3d;transform-origin:260px 0 170px;transform:translateX(calc(var(--sh,0) * -34px)) rotateX(var(--pitch,-20deg)) rotateY(var(--yaw,-10deg))}
.base{position:absolute;left:0;top:0;width:520px;height:340px;transform-origin:50% 0;transform:rotateX(90deg);transform-style:preserve-3d;border-radius:4px 4px 18px 18px;background:linear-gradient(180deg,#2a3850,#1a2539 70%,#151f30)}
.base > *{position:absolute}
.kb{left:34px;right:34px;top:26px;height:150px;border-radius:7px;background-color:#0b111c;background-image:linear-gradient(90deg,transparent 0 27px,#0b111c 27px 31px),linear-gradient(transparent 0 22px,#0b111c 22px 25px),linear-gradient(#25334a,#1d293d);background-size:31px 25px,31px 25px,100% 100%;background-position:4px 4px,4px 4px,0 0;box-shadow:inset 0 0 0 4px #0b111c}
.pad{left:50%;top:196px;width:170px;height:104px;margin-left:-85px;border-radius:10px;background:linear-gradient(160deg,#2c3a52,#202c41);box-shadow:inset 0 0 0 1px rgba(255,255,255,.08)}
.b-front{left:0;top:340px;width:520px;height:14px;transform-origin:50% 0;transform:rotateX(-90deg);background:linear-gradient(#18233a,#0a111d);border-radius:0 0 12px 12px}
.b-side{top:0;width:14px;height:340px;transform-origin:0 50%;transform:rotateY(90deg);background:#0f1828}
.b-side.r{left:520px}.b-side.l{left:0}
.b-bot{inset:0;transform:translateZ(-14px);background:#050911;border-radius:4px 4px 18px 18px;box-shadow:0 0 44px rgba(0,212,255,.16)}
.lid{position:absolute;left:0;top:-330px;width:520px;height:330px;transform-style:preserve-3d;transform-origin:50% 100%;transform:rotateX(calc(-87deg + var(--open,1) * 97deg))}
.lid-front,.lid-back{position:absolute;inset:0;border-radius:16px 16px 5px 5px;-webkit-backface-visibility:hidden;backface-visibility:hidden}
.lid-front{background:#05080f;box-shadow:inset 0 0 0 1.5px #2a3a52,0 0 60px rgba(0,212,255,calc(var(--open,1) * .25))}
.lid-back{transform:translateZ(-6px) rotateY(180deg);background:linear-gradient(135deg,#2b3a54,#162236 60%,#111b2c);box-shadow:inset 0 0 0 1px rgba(255,255,255,.08)}
.lid-back::after{content:"IR";position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);font:800 38px/1 var(--sans);color:rgba(71,232,255,.75);text-shadow:0 0 18px rgba(0,212,255,.7)}
.lid-top{position:absolute;left:0;top:0;width:520px;height:6px;transform-origin:50% 0;transform:rotateX(-90deg);background:#131d2e;border-radius:3px}
.screen{position:absolute;left:12px;right:12px;top:12px;bottom:20px;overflow:hidden;border-radius:6px;background:#02050b}
.screen::before{content:"";position:absolute;inset:0;z-index:3;pointer-events:none;background:linear-gradient(125deg,rgba(255,255,255,.08),transparent 36%)}
.screen::after{content:"";position:absolute;inset:0;z-index:4;pointer-events:none;background:#000;opacity:calc(1 - var(--open,1))}
.layer{position:absolute;inset:0;visibility:hidden}
.layer:first-child{visibility:inherit}
.phone{position:absolute;left:540px;top:184px;width:142px;height:290px;visibility:hidden;transform-style:preserve-3d;transform:translate3d(calc((1 - var(--ph,0)) * 420px),calc((1 - var(--ph,0)) * 60px),150px) rotateY(calc(-22deg + (1 - var(--ph,0)) * -40deg)) rotateX(-6deg)}
.ph-on .phone{visibility:visible}
.has-phone{--ph:1;--sh:1}
.ph-front,.ph-back{position:absolute;inset:0;border-radius:24px;-webkit-backface-visibility:hidden;backface-visibility:hidden}
.ph-front{background:#05080f;box-shadow:inset 0 0 0 2px #33445f,0 24px 60px rgba(0,0,0,.6),0 0 40px rgba(0,212,255,.18)}
.ph-back{transform:translateZ(-9px) rotateY(180deg);background:linear-gradient(150deg,#2b3a54,#121c2d)}
.ph-edge{position:absolute;top:14px;width:9px;height:262px;transform-origin:0 50%;transform:rotateY(90deg);background:#1f2b40;border-radius:4px}
.ph-edge.l{left:0}.ph-edge.r{left:142px}
.phone .screen{left:7px;right:7px;top:7px;bottom:7px;border-radius:18px}
.phone .screen::after{display:none}
.notch{position:absolute;left:50%;top:10px;z-index:5;width:40px;height:9px;margin-left:-20px;border-radius:6px;background:#05080f}
/* screens */
.shots{position:absolute;inset:0}
.shot{position:absolute;inset:0;margin:0;overflow:hidden;background:#0a1322;visibility:hidden}
.shot.on{visibility:inherit}
.shot img{width:100%;height:100%;object-fit:cover;object-position:50% 0}
.shot.ref{--cover-bg:#000000;--cover-line:var(--sea);--cover-line-2:var(--cyan);--cover-accent:var(--area);--cover-glow:var(--area)}
.shot.ref img{object-position:50% 50%}
.shot.ref .cover{position:absolute;inset:0;width:100%;height:100%;opacity:.42;mix-blend-mode:screen}
.slot{position:absolute;right:8px;bottom:8px;z-index:2;padding:4px 7px;border:1px dashed rgba(71,232,255,.55);border-radius:4px;background:rgba(4,8,18,.82);color:#bcd0e2;font:600 10px/1 var(--mono);letter-spacing:.06em;text-transform:uppercase}
.phone .slot{right:6px;bottom:6px;font-size:8px}
.boot{display:grid;place-items:center;visibility:inherit;background:radial-gradient(closest-side,rgba(0,212,255,.25),transparent),#040812;text-align:center;color:var(--white)}
.boot i{display:inline-grid;place-items:center;width:46px;height:46px;border-radius:13px;background:#111e31;color:#47e8ff;font:700 18px/1 var(--mono);font-style:normal}
.boot b{display:block;margin-top:12px;font-size:16px}
.boot small{display:block;margin-top:5px;font:600 9px/1.2 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:#47e8ff}
.boot .ld{display:block;width:120px;height:3px;margin:12px auto 0;overflow:hidden;border-radius:2px;background:rgba(255,255,255,.12)}
.boot .ld::after{content:"";display:block;width:45%;height:100%;background:#00d4ff}
.stage-cap{position:absolute;left:0;right:0;bottom:1.375rem;display:flex;align-items:center;justify-content:center;gap:.75rem;margin:0;font:600 .75rem/1.3 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--text-soft)}
.stage-cap b{color:var(--primary-light)}
.stage-cap .track{width:120px;height:3px;overflow:hidden;border-radius:2px;background:var(--hair-dark)}
.stage-cap .track i{display:block;height:100%;background:var(--primary);transform-origin:left;transform:scaleX(0)}
/* no-JS sizing fallback (JS sets --k from the real cell width) */
.dev{--k:.75}
@media (max-width:73.75rem){.dev{--k:.64}}
@media (max-width:67.5rem){.dev{--k:.6}}
@media (max-width:62.49rem){.dev{--k:.95}}
@media (max-width:50rem){.dev{--k:.85}}
@media (max-width:43.75rem){.dev{--k:.75}}
@media (max-width:38.75rem){.dev{--k:.66}}
@media (max-width:33.75rem){.dev{--k:.54}}
@media (max-width:28.75rem){.dev{--k:.46}}
@media (max-width:23.75rem){.dev{--k:.42}}
@media (max-width:62.49rem){.chapter{grid-template-columns:minmax(0,1fr);gap:1.75rem}.dev-cell{order:-1;position:static}}
@media (max-width:40rem){.chapter{padding:3rem 0}}
/* enhanced (JS + motion allowed): narrow keeps one device per chapter, index becomes a sticky chip bar */
html.fx .chap-index{position:sticky;top:var(--hh);z-index:6;margin:0 -1.25rem .5rem;padding:.625rem 1.25rem;background:rgba(4,8,18,.92);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);border-bottom:1px solid var(--hair-dark)}
html.fx .chap-index .ci-title{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
html.fx .chap-index ol{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;padding:2px}
html.fx .chap-index li{flex:none}
@media (min-width:52rem){html.fx .chap-index{margin-inline:-2rem;padding-inline:2rem}}
@media (min-width:62.5rem) and (min-height:35rem){
 html.fx .story{padding:0}
 html.fx .story-grid{display:grid;grid-template-columns:minmax(20rem,27rem) minmax(0,1fr) 11.5rem;column-gap:1.75rem;align-items:start}
 html.fx .story-head{grid-column:1;grid-row:1;display:flex;flex-direction:column;justify-content:center;min-height:clamp(640px,100vh,980px);margin:0;padding:5rem 0}
 html.fx .chapters{grid-column:1;grid-row:2;padding-bottom:22vh}
 html.fx .stage{grid-column:2;grid-row:1 / span 2;position:sticky;top:var(--hh);display:block;height:calc(100vh - var(--hh));overflow:hidden;align-self:start}
 html.fx .stage .dev{position:absolute;left:50%;top:46%;margin:0;overflow:visible;transform:translate(-50%,-50%)}
 html.fx .chap-index{grid-column:3;grid-row:1 / span 2;position:sticky;top:var(--hh);display:flex;flex-direction:column;justify-content:center;height:calc(100vh - var(--hh));margin:0;padding:0;background:none;-webkit-backdrop-filter:none;backdrop-filter:none;border:0;align-self:start}
 html.fx .chap-index .ci-title{position:static;width:auto;height:auto;clip-path:none;margin-left:.75rem}
 html.fx .chap-index ol{flex-direction:column;gap:3px;overflow:visible;padding:0}
 html.fx .chap-index a{padding:.5rem .75rem;border-color:transparent;border-radius:12px;background:transparent;font-size:.84rem}
 html.fx .chap-index a:hover{background:rgba(17,30,49,.8)}
 html.fx .chap-index a[aria-current]{border-color:rgba(0,212,255,.65);background:rgba(0,212,255,.11)}
 html.fx .chap-index .more a{margin-top:.5rem;border:1px dashed var(--hair-dark)}
 html.fx .chapter{display:block;min-height:clamp(720px,100vh,1040px);padding:clamp(70px,14vh,150px) 0 clamp(50px,10vh,110px);border:0}
 html.fx .chapter .dev-cell{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
 html.fx .mod-list{grid-template-columns:minmax(0,1fr)}
}
html:not(.fx) .lead-fx,html.fx .lead-static{display:none}
"""
