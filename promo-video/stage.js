// Vibe Coding UNleashed — ENGR-126 promo. Deterministic: render(t) draws the frame at time t (seconds).
const V=location.hash==='#v'; // vertical 9:16 layout
const W=V?1080:1920,H=V?1920:1080,cv=document.getElementById('c');cv.width=W;cv.height=H;const g=cv.getContext('2d');
const YO=(H-1080)/2;
const GOLD='#FFB300',GOLDL='#FFD54F',WHITE='#F6F2E9',DIM='#9a937f',INK='#0c0b09';
const DUR=78;
const clamp=(x,a=0,b=1)=>x<a?a:x>b?b:x, lerp=(a,b,t)=>a+(b-a)*t;
const P=(t,a,b)=>clamp((t-a)/(b-a));
const E={out:t=>1-Math.pow(1-t,3),in:t=>t*t*t,io:t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2,
  back:t=>{const c1=2.0,c3=c1+1;return 1+c3*Math.pow(t-1,3)+c1*Math.pow(t-1,2)},
  expo:t=>t>=1?1:1-Math.pow(2,-10*t), sine:t=>0.5-0.5*Math.cos(Math.PI*t)};
function R(seed){let s=seed>>>0;return()=>{s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const B=0.5; // 120 BPM
const beatPulse=(t,dec=7)=>Math.exp(-(((t%B)+B)%B)*dec);
const TAU=Math.PI*2;

const rod=new Image(); rod.src='rodney.png';

/* ---------------- text helpers ---------------- */
function font(o){return `${o.weight||''} ${o.size||60}px ${o.font||'Anton'}`.trim()}
function T(s,x,y,o={}){g.save();g.font=font(o);g.textAlign=o.align||'left';g.textBaseline=o.base||'alphabetic';
  g.letterSpacing=(o.track||0)+'px';g.globalAlpha*=(o.alpha??1);
  if(o.glow){g.shadowColor=o.glowColor||o.color||GOLD;g.shadowBlur=o.glow;}
  g.fillStyle=o.color||WHITE;g.fillText(s,x,y);
  if(o.stroke){g.shadowBlur=0;g.lineWidth=o.lw||2;g.strokeStyle=o.stroke;g.strokeText(s,x,y);}
  g.restore();}
function TW(s,o={}){g.save();g.font=font(o);g.letterSpacing=(o.track||0)+'px';const w=g.measureText(s).width;g.restore();return w}
// mixed colour line: parts=[[text,color],...]
function TM(parts,x,y,o={}){const ws=parts.map(p=>TW(p[0],o));const tot=ws.reduce((a,b)=>a+b,0);
  let cx=o.align==='center'?x-tot/2:o.align==='right'?x-tot:x;
  parts.forEach((p,i)=>{T(p[0],cx,y,{...o,align:'left',color:p[1],glowColor:p[2]||p[1]});cx+=ws[i]});return tot}
function sweepFill(x0,x1,p,a=0.85){const gr=g.createLinearGradient(x0,0,x1,0);const c=clamp(p,0.001,0.999);
  gr.addColorStop(0,'rgba(255,255,255,0)');gr.addColorStop(clamp(c-0.08),'rgba(255,255,255,0)');
  gr.addColorStop(c,`rgba(255,255,255,${a})`);gr.addColorStop(clamp(c+0.08),'rgba(255,255,255,0)');gr.addColorStop(1,'rgba(255,255,255,0)');return gr}
function typed(s,t,t0,cps){const n=Math.floor(clamp((t-t0)*cps,0,s.length));return s.slice(0,n)}
function rr(x,y,w,h,r){g.beginPath();g.roundRect(x,y,w,h,r)}
function panel(x,y,w,h,o={}){g.save();rr(x,y,w,h,o.r??18);g.fillStyle=o.fill||'rgba(16,15,12,0.94)';g.fill();
  g.lineWidth=o.lw||2;g.strokeStyle=o.stroke||'rgba(255,179,0,0.5)';g.stroke();g.restore()}
function brackets(x,y,w,h,L,col,lw){g.save();g.strokeStyle=col;g.lineWidth=lw;g.beginPath();
  g.moveTo(x,y+L);g.lineTo(x,y);g.lineTo(x+L,y);g.moveTo(x+w-L,y);g.lineTo(x+w,y);g.lineTo(x+w,y+L);
  g.moveTo(x+w,y+h-L);g.lineTo(x+w,y+h);g.lineTo(x+w-L,y+h);g.moveTo(x+L,y+h);g.lineTo(x,y+h);g.lineTo(x,y+h-L);g.stroke();g.restore()}
function chip(s,x,y,o={}){const f={font:'Barlow Condensed',weight:700,size:o.size||26,track:3};const w=TW(s,f)+36;
  g.save();rr(x,y,w,44,22);g.fillStyle=o.fill||'rgba(255,179,0,0.12)';g.fill();g.strokeStyle=o.stroke||'rgba(255,179,0,0.7)';g.lineWidth=1.5;g.stroke();g.restore();
  T(s,x+18,y+31,{...f,color:o.color||GOLD});return w}

/* ---------------- backgrounds ---------------- */
const dustP=(()=>{const r=R(11);return Array.from({length:120},()=>({x:r()*W,y:r()*H,z:r(),p:r()*TAU,v:0.3+r()}))})();
function bg(t,o={}){
  const gr=g.createRadialGradient(W/2,H*0.42,40,W/2,H/2,Math.max(W,H)*0.78);gr.addColorStop(0,o.c0||'#1b160a');gr.addColorStop(0.55,'#070605');gr.addColorStop(1,'#000');
  g.fillStyle=gr;g.fillRect(0,0,W,H);
  if(o.grid!==false)grid(t,o.gridA??0.45,o.speed??1);
  dust(t,o.dustA??0.7);
}
function grid(t,a,speed){const hy=H*0.64,vp=W/2;g.save();
  const hg=g.createLinearGradient(0,hy-160,0,hy+30);hg.addColorStop(0,'rgba(255,179,0,0)');hg.addColorStop(1,`rgba(255,179,0,${0.22*a})`);
  g.fillStyle=hg;g.fillRect(0,hy-160,W,190);
  g.beginPath();g.rect(0,hy,W,H-hy);g.clip();g.strokeStyle=GOLD;g.lineWidth=1.4;
  for(let i=-30;i<=30;i++){g.globalAlpha=a*0.45*(1-Math.abs(i)/32);g.beginPath();g.moveTo(vp+i*14,hy);g.lineTo(vp+i*300,H+20);g.stroke()}
  const off=(t*speed*1.5)%1;
  for(let k=1;k<40;k++){const d=k-off;if(d<=0.05)continue;const y=hy+380/d*1.0;if(y>H+10)continue;
    g.globalAlpha=a*clamp(1.4/d)*0.9;g.beginPath();g.moveTo(0,y);g.lineTo(W,y);g.stroke()}
  g.restore()}
function dust(t,a){g.save();g.globalCompositeOperation='lighter';
  for(const p of dustP){const y=((p.y-t*30*p.v*(0.4+p.z))%H+H)%H;const x=p.x+Math.sin(t*0.5+p.p)*20;
    const s=1+p.z*3.5;g.globalAlpha=a*(0.15+0.45*p.z)*(0.6+0.4*Math.sin(t*2+p.p));
    g.fillStyle=p.z>0.8?GOLDL:GOLD;g.beginPath();g.arc(x,y,s,0,TAU);g.fill()}
  g.restore()}
function rays(t,cx,cy,a,n=18,rot=0.15){g.save();g.translate(cx,cy);g.rotate(t*rot);g.globalCompositeOperation='lighter';
  for(let i=0;i<n;i++){g.rotate(TAU/n);const gr=g.createLinearGradient(0,0,1400,0);gr.addColorStop(0,`rgba(255,179,0,${0.16*a})`);gr.addColorStop(1,'rgba(255,179,0,0)');
    g.fillStyle=gr;g.beginPath();g.moveTo(0,0);g.lineTo(1500,-90);g.lineTo(1500,90);g.closePath();g.fill()}
  g.restore()}

/* splatter (VCU "UN" window homage) */
const splatCache={};
function splat(cx,cy,rw,rh,seed,prog,o={}){
  if(!splatCache[seed]){const r=R(seed);const n=o.n||160;splatCache[seed]=Array.from({length:n},()=>{
    let x,y;if(o.mode==='rise'){x=r()*2-1;y=1-Math.pow(r(),1.7)*2}else{const a=r()*TAU,d=Math.pow(r(),0.55);x=Math.cos(a)*d;y=Math.sin(a)*d}
    return{x,y,rad:1.2+Math.pow(r(),5)*30,del:(o.mode==='rise'?(1-y)/2*0.5:Math.hypot(x,y)*0.35)+r()*0.25,sh:r()}})}
  g.save();g.fillStyle=o.color||GOLD;
  for(const p of splatCache[seed]){const k=clamp((prog-p.del)/0.2);if(k<=0)continue;const e=E.out(k);
    g.globalAlpha=(o.alpha??0.92)*(0.55+0.45*p.sh);const px=cx+p.x*rw,py=cy+p.y*rh;
    g.beginPath();g.ellipse(px,py,p.rad*e,p.rad*e*(0.7+0.3*p.sh),p.sh*3,0,TAU);g.fill()}
  g.restore()}

/* ---------------- post FX ---------------- */
const tmp=document.createElement('canvas');tmp.width=W;tmp.height=H;const tg=tmp.getContext('2d');
const noise=document.createElement('canvas');noise.width=noise.height=256;
{const n=noise.getContext('2d'),id=n.createImageData(256,256),r=R(5);for(let i=0;i<id.data.length;i+=4){const v=r()*255;id.data[i]=id.data[i+1]=id.data[i+2]=v;id.data[i+3]=255}n.putImageData(id,0,0)}
const CUTS=[6,12,20,20.5,26,34,36,38,40,42,44,46,48,50,52,54,58,62,68];
const IMPACTS=[[6,26],[20.5,34],[62,30],[68,26]];
function shakeAt(t){let x=0,y=0;for(const [c,a] of IMPACTS){const d=t-c;if(d>=0&&d<0.6){const k=a*Math.exp(-d*8);x+=Math.sin(d*90)*k;y+=Math.cos(d*77)*k*0.7}}return[x,y]}
function post(t){
  g.setTransform(1,0,0,1,0,0);g.globalAlpha=1;g.globalCompositeOperation='source-over';
  for(const c of CUTS){const d=t-c;
    if(d>=0&&d<0.14){const amt=1-d/0.14;tg.clearRect(0,0,W,H);tg.drawImage(cv,0,0);const r=R(Math.floor(c*100));
      for(let i=0;i<16;i++){const y=r()*H,h=8+r()*70,dx=(r()-.5)*220*amt;g.drawImage(tmp,0,y,W,h,dx,y,W,h)}
      g.save();g.globalCompositeOperation='lighter';g.globalAlpha=0.28*amt;g.drawImage(tmp,14*amt,0);g.globalAlpha=0.18*amt;g.drawImage(tmp,-14*amt,0);g.restore()}
    if(d>=0&&d<0.35){g.save();g.globalAlpha=0.55*Math.exp(-d*14);g.fillStyle=d<0.05?'#fff':'#ffe08a';g.fillRect(0,0,W,H);g.restore()}}
  // vignette
  const v=g.createRadialGradient(W/2,H/2,Math.hypot(W,H)*0.22,W/2,H/2,Math.hypot(W,H)*0.515);v.addColorStop(0,'rgba(0,0,0,0)');v.addColorStop(1,'rgba(0,0,0,0.7)');g.fillStyle=v;g.fillRect(0,0,W,H);
  // grain
  g.save();g.globalAlpha=0.07;g.globalCompositeOperation='overlay';const r=R(Math.floor(t*30)+1);
  g.translate(-r()*256,-r()*256);g.fillStyle=g.createPattern(noise,'repeat');g.fillRect(0,0,W+256,H+256);g.restore();
  // fade in/out
  const fo=Math.max(1-P(t,0,0.4),P(t,DUR-1.6,DUR-0.2));if(fo>0){g.fillStyle=`rgba(0,0,0,${fo})`;g.fillRect(0,0,W,H)}
}

/* =========================== SCENES =========================== */
// S1 — terminal cold open (0–6)
const S1L=[{s:'~/engr126 $ claude',t0:0.3,cps:30,c:DIM},{s:'> I have never written a line of code.',t0:1.2,cps:30,c:WHITE},
  {s:'> Can I still build something amazing?',t0:2.7,cps:30,c:WHITE},{s:"● Absolutely. Let's vibe code it.",t0:4.3,cps:40,c:GOLD}];
function s1(lt,t){bg(t,{grid:false,dustA:0.35*P(lt,0,2)});
  const push=lerp(1,1.06,E.sine(P(lt,0,5.1)))*lerp(1,4.5,E.in(P(lt,5.1,6)));
  const fk=V?0.88:1;g.save();g.translate(W/2,H/2);g.scale(push*fk,push*fk);g.translate(-960,-540);
  const x=380,y=300,w=1160,h=440;
  g.save();g.shadowColor='rgba(255,179,0,0.35)';g.shadowBlur=60;panel(x,y,w,h,{fill:'#0e0d0b',stroke:'rgba(255,179,0,0.35)'});g.restore();
  g.save();rr(x,y,w,56,[18,18,0,0]);g.fillStyle='#17150f';g.fill();g.restore();
  ['#ff5f57','#febc2e','#28c840'].forEach((c,i)=>{g.fillStyle=c;g.beginPath();g.arc(x+32+i*28,y+28,8,0,TAU);g.fill()});
  T('claude — engr-126',x+w/2,y+37,{font:'JetBrains Mono',size:20,color:DIM,align:'center'});
  let cur=null;S1L.forEach((L,i)=>{const s=typed(L.s,lt,L.t0,L.cps);if(lt>=L.t0){cur={i,s};
    T(s,x+46,y+125+i*72,{font:'JetBrains Mono',size:31,weight:L.c===GOLD?700:400,color:L.c,glow:L.c===GOLD?18:0})}});
  if(cur){const cw=TW(cur.s,{font:'JetBrains Mono',size:31});if(Math.floor(lt*2.4)%2===0||lt<5){g.fillStyle=GOLD;g.fillRect(x+48+cw,y+125+cur.i*72-28,16,34)}}
  g.restore();
  // pre-title whisper
  T('ENGR-126',W/2,V?1330:980,{font:'Barlow Condensed',weight:700,size:28,track:14,align:'center',color:GOLD,alpha:0.7*P(lt,0.5,1.5)*(1-P(lt,5,5.5))});
}

// S2 — UN- words + UNLIMITED (6–12)
const UNW=['LOCK','BOX','PLUG','STUCK','AFRAID','STOPPABLE'];
function s2(lt,t){bg(t,{gridA:0.55,speed:2});
  if(lt<3){const i=Math.floor(lt/0.5),wl=lt-i*0.5;const word=UNW[i];
    rays(t,W/2,H/2,0.6,16,0.4);
    splat(W/2,H/2+20,V?470:620,V?470:300,100+i,wl*2.2,{n:110,alpha:0.5});
    const sc=lerp(1.7,1,E.out(clamp(wl/0.16)));const rot=(R(i+3)()-0.5)*0.08;
    if(V){const ws=Math.min(400,Math.floor(96000/TW(word,{size:100})));const wb=20+ws*0.86;
      g.save();g.translate(W/2,H/2);g.rotate(rot);g.scale(sc,sc);
      T('UN',0,-20,{size:400,align:'center',color:GOLD,glow:30,glowColor:'rgba(0,0,0,0.6)'});T(word,0,wb,{size:ws,align:'center',glow:30,glowColor:'rgba(0,0,0,0.6)'});g.restore();
      T(['ideas','projects','creativity','your potential','of code','you'][i].toUpperCase(),W/2,H/2+wb+90,{font:'Barlow Condensed',weight:700,size:40,track:16,align:'center',color:DIM,alpha:E.out(clamp((wl-0.08)/0.15))});
      return}
    g.save();g.translate(W/2,H/2+120);g.rotate(rot);g.scale(sc,sc);
    TM([['UN',GOLD],[word,WHITE]],0,0,{size:word.length>6?260:320,align:'center',glow:30,glowColor:'rgba(0,0,0,0.6)'});
    g.restore();
    T(['ideas','projects','creativity','your potential','of code','you'][i].toUpperCase(),W/2,H/2+250,{font:'Barlow Condensed',weight:700,size:40,track:16,align:'center',color:DIM,alpha:E.out(clamp((wl-0.08)/0.15))});
    return}
  // UNLIMITED window homage
  const k=lt-3;
  if(V){const sc=lerp(1.25,1,E.out(P(k,0.1,0.45)));const ls=Math.min(400,Math.floor(98000/TW('LIMITED',{size:100})));const by=860,d2=40+ls*0.86;
    splat(W/2,1480,520,430,777,k*0.9,{mode:'rise',n:420,alpha:0.85});
    T('BUILD IN A WORLD OF',50,by-430,{font:'Barlow Condensed',weight:700,size:54,track:12,alpha:E.out(P(k,0,0.4))});
    g.save();g.translate(W/2,by);g.scale(sc,sc);g.globalAlpha=P(k,0.1,0.25);
    T('UN',-W/2+44,0,{size:430,color:GOLD});T('LIMITED',0,d2,{size:ls,align:'center'});
    g.globalCompositeOperation='source-atop';const r=R(41);g.fillStyle='rgba(0,0,0,0.55)';
    for(let i=0;i<420;i++){g.beginPath();g.arc((r()-0.5)*1080,-340+r()*(d2+340),r()*r()*7,0,TAU);g.fill()}
    g.restore();
    T('POSSIBILITIES.',W-50,by+d2+68,{font:'Barlow Condensed',weight:700,size:64,track:12,align:'right',alpha:E.out(P(k,0.5,0.9))});
  }else{
  const cx=W/2,cy=720;
  splat(cx-300,cy+120,900,330,777,k*0.9,{mode:'rise',n:420,alpha:0.85});
  T('BUILD IN A WORLD OF',W/2-640,cy-300,{font:'Barlow Condensed',weight:700,size:54,track:12,alpha:E.out(P(k,0,0.4))});
  const sc=lerp(1.25,1,E.out(P(k,0.1,0.45)));g.save();g.translate(cx,cy);g.scale(sc,sc);g.globalAlpha=P(k,0.1,0.25);
  TM([['UN',GOLD],['LIMITED',WHITE]],0,0,{size:330,align:'center',track:4});
  // distress specks
  g.globalCompositeOperation='source-atop';const r=R(41);g.fillStyle='rgba(0,0,0,0.55)';
  for(let i=0;i<420;i++){g.beginPath();g.arc((r()-0.5)*1500,-r()*300,r()*r()*7,0,TAU);g.fill()}
  g.restore();
  T('POSSIBILITIES.',W/2+640,cy+110,{font:'Barlow Condensed',weight:700,size:64,track:12,align:'right',alpha:E.out(P(k,0.5,0.9))});
  }
  // window mullions + glass reflection
  g.save();g.strokeStyle='rgba(30,30,34,0.9)';g.lineWidth=10;const mc=V?4:8,mr=V?6:3;for(let i=0;i<=mc;i++){g.beginPath();g.moveTo(i*W/mc,0);g.lineTo(i*W/mc,H);g.stroke()}
  for(let j=0;j<=mr;j++){g.beginPath();g.moveTo(0,j*H/mr);g.lineTo(W,j*H/mr);g.stroke()}
  const sx=lerp(-600,W+600,P(k,0.3,2.6));const gr=g.createLinearGradient(sx-300,0,sx+300,0);gr.addColorStop(0,'rgba(255,255,255,0)');gr.addColorStop(0.5,'rgba(255,255,255,0.10)');gr.addColorStop(1,'rgba(255,255,255,0)');
  g.fillStyle=gr;g.fillRect(0,0,W,H);g.restore();
}

// S3 — Vibe Coding UNleashed → VCU (12–20)
const S3W=[['VIBE',330],['CODING',560],['UNLEASHED',790]];
let s3lay=null;
function s3layout(){const o={size:210};s3lay=[];S3W.forEach(([w,y],wi)=>{let x=W/2-TW(w,o)/2;for(let i=0;i<w.length;i++){const ch=w[i];const cw=TW(ch,o);
  s3lay.push({ch,x,y:y+YO,wi,i,init:i===0,w:cw});x+=cw}});
  const big={size:470,track:10};const tw=TW('VCU',big);let x=W/2-tw/2;s3lay.filter(l=>l.init).forEach((l,j)=>{l.tx=x;l.tw=TW(l.ch,big)+10;x+=l.tw})}
function s3(lt,t){bg(t,{gridA:0.4});if(!s3lay)s3layout();
  const m=E.io(P(lt,2.6,3.6));// morph
  if(lt>3.4){rays(t,W/2,470+YO,P(lt,3.4,4)*0.9,20,0.2)}
  // shockwave
  if(lt>3.6&&lt<4.6){const k=P(lt,3.6,4.6);g.save();g.strokeStyle=GOLD;g.globalAlpha=1-k;g.lineWidth=14*(1-k)+1;g.beginPath();g.arc(W/2,450+YO,60+k*1100,0,TAU);g.stroke();g.restore()}
  s3lay.forEach((l,n)=>{const d=12+n*0.035;const k=E.back(P(lt,n*0.045,n*0.045+0.45));if(k<=0)return;
    let y=l.y-(1-k)*300,x=l.x,size=210,a=clamp(k*2),col=l.init?GOLD:WHITE,glow=l.init?25:0;
    if(!l.init){const r=R(n+9);const f=E.in(P(lt,2.3,3.0));x+=(r()-0.5)*700*f;y+=(r()-0.3)*-500*f;a*=1-f}
    else{x=lerp(l.x,l.tx,m);y=lerp(l.y,700+YO,m);size=lerp(210,470,m);glow=lerp(25,60,m)}
    if(a<=0.01)return;T(l.ch,x,y,{size,color:col,alpha:a,glow,track:l.init?lerp(0,10,m):0})});
  if(lt>3.6){const p=P(lt,4.0,5.5);g.save();T('VCU',W/2,700+YO,{size:470,track:10,align:'center',color:sweepFill(W/2-500,W/2+500,p,0.9)});g.restore()}
  const a1=E.out(P(lt,4.1,4.6)),a2=E.out(P(lt,4.6,5.1));
  T('VIBE  CODING  UNLEASHED',W/2,800+YO,{font:'Barlow Condensed',weight:800,size:V?50:60,track:V?12:20,align:'center',alpha:a1});
  g.save();g.fillStyle=GOLD;g.globalAlpha=a2;g.fillRect(W/2-lerp(0,300,a2),838+YO,lerp(0,600,a2),4);g.restore();
  T('ENGR-126  ·  VIBE CODING WITH AI',W/2,905+YO,{font:'Barlow Condensed',weight:700,size:44,track:10,align:'center',color:GOLD,alpha:a2});
}

// S4 — Rodney (20–26)
function drawRodney(cx,by,h,t,o={}){if(!rod.complete||!rod.naturalWidth)return;const w=h*rod.naturalWidth/rod.naturalHeight;const br=1+0.008*Math.sin(t*3);
  g.save();g.translate(cx,by);g.scale(br,br);g.globalAlpha*=(o.alpha??1);
  g.shadowColor='rgba(255,179,0,0.9)';g.shadowBlur=o.glow??70;g.drawImage(rod,-w/2,-h,w,h);
  g.shadowBlur=0;g.globalCompositeOperation='lighter';g.globalAlpha*=0.12;g.drawImage(rod,-w/2,-h,w,h);g.restore()}
function s4(lt,t){const RX=V?W/2+130:1330,ty=V?60:0;bg(t,{gridA:0.35,c0:'#241a06'});rays(t,RX,V?1350:430,0.9,22,0.12);
  const k=E.back(P(lt,0,0.5));drawRodney(RX,H+60+(1-k)*1000,V?980:1080,t);
  if(lt>0.5&&lt<1.4){const r=R(77);const d=lt-0.5;g.save();g.globalCompositeOperation='lighter';
    for(let i=0;i<70;i++){const a=r()*TAU,sp=400+r()*900;g.globalAlpha=(1-d/0.9)*0.9;g.fillStyle=r()<0.5?GOLD:GOLDL;
      g.beginPath();g.arc(RX+Math.cos(a)*sp*d,(V?1300:560)+Math.sin(a)*sp*d*0.7+d*d*400,2+r()*5,0,TAU);g.fill()}g.restore()}
  const x=V?70:150;
  T('RODNEY THE RAM ASKS:',x,300+ty,{font:'Barlow Condensed',weight:700,size:40,track:12,color:GOLD,alpha:E.out(P(lt,0.7,1.0))});
  [['ZERO CODING',1.0,440],['EXPERIENCE?',1.35,590]].forEach(([s,a,y])=>{const e=E.out(P(lt,a,a+0.3));T(s,x-(1-e)*120,y+ty,{size:150,alpha:e})});
  if(lt>2.5){const e=E.back(P(lt,2.5,2.8));splat(x+330,700+ty,400,120,321,(lt-2.5)*2,{n:90,alpha:0.6});
    g.save();g.translate(x,770+ty);g.scale(lerp(1.6,1,e),lerp(1.6,1,e));T('PERFECT.',0,0,{size:200,color:GOLD,glow:30,alpha:clamp(e*2)});g.restore()}
  T('No experience needed. Just bring your ideas.',x,860+ty,{font:'Barlow',weight:500,size:40,color:WHITE,alpha:E.out(P(lt,3.3,3.7))});
  // speech bubble
  if(lt>3.6){const e=E.back(P(lt,3.6,3.9));g.save();g.translate(V?250:1060,V?1180:250);g.scale(e,e);
    rr(-200,-70,400,120,40);g.fillStyle=WHITE;g.fill();g.beginPath();g.moveTo(90,40);g.lineTo(150,110);g.lineTo(40,48);g.fill();
    T("LET'S BUILD!",0,15,{size:62,color:INK,align:'center'});g.restore()}
}

// S5 — how it works (26–34)
const CODE=[['import',' cv2, mediapipe ','as',' mp'],['from',' game ','import',' Invaders'],[''],['def',' mouth_open(face):'],['    gap = lip_dist(face)'],['    ','return',' gap > 0.35'],[''],['while',' playing:'],['    face = cam.read_face()'],['    ship.x = face.nose.x * W'],['    ','if',' mouth_open(face):'],['        ship.fire()'],['    invaders.step()'],['    draw(score)']];
const KW=new Set(['import','from','as','def','return','while','if']);
function faceInvaders(x,y,w,h,lt,t){g.save();rr(x,y,w,h,12);g.clip();g.fillStyle='#050608';g.fillRect(x,y,w,h);
  const r=R(3);for(let i=0;i<40;i++){g.fillStyle='rgba(255,255,255,0.5)';g.fillRect(x+r()*w,y+((r()*h+lt*40*(0.3+r()))%h),2,2)}
  const shipX=x+w/2+Math.sin(lt*2.2)*w*0.33;const dx=Math.sin(lt*1.4)*40;
  const killed=new Set();const fires=[];for(let f=0;f<Math.floor(lt/0.5)+1;f++){fires.push(f*0.5)}
  for(let row=0;row<3;row++)for(let c=0;c<6;c++){const ix=x+70+c*62+dx,iy=y+60+row*48+lt*6;
    const id=row*6+c;const hitT=0.9+((id*7)%18)*0.18;if(lt>hitT){if(lt<hitT+0.3){const k=(lt-hitT)/0.3;g.fillStyle=`rgba(255,179,0,${1-k})`;for(let j=0;j<8;j++){g.fillRect(ix+14+Math.cos(j)*k*30,iy+10+Math.sin(j*1.7)*k*30,5,5)}}continue}
    g.fillStyle=row===0?GOLD:row===1?'#e8e2d0':'#c99a2e';const b=Math.floor(lt*4)%2;
    g.fillRect(ix+6,iy,24,6);g.fillRect(ix,iy+6,36,10);g.fillRect(ix+(b?0:6),iy+16,8,6);g.fillRect(ix+(b?28:22),iy+16,8,6);g.fillStyle='#000';g.fillRect(ix+9,iy+8,5,5);g.fillRect(ix+22,iy+8,5,5)}
  fires.forEach(f=>{const d=lt-f;if(d<0||d>0.6)return;const bx=x+w/2+Math.sin(f*2.2)*w*0.33;g.fillStyle=GOLDL;g.shadowColor=GOLD;g.shadowBlur=12;g.fillRect(bx-3,y+h-90-d*600,6,22);g.shadowBlur=0});
  g.fillStyle=WHITE;g.beginPath();g.moveTo(shipX,y+h-90);g.lineTo(shipX-30,y+h-50);g.lineTo(shipX+30,y+h-50);g.fill();
  T('SCORE '+String(Math.floor(lt*230)).padStart(5,'0'),x+18,y+34,{font:'JetBrains Mono',weight:700,size:20,color:GOLD});
  // webcam face inset
  const fx=x+w-110,fy=y+h-110,open=beatPulse(t,10)>0.4;g.fillStyle='rgba(255,179,0,0.15)';rr(fx-60,fy-70,120,140,10);g.fill();g.strokeStyle=GOLD;g.lineWidth=2;g.stroke();
  g.fillStyle='#e9d2b0';g.beginPath();g.ellipse(fx,fy,38,46,0,0,TAU);g.fill();g.fillStyle='#222';g.beginPath();g.arc(fx-14,fy-10,5,0,TAU);g.arc(fx+14,fy-10,5,0,TAU);g.fill();
  g.beginPath();g.ellipse(fx,fy+20,12,open?13:3,0,0,TAU);g.fill();T(open?'FIRE!':'cam',fx,fy+64,{font:'JetBrains Mono',size:15,color:GOLD,align:'center'});
  g.restore()}
function s5(lt,t){bg(t,{gridA:0.25});
  T('HOW VIBE CODING WORKS',W/2,V?270:150,{font:'Barlow Condensed',weight:800,size:56,track:18,align:'center',color:GOLD,alpha:E.out(P(lt,0,0.4))});
  const cards=[[90,0.2,'01','YOU DESCRIBE IT'],[700,1.5,'02','AI WRITES THE CODE'],[1310,2.8,'03','YOU PLAY IT']];
  cards.forEach(([x,a,n,title],ci)=>{const e=E.out(P(lt,a,a+0.5));if(e<=0)return;let y=250+(1-e)*80;g.save();g.globalAlpha=e;
    if(V){const L=[[60,320,0.9],[552,320,0.9],[267,920,1.05]][ci];g.translate(L[0],L[1]+(1-e)*80);g.scale(L[2],L[2]);x=0;y=0}
    panel(x,y,520,640,{});T(n,x+30,y+70,{size:54,color:GOLD});T(title,x+110,y+66,{font:'Barlow Condensed',weight:800,size:38,track:3});
    g.fillStyle='rgba(255,179,0,0.3)';g.fillRect(x+30,y+95,460,2);
    if(ci===0){const msg='Make Space Invaders that I control with my face. Open my mouth to fire!';
      const s=typed(msg,lt,0.6,38);const lines=wrap(s,{font:'Barlow',size:34,weight:500},400);
      rr(x+70,y+140,420,40+lines.length*46,22);g.fillStyle='#f3ead6';g.fill();
      lines.forEach((l,i)=>T(l,x+92,y+190+i*46,{font:'Barlow',size:34,weight:500,color:INK}));
      T('YOU',x+470,y+130,{font:'Barlow Condensed',weight:700,size:22,track:4,color:DIM,align:'right'});
      if(lt>2.5){const e2=E.out(P(lt,2.5,2.8));g.globalAlpha=e*e2;rr(x+30,y+430,380,120,22);g.fillStyle='rgba(255,179,0,0.16)';g.fill();g.strokeStyle=GOLD;g.lineWidth=1.5;g.stroke();
        T('On it! Building',x+54,y+478,{font:'Barlow',size:32,weight:600,color:GOLD});T('Face Invaders...',x+54,y+522,{font:'Barlow',size:32,weight:600,color:GOLD});
        T('AI',x+30,y+418,{font:'Barlow Condensed',weight:700,size:22,track:4,color:DIM})}}
    if(ci===1){const nl=Math.floor(clamp((lt-1.9)*9,0,CODE.length));const scroll=Math.max(0,nl-11)*38;
      g.save();g.beginPath();g.rect(x+20,y+110,480,510);g.clip();
      for(let i=0;i<nl;i++){let cx=x+40;const yy=y+150+i*38-scroll;T(String(i+1).padStart(2,' '),x+22,yy,{font:'JetBrains Mono',size:20,color:'#4b4636'});
        CODE[i].forEach(seg=>{const c=KW.has(seg.trim())?GOLD:seg.includes('(')?'#7fd1c7':WHITE;T(seg,cx+28,yy,{font:'JetBrains Mono',size:23,color:c,weight:KW.has(seg.trim())?700:400});cx+=TW(seg,{font:'JetBrains Mono',size:23})})}
      g.restore()}
    if(ci===2){if(lt>3.1)faceInvaders(x+24,y+118,472,496,lt-3.1,t);else{T('waiting for code…',x+260,y+380,{font:'JetBrains Mono',size:22,color:DIM,align:'center'})}}
    g.restore();
    if(!V&&ci<2&&lt>a+1){const k=P(lt,a+1,a+1.3);for(let j=0;j<3;j++){g.save();g.globalAlpha=k*(0.4+0.6*Math.max(0,Math.sin(lt*8-j)));
      g.strokeStyle=GOLD;g.lineWidth=6;g.beginPath();const ax=x+535+j*22;g.moveTo(ax,540);g.lineTo(ax+16,570);g.lineTo(ax,600);g.stroke();g.restore()}}});
  T('Plain English in.  Working software out.',W/2,V?1670:1000,{font:'Barlow',weight:600,size:40,align:'center',alpha:E.out(P(lt,5.5,6))});
}
function wrap(s,o,maxw){const words=s.split(' ');const out=[];let cur='';for(const w of words){const tst=cur?cur+' '+w:w;if(TW(tst,o)>maxw&&cur){out.push(cur);cur=w}else cur=tst}if(cur)out.push(cur);return out}

/* --------- project visuals (drawn in a 980x760 panel; local coords) --------- */
const PW=980,PH=760;
function visHand(lt,t){const gr=g.createLinearGradient(0,0,0,PH);gr.addColorStop(0,'#13202a');gr.addColorStop(1,'#07090c');g.fillStyle=gr;g.fillRect(0,0,PW,PH);
  const G=[['FIST',[0,0,0,0,0]],['POINT',[0,1,0,0,0]],['PEACE',[0,1,1,0,0]],['OPEN PALM',[1,1,1,1,1]]];
  const gi=Math.min(3,Math.floor(lt/0.5)),wl=lt-gi*0.5,prev=G[Math.max(0,gi-1)][1],cur=G[gi][1];const k=E.io(clamp(wl/0.18));const ext=cur.map((v,i)=>lerp(gi?prev[i]:v,v,k));
  const ox=360+Math.sin(lt*2)*20,oy=640+Math.cos(lt*1.6)*10;const wrist=[ox,oy],palm=[ox,oy-170];
  const bases=[[-110,-110],[-70,-250],[0,-268],[62,-250],[115,-210]],lens=[[75,60,50],[95,60,48],[100,65,50],[95,60,46],[75,48,40]];
  const pts=[];g.lineCap='round';
  bases.forEach((b,f)=>{const base=[ox+b[0],oy+b[1]];const dir=f===0?[-0.75,-0.66]:[(b[0])/600,-1];const dl=Math.hypot(...dir);const u=[dir[0]/dl,dir[1]/dl];
    let acc=0;const js=[base];lens[f].forEach((L,j)=>{acc+=L;const exP=[base[0]+u[0]*acc,base[1]+u[1]*acc];const fold=[lerp(base[0],palm[0],[0.15,0.35,0.5][j])+u[0]*[38,30,10][j],lerp(base[1],palm[1],[0.15,0.35,0.5][j])+u[1]*[38,30,10][j]+[0,25,45][j]];
      js.push([lerp(fold[0],exP[0],ext[f]),lerp(fold[1],exP[1],ext[f])])});pts.push(js)});
  g.strokeStyle='rgba(127,209,199,0.9)';g.lineWidth=5;g.beginPath();g.moveTo(...wrist);pts.forEach(js=>{g.moveTo(...wrist);g.lineTo(...js[0])});
  for(let f=1;f<4;f++){g.moveTo(...pts[f][0]);g.lineTo(...pts[f+1][0])}g.stroke();
  pts.forEach(js=>{g.beginPath();g.moveTo(...js[0]);js.slice(1).forEach(p=>g.lineTo(...p));g.stroke()});
  [wrist,...pts.flat()].forEach(p=>{g.fillStyle=GOLD;g.beginPath();g.arc(p[0],p[1],8,0,TAU);g.fill();g.fillStyle='#fff';g.beginPath();g.arc(p[0],p[1],3,0,TAU);g.fill()});
  const all=[wrist,...pts.flat()];const xs=all.map(p=>p[0]),ys=all.map(p=>p[1]);const bx=Math.min(...xs)-30,by=Math.min(...ys)-30,bw=Math.max(...xs)-bx+30,bh=Math.max(...ys)-by+30;
  brackets(bx,by,bw,bh,36,GOLD,4);g.fillStyle=GOLD;g.fillRect(bx,by-46,TW(G[gi][0],{font:'Barlow Condensed',weight:800,size:34,track:3})+120,42);
  T(G[gi][0]+'  0.9'+(7+gi%2),bx+12,by-14,{font:'Barlow Condensed',weight:800,size:34,track:3,color:INK});
  G.forEach((gg,i)=>{const y=210+i*95,on=i===gi;rr(690,y,250,72,10);g.fillStyle=on?'rgba(255,179,0,0.2)':'rgba(255,255,255,0.04)';g.fill();if(on){g.strokeStyle=GOLD;g.lineWidth=2;g.stroke()}
    T(gg[0],712,y+46,{font:'Barlow Condensed',weight:700,size:32,track:2,color:on?GOLD:DIM})});
  T('● webcam · 21 hand landmarks',30,50,{font:'JetBrains Mono',size:20,color:'#7fd1c7'})}
function visSquat(lt,t){g.fillStyle='#0a0c0a';g.fillRect(0,0,PW,PH);g.strokeStyle='rgba(255,255,255,0.05)';g.lineWidth=1;for(let i=0;i<PW;i+=40){g.beginPath();g.moveTo(i,0);g.lineTo(i,PH);g.stroke()}for(let j=0;j<PH;j+=40){g.beginPath();g.moveTo(0,j);g.lineTo(PW,j);g.stroke()}
  const d=E.sine(clamp(lt/1.9))*(lt<0.95?1:1)*Math.sin(Math.PI*clamp(lt/1.9));const A=[420,660],L1=175,L2=185;
  const Hp=[lerp(420,300,d),lerp(660-350,660-205,d)];const D=Math.hypot(Hp[0]-A[0],Hp[1]-A[1]);
  const a=Math.atan2(Hp[1]-A[1],Hp[0]-A[0]);const c=Math.acos(clamp((L1*L1+D*D-L2*L2)/(2*L1*D),-1,1));const K=[A[0]+L1*Math.cos(a+c),A[1]+L1*Math.sin(a+c)];
  const lean=0.12+0.62*d;const S=[Hp[0]+Math.sin(lean)*210,Hp[1]-Math.cos(lean)*210];const head=[S[0]+Math.sin(lean)*55,S[1]-Math.cos(lean)*55];
  const hand=[S[0]+170,S[1]+20*d];
  const v1=[Hp[0]-K[0],Hp[1]-K[1]],v2=[A[0]-K[0],A[1]-K[1]];const knee=Math.round(Math.acos((v1[0]*v2[0]+v1[1]*v2[1])/(Math.hypot(...v1)*Math.hypot(...v2)))*180/Math.PI);
  const u1=[S[0]-Hp[0],S[1]-Hp[1]],u2=[K[0]-Hp[0],K[1]-Hp[1]];const hip=Math.round(Math.acos((u1[0]*u2[0]+u1[1]*u2[1])/(Math.hypot(...u1)*Math.hypot(...u2)))*180/Math.PI);
  const good=knee<100;g.strokeStyle='#d9d2bf';g.lineWidth=16;g.lineCap='round';g.lineJoin='round';
  g.beginPath();g.moveTo(A[0]+60,A[1]);g.lineTo(...A);g.lineTo(...K);g.lineTo(...Hp);g.lineTo(...S);g.moveTo(...S);g.lineTo(...hand);g.stroke();
  g.fillStyle='#d9d2bf';g.beginPath();g.arc(head[0],head[1],38,0,TAU);g.fill();
  g.strokeStyle='rgba(255,255,255,0.3)';g.lineWidth=3;g.beginPath();g.moveTo(80,A[1]+12);g.lineTo(900,A[1]+12);g.stroke();
  const col=good?'#4ade80':GOLD;[[K,a+c+Math.PI,knee],[Hp,0,hip]].forEach(([p],i)=>{g.strokeStyle=col;g.lineWidth=4;g.beginPath();g.arc(p[0],p[1],48,0,TAU*(i?hip:knee)/360);g.stroke()});
  [A,K,Hp,S].forEach(p=>{g.fillStyle=col;g.beginPath();g.arc(p[0],p[1],11,0,TAU);g.fill()});
  T('KNEE '+knee+'°',K[0]+60,K[1]+10,{font:'JetBrains Mono',weight:700,size:30,color:col});T('HIP '+hip+'°',Hp[0]-210,Hp[1]+10,{font:'JetBrains Mono',weight:700,size:30,color:col});
  rr(640,40,300,120,12);g.fillStyle='rgba(255,255,255,0.05)';g.fill();T('REPS',665,85,{font:'Barlow Condensed',weight:700,size:28,track:4,color:DIM});
  T(String(lt>1.0?8:7),665,145,{size:56,color:WHITE});T(good?'GOOD DEPTH ✓':'GO LOWER',790,120,{font:'Barlow Condensed',weight:800,size:30,color:good?'#4ade80':GOLD,align:'center'})}
function cube(cx,cy,s,lt){const cols=['#e53935','#1e88e5','#43a047','#fdd835','#fb8c00','#f5f5f5'];const r=R(17);
  const U=[s*0.86,s*0.45],V=[-s*0.86,s*0.45],D=[0,s];const T0=[cx,cy-s*3.2];
  const add=(a,b,k=1)=>[a[0]+b[0]*k,a[1]+b[1]*k];
  const face=(o,u,v,shade)=>{g.fillStyle='#0d0d0d';const q0=[o,add(o,u,3),add(add(o,u,3),v,3),add(o,v,3)];g.beginPath();g.moveTo(...q0[0]);q0.slice(1).forEach(z=>g.lineTo(...z));g.closePath();g.fill();
    for(let i=0;i<3;i++)for(let j=0;j<3;j++){const p=(a,b)=>add(add(o,u,a),v,b);const q=[p(i+0.08,j+0.08),p(i+0.92,j+0.08),p(i+0.92,j+0.92),p(i+0.08,j+0.92)];
    g.fillStyle=cols[Math.floor(r()*6)];g.beginPath();g.moveTo(...q[0]);q.slice(1).forEach(z=>g.lineTo(...z));g.closePath();g.fill();
    if(shade){g.fillStyle=`rgba(0,0,0,${shade})`;g.fill()}}};
  face(T0,U,V,0);face(add(T0,V,3),U,D,0.18);face(add(T0,U,3),V,D,0.38)}
function visYolo(lt,t){const gr=g.createLinearGradient(0,0,0,PH);gr.addColorStop(0,'#1a1712');gr.addColorStop(1,'#0b0a08');g.fillStyle=gr;g.fillRect(0,0,PW,PH);
  g.fillStyle='#2a241a';g.fillRect(0,560,PW,200);
  // mug
  g.fillStyle='#c9c2b2';rr(110,400,130,170,12);g.fill();g.strokeStyle='#c9c2b2';g.lineWidth=16;g.beginPath();g.arc(245,480,40,-1.2,1.2);g.stroke();
  // phone
  g.fillStyle='#222';rr(790,330,110,230,16);g.fill();g.fillStyle='#3a5d7a';rr(800,345,90,195,8);g.fill();
  g.save();g.translate(0,Math.sin(lt*2)*6);cube(500,600,58,lt);g.restore();
  const scan=P(lt,0,0.6);if(scan<1){g.fillStyle='rgba(255,179,0,0.25)';g.fillRect(0,scan*PH-4,PW,8)}
  const box=(x,y,w,h,label,col,lw,at)=>{const e=E.out(P(lt,at,at+0.25));if(e<=0)return;const ex=(1-e)*40;g.globalAlpha=e;brackets(x-ex,y-ex,w+2*ex,h+2*ex,30,col,lw);g.strokeStyle=col;g.lineWidth=1;g.strokeRect(x-ex,y-ex,w+2*ex,h+2*ex);
    const tw=TW(label,{font:'JetBrains Mono',weight:700,size:24})+24;g.fillStyle=col;g.fillRect(x-ex,y-ex-40,tw,40);T(label,x-ex+12,y-ex-12,{font:'JetBrains Mono',weight:700,size:24,color:INK});g.globalAlpha=1};
  box(95,385,200,200,'cup 0.91','#cfd8dc',3,0.35);box(775,315,140,260,'cell phone 0.88','#cfd8dc',3,0.45);box(330,330,340,320,"rubik's cube 0.97",GOLD,6,0.6);
  if(lt>0.9){const e=E.back(P(lt,0.9,1.15));g.save();g.translate(500,720);g.scale(e,e);rr(-190,-34,380,60,30);g.fillStyle=GOLD;g.fill();T('NEW CLASS #81 LEARNED',0,7,{font:'Barlow Condensed',weight:800,size:30,track:3,color:INK,align:'center'});g.restore()}
  T('YOLO · 80 classes + 1',30,50,{font:'JetBrains Mono',size:20,color:GOLD})}
function visJarvis(lt,t){g.fillStyle='#0a1016';g.fillRect(0,0,PW,PH);
  T('J.A.R.V.I.S.',30,62,{font:'Barlow',weight:700,size:44,color:'#29c5f6'});chip('OFFLINE · ON THIS PC',640,26,{color:'#4ade80',stroke:'rgba(74,222,128,0.7)',fill:'rgba(74,222,128,0.1)',size:22});
  const cx=270,cy=360,listen=lt>0.5&&lt<1.3;const teal='#1f8fa8';
  g.save();g.translate(cx,cy);
  for(let ring=0;ring<3;ring++){const rad=[200,160,118][ring];g.rotate((ring%2?-1:1)*lt*(0.5+ring*0.3));g.strokeStyle=teal;g.lineWidth=[6,3,8][ring];
    const seg=[10,6,1][ring];for(let i=0;i<seg;i++){g.beginPath();g.arc(0,0,rad,i*TAU/seg,i*TAU/seg+TAU/seg*0.7);g.stroke()}}
  g.restore();for(let i=0;i<60;i++){const a=i/60*TAU;g.strokeStyle='rgba(41,197,246,0.35)';g.lineWidth=2;g.beginPath();g.moveTo(cx+Math.cos(a)*218,cy+Math.sin(a)*218);g.lineTo(cx+Math.cos(a)*(228+(i%5?0:10)),cy+Math.sin(a)*(228+(i%5?0:10)));g.stroke()}
  g.save();g.shadowColor='#29c5f6';g.shadowBlur=listen?40:15;T('JARVIS',cx,cy+18,{font:'Barlow',weight:700,size:62,color:listen?'#7fe3ff':teal,align:'center'});g.restore();
  T(listen?'listening…':lt>1.3?'speaking':'standby',cx,cy+60,{font:'Barlow',size:26,color:teal,align:'center'});
  for(let i=0;i<36;i++){const h=listen||lt>1.3?6+Math.abs(Math.sin(i*0.9+lt*14)*Math.sin(i*0.31+lt*5))*44:6;g.fillStyle='#29c5f6';g.fillRect(70+i*13,640-h/2,6,h)}
  g.fillStyle='#111a22';g.fillRect(540,110,420,620);
  const msgs=[[0.1,'you','"Jarvis, what\'s on my notes for Friday?"'],[1.15,'JARVIS','Friday: ENGR-126 demo day at 2 PM. Bring the robot.']];
  msgs.forEach(([a,who,s],i)=>{if(lt<a)return;const y=150+i*200;T(who.toUpperCase(),560,y,{font:'Barlow',weight:700,size:24,color:i?'#29c5f6':DIM});
    wrap(typed(s,lt,a,55),{font:'Barlow',size:30},380).forEach((l,j)=>T(l,560,y+44+j*38,{font:'Barlow',size:30,color:WHITE}))});
  T('Whisper · gemma · EN TR ES',560,700,{font:'JetBrains Mono',size:18,color:DIM})}
function visDiff(lt,t){g.fillStyle='#0b0a08';g.fillRect(0,0,PW,PH);
  const prompt='"golden sunrise over the Blue Ridge, oil painting"';rr(40,30,900,70,12);g.fillStyle='#17140e';g.fill();g.strokeStyle='rgba(255,179,0,0.5)';g.lineWidth=1.5;g.stroke();
  T(typed(prompt,lt,0,70),62,76,{font:'JetBrains Mono',size:24,color:WHITE});
  const N=64,cs=9,x0=PW/2-N*cs/2,y0=130;const step=Math.min(30,Math.floor(P(lt,0.4,1.8)*30));const a=1-E.io(P(lt,0.4,1.8));const r=R(step*31+7);
  for(let j=0;j<N;j++)for(let i=0;i<N;i++){const u=i/N,v=j/N;let c;
    const ridge=0.6+0.07*Math.sin(u*8+1)+0.035*Math.sin(u*23),ridge2=0.72+0.05*Math.sin(u*5+3)+0.03*Math.sin(u*17);const sd=Math.hypot(u-0.5,(v-0.48)*1.1);
    if(v>ridge2)c=[40+30*v,24+12*v,12];else if(v>ridge)c=[70,45,40];else{const k=v/ridge;c=[lerp(30,255,k*k),lerp(20,150,k*k),lerp(50,40,k)];if(sd<0.12){c=[255,230,140]}else if(sd<0.2){const q=(sd-0.12)/0.08;c=[lerp(255,c[0],q),lerp(200,c[1],q),lerp(90,c[2],q)]}}
    const br=(Math.sin(i*1.7+j*0.9)*0.5+0.5)*14;const nz=r()*255;
    g.fillStyle=`rgb(${lerp(c[0]+br,nz,a)|0},${lerp(c[1]+br,nz*0.85,a)|0},${lerp(c[2],nz*0.7,a)|0})`;g.fillRect(x0+i*cs,y0+j*cs,cs+0.5,cs+0.5)}
  g.strokeStyle=GOLD;g.lineWidth=3;g.strokeRect(x0,y0,N*cs,N*cs);
  T('denoising step '+step+'/30',x0,y0+N*cs+44,{font:'JetBrains Mono',size:22,color:GOLD});
  g.fillStyle='rgba(255,179,0,0.2)';g.fillRect(x0+300,y0+N*cs+28,276,12);g.fillStyle=GOLD;g.fillRect(x0+300,y0+N*cs+28,276*step/30,12)}
function visDrone(lt,t){const gr=g.createLinearGradient(0,0,0,PH);gr.addColorStop(0,'#1a2230');gr.addColorStop(1,'#0c0e10');g.fillStyle=gr;g.fillRect(0,0,PW,PH);g.fillStyle='#14120e';g.fillRect(0,600,PW,160);
  const sig=['UP','LEFT','RIGHT','UP'][Math.min(3,Math.floor(lt/0.5))];const tx=420+(-Math.sin(clamp((lt-0.5)/0.5)*Math.PI)*0)+(lt>0.5&&lt<1?-180*E.io(P(lt,0.5,0.9)):0)+(lt>=1?lerp(-180,170,E.io(P(lt,1,1.4))):0)-(lt>=1.5?170*E.io(P(lt,1.5,1.9))*0:0);
  const ty=lerp(400,300,E.io(P(lt,0,0.5)))+Math.sin(lt*7)*6+(lt>1.5?-60*E.io(P(lt,1.5,1.9)):0);
  g.fillStyle='rgba(0,0,0,0.5)';g.beginPath();g.ellipse(tx,650,140-((400-ty)/5),18,0,0,TAU);g.fill();
  g.save();g.translate(tx,ty);g.rotate(lt>0.5&&lt<0.9?-0.12:lt>1&&lt<1.4?0.12:0);
  g.fillStyle='#2b2b2b';g.fillRect(-170,-6,340,12);[-170,170].forEach(x=>{g.fillStyle='#444';g.fillRect(x-12,-18,24,22);
    g.fillStyle='rgba(200,200,200,0.25)';g.beginPath();g.ellipse(x,-22,95,10,0,0,TAU);g.fill();const pa=lt*80;g.strokeStyle='rgba(255,255,255,0.7)';g.lineWidth=3;g.beginPath();g.moveTo(x-Math.cos(pa)*90,-22);g.lineTo(x+Math.cos(pa)*90,-22);g.stroke()});
  rr(-70,-28,140,52,18);g.fillStyle='#e8e2d0';g.fill();g.fillStyle=GOLD;g.fillRect(-70,0,140,6);g.fillStyle='#111';g.beginPath();g.arc(0,30,13,0,TAU);g.fill();
  g.fillStyle=Math.floor(lt*6)%2?'#4ade80':'#14532d';g.beginPath();g.arc(50,-12,5,0,TAU);g.fill();g.restore();
  // webcam inset with person signalling
  const ix=40,iy=440;rr(ix,iy,250,280,12);g.fillStyle='#0d1117';g.fill();g.strokeStyle=GOLD;g.lineWidth=2;g.stroke();
  const px=ix+125,py=iy+150;g.strokeStyle='#e8e2d0';g.lineWidth=9;g.lineCap='round';g.beginPath();g.arc(px,py-75,22,0,TAU);g.stroke();
  g.beginPath();g.moveTo(px,py-50);g.lineTo(px,py+40);g.lineTo(px-30,py+100);g.moveTo(px,py+40);g.lineTo(px+30,py+100);g.stroke();
  const arms={UP:[[-40,-120],[40,-120]],LEFT:[[-95,-35],[25,20]],RIGHT:[[-25,20],[95,-35]]}[sig];
  g.strokeStyle=GOLD;g.beginPath();g.moveTo(px,py-35);g.lineTo(px+arms[0][0],py-35+arms[0][1]*0.6+ (sig==='UP'?-0:0));g.moveTo(px,py-35);g.lineTo(px+arms[1][0],py-35+arms[1][1]*0.6);g.stroke();
  T('SIGNAL: '+sig,ix+125,iy+268,{font:'Barlow Condensed',weight:800,size:28,track:3,color:GOLD,align:'center'});
  T('→ '+{UP:'ASCEND',LEFT:'FLY LEFT',RIGHT:'FLY RIGHT'}[sig],610,700,{font:'JetBrains Mono',weight:700,size:30,color:WHITE})}
function visRobot(lt,t){g.fillStyle='#0d0d10';g.fillRect(0,0,PW,PH);g.fillStyle='#17161a';g.fillRect(0,560,PW,200);
  const wave=lt>1.1;const bx=360,by=380+Math.sin(lt*12)*(wave?0:4);
  g.fillStyle='#d9d4c7';rr(bx-150,by-40,300,90,30);g.fill();g.fillStyle=GOLD;g.fillRect(bx-60,by-40,120,14);
  g.fillStyle='#d9d4c7';rr(bx+120,by-110,110,90,26);g.fill();g.fillStyle='#111';g.beginPath();g.arc(bx+195,by-75,9,0,TAU);g.fill();g.fillStyle=GOLD;g.beginPath();g.arc(bx+235,by-60,10,0,TAU);g.fill();
  g.strokeStyle='#d9d4c7';g.lineWidth=8;g.beginPath();g.moveTo(bx-150,by-20);g.lineTo(bx-200,by-80+Math.sin(lt*16)*15);g.stroke();
  const leg=(hx,ph,front)=>{let a1=Math.sin(lt*10+ph)*0.35,a2=0.5+Math.max(0,Math.sin(lt*10+ph))*0.5;
    if(wave&&front){const w=E.out(P(lt,1.1,1.3));a1=lerp(a1,-1.9+Math.sin(lt*18)*0.25,w);a2=lerp(a2,-0.6,w)}
    const k=[hx+Math.sin(a1)*95,by+40+Math.cos(a1)*95],f=[k[0]+Math.sin(a1-a2)*100,k[1]+Math.cos(a1-a2)*100];
    g.strokeStyle='#bfb9aa';g.lineWidth=18;g.lineCap='round';g.beginPath();g.moveTo(hx,by+40);g.lineTo(...k);g.lineTo(...f);g.stroke();g.fillStyle=GOLD;g.beginPath();g.arc(k[0],k[1],9,0,TAU);g.fill()};
  leg(bx-110,0,false);leg(bx+110,Math.PI,true);leg(bx-80,Math.PI,false);leg(bx+130,0,false);
  const skills=[['sit',0.1],['lift paw',0.35],['bark',0.6]];T('BASIC MOVES',620,90,{font:'Barlow Condensed',weight:700,size:28,track:6,color:DIM});
  skills.forEach(([s,a],i)=>{if(lt>a)chip(s.toUpperCase(),620,110+i*62,{color:WHITE,stroke:'rgba(255,255,255,0.4)',fill:'rgba(255,255,255,0.05)'})});
  if(lt>0.85){const e=E.back(P(lt,0.85,1.1));g.save();g.globalAlpha=clamp(e);T('GEMMA COMBINED →',620,340,{font:'Barlow Condensed',weight:700,size:28,track:6,color:DIM});
    g.translate(620,360);g.scale(e,e);rr(0,0,330,70,35);g.fillStyle=GOLD;g.fill();T('"SAY HELLO"',165,48,{font:'Barlow Condensed',weight:800,size:36,track:3,color:INK,align:'center'});g.restore()}
  T('AiNex · PiDog · Reachy Mini',30,720,{font:'JetBrains Mono',size:22,color:GOLD})}
function heart(x,y,s){g.beginPath();g.moveTo(x,y+s*0.3);g.bezierCurveTo(x,y,x-s*0.5,y,x-s*0.5,y+s*0.3);g.bezierCurveTo(x-s*0.5,y+s*0.6,x,y+s*0.8,x,y+s);g.bezierCurveTo(x,y+s*0.8,x+s*0.5,y+s*0.6,x+s*0.5,y+s*0.3);g.bezierCurveTo(x+s*0.5,y,x,y,x,y+s*0.3);g.fill()}
function visMars(lt,t){g.fillStyle='#04050a';g.fillRect(0,0,PW,PH);const r=R(8);for(let i=0;i<150;i++){g.fillStyle=`rgba(255,255,255,${r()*0.8})`;g.fillRect(r()*PW,r()*PH,1.5,1.5)}
  const mg=g.createRadialGradient(150,260,20,190,300,150);mg.addColorStop(0,'#ff8a50');mg.addColorStop(1,'#7a2410');g.fillStyle=mg;g.beginPath();g.arc(190,300,140,0,TAU);g.fill();
  g.fillStyle='rgba(80,20,8,0.5)';[[150,260,22],[230,340,30],[170,370,14]].forEach(c=>{g.beginPath();g.arc(...c,0,TAU);g.fill()});
  const eg=g.createRadialGradient(780,250,10,800,280,110);eg.addColorStop(0,'#7cc6ff');eg.addColorStop(1,'#123d7a');g.fillStyle=eg;g.beginPath();g.arc(800,280,105,0,TAU);g.fill();
  g.fillStyle='rgba(70,160,90,0.8)';g.beginPath();g.ellipse(780,260,40,25,0.5,0,TAU);g.fill();
  T('MARS',190,490,{font:'Barlow Condensed',weight:700,size:28,track:8,color:'#ff8a50',align:'center'});T('EARTH',800,440,{font:'Barlow Condensed',weight:700,size:28,track:8,color:'#7cc6ff',align:'center'});
  g.fillStyle='#0e6e6e';rr(260,150,90,60,6);g.fill();g.fillStyle=GOLD;for(let i=0;i<6;i++)g.fillRect(266+i*14,150,6,8);
  for(let w=0;w<4;w++){const k=((lt*0.9+w*0.25)%1);g.strokeStyle=`rgba(255,179,0,${1-k})`;g.lineWidth=3;g.beginPath();g.arc(330,190,30+k*470,-0.4,0.4);g.stroke()}
  const pk=(lt*0.7)%1;const px=lerp(360,690,pk),py=lerp(200,260,pk);g.fillStyle=GOLD;rr(px-110,py-26,220,52,10);g.fill();T('I AM ALIVE',px,py+10,{font:'Barlow Condensed',weight:800,size:30,track:2,color:INK,align:'center'});
  // ECG strip
  g.fillStyle='rgba(255,179,0,0.06)';g.fillRect(30,560,920,170);g.strokeStyle=GOLD;g.lineWidth=4;g.shadowColor=GOLD;g.shadowBlur=14;g.beginPath();
  const ecg=x=>{const p=((x%0.83)+0.83)%0.83/0.83;return p>0.4&&p<0.43?-(p-0.4)/0.03*90:p>=0.43&&p<0.46?(-90+(p-0.43)/0.03*130):p>=0.46&&p<0.49?40-(p-0.46)/0.03*40:p>0.6&&p<0.7?-Math.sin((p-0.6)/0.1*Math.PI)*15:0};
  for(let i=0;i<=460;i++){const x=30+i*2;const tt=lt*1.3+i/460*2.2;const y=650+ecg(tt);i?g.lineTo(x,y):g.moveTo(x,y)}g.stroke();g.shadowBlur=0;
  g.fillStyle='#ff4d6d';const hb=1+0.25*Math.exp(-(((lt*1.3)%0.83))*12);g.save();g.translate(905,500);g.scale(hb,hb);heart(0,-30,40);g.restore();
  T('72',800,540,{size:54,color:WHITE,align:'right'});T('BPM',808,540,{font:'Barlow Condensed',weight:700,size:26,color:DIM})}
function visRace(lt,t){const hy=250,F=520,cxp=PW/2;const sk=g.createLinearGradient(0,0,0,hy);sk.addColorStop(0,'#cfd3d6');sk.addColorStop(1,'#eef0f0');g.fillStyle=sk;g.fillRect(0,0,PW,hy);
  // skyline
  const r=R(4);for(let i=0;i<16;i++){const x=r()*PW,w=40+r()*90,h=40+r()*120;g.fillStyle=r()<0.4?'#b5654e':'#aab3bb';g.fillRect(x,hy-h,w,h)}
  g.fillStyle='#4a7a3a';g.fillRect(PW/2+60,hy,PW,PH);g.fillStyle='#55585c';g.fillRect(0,hy,PW/2-60,PH);
  const pr=(x,z)=>[cxp+x*F/z,hy+1.2*F/z];const sp=lt*28;
  // road
  g.fillStyle='#2b2d31';const a=pr(-7,1),b=pr(7,1),c=pr(7,200),d=pr(-7,200);g.beginPath();g.moveTo(...a);g.lineTo(...b);g.lineTo(...c);g.lineTo(...d);g.fill();
  for(let k=0;k<60;k++){const z0=k*2-(sp%4)+0.6,z1=z0+1;if(z0<0.5)continue;
    [[-7.4,-7],[7,7.4]].forEach(([x0,x1])=>{g.fillStyle=(k%2)?'#d64545':'#f2f2f2';const p=[pr(x0,z0),pr(x1,z0),pr(x1,z1),pr(x0,z1)];g.beginPath();g.moveTo(...p[0]);p.slice(1).forEach(q=>g.lineTo(...q));g.fill()});
    if(k%2===0){g.fillStyle='#f2f2f2';const p=[pr(-0.12,z0),pr(0.12,z0),pr(0.12,z0+0.8),pr(-0.12,z0+0.8)];g.beginPath();g.moveTo(...p[0]);p.slice(1).forEach(q=>g.lineTo(...q));g.fill()}}
  // crowd + trees on right
  for(let k=40;k>=0;k--){const z=k*1.5-(sp%1.5)+1.2;if(z<1)continue;const [x,y]=pr(9,z),s=F/z;
    for(let m=0;m<3;m++){g.fillStyle=['#ffcc00','#222','#ffcc00'][m];g.fillRect(x+m*s*0.35,y-s*1.1,s*0.22,s*0.6);g.fillStyle='#e0c09a';g.beginPath();g.arc(x+m*s*0.35+s*0.11,y-s*1.2,s*0.1,0,TAU);g.fill()}
    if(k%3===0){const [tx2,ty2]=pr(14,z);g.fillStyle='#2f6b2a';g.beginPath();g.arc(tx2,ty2-s*3,s*1.4,0,TAU);g.fill()}}
  // gate
  const gz=lerp(16,0.9,P(lt,0,1.7));if(gz>1){const [lx,ly]=pr(-7.6,gz),[rx]=pr(7.6,gz),s=F/gz;g.fillStyle='#1d2329';g.fillRect(lx-s*0.25,ly-s*5.5,s*0.5,s*5.5);g.fillRect(rx-s*0.25,ly-s*5.5,s*0.5,s*5.5);
    g.fillStyle='#1d2329';g.fillRect(lx-s*0.25,ly-s*6.2,rx-lx+s*0.5,s*1.1);g.fillStyle='#c9a227';g.fillRect(lx,ly-s*6.05,rx-lx,s*0.8);
    T('VCU CAMPUS RACE',(lx+rx)/2,ly-s*5.45,{size:s*0.62,color:'#1d2329',align:'center'})}
  // car
  const cx=PW/2+Math.sin(lt*2.3)*40,cy=640;g.save();g.translate(cx,cy);g.rotate(Math.sin(lt*2.3+1)*0.02);
  g.fillStyle='rgba(0,0,0,0.45)';g.beginPath();g.ellipse(0,40,190,22,0,0,TAU);g.fill();
  g.fillStyle='#111';g.fillRect(-170,0,60,44);g.fillRect(110,0,60,44);
  g.fillStyle='#c41d1d';g.beginPath();g.moveTo(-180,20);g.lineTo(-170,-40);g.quadraticCurveTo(-120,-70,-80,-72);g.lineTo(80,-72);g.quadraticCurveTo(120,-70,170,-40);g.lineTo(180,20);g.closePath();g.fill();
  g.fillStyle='#8c1212';g.fillRect(-180,8,360,18);g.fillStyle='#1a1a1a';rr(-95,-115,190,50,14);g.fill();g.fillStyle='#c41d1d';rr(-110,-80,220,16,6);g.fill();
  g.fillStyle='#ff2b2b';g.shadowColor='#ff2b2b';g.shadowBlur=20;[-140,140].forEach(x=>{g.beginPath();g.arc(x,-28,15,0,TAU);g.fill()});g.shadowBlur=0;
  g.fillStyle='#f5f5f0';rr(-48,-30,96,30,4);g.fill();T('DR TOPS',0,-8,{font:'Barlow Condensed',weight:800,size:20,color:'#1a2a6c',align:'center'});g.restore();
  g.fillStyle='rgba(0,0,0,0.55)';rr(20,20,320,120,12);g.fill();T('LAP 2/3',40,62,{font:'Barlow Condensed',weight:800,size:34,track:4,color:GOLD});
  const tm=37.9+lt;T('0:'+tm.toFixed(2),40,120,{size:52,color:WHITE});
  T(Math.round(142+Math.sin(lt*3)*6)+' KM/H',PW-30,PH-30,{size:48,color:WHITE,align:'right'})}
function visRag(lt,t){g.fillStyle='#0d0c0a';g.fillRect(0,0,PW,PH);
  g.save();g.translate(40,40);g.rotate(-0.02);g.fillStyle='#efe6d2';g.fillRect(0,0,420,680);
  T('THE RAVEN',30,62,{font:'Barlow Condensed',weight:800,size:34,track:6,color:'#2a2418'});T('Edgar Allan Poe · stanza 8',30,94,{font:'Barlow',size:20,color:'#7a705c'});
  const L=['Then this ebony bird beguiling','my sad fancy into smiling,','By the grave and stern decorum','of the countenance it wore,','"Though thy crest be shorn and','shaven, thou," I said, "art sure','no craven, ghastly grim and','ancient Raven wandering from','the Nightly shore— Tell me what','thy lordly name is on the Night\'s','Plutonian shore!"','Quoth the Raven "Nevermore."'];
  L.forEach((l,i)=>{const y=150+i*42;if(i===11){const hp=E.out(P(lt,0.8,1.1));g.fillStyle='rgba(255,179,0,0.55)';g.fillRect(24,y-28,TW(l,{font:'Barlow',size:22,weight:700})*hp+12,38)}
    T(l,30,y,{font:'Barlow',size:22,weight:i===11?700:400,color:'#2a2418'})});g.restore();
  T('Q',500,120,{size:30,color:DIM});rr(540,80,400,80,16);g.fillStyle='#f3ead6';g.fill();T(typed('What does the raven keep saying?',lt,0,60),560,130,{font:'Barlow',size:26,weight:600,color:INK});
  if(lt>0.85){const s=typed('"Nevermore." The Raven first says it at the end of stanza 8.',lt,0.85,60);rr(500,200,440,220,16);g.fillStyle='rgba(255,179,0,0.12)';g.fill();g.strokeStyle=GOLD;g.lineWidth=1.5;g.stroke();
    wrap(s,{font:'Barlow',size:30,weight:500},400).forEach((l,i)=>T(l,522,250+i*42,{font:'Barlow',size:30,weight:500,color:WHITE}));
    if(lt>1.6)chip('[1] THE RAVEN · STANZA 8',522,440,{size:22})}
  T('runs locally · cites its sources',500,700,{font:'JetBrains Mono',size:20,color:DIM})}

const PROJ=[
  {n:'01',t:['HAND','GESTURES'],d:'Your webcam names fist, point, peace and open palm.',tags:['ENGINEERING','LAPTOP'],v:visHand},
  {n:'03',t:['SQUAT','COACH'],d:'Measures knee and hip angles while you move.',tags:['MEDICINE','LAPTOP'],v:visSquat},
  {n:'04',t:['THE 81ST','OBJECT'],d:"Teach YOLO to spot a Rubik's cube.",tags:['ENGINEERING','LAPTOP'],v:visYolo},
  {n:'19',t:['J.A.R.V.I.S.'],d:'A voice assistant that hears, speaks, sees and acts, all offline.',tags:['ENGINEERING','LAPTOP'],v:visJarvis},
  {n:'14',t:['TEXT TO','IMAGE'],d:'Stable Diffusion paints whatever you type.',tags:['ART','COLAB'],v:visDiff},
  {n:'22',t:['GESTURE','DRONE'],d:'Arm signals from your webcam fly a real drone.',tags:['ENGINEERING','LAPTOP + DRONE'],v:visDrone},
  {n:'23',t:['ROBOT','SKILLS'],d:'Code basic moves. Gemma combines them into new skills.',tags:['ENGINEERING','LAPTOP + ROBOT'],v:visRobot},
  {n:'25',t:['MARTIAN','HEARTBEAT'],d:'Stranded on Mars? An Arduino radios your heart rate to Earth.',tags:['MEDICINE','2 ARDUINOS'],v:visMars},
  {n:'20C',t:['VCU CAMPUS','RACE'],d:'A 3D game on real Richmond streets around Monroe Park.',tags:['GAMING','LAPTOP'],v:visRace},
  {n:'18',t:['RAG','READER'],d:"A chatbot that answers from Poe's works and cites its sources.",tags:['LITERATURE','LAPTOP'],v:visRag}];
function s6(lt,t){bg(t,{gridA:0.18,dustA:0.4});const i=Math.min(PROJ.length-1,Math.floor(lt/2)),pl=lt-i*2,p=PROJ[i];
  const ein=E.out(P(pl,0,0.35));
  // left text
  const tx=V?60:110,ly=V?300:270,t0=V?430:400;
  g.save();g.beginPath();g.rect(0,0,V?W:800,H);g.clip();const ox=-(1-ein)*300;
  T('PROJECT',tx+ox,ly,{font:'Barlow Condensed',weight:700,size:36,track:14,color:DIM});T(p.n,tx+ox+TW('PROJECT',{font:'Barlow Condensed',weight:700,size:36,track:14})+16,ly+2,{size:56,color:GOLD,glow:18});
  p.t.forEach((l,j)=>T(l,tx-4+ox*(1+j*0.3),t0+j*130,{size:p.t.length===1?120:130,color:j?GOLD:WHITE}));
  const dy=V?1475:400+p.t.length*130-40;wrap(p.d,{font:'Barlow',size:36,weight:500},V?940:620).forEach((l,j)=>T(l,tx+ox,dy+j*48,{font:'Barlow',size:36,weight:500,color:'#d9d2c2',alpha:E.out(P(pl,0.15,0.5))}));
  let cx=tx;p.tags.forEach(s=>{g.globalAlpha=E.out(P(pl,0.25,0.55));cx+=chip(s,cx+ox,V?1570:dy+120)+14});g.globalAlpha=1;g.restore();
  // index dots
  PROJ.forEach((_,j)=>{g.fillStyle=j===i?GOLD:'rgba(255,255,255,0.18)';g.fillRect(tx+j*46,V?1660:980,36,6)});
  // right panel
  const px=(V?50:840)+(1-ein)*1100,py=V?640:160;g.save();g.translate(px,py);g.shadowColor='rgba(255,179,0,0.35)';g.shadowBlur=50;rr(0,0,PW,PH,20);g.fillStyle='#000';g.fill();g.shadowBlur=0;
  rr(0,0,PW,PH,20);g.clip();p.v(pl,t);g.restore();
  g.save();g.translate(px,py);rr(0,0,PW,PH,20);g.strokeStyle='rgba(255,179,0,0.75)';g.lineWidth=3;g.stroke();
  g.fillStyle='#ff3b3b';g.globalAlpha=Math.floor(t*2)%2?1:0.3;g.beginPath();g.arc(PW-TW('STUDENT BUILD',{font:'Barlow Condensed',weight:700,size:24,track:6})-22,-24,8,0,TAU);g.fill();g.globalAlpha=1;
  T('STUDENT BUILD',PW,-16,{font:'Barlow Condensed',weight:700,size:24,track:6,color:DIM,align:'right'});g.restore();
  // exit wipe
  if(pl>1.82&&i<PROJ.length-1){const k=E.in(P(pl,1.82,2));g.fillStyle=GOLD;g.fillRect(-200+k*0,0,k*W*1.2,H)}
  if(pl<0.12&&i>0){const k=E.out(P(pl,0,0.12));g.fillStyle=GOLD;g.fillRect(k*W*1.1,0,W*1.2,H)}
}
const ALL=['Hand Gestures','Handwriting AI','Squat Coach','The 81st Object','FaceHello','Distance Alarm','Air Mouse','Wake-up Alarm','Face Invaders','Face Off','Green Screen','CLIP Talking Camera','Beyond the Laptop','Text to Image','Text to Video','Paint Like a Master','Gemma Chatbot','RAG Reader','J.A.R.V.I.S.','Indie 3D Game','Receipt Reader','Gesture Drone','Robot Skills','UHF TV Antenna','Martian Heartbeat'];
const HW=new Set([6,16,22,23,24,25]);
function s6b(lt,t){bg(t,{gridA:0.3});const push=lerp(1,1.05,lt/4);g.save();g.translate(W/2,H/2);g.scale(push,push);g.translate(-W/2,-H/2);
  const n=Math.round(25*E.out(P(lt,0,1.4)));const hs=V?130:150,hy=V?320:175;T(String(n),W/2-(V?190:30),hy,{size:hs,color:GOLD,align:'right',glow:30});T('PROJECTS.',W/2-(V?170:10),hy,{size:hs,color:WHITE});
  T('BUILT BY BEGINNERS IN ONE SEMESTER',W/2,V?385:232,{font:'Barlow Condensed',weight:700,size:36,track:12,align:'center',color:DIM,alpha:E.out(P(lt,0.6,1))});
  const NC=V?3:5,tw=320,th=V?110:128,gx=16,gy=V?12:14,x0=W/2-(NC*tw+(NC-1)*gx)/2,y0=V?430:270;
  ALL.forEach((s,i)=>{const c=i%NC,r=Math.floor(i/NC);const a=0.05+i*0.045;const e=E.back(P(lt,a,a+0.4));if(e<=0)return;
    const x=x0+c*(tw+gx),y=y0+r*(th+gy);const lit=lt>2&&(Math.floor(lt*2)*7+i*3)%11===0;
    g.save();g.translate(x+tw/2,y+th/2);g.scale(e,e);g.globalAlpha=clamp(e);rr(-tw/2,-th/2,tw,th,12);g.fillStyle=lit?'rgba(255,179,0,0.28)':'rgba(20,18,13,0.92)';g.fill();g.strokeStyle=lit?GOLD:'rgba(255,179,0,0.35)';g.lineWidth=lit?3:1.5;g.stroke();
    T(String(i+1).padStart(2,'0'),-tw/2+20,-th/2+48,{size:36,color:GOLD});
    if(HW.has(i+1))T('HW',tw/2-18,-th/2+40,{font:'Barlow Condensed',weight:800,size:22,track:3,color:INK,align:'right'}),g.fillStyle=GOLD,g.globalAlpha=0.9;
    if(HW.has(i+1)){rr(tw/2-70,-th/2+14,56,34,8);g.fill();T('HW',tw/2-42,-th/2+39,{font:'Barlow Condensed',weight:800,size:22,track:2,color:INK,align:'center'})}
    T(s,-tw/2+20,th/2-24,{font:'Barlow Condensed',weight:700,size:36,color:WHITE});g.restore()});
  const fo={font:'Barlow Condensed',weight:700,size:36,track:8,align:'center',color:GOLD,alpha:E.out(P(lt,1.6,2.1))};
  if(V){T('ENGINEERING · MEDICINE · ART',W/2,1600,fo);T('BUSINESS · GAMING · LITERATURE',W/2,1652,fo)}
  else T('ENGINEERING · MEDICINE · ART · BUSINESS · GAMING · LITERATURE',W/2,1020,fo);
  g.restore()}
function s7(lt,t){bg(t,{grid:false,dustA:0.6,c0:'#120f08'});const z=lerp(1,1.08,lt/4);g.save();g.translate(W/2,H/2);g.scale(z,z);g.translate(-W/2,-H/2);g.translate(0,YO);
  const f1=1-E.in(P(lt,1.9,2.2));
  [['YOU BRING',0.1,430],['THE IDEAS.',0.4,600]].forEach(([s,a,y])=>{const e=E.out(P(lt,a,a+0.4));T(s,W/2,y+(1-e)*40,{size:180,align:'center',alpha:e*f1})});
  [['AI BRINGS',2.1,430],['THE CODE.',2.4,600]].forEach(([s,a,y])=>{const e=E.out(P(lt,a,a+0.4));T(s,W/2,y+(1-e)*40,{size:180,align:'center',color:GOLD,glow:30,alpha:e})});
  T('NO CODING EXPERIENCE REQUIRED',W/2,760,{font:'Barlow Condensed',weight:700,size:V?40:46,track:V?8:16,align:'center',alpha:E.out(P(lt,3.0,3.4))});
  g.restore();
  // riser light
  g.save();g.globalCompositeOperation='lighter';g.globalAlpha=E.in(P(lt,2.5,4))*0.5;rays(t*3,W/2,H/2,1,24,0.6);g.restore()}
function s8(lt,t){const NS=V?285:330;bg(t,{gridA:0.45,c0:'#221905'});rays(t,W/2,470+YO,0.7,20,0.1);
  T('YOUR GUIDE',W/2,300+YO,{font:'Barlow Condensed',weight:700,size:48,track:22,align:'center',color:GOLD,alpha:E.out(P(lt,0.1,0.4))});
  // glitch-in name
  const gk=1-P(lt,0,0.7);const r=R(Math.floor(lt*24));
  g.save();g.translate(W/2,600+YO);
  if(gk>0){for(let s=0;s<8;s++){const y0=-300+s*45;g.save();g.beginPath();g.rect(-900,y0,1800,45);g.clip();T('DR. TOPS',(r()-0.5)*160*gk,0,{size:NS,align:'center',color:r()<0.3?GOLD:WHITE,alpha:r()<gk*0.4?0:1});g.restore()}}
  else{splat(0,-100,700,220,909,(lt-0.7)*2,{n:120,alpha:0.35});T('DR. TOPS',0,0,{size:NS,align:'center',color:WHITE,glow:40,glowColor:'rgba(255,179,0,0.6)'});
    T('DR. TOPS',0,0,{size:NS,align:'center',color:sweepFill(-700,700,P(lt,1.0,2.4),0.9)})}
  g.restore();
  T('Prof. Erdem Topsakal',W/2,720+YO,{font:'Barlow',weight:600,size:54,align:'center',alpha:E.out(P(lt,0.9,1.3))});
  T('VCU COLLEGE OF ENGINEERING',W/2,785+YO,{font:'Barlow Condensed',weight:700,size:38,track:14,align:'center',color:DIM,alpha:E.out(P(lt,1.2,1.6))});
  // license plate callback
  const e=E.back(P(lt,2.4,2.8));if(e>0){g.save();g.translate(W/2,930+YO);g.rotate(-0.04);g.scale(e,e);rr(-170,-60,340,120,14);g.fillStyle='#f6f4ee';g.fill();g.strokeStyle='#1a2a6c';g.lineWidth=5;g.stroke();
    T('ENGR-126',0,-30,{font:'Barlow Condensed',weight:700,size:22,track:6,color:'#1a2a6c',align:'center'});T('DR TOPS',0,40,{size:70,color:'#1a2a6c',align:'center'});g.restore();
    T('(yes, it\'s on the race car)',V?W/2:W/2+230,V?1045+YO:960,{font:'Barlow',size:28,color:DIM,align:V?'center':'left',alpha:E.out(P(lt,3.0,3.4))})}
}
function s9(lt,t){const RX=V?W/2+170:1450,ty=V?60:0;bg(t,{gridA:0.5,c0:'#261b05'});rays(t,RX,V?1400:430,0.9,22,0.1);
  splat(RX,V?1750:900,520,260,555,lt*0.7,{mode:'rise',n:260,alpha:0.7});
  const k=E.back(P(lt,0,0.55));drawRodney(RX,H+40+(1-k)*900,V?900:1000,t);
  const x=V?60:120;
  const e1=E.out(P(lt,0.15,0.5));TM([['V',GOLD],['IBE ',WHITE],['C',GOLD],['ODING',WHITE]],x-(1-e1)*200,300+ty,{size:150,alpha:e1});
  const e2=E.back(P(lt,0.45,0.8));g.save();g.translate(x,490+ty);g.scale(lerp(1.3,1,e2),lerp(1.3,1,e2));TM([['UN',GOLD],['LEASHED',WHITE]],0,0,{size:200,alpha:clamp(e2*2),glow:20,glowColor:'rgba(0,0,0,0.5)'});g.restore();
  T('UN',x,490+ty,{size:200,color:sweepFill(x,x+800,P(lt,1.2,2.6),0.8)});
  const e3=E.out(P(lt,1.0,1.4));g.fillStyle=GOLD;g.fillRect(x,530+ty,lerp(0,700,e3),5);
  T('ENGR-126  ·  VIBE CODING WITH AI',x,600+ty,{font:'Barlow Condensed',weight:800,size:V?44:52,track:V?6:8,alpha:e3});
  const e4=E.back(P(lt,1.6,1.95));g.save();g.translate(x,760+ty);g.scale(lerp(1.5,1,e4),lerp(1.5,1,e4));T('SPRING 2027',0,0,{size:150,color:GOLD,glow:35,alpha:clamp(e4*2)});g.restore();
  const e5=E.out(P(lt,2.3,2.7));if(e5>0){const pulse=1+0.03*beatPulse(t,6);g.save();g.translate(x+300,860+ty);g.scale(pulse,pulse);g.globalAlpha=e5;
    rr(-300,-46,600,92,6);g.fillStyle=GOLD;g.shadowColor=GOLD;g.shadowBlur=30*beatPulse(t,5);g.fill();g.shadowBlur=0;
    T('REGISTER NOW',-260,16,{font:'Barlow Condensed',weight:800,size:46,track:14,color:INK});T('↗',250,18,{font:'Barlow',weight:700,size:46,color:INK,align:'right'});g.restore()}
  const fo={font:'Barlow',weight:500,size:30,color:'#cfc7b4',alpha:E.out(P(lt,3.0,3.4))};
  if(V){const vo={...fo,size:30,color:WHITE};T('No coding experience required  ·  with Dr. Tops',x,1018,vo);T('VCU College of Engineering',x,1060,vo)}
  else T('No coding experience required  ·  with Dr. Tops  ·  VCU College of Engineering',x,990,fo);
}

const SCENES=[[0,6,s1],[6,12,s2],[12,20,s3],[20,26,s4],[26,34,s5],[34,54,s6],[54,58,s6b],[58,62,s7],[62,68,s8],[68,DUR,s9]];
function render(t){g.setTransform(1,0,0,1,0,0);g.globalAlpha=1;g.globalCompositeOperation='source-over';g.shadowBlur=0;g.fillStyle='#000';g.fillRect(0,0,W,H);
  const drop=(t>=6&&t<58)||(t>=62&&t<74);const z=drop?1+0.01*beatPulse(t,9):1;const [sx,sy]=shakeAt(t);
  g.save();g.translate(W/2+sx,H/2+sy);g.scale(z,z);g.translate(-W/2,-H/2);
  for(const [a,b,f] of SCENES)if(t>=a&&t<b){f(t-a,t);break}
  g.restore();post(t)}
window.render=render;window.DUR=DUR;
window.ready=Promise.all([document.fonts.load('100px Anton'),document.fonts.load('700 50px "Barlow Condensed"'),document.fonts.load('800 50px "Barlow Condensed"'),document.fonts.load('400 30px Barlow'),document.fonts.load('500 30px Barlow'),document.fonts.load('600 30px Barlow'),document.fonts.load('700 30px Barlow'),document.fonts.load('30px "JetBrains Mono"'),document.fonts.load('700 30px "JetBrains Mono"'),new Promise(r=>{if(rod.complete)r();else rod.onload=r})]).then(()=>document.fonts.ready);
