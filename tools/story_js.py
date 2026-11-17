"""Scroll scene of the featured-work story (ported from the D3 artboard).

Wide screens (html.fx and the wide media query): one pinned laptop + phone
stage; its lid opens with the story intro, then the screen swaps per chapter
(and per screenshot inside a chapter) while the phone joins for chapters that
have one. Narrow screens: each chapter animates its own device. Reduced motion
removes html.fx and leaves the static, fully readable layout. Runs before the
cover observer so cloned covers are observed too.
"""

STORY_JS = r"""
(()=>{
const d=document,R=d.documentElement,$=(s,c=d)=>c.querySelector(s),$$=(s,c=d)=>[...c.querySelectorAll(s)];
const story=$('#work'),stage=$('#stage-dev');if(!story||!stage)return;
const clamp=(v,a=0,b=1)=>Math.min(b,Math.max(a,v)),sm=t=>{t=clamp(t);return t*t*(3-2*t)},lerp=(a,b,t)=>a+(b-a)*t;
const rm=matchMedia('(prefers-reduced-motion: reduce)'),wq=matchMedia('(min-width: 62.5rem) and (min-height: 35rem)');
const hdr=$('#site-header'),head=$('.story-head',story),idx=$('.chap-index',story),chs=$$('.chapter',story);
const texts=chs.map(c=>$('.ch-text',c)),devs=chs.map(c=>$('.dev',c));
const lapS=chs.map(c=>$('.lid .shots',c)),phS=chs.map(c=>$('.phone .shots',c));
const links=$$('a[data-i]',idx),ol=$('ol',idx),cap=$('.stage-cap',story);
const n=chs.length,P=devs.map(v=>v.classList.contains('has-phone')?1:0),FR=devs.map(v=>v.classList.contains('ph-lead')?1:0),Y=[-12,11,-9,13,-11,9,-13,14];
const names=links.map(a=>$('.l',a).textContent);
// Cloned covers keep unique ids: rename every id inside the clone and its #references.
const reid=el=>{const ids={};$$('[id]',el).forEach(x=>{ids[x.id]=x.id+'-s';x.id+='-s'});if(!Object.keys(ids).length)return el;
  $$('*',el).forEach(x=>[...x.attributes].forEach(a=>{const v=a.value.replace(/#([\w-]+)/g,(m,k)=>ids[k]?'#'+ids[k]:m);if(v!==a.value)x.setAttribute(a.name,v)}));return el};
// Stage layers: the chapter's device shots plus its module thumbnails, cloned once.
// They load their screenshots only when the layer is about to show.
const gather=(c,dev,thumbs,size)=>{const s=$(dev,c);if(!s)return null;const k=reid(s.cloneNode(true)),seen=new Set($$('img',k).map(i=>i.getAttribute('src')));
  $$(thumbs,c).forEach(i=>{const src=i.getAttribute('src');if(seen.has(src))return;seen.add(src);const w=d.createElement('div'),x=i.cloneNode();
    w.className='shot';x.setAttribute('sizes',size);w.append(x);k.append(w)});return k};
const layer=(box,k)=>{const w=d.createElement('div');w.className='layer';
  $$('img',k).forEach(i=>{i.alt='';i.dataset.src=i.getAttribute('src');i.dataset.srcset=i.getAttribute('srcset')||'';i.removeAttribute('srcset');i.removeAttribute('src')});w.append(k);box.append(w);return k};
const wake=w=>{if(w._w)return;w._w=1;$$('img[data-src]',w).forEach(i=>{if(i.dataset.srcset)i.srcset=i.dataset.srcset;i.src=i.dataset.src})};
const scr=$('.lid .screen',stage),pscr=$('.phone .screen',stage);
const SL=chs.map(c=>layer(scr,gather(c,'.lid .shots','.mod-shot:not(.ph) img','34rem')));
const L=[$('.layer',scr)].concat(SL.map(k=>k.parentNode));
const PL=chs.map(c=>{const k=gather(c,'.phone .shots','.mod-shot.ph img','10rem');return k?layer(pscr,k):null});
const swap=(el,t)=>{if(!el)return;const a=el.children;if(a.length<2)return;const k=Math.min(a.length-1,Math.floor(clamp(t)*a.length));
  if(el._k===k)return;el._k=k;for(let j=0;j<a.length;j++)a[j].classList.toggle('on',j===k)};
let fx=false,wide=false,last=-2;
function fit(){
  devs.forEach(v=>v.style.setProperty('--k',Math.min(1,v.parentElement.clientWidth/760).toFixed(3)));
  if(wide){const st=stage.parentElement;stage.style.setProperty('--k',Math.max(.3,Math.min(1.2,st.clientWidth/740,(st.clientHeight-70)/600)).toFixed(3))}
}
function clearInline(){
  devs.forEach((v,i)=>{['--open','--yaw','--pitch','--ph','--sh','--fr'].forEach(p=>v.style.removeProperty(p));v.classList.toggle('ph-on',!!P[i])});
  texts.forEach(t=>{t.style.opacity='';t.style.transform=''});
  links.forEach(a=>{a.removeAttribute('aria-current');a.style.removeProperty('--p')});last=-2;
}
function setMode(){fx=!rm.matches;wide=fx&&wq.matches;R.classList.toggle('fx',fx);clearInline();fit();tick()}
function tick(){
  if(!fx)return;
  const vh=innerHeight,F=vh*.5,hh=hdr?hdr.offsetHeight:0;
  let f=-1,t=0;const rects=chs.map(c=>c.getBoundingClientRect());
  for(let i=0;i<n;i++)if(rects[i].top<=F){f=i;t=clamp((F-rects[i].top)/rects[i].height)}
  if(f!==last){links.forEach((a,i)=>i===f?a.setAttribute('aria-current','step'):a.removeAttribute('aria-current'));
    if(!wide&&f>=0&&ol.scrollWidth>ol.clientWidth)ol.scrollLeft=links[f].parentElement.offsetLeft-24;last=f}
  links.forEach((a,i)=>a.style.setProperty('--p',i<f?1:i===f?t.toFixed(3):0));
  if(wide){
    const hr=head.getBoundingClientRect(),g0=hh+vh*.15,ip=clamp((g0-hr.top)/(g0-F+hr.height)),open=sm(ip/.7);
    const s=f<0?-1+sm((ip-.84)/.16):f+(f<n-1?sm((t-.9)/.1):0);
    const i0=Math.floor(s),fr=s-i0,yA=i0<0?-28:Y[i0%8],yB=Y[Math.min(n-1,i0+1)%8],pA=i0<0?0:P[i0],pB=P[Math.min(n-1,i0+1)];
    const ph=lerp(pA,pB,fr)*open,st=stage.style,fA=i0<0?0:FR[i0],fB=FR[Math.min(n-1,i0+1)];
    st.setProperty('--open',open.toFixed(3));st.setProperty('--yaw',lerp(yA,yB,fr).toFixed(2)+'deg');
    st.setProperty('--pitch',lerp(-34,-20,open).toFixed(2)+'deg');st.setProperty('--ph',ph.toFixed(3));st.setProperty('--sh',ph.toFixed(3));st.setProperty('--fr',(lerp(fA,fB,fr)*open).toFixed(3));
    stage.classList.toggle('ph-on',ph>.005);
    L.forEach((w,j)=>{const dd=j-1-s,a=Math.abs(dd);if(a<2)wake(w);if(a>=1){w.style.visibility='hidden';return}
      w.style.visibility='inherit';w.style.opacity=(1-a).toFixed(3);w.style.transform=`translate3d(0,${(dd*55).toFixed(2)}%,0) scale(${(1-a*.1).toFixed(3)})`});
    if(f>=0){swap(SL[f],t/.9);swap(PL[f],t/.9)}
    let best=-1,bd=99;PL.forEach((w,j)=>{if(w&&Math.abs(j-s)<bd){bd=Math.abs(j-s);best=j}});
    PL.forEach((w,j)=>{if(!w)return;if(Math.abs(j-s)<2)wake(w.parentNode);w.parentNode.style.visibility=j===best?'inherit':'hidden'});
    const ci=Math.round(s);$('b',cap).textContent=ci<0?cap.dataset.start:`${cap.dataset.ch} ${String(ci+1).padStart(2,'0')} / ${String(n).padStart(2,'0')}`;
    $('.nm',cap).textContent=ci<0?cap.dataset.open:names[ci];$('.track i',cap).style.transform=`scaleX(${clamp((s+1)/n)})`;
    texts.forEach(tx=>{const r=tx.getBoundingClientRect(),dd=r.top<=F&&r.bottom>=F?0:(r.top>F?r.top-F:r.bottom-F)/vh,v=1-clamp(Math.abs(dd)*2.2);
      tx.style.opacity=(.72+.28*v).toFixed(3);tx.style.transform=`translate3d(${((1-v)*-28).toFixed(1)}px,${(dd*-24).toFixed(1)}px,0)`});
  }else{
    devs.forEach((v,i)=>{const r=v.getBoundingClientRect();if(r.bottom<-200||r.top>vh+200)return;
      const p=clamp((vh-r.top)/(vh*.62)),o=sm(p/.8),s=v.style;
      s.setProperty('--open',o.toFixed(3));s.setProperty('--yaw',lerp(-30,Y[i%8]*.55,o).toFixed(2)+'deg');s.setProperty('--pitch',lerp(-34,-20,o).toFixed(2)+'deg');
      if(P[i]){const ph=sm((p-.55)/.4);s.setProperty('--ph',ph.toFixed(3));s.setProperty('--sh',ph.toFixed(3));v.classList.toggle('ph-on',ph>.005)}
      const tc=clamp((vh*.9-r.top)/Math.max(1,rects[i].bottom-r.top));swap(lapS[i],tc);swap(phS[i],tc)});
  }
}
let ticking=false;
addEventListener('scroll',()=>{if(!ticking){ticking=true;requestAnimationFrame(()=>{ticking=false;tick()})}},{passive:true});
addEventListener('resize',()=>{fit();tick()});
const on=(m,f)=>m.addEventListener?m.addEventListener('change',f):m.addListener(f);
on(rm,setMode);on(wq,setMode);
// Chapter index: jump to a chapter and move focus to its heading.
idx.addEventListener('click',e=>{const a=e.target.closest('a[data-i]');if(!a||!fx)return;e.preventDefault();
  const c=chs[+a.dataset.i],off=(hdr?hdr.offsetHeight:0)+(wide?0:idx.offsetHeight+8);
  scrollTo({top:c.getBoundingClientRect().top+scrollY-off+(wide?2:0),behavior:rm.matches?'auto':'smooth'});
  history.replaceState(null,'','#'+c.id);$('h3',c).focus({preventScroll:true})});
setMode();
if(location.hash){const el=d.getElementById(location.hash.slice(1));if(el)requestAnimationFrame(()=>{el.scrollIntoView();tick()})}
})();
"""
