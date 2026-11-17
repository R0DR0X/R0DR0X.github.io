"""Stylesheet for the lower sections, the motion layer and print.

SECTIONS_CSS: project grid, methods, skills, experience, contact, footer.
MOTION_CSS: every animation and transition, only under no-preference.
PRINT_CSS: the light A4 layout used for the portfolio PDF.
"""

SECTIONS_CSS = """
/* all projects */
.filters{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:1rem}
.chip{display:inline-flex;align-items:center;gap:.5rem;min-height:44px;padding:0 1rem;border:1px solid var(--control);border-radius:999px;background:var(--c-card);color:var(--c-text);font:500 .9375rem/1.2 var(--sans);cursor:pointer}
.chip .n{font:600 .8125rem/1 var(--mono);color:var(--c-muted)}
.chip:hover{border-color:var(--c-text)}
.chip[aria-pressed="true"]{border-color:var(--c-text);background:var(--c-text);color:var(--c-page);font-weight:650}
.chip[aria-pressed="true"] .n{color:var(--c-page)}
.count{margin:0 0 1.5rem;font:500 .875rem/1.4 var(--mono);color:var(--c-muted)}
.empty{margin-bottom:1.5rem;padding:1.5rem;border:1px dashed var(--control);border-radius:var(--r)}
.empty p{margin:0 0 1rem}
.empty .btn{border-color:var(--control);background:transparent;color:var(--c-text)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,19rem),1fr));gap:1.25rem}
.card{position:relative;display:flex;flex-direction:column;overflow:hidden;border:1px solid var(--c-line);border-radius:var(--r);background:var(--c-card);box-shadow:var(--sh-l)}
.card:hover{border-color:var(--control)}
.card-cover{position:relative;aspect-ratio:16/9;overflow:hidden;border-bottom:1px solid var(--c-line);background:var(--cover-bg);--cover-bg:var(--cover-bg);--cover-line:var(--steel);--cover-line-2:var(--sea);--cover-accent:var(--area);--cover-glow:var(--area)}
.card-cover .cover{width:100%;height:100%}
.card-body{display:flex;flex:1;flex-direction:column;padding:1.125rem 1.25rem 1.25rem}
.card-top{display:flex;align-items:center;justify-content:space-between;gap:1rem;margin:0 0 .625rem}
.card-top .n{font:700 1rem/1 var(--mono);color:var(--c-text)}
.card h3{margin:0 0 .375rem;font:800 1.1875rem/1.25 var(--sans);letter-spacing:-.02em}
.card h3 a{color:var(--c-text);text-decoration:none}
.card h3 a:hover{text-decoration:underline}
.card .meta{margin:0 0 .625rem;font:500 .8125rem/1.5 var(--mono);color:var(--c-muted)}
.card .summary{margin:0 0 1rem;font-size:.9375rem;color:var(--c-muted)}
.card details{margin-top:auto;border-top:1px solid var(--c-line)}
.card summary{display:flex;align-items:center;justify-content:space-between;min-height:44px;font:600 .8125rem/1.3 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--c-link);cursor:pointer;list-style:none}
.card summary::-webkit-details-marker{display:none}
.card summary::after{content:"+";font-size:1.25rem;line-height:1;color:var(--c-text)}
.card details[open] summary::after{content:"\\2212"}
.hl{margin:0 0 1rem;padding:0;list-style:none;display:grid;gap:.5rem}
.hl li{position:relative;padding-left:1.375rem}
.hl li::before{content:"";position:absolute;left:2px;top:.55em;width:8px;height:8px;border:1.5px solid var(--primary);border-radius:2px;transform:rotate(45deg)}
.card .hl{margin:.5rem 0 1rem;font-size:.9375rem}
.stack-label{margin:0 0 .5rem;font:600 .75rem/1.3 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--c-muted)}
.go{display:inline-flex;align-items:center;min-height:44px;margin-top:.25rem;font:600 .875rem/1.2 var(--mono)}

/* methods, skills */
.methods{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,19rem),1fr));gap:1rem}
.method{padding:1.5rem;border:1px solid var(--c-line);border-radius:var(--r);background:var(--c-card)}
.m-num{display:inline-grid;place-items:center;width:2.5rem;height:2.5rem;border-radius:11px;background:var(--bg);color:var(--primary-light);font:700 .875rem/1 var(--mono)}
.method h3{margin:1rem 0 .5rem;font:800 1.1875rem/1.25 var(--sans);letter-spacing:-.02em}
.method p{margin:0;color:var(--c-muted)}
.skills{margin:0}
.skill{display:grid;gap:.875rem;padding:1.375rem 0;border-top:1px solid var(--c-line)}
.skill dt{font:600 .8125rem/1.4 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--c-muted)}
.skill dd{margin:0}
@media (min-width:48rem){.skill{grid-template-columns:15rem minmax(0,1fr);gap:2rem}}

/* experience timeline */
.tl{position:relative;padding-left:2.5rem}
.tl-line{position:absolute;left:.5rem;top:.5rem;bottom:.5rem;width:2px;background:var(--c-line)}
.tl-line span{position:absolute;inset:0;transform-origin:50% 0;background:var(--primary)}
.timeline li{position:relative;padding-bottom:2.75rem}
.timeline li:last-child{padding-bottom:0}
.tl-dot{position:absolute;left:calc(-2.5rem + .5rem + 1px - 9px);top:.3rem;width:18px;height:18px;border:2px solid var(--control);border-radius:50%;background:var(--c-page)}
.tl-dot i{position:absolute;inset:3px;border-radius:50%;background:var(--primary)}
.tl-dot.now{border-color:var(--primary)}
.when{margin:0 0 .375rem;font:600 .875rem/1.4 var(--mono);color:var(--c-muted)}
.timeline h3{font:800 1.25rem/1.25 var(--sans);letter-spacing:-.02em}
.org{margin:.25rem 0 0;color:var(--c-muted)}
.timeline .body{margin:.625rem 0 0;max-width:62ch}
@media (min-width:48rem){.timeline li{display:grid;grid-template-columns:11rem minmax(0,1fr);gap:2rem}}
.more{display:grid;gap:0 2.5rem;grid-template-columns:repeat(auto-fill,minmax(min(100%,26rem),1fr))}
.more li{position:relative;padding:1rem 0 1rem 1.75rem;border-top:1px solid var(--c-line)}
.more li::before{content:"+";position:absolute;left:0;top:1rem;font:700 1rem/1.6 var(--mono);color:var(--c-link)}

/* contact card + footer */
.cta-card{position:relative;isolation:isolate;overflow:hidden;padding:clamp(2.5rem,2rem + 4vw,5rem) clamp(1.375rem,1rem + 4vw,4.5rem);border-radius:28px;box-shadow:var(--sh-d)}
.cta-card::before{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;background:radial-gradient(36rem 22rem at 85% 0%,rgba(0,212,255,.22),transparent 70%),radial-gradient(28rem 18rem at 0% 100%,rgba(0,212,255,.1),transparent 70%)}
.contact-title{margin:0 0 1.25rem;max-width:18ch;font:800 clamp(2rem,1.2rem + 3.6vw,3.75rem)/1.04 var(--sans);letter-spacing:-.04em;text-wrap:balance}
.contact-text{margin:0 0 2rem;max-width:52ch;color:var(--c-muted);font-size:1.0625rem}
.contact-links{display:flex;flex-wrap:wrap;gap:.25rem 1.5rem;margin-top:1.75rem}
.contact-links a{display:inline-flex;align-items:center;min-height:44px;font:500 .9375rem/1.3 var(--mono);overflow-wrap:anywhere}
.site-footer{padding:2rem 0 2.5rem;font:500 .8125rem/1.6 var(--mono);color:var(--c-muted)}
.site-footer .wrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:.5rem 2rem}
.site-footer p{margin:0}
.site-footer a{display:inline-flex;align-items:center;min-height:44px}
"""

MOTION_CSS = """
@media (prefers-reduced-motion: no-preference){
 html{scroll-behavior:smooth}
 .btn,.chip,.icon-btn,.lang a,.card,.site-nav a,.chap-index a{transition:background-color .2s,border-color .2s,color .2s,transform .2s}
 .btn:hover{transform:translateY(-1px)}
 .hint::before{animation:ping 2.4s var(--ease) infinite}
 .mq{overflow:hidden;padding-inline:0;-webkit-mask-image:linear-gradient(90deg,transparent,#000 7%,#000 93%,transparent);mask-image:linear-gradient(90deg,transparent,#000 7%,#000 93%,transparent)}
 .mq-row{width:max-content}
 .mq-track,.mq-track[aria-hidden="true"]{display:flex;flex-wrap:nowrap;padding-right:.625rem;animation:marquee var(--dur,90s) linear infinite}
 .mq-row.rev .mq-track{animation-direction:reverse}
 .mq:hover .mq-track,.mq:focus-within .mq-track,html.motion-paused .mq-track{animation-play-state:paused}
 html.motion-paused .hint::before{animation:none}
 @supports ((animation-timeline: scroll()) and (animation-range: 0% 100%)){
  .progress{display:block;animation:grow-x linear both;animation-timeline:scroll(root block)}
 }
 @supports ((animation-timeline: view()) and (animation-range: 0% 100%)){
  html.js:not(.motion-paused) .reveal{animation:rise linear both;animation-timeline:view();animation-range:cover calc(var(--i, 0) * 40px) cover calc(220px + var(--i, 0) * 40px)}
  .tl{view-timeline:--tl block}
  html.js:not(.motion-paused) .tl-line span{animation:grow-y linear both;animation-timeline:--tl;animation-range:entry 10% entry 100%}
 }
 @supports not ((animation-timeline: view()) and (animation-range: 0% 100%)){
  html.js:not(.motion-paused) .reveal:not(.is-in){opacity:0;transform:translateY(22px)}
  html.js .reveal{transition:opacity .7s var(--ease),transform .7s var(--ease);transition-delay:calc(var(--i, 0) * 70ms)}
  html.js:not(.motion-paused) .tl:not(.is-in) .tl-line span{transform:scaleY(0)}
  html.js .tl-line span{transition:transform 1.6s var(--ease)}
 }
 .boot .ld::after{animation:load 1.6s ease-in-out infinite}
 html.motion-paused .boot .ld::after{animation:none}
 @keyframes rise{from{opacity:0;transform:translateY(32px)}to{opacity:1;transform:none}}
 @keyframes grow-x{to{transform:scaleX(1)}}
 @keyframes grow-y{from{transform:scaleY(0)}to{transform:scaleY(1)}}
 @keyframes ping{0%{box-shadow:0 0 0 0 rgba(0,212,255,.5)}80%,100%{box-shadow:0 0 0 10px rgba(0,212,255,0)}}
 @keyframes marquee{to{transform:translateX(-100%)}}
 @keyframes load{from{transform:translateX(-100%)}to{transform:translateX(230%)}}
 ::view-transition-group(*){animation-duration:.38s;animation-timing-function:var(--ease)}
}
"""

PRINT_CSS = """
@media print{
 @page{size:A4;margin:13mm 14mm 14mm}
 :root,[data-theme="dark"],.on-dark{--c-page:var(--print-paper);--c-text:var(--print-ink);--c-muted:var(--print-muted);--c-mist:var(--print-paper);--c-card:var(--print-paper);--c-line:var(--print-rule);--c-link:var(--print-accent);--text-soft:var(--print-muted);--white:var(--print-ink);--primary:var(--print-accent);--primary-light:var(--print-accent);--highlight:transparent}
 *,*::before,*::after{animation:none!important;transition:none!important;box-shadow:none!important;text-shadow:none!important}
 html{font-size:8.75pt;color-scheme:light;background:#ffffff}
 body{background:#ffffff;color:var(--c-text);line-height:1.45;-webkit-print-color-adjust:exact;print-color-adjust:exact}
 .on-dark,.mist{background:#ffffff}
 .skip,.site-header,#orbit,.hero-glow,.hero::after,.hint,.cta,.stack-sec,.filters,.count,.empty,.card-cover,.go,.tl-line,.tl-dot,.site-footer .top,.card.is-featured .summary,.card.is-featured details,.chap-index,.stage,.dev-cell,.story-head .lead-fx,.mod-shot,.ch-link,.pill b{display:none!important}
 .reveal,.ch-text{opacity:1!important;transform:none!important}
 .card[hidden]{display:block!important}
 .print-only{display:block}
 .wrap{width:auto;margin:0}
 a{color:inherit;text-decoration:none}
 .hero{display:block;min-height:0;overflow:visible;padding:0 0 3mm;border-bottom:1px solid var(--c-line)}
 .hero-copy{max-width:none;padding:0}
 .pill{padding:0;border:0;background:none;font-size:.85rem}
 .name{margin:1mm 0;font-size:2.6rem;letter-spacing:-.02em}
 .headline,.lede{margin:0 0 1mm;max-width:none;color:var(--c-text)}
 .sec,.story{padding:3mm 0!important}
 .sec + .sec{border-top:1px solid var(--c-line)}
 .cta-card{padding:0;border-radius:0}
 .cta-card::before{display:none}
 .sec-head,.story-head{margin-bottom:2mm;min-height:0!important;padding:0!important;break-after:avoid}
 .kicker{margin-bottom:1mm}
 .kicker::before,.kicker::after{display:none}
 .sec-title,.story-head h2{font-size:1.65rem;letter-spacing:-.01em}
 .note{margin-top:1mm;max-width:none}
 .about-grid{grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);gap:6mm}
 .about-text{max-width:none;font-size:1.1rem;font-weight:500}
 .facts{gap:2mm}
 .facts > div,.stat,.method,.card,.mod{padding:1.2mm 0;border:0;border-radius:0;background:none}
 .hl{gap:.4mm}
 .stats{grid-template-columns:repeat(4,minmax(0,1fr));gap:3mm}
 .stat::before{display:none}
 .stat .v{margin-bottom:1mm;font-size:1.8rem}
 .stat .v .tally{display:none}
 .stat .v .sr-only{position:static;width:auto;height:auto;margin:0;overflow:visible;clip:auto;white-space:nowrap}
 .story-grid,.chapters,.chapter{display:block!important;min-height:0!important}
 .chapter{padding:2.5mm 0!important;border-top:1px solid var(--c-line)}
 .ch-meta,.ch-sum{margin-top:1mm}
 .mods{margin-top:1.5mm}
 .ch-kicker .num{background:none;color:var(--c-text);padding:0}
 .chapter h3{font-size:1.35rem}
 .prod{display:inline}
 .ch-meta .pill{display:inline;margin-right:.5em}
 .ch-text details > summary{display:none}
 details::details-content{content-visibility:visible;display:block}
 .story::before{display:none}
 .impact{padding:1mm 0;border:0;background:none}
 .mods-h{margin-bottom:1mm}
 .mod-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1mm 6mm}
 .mod{break-inside:avoid;border-top:1px solid var(--c-line)!important}
 .mod-top{margin-bottom:.5mm}
 .mod-n{padding:0;background:none;color:var(--c-text)}
 .mod h4{font-size:1rem}
 .mod dl{display:block}
 .mod dl > div,.mod .sv{margin-top:.5mm;padding:0;border:0;border-radius:0;background:none}
 .mod dt{display:inline;margin-right:.4em;font-size:.7rem}
 .mod dd{display:inline;margin:0;font-size:.9rem;line-height:1.35}
 .mod-list,.mod-top{break-before:avoid}
 .ch-text .hl{margin:1mm 0;font-size:.95rem}
 .chips{display:block}
 .chips li,.ch-text .chips li{display:inline;padding:0;border:0;background:none;font-size:.8rem}
 .chips li::before{display:none}
 .chips li:not(:last-child)::after{content:" \\00b7 "}
 .stack-label{display:inline;margin-right:.5em}
 .hl li{padding-left:1.1rem}
 .cards,.more{display:block}
 .methods{grid-template-columns:repeat(3,minmax(0,1fr));gap:0 6mm}
 .card{border-top:1px solid var(--c-line)}
 .card-body{padding:0}
 .card-top{justify-content:flex-start;margin-bottom:.5mm}
 .card h3{font-size:1.1rem}
 .card .summary{margin-bottom:.5mm;color:var(--c-text);font-size:1rem}
 .card .hl{margin:.5mm 0;font-size:.95rem}
 .card details{border:0}
 .card details > summary{display:none}
 .method h3{margin:1mm 0;font-size:1.15rem}
 .m-num{width:auto;height:auto;background:none;color:var(--c-text)}
 .skill{grid-template-columns:11rem minmax(0,1fr);gap:1rem;padding:1.25mm 0}
 .tl{padding-left:0}
 .timeline li{display:grid;grid-template-columns:8rem minmax(0,1fr);gap:1rem;padding-bottom:3mm}
 .more li{padding:.75mm 0 .75mm 1.25rem;border:0}
 .contact-title{max-width:none;margin-bottom:1mm;font-size:1.65rem}
 .contact-text{margin-bottom:1mm;font-size:1rem}
 .contact-links{margin-top:0}
 .contact-links a{min-height:0}
 .site-footer{padding:2mm 0 0}
 .card,.method,.timeline li,.skill,.stat,.more li{break-inside:avoid;page-break-inside:avoid}
 h2,h3,.ch-kicker,.card-top{break-after:avoid;page-break-after:avoid}
 p,li{orphans:3;widows:3}
}
"""
