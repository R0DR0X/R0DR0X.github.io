"""Base stylesheet of the portfolio website (escorpia.com design language).

Light page by default; `[data-theme="dark"]` and `.on-dark` sections swap the
color roles. %VARS% is replaced with the palette from tools/build.py.
Every animation and transition lives in MOTION_CSS, inside
`@media (prefers-reduced-motion: no-preference)`.
"""

SITE_CSS = """
:root{
%VARS%
--c-page:var(--paper);--c-text:var(--bg);--c-muted:var(--muted);--c-mist:var(--mist);--c-card:var(--paper);--c-line:var(--line);--c-link:var(--link);--c-focus:var(--bg);--c-header:rgba(255,255,255,.9);--highlight:rgba(0,212,255,.45);
--sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;--mono:ui-monospace,"SF Mono","Cascadia Code",Menlo,Consolas,"Liberation Mono",monospace;
--r:18px;--hh:4rem;--max:77.5rem;--ease:cubic-bezier(.2,.8,.2,1);--sh-l:0 18px 44px rgba(4,8,18,.1);--sh-d:0 30px 80px rgba(4,8,18,.65);color-scheme:light}
[data-theme="dark"],.on-dark{--c-page:var(--bg);--c-text:var(--white);--c-muted:var(--text-soft);--c-mist:var(--bg-alt);--c-card:var(--surface);--c-line:rgba(255,255,255,.12);--c-link:var(--primary-light);--c-focus:var(--primary-light);--c-header:rgba(4,8,18,.88);--highlight:rgba(0,212,255,.4);--sh-l:0 20px 50px rgba(0,0,0,.45)}
[data-theme="dark"]{color-scheme:dark}
.on-dark{background:var(--c-page);color:var(--c-text)}
*,*::before,*::after{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%;scroll-padding-top:calc(var(--hh) + 1rem);background:var(--c-page)}
body{margin:0;background:var(--c-page);color:var(--c-text);font:400 clamp(1rem,.96rem + .2vw,1.0625rem)/1.6 var(--sans);overflow-x:clip;overflow-wrap:break-word;-webkit-font-smoothing:antialiased}
h1,h2,h3{margin:0;color:var(--c-text)}
a{color:var(--c-link);text-underline-offset:.2em;text-decoration-thickness:1px}
a:hover{color:var(--c-text)}
:focus-visible{outline:2px solid var(--c-focus);outline-offset:3px;border-radius:6px}
main:focus{outline:none}
img,svg,canvas{display:block;max-width:100%}
mark{background:linear-gradient(transparent 56%,var(--highlight) 56%,var(--highlight) 92%,transparent 92%);color:inherit;padding:0 .06em}
.wrap{width:min(100% - 2.5rem,var(--max));margin-inline:auto}
@media (min-width:52rem){.wrap{width:min(100% - 4rem,var(--max))}}
.plain{list-style:none;margin:0;padding:0}
.sr-only{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
.print-only{display:none}
.skip{position:absolute;left:-9999px;top:8px;z-index:100;display:inline-flex;align-items:center;min-height:44px;padding:0 1rem;border-radius:8px;background:var(--bg);color:var(--white);font-weight:700}
.skip:focus{left:8px;color:var(--white)}

/* header */
.site-header{position:sticky;top:0;z-index:50;height:var(--hh);background:var(--c-header);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);border-bottom:1px solid var(--c-line)}
.bar{position:relative;height:100%;display:flex;align-items:center;gap:.375rem}
.mark{display:inline-flex;align-items:center;gap:.625rem;min-height:44px;margin-right:auto;color:var(--c-text);font-weight:700;letter-spacing:-.01em;text-decoration:none;white-space:nowrap}
.mark:hover{color:var(--c-text)}
.mark-glyph{display:grid;place-items:center;width:2.25rem;height:2.25rem;border-radius:10px;background:var(--bg);color:var(--primary-light);font:700 .8125rem/1 var(--mono);box-shadow:inset 0 0 0 1px rgba(71,232,255,.35)}
.mark-name{display:none}
.site-nav ul{display:flex;gap:.125rem}
.site-nav a{display:inline-flex;align-items:center;min-height:44px;padding:0 .75rem;border-radius:8px;color:var(--c-muted);font-size:.9375rem;text-decoration:none}
.site-nav a:hover{color:var(--c-text);background:var(--c-mist)}
.site-nav a.is-active{color:var(--c-text);box-shadow:inset 0 -2px 0 var(--primary);border-radius:0}
.tools{display:flex;align-items:center;gap:.375rem}
.lang ul{display:flex}
.lang a{display:inline-grid;place-items:center;min-width:44px;min-height:44px;border:1px solid var(--control);color:var(--c-text);font:600 .8125rem/1 var(--mono);letter-spacing:.06em;text-decoration:none}
.lang li:first-child a{border-radius:11px 0 0 11px}
.lang li:last-child a{border-radius:0 11px 11px 0;border-left:0}
.lang a:hover{background:var(--c-mist);color:var(--c-text)}
.lang a[aria-current="page"]{background:var(--c-text);border-color:var(--c-text);color:var(--c-page)}
.icon-btn{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;min-width:44px;min-height:44px;padding:0 .75rem;border:1px solid var(--control);border-radius:11px;background:transparent;color:var(--c-text);font:500 .875rem/1 var(--sans);cursor:pointer}
.icon-btn:hover{background:var(--c-mist)}
.icon-btn svg{width:16px;height:16px;flex:none}
.pause .i-play,.pause.is-paused .i-pause{display:none}
.pause.is-paused .i-play{display:block}
.theme{padding:0}
.theme .i-sun,[data-theme="dark"] .theme .i-moon{display:none}
[data-theme="dark"] .theme .i-sun{display:block}
.progress{display:none;position:absolute;left:0;right:0;bottom:-1px;height:3px;transform-origin:0 50%;transform:scaleX(0);background:var(--primary);box-shadow:0 0 12px rgba(0,212,255,.7)}
@media (min-width:40rem){.mark-name{display:inline}}
@media (max-width:83.99rem){.pause-label{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}.pause{padding:0}}
@media (max-width:67.99rem){
 .site-nav{position:absolute;top:100%;left:-1.25rem;right:-1.25rem;padding:.25rem 1.25rem;background:var(--c-page);border-bottom:1px solid var(--c-line);box-shadow:var(--sh-l);overflow-x:auto}
 html.js .site-nav{display:none;padding:.5rem 1.25rem 1.25rem}
 html.js .site-header.menu-open .site-nav{display:block}
 html.js .site-nav ul{flex-direction:column}
 html.js .site-nav a{min-height:52px;color:var(--c-text);font-size:1.125rem;font-weight:600}
 html.js .site-nav a.is-active{box-shadow:inset 3px 0 0 var(--primary)}
}
@media (min-width:68rem){.menu{display:none!important}}
@media (max-width:25rem){.lang a{min-width:40px}.tools{gap:.25rem}}

/* hero: canvas sphere of skills; html.scrub pins the stage while it unrolls (S12) */
.hero{--stage-h:calc(100vh - var(--hh));--scrub:120vh;position:relative;isolation:isolate;overflow:clip}
.hero-stage{position:absolute;inset:0;overflow:hidden}
.hero>.wrap{position:relative;z-index:0;display:flex;align-items:center;min-height:clamp(34rem,calc(100svh - var(--hh)),56rem)}
html.scrub .hero::after{content:"";display:block;height:var(--scrub)}
html.scrub .hero-stage{position:sticky;top:var(--hh);height:var(--stage-h);margin-bottom:calc(-1 * var(--stage-h))}
html.scrub .hero>.wrap{min-height:var(--stage-h)}
.hint-scrub,html:not(.scrub) .handoff{display:none}
html.scrub .hint-scrub{display:inline}
.handoff{position:absolute;left:50%;top:1.25rem;margin:0;opacity:0;white-space:nowrap;transform:translateX(-50%);pointer-events:none}
.hero-glow{position:absolute;inset:0;z-index:-2;pointer-events:none;background:radial-gradient(40% 55% at 70% 48%,rgba(0,212,255,.22),rgba(0,212,255,.05) 60%,transparent)}
#orbit{position:absolute;inset:0;z-index:-1;width:100%;height:100%;touch-action:pan-y}
.hero-copy{max-width:38rem;padding:3.5rem 0}
.pill{display:inline-flex;align-items:center;gap:.5rem;padding:.375rem .875rem .375rem .5rem;border-radius:999px;border:1px solid rgba(71,232,255,.3);background:rgba(17,30,49,.72);font-size:.875rem;line-height:1.35;color:var(--text-soft)}
.pill b{display:inline-grid;place-items:center;min-width:26px;height:26px;padding:0 6px;border-radius:999px;background:var(--primary);color:var(--bg);font:700 .6875rem/1 var(--mono)}
.name{margin:1.375rem 0 0;font:750 clamp(2.5rem,1.2rem + 5vw,4.75rem)/1.02 var(--sans);letter-spacing:-.045em;text-wrap:balance}
.headline{margin:1.375rem 0 0;max-width:34ch;color:var(--text-soft);font-size:clamp(1.0625rem,1rem + .4vw,1.25rem);font-weight:500;line-height:1.5}
.lede{margin:1rem 0 0;max-width:52ch;color:var(--text-soft)}
.cta{display:flex;flex-wrap:wrap;gap:.75rem;margin-top:1.875rem}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;min-height:46px;padding:.625rem 1.25rem;border:1px solid transparent;border-radius:11px;font:600 .9375rem/1.2 var(--sans);text-align:center;text-decoration:none;cursor:pointer}
.btn.primary{background:var(--primary);color:var(--bg);box-shadow:0 12px 30px rgba(0,212,255,.25)}
.btn.primary:hover{background:var(--primary-light);color:var(--bg)}
.btn.ghost{background:rgba(255,255,255,.04);border-color:var(--control);color:var(--c-text)}
.btn.ghost:hover{border-color:var(--primary-light);color:var(--c-text)}
.hint{display:flex;align-items:center;gap:.625rem;margin:1.875rem 0 0;font:500 .8125rem/1.4 var(--mono);color:var(--text-soft)}
.hint::before,.dot{content:"";width:8px;height:8px;flex:none;border-radius:50%;background:var(--primary);box-shadow:0 0 0 4px rgba(0,212,255,.18)}
@media (max-width:51.25rem){
 .hero>.wrap{align-items:flex-end}
 .hero>.wrap::before{content:"";position:absolute;inset:0 -1.25rem;z-index:-1;pointer-events:none;background:linear-gradient(transparent 8rem,rgba(4,8,18,.9) 12.5rem,var(--bg))}
 .hero-glow{background:radial-gradient(70% 36% at 50% 22%,rgba(0,212,255,.22),transparent 70%)}
 .hero-copy{padding:13rem 0 2.25rem}
 .cta .btn{flex:1 1 auto}
}

/* sections */
.sec{position:relative;padding:clamp(4.5rem,3rem + 5vw,7rem) 0}
.mist{background:var(--c-mist)}
.sec-head{max-width:46rem;margin-bottom:clamp(2.25rem,2rem + 1.5vw,3.5rem)}
.kicker{display:inline-flex;align-items:center;gap:.625rem;margin:0 0 1rem;font:600 .78rem/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--c-muted)}
.kicker::before{content:"";order:-2;width:26px;height:1.5px;background:currentColor}
.kicker::after{content:"";order:-1;width:8px;height:8px;margin-left:-10px;border:1.5px solid currentColor;border-radius:50%}
.on-dark .kicker{color:var(--primary-light)}
.sec-title{font:800 clamp(1.875rem,1.2rem + 2.6vw,3rem)/1.08 var(--sans);letter-spacing:-.035em;text-wrap:balance}
.note{margin:1.125rem 0 0;max-width:40rem;color:var(--c-muted);font-size:1.0625rem}
.tag{display:inline-flex;align-items:center;gap:.5rem;font:600 .75rem/1.3 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--c-muted)}
.tag::before{content:"";width:8px;height:8px;flex:none;border-radius:50%;background:var(--area,var(--primary))}
.chips{display:flex;flex-wrap:wrap;gap:.375rem}
.chips li{display:inline-flex;align-items:center;gap:.375rem;padding:.3rem .625rem;border:1px solid var(--c-line);border-radius:8px;background:var(--c-card);font:600 .75rem/1.3 var(--mono);color:var(--c-text)}
.chips li::before{content:"";width:7px;height:7px;flex:none;border-radius:50%;background:var(--primary)}

/* about + numbers */
.about-grid{display:grid;gap:2.5rem}
.about-text{margin:0;max-width:36ch;font-size:clamp(1.3rem,1rem + 1.2vw,1.875rem);font-weight:600;line-height:1.35;letter-spacing:-.02em}
.facts{display:grid;gap:1.5rem;margin:0}
.facts > div{padding:1.25rem 1.375rem;border:1px solid var(--c-line);border-radius:14px;background:var(--c-card)}
.facts dt{margin-bottom:.5rem;font:600 .75rem/1.3 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--c-muted)}
.facts dd{margin:0}
.facts dd li + li{margin-top:.25rem}
@media (min-width:60rem){.about-grid{grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);gap:4rem;align-items:start}}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,14rem),1fr));gap:1rem}
.stat{position:relative;padding:1.75rem 1.5rem;border:1px solid var(--c-line);border-radius:var(--r);background:var(--c-card);box-shadow:var(--sh-l)}
.stat::before{content:"";position:absolute;top:-1px;left:1.5rem;width:3rem;height:3px;border-radius:0 0 3px 3px;background:var(--primary)}
.stat .v{margin:0 0 .625rem;font:700 clamp(2.25rem,1.5rem + 2.4vw,3.5rem)/1 var(--mono);letter-spacing:-.05em;font-variant-numeric:tabular-nums;white-space:nowrap;overflow-wrap:normal}
.stat .l{margin:0;max-width:28ch;color:var(--c-muted)}

/* stack marquee (static wrapped list unless motion is allowed) */
.stack-sec{padding:clamp(3.5rem,3rem + 3vw,5rem) 0}
.stack-sec .sec-head{margin-bottom:2rem}
.mq{display:grid;gap:.75rem;padding-inline:max(1.25rem,(100% - var(--max)) / 2)}
.mq-row{display:flex}
.mq-track{display:flex;flex-wrap:wrap;gap:.625rem}
.mq-track[aria-hidden="true"]{display:none}
.mq-track li{display:inline-flex;align-items:center;gap:.5rem;padding:.625rem 1.125rem;border:1px solid var(--c-line);border-radius:12px;background:var(--c-card);font:600 clamp(.875rem,.82rem + .25vw,1rem)/1.2 var(--mono);white-space:nowrap}
.mq-track li::before{content:"";width:8px;height:8px;border-radius:50%;border:2px solid var(--primary);box-shadow:0 0 0 3px rgba(0,212,255,.14)}
.mq-row.rev li{color:var(--c-muted)}
"""
