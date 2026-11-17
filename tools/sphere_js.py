"""Hero canvas: the D2 "Orbita 3D" sphere of skills with its scroll scrub.

Fibonacci sphere, three nearest-neighbour links per node, perspective
projection, depth-faded labels from the skill chips named by data-labels and a
pointer that steers yaw and pitch. With motion allowed (html.scrub) the stage
is pinned while the page scrolls: the copy scrolls away, then the sphere
unrolls row by row into a flat grid, tilts into a floor and lights up the
numbered project tiles named by data-tiles (ported from
design/portafolio-escorpia/02-orbita-3d.html). Labels never cover the hero
copy. The loop stops off screen and in hidden tabs; when paused the frame only
follows the scroll; under reduced motion it is one still sphere.

Mobile (S16): the pure helpers between /*pure*/ and /*/pure*/ are pinned by
tests/test_build.py. floorFit sizes and places the final floor so every tile
row sits below the handoff badge inside the stage (centered on narrow
screens); lit/reveal light all tiles by 80 % of the scrub, and the last part
of the pinned scroll (hold) keeps the lit floor still before the next section;
fade masks the copy out under the sticky header so no line peeks below it.
While the copy leaves, the narrow-screen sphere drifts to the stage center.
"""

SPHERE_JS = r"""
(function(){
var cv=document.getElementById('orbit'),cx=cv&&cv.getContext&&cv.getContext('2d');if(!cx)return;
var d=document,W=window,root=d.documentElement,hero=cv.closest('.hero'),stage=cv.parentNode,copy=hero.querySelector('.hero-copy'),hand=hero.querySelector('.handoff'),hdr=d.getElementById('site-header');
var txt=function(s){return [].map.call(d.querySelectorAll(s),function(e){return e.textContent})};
var SK=txt(cv.getAttribute('data-labels')||'#skills li');if(!SK.length)SK=['·'];
var TA=d.querySelectorAll(cv.getAttribute('data-tiles')||'#none'),TL=[].map.call(TA,function(a){var n=a.querySelector('.n'),l=a.querySelector('.l');return [n?n.textContent:'',l?l.textContent:a.textContent]});
var rm=W.matchMedia('(prefers-reduced-motion: reduce)'),MONO=getComputedStyle(root).getPropertyValue('--mono')||'monospace';
var cw=0,ch=0,small=null,N=0,COLS=0,ROWS=0,nodes=[],sE=[],gE=[],tiles=[],F=null,mk0='';
var yaw=.7,pitch=-.32,yawV=.16,tYawV=.16,tPitch=-.32,pT=0,pS=0,mouse={x:-1e4,y:-1e4};
var hl0=0,vis=true,raf=0,last=0,dq=0,scrub=false,headH=0,stageH=0,start=0,len=1,free=0;
/*pure*/function clamp(v,a,b){return v<a?a:v>b?b:v}
function sstep(a,b,v){v=clamp((v-a)/(b-a),0,1);return v*v*(3-2*v)}
function lerp(a,b,t){return a+(b-a)*t}
function lit(p){return sstep(.6,.82,p)}
function reveal(i,hl){return sstep(i*.05,i*.05+.4,hl)}
// Copy fade (top = copy box top, bottom = its last line): once scrolled 64 px, nothing
// shows within 32 px under the header, opaque 32 px lower; o fades the block as it leaves.
function fade(top,bottom,head,stage){var b=32,f=32,k=clamp((head-top)/(b+f),0,1);return {o:clamp((bottom-head-b-f)/(stage*.2),0,1),cut:head-top+b*k,fe:Math.max(1,f*k)}}
// Final floor: unit, center, tilt and the [top,bottom] of each tile row (canvas px); bt = badge bottom.
function floorFit(cw,ch,small,C,R,bt){
 var sp=small?.5:.36,tl=small?.45:.78,cT=Math.cos(tl),sT=Math.sin(tl),r0=Math.floor(R/2)-1,rows=small?[0,2,4,6]:[r0-1,r0+1];
 var K=function(r){return 4/(4+((R-1)/2-r)*sp*sT)},Y=function(r,u){return -((R-1)/2-r)*sp*cT*u*K(r)};
 var u=Math.min(cw*(small?.74:.7),ch*1.15)/((C-1)*sp),g=12,lab=18,av=ch-bt-2*g,oy=ch*.5-tl*ch*.03;
 if(small)u=Math.max(8,Math.min(u,(av-lab-27)/(Y(R-1,1)-Y(0,1))));
 var H=function(r){return small?Math.max(54,sp*u*K(r)*.62):62};
 var a=Y(0,u)-H(0)/2,z=Y(R-1,u)+lab;if(small)oy=bt+g+(av-(z-a))/2-a;
 return {unit:u,oy:oy,tilt:tl,box:[oy+a,oy+z],rows:rows.map(function(r){var y=oy+Y(r,u);return [y-H(r)/2,y+H(r)/2]})}}/*/pure*/
function still(){return rm.matches||root.classList.contains('motion-paused')}
function build(){
 N=small?40:96;COLS=small?5:12;ROWS=Math.ceil(N/COLS);nodes=[];sE=[];gE=[];tiles=[];
 var L=SK.length,i,j,g={},seen={};
 for(i=0;i<N;i++){var y=1-2*(i+.5)/N,r=Math.sqrt(1-y*y),th=i*2.39996323,x=Math.cos(th)*r,z=Math.sin(th)*r,li=Math.floor(i*L/N);
  nodes.push({x:x,y:y,z:z,lat:Math.asin(y),lon:Math.atan2(z,x),lab:(small||li!==Math.floor((i-1)*L/N))?SK[li]:null,pj:-1})}
 var byLat=nodes.slice().sort(function(a,b){return b.lat-a.lat});
 for(var rr=0;rr<ROWS;rr++)byLat.slice(rr*COLS,(rr+1)*COLS).sort(function(a,b){return a.lon-b.lon}).forEach(function(n,c){n.gc=c;n.gr=rr;g[rr+','+c]=n});
 nodes.forEach(function(n){var a=g[n.gr+','+(n.gc+1)],b=g[(n.gr+1)+','+n.gc];if(a)gE.push([n,a]);if(b)gE.push([n,b])});
 for(i=0;i<N;i++){var best=[];for(j=0;j<N;j++)if(i!==j)best.push([nodes[i].x*nodes[j].x+nodes[i].y*nodes[j].y+nodes[i].z*nodes[j].z,j]);
  best.sort(function(a,b){return b[0]-a[0]});
  for(j=0;j<3;j++){var k=Math.min(i,best[j][1])+'-'+Math.max(i,best[j][1]);if(!seen[k]){seen[k]=1;sE.push([nodes[i],nodes[best[j][1]]])}}}
 var r0=Math.floor(ROWS/2)-1,pr,pc,n;
 for(pr=0;pr<(small?4:2);pr++)for(pc=0;pc<(small?2:4);pc++){n=small?g[(pr*2)+','+(1+pc*2)]:g[(r0-1+pr*2)+','+(2+pc*2)];if(n&&tiles.length<TL.length){n.pj=tiles.length;tiles.push(n)}}
}
function layout(){
 scrub=!rm.matches&&TL.length>0;root.classList.toggle('scrub',scrub);
 headH=hdr?hdr.offsetHeight:0;stageH=Math.round(Math.min(innerHeight-headH,960));
 var wrap=copy.parentNode,hs=hero.style,hold=Math.round(stageH*.3);
 hs.setProperty('--stage-h',stageH+'px');hs.setProperty('--scrub',Math.round(Math.min(innerHeight*1.25,1150)+stageH*.45)+hold+'px');
 start=Math.max(0,wrap.offsetHeight-stageH*.55);len=Math.max(1,hero.offsetHeight-stageH-start-hold);
 var r=cv.getBoundingClientRect(),dpr=Math.min(W.devicePixelRatio||1,2);
 cw=Math.max(1,r.width);ch=Math.max(1,r.height);cv.width=Math.round(cw*dpr);cv.height=Math.round(ch*dpr);cx.setTransform(dpr,0,0,dpr,0,0);
 var s=cw<820;if(s!==small){small=s;build()}
 free=Math.min(ch,wrap.offsetTop+copy.offsetTop+parseFloat(getComputedStyle(copy).paddingTop||0));
 F=floorFit(cw,ch,small,COLS,ROWS,hand.offsetTop+hand.offsetHeight);
}
function progress(){if(!scrub){pT=0;return}pT=clamp((headH-hero.getBoundingClientRect().top-start)/len,0,1)}
function fit(t,w){if(cx.measureText(t).width<=w)return t;while(t.length>2&&cx.measureText(t+'…').width>w)t=t.slice(0,-1);return t+'…'}
function rr(x,y,w,h,r){cx.beginPath();cx.moveTo(x+r,y);cx.arcTo(x+w,y,x+w,y+h,r);cx.arcTo(x+w,y+h,x,y+h,r);cx.arcTo(x,y+h,x,y,r);cx.arcTo(x,y,x+w,y,r);cx.closePath()}
function draw(){
 var p=pS,t=sstep(.06,.5,p),tilt=sstep(.45,.8,p)*F.tilt,hl=hl0=lit(p),i,n,e,a;
 var top=cv.getBoundingClientRect(),blocks=[],cr=copy.getBoundingClientRect(),gone=small?sstep(.55,.1,(cr.bottom-top.top)/ch):0,fr=lerp(free,ch*.8,gone);
 // The copy keeps its space: labels never cover its text while the sphere is round.
 if(t<.35&&cr.bottom>top.top)[].forEach.call(copy.children,function(c){var q=c.getBoundingClientRect();if(q.height)blocks.push([q.left-top.left-6,q.top-top.top-6,q.right-top.left+6,q.bottom-top.top+6])});
 var R=small?Math.min(cw*.34,fr*.36):Math.min(cw*.24,ch*.36),sx=small?cw*.5:cw*.7,sy=small?lerp(free*.48,ch*.5,gone):ch*.5;
 var sp=small?.5:.36,unit=lerp(R,F.unit,t),ox=lerp(sx,cw*.5,t),oy=small?lerp(sy,F.oy,t):lerp(sy,ch*.5,t)-tilt*ch*.03;
 var D=4,cY=Math.cos(yaw),sY=Math.sin(yaw),cP=Math.cos(pitch),sP=Math.sin(pitch),cT=Math.cos(tilt),sT=Math.sin(tilt);
 for(i=0;i<N;i++){n=nodes[i];
  var x1=n.x*cY+n.z*sY,z1=-n.x*sY+n.z*cY,y2=n.y*cP-z1*sP,z2=n.y*sP+z1*cP;
  var X=lerp(x1,(n.gc-(COLS-1)/2)*sp,t),Y=lerp(y2,((ROWS-1)/2-n.gr)*sp,t),Z=lerp(z2,0,t),Y2=Y*cT+Z*sT,Z2=Z*cT-Y*sT,k=D/(D-Z2);
  n.sx=ox+X*unit*k;n.sy=oy-Y2*unit*k;n.k=k;n.dz=clamp((Z2+1)/2,0,1);n.a=clamp(.14+.86*n.dz+t*.4,0,1)}
 cx.clearRect(0,0,cw,ch);cx.lineWidth=1;
 function edges(E,m){for(i=0;i<E.length;i++){e=E[i];a=(e[0].a+e[1].a)*m;if(a<.01)continue;cx.strokeStyle='rgba(71,232,255,'+a.toFixed(3)+')';cx.beginPath();cx.moveTo(e[0].sx,e[0].sy);cx.lineTo(e[1].sx,e[1].sy);cx.stroke()}}
 if(t<.98)edges(sE,.17*(1-t));if(t>.02)edges(gE,.11*t);
 var order=nodes.slice().sort(function(a,b){return a.dz-b.dz}),hov=null,hd=34*34,fs=small?10:11,cell=sp*unit,labs=[];
 if(t<.3)for(i=0;i<N;i++){n=nodes[i];if(n.dz<.55||!n.lab)continue;var dx=n.sx-mouse.x,dy=n.sy-mouse.y,q=dx*dx+dy*dy;if(q<hd){hd=q;hov=n}}
 cx.textBaseline='middle';
 for(i=0;i<N;i++){n=order[i];
  var rad=(n.lab?2.4:1.6)*n.k*(small?.95:1.1);
  if(n.dz>.7&&t<.5){cx.fillStyle='rgba(0,212,255,'+(.1*n.a).toFixed(3)+')';cx.beginPath();cx.arc(n.sx,n.sy,rad*3.4,0,6.2832);cx.fill()}
  cx.fillStyle=n===hov?'#ffffff':'rgba(0,212,255,'+n.a.toFixed(3)+')';cx.beginPath();cx.arc(n.sx,n.sy,n===hov?rad*1.6:rad,0,6.2832);cx.fill();
  if(n===hov){cx.strokeStyle='rgba(71,232,255,.9)';cx.beginPath();cx.arc(n.sx,n.sy,rad*4,0,6.2832);cx.stroke()}
  if(!n.lab)continue;
  var la=n===hov?1:lerp(sstep(small?.72:.6,.92,n.dz),1,t)*(1-hl*(n.pj>=0?1:(small?.85:.55)));if(la<.04)continue;
  var f=Math.max(8,fs*n.k*(n===hov?1.15:1));cx.font='600 '+f.toFixed(1)+'px '+MONO;
  var s=t>.35?fit(n.lab,Math.max(20,cell*n.k-10)):n.lab,tw=cx.measureText(s).width;
  labs.push({t:s,x:n.sx+lerp(rad+6,-tw/2,t),y:n.sy+lerp(0,rad+10,t),w:tw,f:f,a:la,h:n===hov,z:n.dz})}
 labs.sort(function(a,b){return (b.h-a.h)||(b.z-a.z)});
 for(i=0;i<labs.length;i++){var l=labs[i],bx=[l.x-3,l.y-l.f*.6,l.x+l.w+3,l.y+l.f*.6],hit=false;
  if(t<.35){if(!l.h&&(bx[0]<2||bx[2]>cw-2))continue;
   for(var j=0;j<blocks.length;j++){var o=blocks[j];if(bx[0]<o[2]&&bx[2]>o[0]&&bx[1]<o[3]&&bx[3]>o[1]){hit=true;break}}}
  if(hit)continue;blocks.push(bx);
  cx.font='600 '+l.f.toFixed(1)+'px '+MONO;cx.fillStyle=l.h?'#ffffff':'rgba(214,224,234,'+l.a.toFixed(3)+')';cx.fillText(l.t,l.x,l.y)}
 if(hl>.01)for(i=0;i<tiles.length;i++){n=tiles[i];
  var w=cell*n.k*1.9,h=small?Math.max(54,cell*n.k*.62):62,x0=n.sx-w/2+(small?0:cell*n.k*.5),e2=reveal(i,hl),y0=n.sy-h/2+(1-e2)*14;
  n.box=e2>.5?[x0,y0,x0+w,y0+h]:null;if(e2<.01)continue;
  cx.save();cx.globalAlpha=e2;rr(x0,y0,w,h,Math.min(12,w*.1));cx.fillStyle='rgba(17,30,49,.94)';cx.fill();cx.strokeStyle='rgba(71,232,255,.85)';cx.lineWidth=1.2;cx.stroke();
  cx.textBaseline='top';cx.font='700 '+(small?10:11)+'px '+MONO;cx.fillStyle='#47e8ff';cx.fillText(TL[i][0],x0+8,y0+8);
  cx.font='600 '+(small?9.5:10.5)+'px '+MONO;cx.fillStyle='#ffffff';
  var words=TL[i][1].split(' '),line='',lines=[];
  for(var wi=0;wi<words.length;wi++){var tl=line?line+' '+words[wi]:words[wi];if(cx.measureText(tl).width>w-16&&line){lines.push(line);line=words[wi]}else line=tl}
  lines.push(line);for(j=0;j<2&&j<lines.length;j++)cx.fillText(fit(lines[j],w-16),x0+8,y0+(small?27:30)+j*(small?13:15));
  cx.restore();cx.textBaseline='middle'}
 // The copy fades as it leaves, and nothing of it shows right under the sticky header.
 var fd=fade(cr.top,copy.lastElementChild.getBoundingClientRect().bottom,headH,stageH),cs=copy.style,mk=scrub&&fd.cut>-fd.fe?'linear-gradient(transparent '+Math.round(fd.cut)+'px,#000 '+Math.round(fd.cut+fd.fe)+'px)':'';
 cs.opacity=scrub?fd.o.toFixed(3):'';if(mk!==mk0){mk0=mk;cs.webkitMaskImage=mk;cs.maskImage=mk}
 hand.style.opacity=scrub?sstep(.7,.85,p).toFixed(3):'';
}
// A lit tile opens its chapter through the chapter index link.
function tileAt(e){var r=cv.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;for(var i=0;i<tiles.length;i++){var b=hl0>.5&&tiles[i].box;if(b&&x>b[0]&&x<b[2]&&y>b[1]&&y<b[3])return TA[i]}return null}
cv.addEventListener('click',function(e){var a=tileAt(e);if(a)a.click()});
function running(){return vis&&!d.hidden&&!still()}
function tick(ts){raf=0;var raw=Math.max(0,ts-last)||16,dt=Math.min(50,raw);last=ts;
 yawV+=(tYawV-yawV)*.05;yaw+=yawV*dt/1000;pitch+=(tPitch-pitch)*.05;pS+=(pT-pS)*(1-Math.exp(-raw/110));
 draw();if(running())raf=requestAnimationFrame(tick)}
function frame(){if(raf||dq)return;dq=requestAnimationFrame(function(){dq=0;pS=pT;draw()})}
function update(){progress();if(running()){if(!raf){last=performance.now();raf=requestAnimationFrame(tick)}return}
 if(raf){cancelAnimationFrame(raf);raf=0}frame()}
W.addEventListener('scroll',function(){if(!vis)return;progress();if(!raf)frame()},{passive:true});
W.addEventListener('pointermove',function(e){if(!vis)return;cv.style.cursor=tileAt(e)?'pointer':'';if(still())return;var r=cv.getBoundingClientRect();mouse.x=e.clientX-r.left;mouse.y=e.clientY-r.top;
 tYawV=.16+(clamp(mouse.x/r.width,0,1)-.5)*1.5;tPitch=-.32+(clamp(mouse.y/r.height,0,1)-.5)*.9},{passive:true});
d.addEventListener('pointerleave',function(){mouse.x=mouse.y=-1e4;tYawV=.16;tPitch=-.32});
var timer=0;W.addEventListener('resize',function(){clearTimeout(timer);timer=setTimeout(function(){layout();update()},120)});
if('IntersectionObserver' in W)new IntersectionObserver(function(en){vis=en[0].isIntersecting;update()}).observe(hero);
d.addEventListener('visibilitychange',update);d.addEventListener('motionchange',update);
function mode(){layout();update()}
if(rm.addEventListener)rm.addEventListener('change',mode);
mode();
})();
"""
