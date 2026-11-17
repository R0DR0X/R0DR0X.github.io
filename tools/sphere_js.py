"""Hero canvas: a rotating sphere of skill nodes (D2 "Orbita 3D", trimmed).

Fibonacci sphere, three nearest-neighbour links per node, perspective
projection, depth-faded labels from the skill chips named by data-labels and a
pointer that steers yaw and pitch. The loop stops off screen, in hidden tabs,
when animations are paused and under reduced motion (one still frame).
"""

SPHERE_JS = r"""
(function () {
  var cv = document.getElementById('orbit');
  var cx = cv && cv.getContext && cv.getContext('2d');
  if (!cx) return;
  var d = document, W = window, root = d.documentElement;
  var hero = cv.closest('.hero') || cv.parentNode, copy = hero.querySelector('.hero-copy');
  // Labels are the skill chips already on the page (selector in data-labels).
  var SK = Array.prototype.map.call(d.querySelectorAll(cv.getAttribute('data-labels') || '#skills li'), function (li) { return li.textContent; });
  if (!SK.length) SK = ['·'];
  var rm = W.matchMedia('(prefers-reduced-motion: reduce)');
  var MONO = getComputedStyle(root).getPropertyValue('--mono') || 'monospace';
  var cw = 0, ch = 0, small = null, N = 0, nodes = [], E = [];
  var yaw = .7, pitch = -.32, yawV = .16, tYawV = .16, tPitch = -.32, mouse = { x: -1e4, y: -1e4 };
  var vis = true, raf = 0, last = 0;
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function sstep(a, b, v) { v = clamp((v - a) / (b - a), 0, 1); return v * v * (3 - 2 * v); }
  function still() { return rm.matches || root.classList.contains('motion-paused'); }
  function build() {
    N = small ? 44 : 96; nodes = []; E = [];
    var L = SK.length, i, j, seen = {};
    for (i = 0; i < N; i++) {
      var y = 1 - 2 * (i + .5) / N, r = Math.sqrt(1 - y * y), th = i * 2.39996323;
      var li = Math.floor(i * L / N), lab = (small || li !== Math.floor((i - 1) * L / N)) ? SK[li] : null;
      nodes.push({ x: Math.cos(th) * r, y: y, z: Math.sin(th) * r, lab: lab });
    }
    for (i = 0; i < N; i++) {
      var best = [];
      for (j = 0; j < N; j++) if (i !== j) best.push([nodes[i].x * nodes[j].x + nodes[i].y * nodes[j].y + nodes[i].z * nodes[j].z, j]);
      best.sort(function (a, b) { return b[0] - a[0]; });
      for (j = 0; j < 3; j++) {
        var k = Math.min(i, best[j][1]) + '-' + Math.max(i, best[j][1]);
        if (!seen[k]) { seen[k] = 1; E.push([nodes[i], nodes[best[j][1]]]); }
      }
    }
  }
  function size() {
    var r = cv.getBoundingClientRect(), dpr = Math.min(W.devicePixelRatio || 1, 2);
    cw = Math.max(1, r.width); ch = Math.max(1, r.height);
    cv.width = Math.round(cw * dpr); cv.height = Math.round(ch * dpr);
    cx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var s = cw < 820;
    if (s !== small) { small = s; build(); }
  }
  function draw() {
    var free = small ? Math.max(ch * .3, copy.offsetTop + parseFloat(getComputedStyle(copy).paddingTop || 0)) : ch;
    var R = small ? Math.min(cw * .36, free * .4) : Math.min(cw * .25, ch * .38);
    var ox = small ? cw * .5 : cw * .7, oy = small ? free * .52 : ch * .5, D = 4;
    var cY = Math.cos(yaw), sY = Math.sin(yaw), cP = Math.cos(pitch), sP = Math.sin(pitch), i, n;
    for (i = 0; i < N; i++) {
      n = nodes[i];
      var x1 = n.x * cY + n.z * sY, z1 = -n.x * sY + n.z * cY, y2 = n.y * cP - z1 * sP, z2 = n.y * sP + z1 * cP, k = D / (D - z2);
      n.sx = ox + x1 * R * k; n.sy = oy - y2 * R * k; n.k = k; n.dz = clamp((z2 + 1) / 2, 0, 1); n.a = clamp(.14 + .86 * n.dz, 0, 1);
    }
    cx.clearRect(0, 0, cw, ch);
    cx.lineWidth = 1;
    for (i = 0; i < E.length; i++) {
      var e = E[i], a = (e[0].a + e[1].a) * .17;
      if (a < .01) continue;
      cx.strokeStyle = 'rgba(71,232,255,' + a.toFixed(3) + ')';
      cx.beginPath(); cx.moveTo(e[0].sx, e[0].sy); cx.lineTo(e[1].sx, e[1].sy); cx.stroke();
    }
    var order = nodes.slice().sort(function (p, q) { return p.dz - q.dz; });
    var hov = null, hd = 34 * 34, labs = [], fs = small ? 10 : 11;
    for (i = 0; i < N; i++) {
      n = nodes[i];
      if (n.dz < .55 || !n.lab) continue;
      var dx = n.sx - mouse.x, dy = n.sy - mouse.y, q = dx * dx + dy * dy;
      if (q < hd) { hd = q; hov = n; }
    }
    cx.textBaseline = 'middle';
    for (i = 0; i < N; i++) {
      n = order[i];
      var rad = (n.lab ? 2.4 : 1.6) * n.k * (small ? .95 : 1.1);
      if (n.dz > .7) { cx.fillStyle = 'rgba(0,212,255,' + (.1 * n.a).toFixed(3) + ')'; cx.beginPath(); cx.arc(n.sx, n.sy, rad * 3.4, 0, 6.2832); cx.fill(); }
      cx.fillStyle = n === hov ? '#ffffff' : 'rgba(0,212,255,' + n.a.toFixed(3) + ')';
      cx.beginPath(); cx.arc(n.sx, n.sy, n === hov ? rad * 1.6 : rad, 0, 6.2832); cx.fill();
      if (n === hov) { cx.strokeStyle = 'rgba(71,232,255,.9)'; cx.beginPath(); cx.arc(n.sx, n.sy, rad * 4, 0, 6.2832); cx.stroke(); }
      if (!n.lab) continue;
      var la = n === hov ? 1 : sstep(small ? .72 : .6, .92, n.dz);
      if (la < .04) continue;
      var f = Math.max(8, fs * n.k * (n === hov ? 1.15 : 1));
      cx.font = '600 ' + f.toFixed(1) + 'px ' + MONO;
      labs.push({ t: n.lab, x: n.sx + rad + 6, y: n.sy, w: cx.measureText(n.lab).width, f: f, a: la, h: n === hov, z: n.dz });
    }
    labs.sort(function (p, q) { return (q.h - p.h) || (q.z - p.z); });
    var placed = [];
    for (i = 0; i < labs.length; i++) {
      var l = labs[i], bx = [l.x - 3, l.y - l.f * .6, l.x + l.w + 3, l.y + l.f * .6], hit = false;
      if (!l.h && (bx[0] < 2 || bx[2] > cw - 2)) continue;
      for (var j = 0; j < placed.length; j++) {
        var p = placed[j];
        if (bx[0] < p[2] && bx[2] > p[0] && bx[1] < p[3] && bx[3] > p[1]) { hit = true; break; }
      }
      if (hit) continue;
      placed.push(bx);
      cx.font = '600 ' + l.f.toFixed(1) + 'px ' + MONO;
      cx.fillStyle = l.h ? '#ffffff' : 'rgba(214,224,234,' + l.a.toFixed(3) + ')';
      cx.fillText(l.t, l.x, l.y);
    }
  }
  function running() { return vis && !d.hidden && !still(); }
  function tick(ts) {
    raf = 0;
    var dt = Math.min(50, Math.max(0, ts - last) || 16); last = ts;
    yawV += (tYawV - yawV) * .05; yaw += yawV * dt / 1000; pitch += (tPitch - pitch) * .05;
    draw();
    if (running()) raf = requestAnimationFrame(tick);
  }
  function update() {
    if (running()) { if (!raf) { last = performance.now(); raf = requestAnimationFrame(tick); } return; }
    if (raf) { cancelAnimationFrame(raf); raf = 0; }
    draw();
  }
  W.addEventListener('pointermove', function (e) {
    if (!vis || still()) return;
    var r = cv.getBoundingClientRect();
    mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top;
    tYawV = .16 + (clamp(mouse.x / r.width, 0, 1) - .5) * 1.5;
    tPitch = -.32 + (clamp(mouse.y / r.height, 0, 1) - .5) * .9;
  }, { passive: true });
  d.addEventListener('pointerleave', function () { mouse.x = mouse.y = -1e4; tYawV = .16; tPitch = -.32; });
  var timer = 0;
  W.addEventListener('resize', function () { clearTimeout(timer); timer = setTimeout(function () { size(); draw(); }, 120); });
  if ('IntersectionObserver' in W) new IntersectionObserver(function (en) { vis = en[0].isIntersecting; update(); }).observe(hero);
  d.addEventListener('visibilitychange', update);
  d.addEventListener('motionchange', update);
  if (rm.addEventListener) rm.addEventListener('change', update);
  size();
  update();
})();
"""
