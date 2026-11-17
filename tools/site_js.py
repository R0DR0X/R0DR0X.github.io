"""Page scripts: header controls, reveals, counters, filter, print, hero sphere.

HEAD_JS runs in <head>: it restores the theme and the motion pause and sets
html.fx when motion is allowed, before the first paint.
BASE_JS: theme toggle, motion pause (WCAG 2.2.2), menu, section spy, reveal
fallback, cover observer, count-up, area filter and print.
SPHERE_JS: the hero canvas, a hand-written 3D projection of a sphere of skill
nodes (ported from design/portafolio-escorpia/02-orbita-3d.html), steered by
the pointer; it draws one still frame under reduced motion or when paused.
"""

HEAD_JS = ("(function(r){r.classList.add('js');try{var t=localStorage.getItem('theme');"
           "if(t==='dark'||t==='light')r.setAttribute('data-theme',t);"
           "if(localStorage.getItem('motion')==='paused')r.classList.add('motion-paused')}catch(e){}"
           "if(!matchMedia('(prefers-reduced-motion: reduce)').matches)r.classList.add('fx')})(document.documentElement);")

BASE_JS = r"""
(function () {
  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var hasIO = 'IntersectionObserver' in window;
  var viewTL = !!(window.CSS && CSS.supports && CSS.supports('(animation-timeline: view()) and (animation-range: 0% 100%)'));
  function paused() { return root.classList.contains('motion-paused'); }
  function still() { return reduce.matches || paused(); }
  function each(sel, fn) { Array.prototype.forEach.call(document.querySelectorAll(sel), fn); }
  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  var theme = document.getElementById('theme-toggle');
  if (theme) {
    var syncTheme = function () { theme.setAttribute('aria-pressed', root.getAttribute('data-theme') === 'dark' ? 'true' : 'false'); };
    syncTheme();
    theme.hidden = false;
    theme.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      store('theme', next);
      syncTheme();
    });
  }

  var toggle = document.getElementById('motion-toggle');
  if (toggle) {
    var label = toggle.querySelector('.pause-label');
    var sync = function () {
      label.textContent = toggle.getAttribute(paused() ? 'data-resume' : 'data-pause');
      toggle.classList.toggle('is-paused', paused());
    };
    sync();
    toggle.hidden = false;
    toggle.addEventListener('click', function () {
      var on = !paused();
      root.classList.toggle('motion-paused', on);
      store('motion', on ? 'paused' : 'running');
      sync();
      document.dispatchEvent(new CustomEvent('motionchange'));
    });
  }

  var header = document.getElementById('site-header');
  var menu = document.getElementById('menu-toggle');
  var nav = document.getElementById('site-nav');
  if (header && menu && nav) {
    var setMenu = function (open, refocus) {
      header.classList.toggle('menu-open', open);
      menu.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (!open && refocus) menu.focus();
    };
    var isOpen = function () { return menu.getAttribute('aria-expanded') === 'true'; };
    menu.hidden = false;
    menu.addEventListener('click', function () { setMenu(!isOpen()); });
    nav.addEventListener('click', function (ev) { if (ev.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape' && isOpen()) setMenu(false, true); });
    document.addEventListener('click', function (ev) { if (isOpen() && !header.contains(ev.target)) setMenu(false); });
  }

  if (hasIO && nav) {
    var links = {};
    each('#site-nav a[href^="#"]', function (a) { links[a.getAttribute('href').slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        Object.keys(links).forEach(function (id) { links[id].classList.toggle('is-active', id === en.target.id); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    each('main > section[id]', function (s) { spy.observe(s); });
  }

  // The marquee loops two copies of each row; the copy is hidden from assistive tech.
  each('.mq-row', function (row) {
    var copy = row.firstElementChild.cloneNode(true);
    copy.setAttribute('aria-hidden', 'true');
    row.appendChild(copy);
  });

  var revealSel = '.reveal, .tl';
  function showAll() { each(revealSel, function (el) { el.classList.add('is-in'); }); }
  if (!viewTL) {
    if (hasIO) {
      var rio = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('is-in'); rio.unobserve(en.target); } });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.04 });
      each(revealSel, function (el) { rio.observe(el); });
    } else showAll();
  }

  if (hasIO) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { en.target.classList.toggle('is-inview', en.isIntersecting); });
    }, { rootMargin: '80px 0px' });
    each('.cover-host', function (el) { cio.observe(el); });
  } else each('.cover-host', function (el) { el.classList.add('is-inview'); });

  var counters = [];
  each('.tally[data-value]', function (el) {
    var m = el.getAttribute('data-value').match(/^([^\d]*)([\d,.]+)(.*)$/);
    if (!m) return;
    var digits = m[2].replace(/,/g, '');
    counters.push({ el: el, pre: m[1], n: parseFloat(digits), dec: (digits.split('.')[1] || '').length, comma: m[2].indexOf(',') >= 0, post: m[3], done: false });
  });
  function fmt(c, v) {
    var s = v.toFixed(c.dec);
    if (c.comma) s = s.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return c.pre + s + c.post;
  }
  function finish(c) { c.done = true; c.el.textContent = c.el.getAttribute('data-value'); }
  function count(c) {
    if (c.done) return;
    c.done = true;
    if (still()) { finish(c); return; }
    var start = null;
    var tick = function (now) {
      if (start === null) start = now;
      var k = Math.min(1, (now - start) / 1400);
      c.el.textContent = fmt(c, c.n * (1 - Math.pow(1 - k, 3)));
      if (k < 1 && !still()) requestAnimationFrame(tick); else finish(c);
    };
    requestAnimationFrame(tick);
  }
  if (counters.length && hasIO && !still()) {
    counters.forEach(function (c) { c.el.textContent = fmt(c, 0); });
    var sio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        counters.forEach(function (c) { if (c.el === en.target) count(c); });
        sio.unobserve(en.target);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (c) { sio.observe(c.el); });
    var settle = function () { if (still()) counters.forEach(finish); };
    document.addEventListener('motionchange', settle);
    if (reduce.addEventListener) reduce.addEventListener('change', settle);
  }

  var group = document.getElementById('filters');
  if (group) {
    var chips = Array.prototype.slice.call(group.querySelectorAll('button[data-filter]'));
    var items = Array.prototype.slice.call(document.querySelectorAll('#index li[data-area]'));
    var countEl = document.getElementById('count');
    var empty = document.getElementById('empty');
    var emptyArea = document.getElementById('empty-area');
    var apply = function (chip) {
      var area = chip.getAttribute('data-filter');
      var shown = 0;
      chips.forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
      items.forEach(function (item) {
        var match = area === 'all' || item.getAttribute('data-area') === area;
        item.hidden = !match;
        if (match) shown++;
      });
      var noun = shown === 1 ? countEl.getAttribute('data-one') : countEl.getAttribute('data-many');
      countEl.textContent = shown + ' ' + noun + ' · ' + chip.getAttribute('data-label');
      emptyArea.textContent = chip.getAttribute('data-label');
      empty.hidden = shown !== 0;
    };
    var choose = function (chip, then) {
      if (document.startViewTransition && !still()) {
        var vt = document.startViewTransition(function () { apply(chip); });
        if (then) vt.finished.then(then, then);
      } else { apply(chip); if (then) then(); }
    };
    chips.forEach(function (chip) { chip.addEventListener('click', function () { choose(chip); }); });
    document.getElementById('reset').addEventListener('click', function () { choose(chips[0], function () { chips[0].focus(); }); });
    group.hidden = false;
    countEl.hidden = false;
  }

  window.addEventListener('beforeprint', function () {
    each('details', function (dt) { if (!dt.open) { dt.open = true; dt.setAttribute('data-print-open', ''); } });
    counters.forEach(finish);
    showAll();
  });
  window.addEventListener('afterprint', function () {
    each('details[data-print-open]', function (dt) { dt.open = false; dt.removeAttribute('data-print-open'); });
  });
})();
"""
