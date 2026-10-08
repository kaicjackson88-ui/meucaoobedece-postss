// =====================================================================
// Personagens 2D (desenho vetorial no canvas, traço de cartoon)
// persona(id, x, y, s, t, st) desenha alguém com os pés em (x,y).
// st = {humor, pose, posePrev, tPose, falando, olhar(-1..1), dir(1|-1), sentado, anda}
// humor: normal feliz radiante triste bravo surpreso preocupado vergonha cansado
// pose:  parado aponta maos_cabeca bracos_cruzados maos_cintura petisco acena
//        celular comemora maos_rosto carinho guia bilhete explica
// =====================================================================
const PELE=['#F6D2B0','#E8B48C','#C98B62','#9A6244','#6E4430'];
const ELENCO={
 ana:{pele:PELE[1],cabelo:'#5A3420',estilo:'longo',roupa:'#2F9C8A',calca:'#3B4A6B',sapato:'#F4EEE4',fase:.3},
 vizinho:{pele:PELE[0],cabelo:'#BDB7AF',estilo:'careca',roupa:'#D9A441',calca:'#6B5A4A',sapato:'#4A3A30',oculos:true,bigode:true,botoes:true,fase:1.7},
 sindica:{pele:PELE[3],cabelo:'#2A2622',estilo:'coque',roupa:'#C85A6A',calca:'#2A2622',sapato:'#2A2622',oculos:true,fase:2.4},
 joao:{pele:PELE[2],cabelo:'#2A2622',estilo:'curto',roupa:'#E07A3F',calca:'#3B4A6B',sapato:'#F4EEE4',barba:true,fase:.9},
 bia:{pele:PELE[4],cabelo:'#2A2622',estilo:'cacheado',roupa:'#8B6FD0',calca:'#2F4858',sapato:'#F4EEE4',fase:1.2},
 carla:{pele:PELE[0],cabelo:'#C9772E',estilo:'rabo',roupa:'#E5B23C',calca:'#3B4A6B',sapato:'#C2410C',fase:2.1},
 pedro:{pele:PELE[1],cabelo:'#3A2A1E',estilo:'curto',roupa:'#1F7A6C',calca:'#2A2622',sapato:'#F4EEE4',fase:.5},
};
const POSES={
 parado:t=>({L:[-110,-342],R:[110,-342]}),
 aponta:t=>({L:[-110,-342],R:[238,-590+Math.sin(t*6)*8]}),
 maos_cabeca:t=>({L:[-98,-748+Math.sin(t*5)*5],R:[98,-748+Math.cos(t*5)*5]}),
 bracos_cruzados:t=>({L:[52,-472],R:[-52,-482],cruz:true}),
 maos_cintura:t=>({L:[-72,-372],R:[72,-372]}),
 petisco:t=>({L:[-110,-342],R:[205,-440+Math.sin(t*4)*6],item:['R','petisco']}),
 acena:t=>({L:[-110,-342],R:[178+Math.sin(t*9)*28,-780]}),
 celular:t=>({L:[-110,-342],R:[82,-700],item:['R','celular']}),
 comemora:t=>({L:[-178,-860+Math.sin(t*10)*14],R:[178,-860+Math.cos(t*10)*14]}),
 maos_rosto:t=>({L:[-38,-690],R:[38,-690]}),
 carinho:t=>({L:[-110,-342],R:[215,-300+Math.sin(t*5)*14]}),
 guia:t=>({L:[-110,-342],R:[160,-410],item:['R','guia']}),
 bilhete:t=>({L:[-64,-488],R:[64,-488],item:['C','bilhete']}),
 explica:t=>({L:[-175,-470+Math.sin(t*4)*10],R:[175,-470-Math.sin(t*4)*10]}),
};
function membro(pts,w,cor){cx.lineCap='round';cx.lineJoin='round';cx.beginPath();cx.moveTo(pts[0][0],pts[0][1]);
  if(pts.length===3)cx.quadraticCurveTo(pts[1][0],pts[1][1],pts[2][0],pts[2][1]);else for(let i=1;i<pts.length;i++)cx.lineTo(pts[i][0],pts[i][1]);
  cx.lineWidth=w+14;cx.strokeStyle=C.ink;cx.stroke();cx.lineWidth=w;cx.strokeStyle=cor;cx.stroke()}
function ik(S,P,L1,L2,sd){let dx=P[0]-S[0],dy=P[1]-S[1];let d=Math.hypot(dx,dy)||1;const m=L1+L2-4;if(d>m){dx*=m/d;dy*=m/d;d=m}
  const a=Math.acos(Math.max(-1,Math.min(1,(L1*L1+d*d-L2*L2)/(2*L1*d))));const b=Math.atan2(dy,dx);
  const e1=[S[0]+L1*Math.cos(b+a),S[1]+L1*Math.sin(b+a)],e2=[S[0]+L1*Math.cos(b-a),S[1]+L1*Math.sin(b-a)];
  return [(e1[0]*sd>e2[0]*sd)?e1:e2,[S[0]+dx,S[1]+dy]]}
function alvosPose(st,t){const cur=(POSES[st.pose]||POSES.parado)(t);if(!st.posePrev||st.posePrev===st.pose)return cur;
  const k=eio(cl((t-(st.tPose||0))/.32));if(k>=1)return cur;const pr=(POSES[st.posePrev]||POSES.parado)(t);
  return Object.assign({},cur,{L:[lerp(pr.L[0],cur.L[0],k),lerp(pr.L[1],cur.L[1],k)],R:[lerp(pr.R[0],cur.R[0],k),lerp(pr.R[1],cur.R[1],k)]})}

function pernas(P,t,st){const sent=!!st.sentado,sw=st.anda?Math.sin(t*8)*24:0;
  for(const sx of[-1,1]){const pts=sent?[[sx*40,-222],[sx*58,-178],[sx*56,-46]]:[[sx*40,-345],[sx*41,-195],[sx*42+(sx<0?sw:-sw),-46]];
    membro(pts,66,P.calca);const a=pts[2];cx.beginPath();cx.ellipse(a[0]+sx*12,a[1]+16,46,24,0,0,7);cx.fillStyle=P.sapato;cx.fill();contorno(6);
    cx.beginPath();cx.moveTo(a[0]+sx*12-30,a[1]+26);cx.lineTo(a[0]+sx*12+30,a[1]+26);cx.lineWidth=4;cx.strokeStyle='rgba(42,38,34,.35)';cx.stroke()}
  const hy=sent?-252:-374;rr(-80,hy,160,66,26);cx.fillStyle=P.calca;cx.fill();contorno(7)}
function cabeloAtras(P,t){cx.fillStyle=P.cabelo;
  if(P.estilo==='longo'){cx.beginPath();cx.moveTo(-98,-735);cx.bezierCurveTo(-114,-866,114,-866,98,-735);cx.bezierCurveTo(104,-660,122,-604,110,-548);cx.quadraticCurveTo(0,-526,-110,-548);cx.bezierCurveTo(-122,-604,-104,-660,-98,-735);cx.closePath();cx.fill();contorno(7)}
  if(P.estilo==='coque'){cx.beginPath();cx.arc(0,-860,42,0,7);cx.fill();contorno(7)}
  if(P.estilo==='rabo'){const w=Math.sin(t*3)*10;membro([[70,-820],[150+w,-760],[128+w,-630]],46,P.cabelo)}
  if(P.estilo==='cacheado'){const pts=[];for(let i=0;i<=12;i++){const a=Math.PI*.82+i*(Math.PI*1.36/12);pts.push([Math.cos(a)*116,-742+Math.sin(a)*112])}
    pts.push([-118,-650],[118,-650],[-104,-600],[104,-600]);
    cx.lineWidth=14;cx.strokeStyle=C.ink;pts.forEach(([a,b])=>{cx.beginPath();cx.arc(a,b,44,0,7);cx.stroke()});pts.forEach(([a,b])=>{cx.beginPath();cx.arc(a,b,44,0,7);cx.fill()})}}
function cabeloFrente(P,t){cx.fillStyle=P.cabelo;const e=P.estilo;
  if(e==='longo'){cx.beginPath();cx.moveTo(-97,-720);cx.bezierCurveTo(-106,-854,106,-854,97,-720);cx.bezierCurveTo(92,-762,70,-802,22,-804);cx.bezierCurveTo(4,-772,-42,-760,-72,-774);cx.bezierCurveTo(-88,-760,-95,-742,-97,-720);cx.closePath();cx.fill();contorno(7);
    for(const sx of[-1,1]){cx.beginPath();cx.moveTo(sx*97,-735);cx.bezierCurveTo(sx*106,-680,sx*102,-636,sx*92,-604);cx.lineTo(sx*78,-640);cx.bezierCurveTo(sx*86,-684,sx*88,-712,sx*82,-744);cx.closePath();cx.fill();contorno(6)}}
  else if(e==='coque'||e==='rabo'){cx.beginPath();cx.moveTo(-96,-722);cx.bezierCurveTo(-104,-850,104,-850,96,-722);cx.bezierCurveTo(82,-790,42,-806,0,-806);cx.bezierCurveTo(-42,-806,-82,-790,-96,-722);cx.closePath();cx.fill();contorno(7);
    cx.beginPath();cx.moveTo(-10,-838);cx.quadraticCurveTo(-30,-820,-40,-806);cx.lineWidth=4;cx.strokeStyle='rgba(255,255,255,.25)';cx.stroke()}
  else if(e==='curto'){cx.beginPath();cx.moveTo(-95,-735);cx.bezierCurveTo(-102,-832,-52,-866,0,-862);cx.bezierCurveTo(56,-870,106,-832,95,-735);cx.bezierCurveTo(86,-772,66,-792,40,-788);cx.bezierCurveTo(22,-808,-10,-804,-26,-792);cx.bezierCurveTo(-52,-804,-86,-778,-95,-735);cx.closePath();cx.fill();contorno(7)}
  else if(e==='careca'){for(const sx of[-1,1]){cx.beginPath();cx.ellipse(sx*88,-752,22,32,sx*.2,0,7);cx.fill();contorno(6)}
    cx.beginPath();cx.ellipse(-34,-812,26,10,-.4,0,7);cx.fillStyle='rgba(255,255,255,.45)';cx.fill()}
  else if(e==='cacheado'){const pts=[];for(let i=-3;i<=3;i++)pts.push([i*27,-806+Math.abs(i)*9]);
    cx.lineWidth=12;cx.strokeStyle=C.ink;pts.forEach(([a,b])=>{cx.beginPath();cx.arc(a,b,25,0,7);cx.stroke()});pts.forEach(([a,b])=>{cx.beginPath();cx.arc(a,b,25,0,7);cx.fill()})}}
function rosto(P,t,st){const h=st.humor||'normal',fal=!!st.falando,look=st.olhar||0;
  if(['feliz','radiante','vergonha'].includes(h)){cx.fillStyle=h==='vergonha'?'rgba(214,72,72,.45)':'rgba(232,110,110,.32)';for(const sx of[-1,1]){cx.beginPath();cx.ellipse(sx*60,-674,20,12,0,0,7);cx.fill()}}
  if(P.barba){cx.beginPath();cx.moveTo(-90,-712);cx.bezierCurveTo(-84,-642,-44,-606,0,-604);cx.bezierCurveTo(44,-606,84,-642,90,-712);cx.bezierCurveTo(64,-668,34,-656,0,-656);cx.bezierCurveTo(-34,-656,-64,-668,-90,-712);cx.closePath();cx.fillStyle=P.cabelo;cx.fill();contorno(5)}
  const blink=((t+(P.fase||0))%3.6)<.12;
  for(const sx of[-1,1]){const ex=sx*35,ey=-730;
    if(h==='radiante'){cx.beginPath();cx.arc(ex,ey+8,15,Math.PI*1.12,Math.PI*1.88);cx.lineWidth=7;cx.strokeStyle=C.ink;cx.lineCap='round';cx.stroke();continue}
    if(blink){cx.beginPath();cx.moveTo(ex-15,ey+2);cx.quadraticCurveTo(ex,ey+8,ex+15,ey+2);cx.lineWidth=6;cx.strokeStyle=C.ink;cx.lineCap='round';cx.stroke();continue}
    const rx=h==='surpreso'?20:17,ry=h==='surpreso'?26:21;cx.beginPath();cx.ellipse(ex,ey,rx,ry,0,0,7);cx.fillStyle='#fff';cx.fill();contorno(5);
    const pr=h==='surpreso'?7:10,px=ex+look*6,py=ey+3;cx.fillStyle=C.ink;cx.beginPath();cx.arc(px,py,pr,0,7);cx.fill();cx.fillStyle='#fff';cx.beginPath();cx.arc(px+3.5,py-3.5,3.4,0,7);cx.fill();
    if(['cansado','triste','vergonha'].includes(h)){const f=h==='cansado'?.95:.5;cx.save();cx.beginPath();cx.ellipse(ex,ey,rx,ry,0,0,7);cx.clip();cx.fillStyle=P.pele;cx.beginPath();
      cx.moveTo(ex-rx-3,ey-ry-3+(h==='cansado'?0:-sx*6));cx.lineTo(ex+rx+3,ey-ry-3+(h==='cansado'?0:sx*6));cx.lineTo(ex+rx+3,ey-ry+ry*2*f*.5+(sx*4));cx.lineTo(ex-rx-3,ey-ry+ry*2*f*.5-(sx*4));cx.fill();cx.restore();
      cx.beginPath();cx.moveTo(ex-rx,ey-ry+ry*f-sx*4);cx.lineTo(ex+rx,ey-ry+ry*f+sx*4);cx.lineWidth=5;cx.strokeStyle=C.ink;cx.stroke()}}
  if(P.oculos){cx.lineWidth=5;cx.strokeStyle=C.ink;for(const sx of[-1,1]){cx.beginPath();cx.arc(sx*35,-728,28,0,7);cx.fillStyle='rgba(255,255,255,.12)';cx.fill();cx.stroke()}cx.beginPath();cx.moveTo(-8,-732);cx.quadraticCurveTo(0,-740,8,-732);cx.stroke()}
  const SB={normal:[0,0],feliz:[-5,-3],radiante:[-8,-6],triste:[-12,6],preocupado:[-13,5],vergonha:[-10,4],bravo:[12,-8],surpreso:[-18,-16],cansado:[2,4]}[h]||[0,0];
  const by=(P.oculos?-768:-764)+(fal&&h!=='bravo'?-Math.abs(Math.sin(t*6))*3:0);
  cx.lineWidth=9;cx.lineCap='round';cx.strokeStyle=P.estilo==='careca'?'#8E877F':(P.cabelo==='#2A2622'?'#1A1714':P.cabelo);
  for(const sx of[-1,1]){cx.beginPath();cx.moveTo(sx*14,by+SB[0]);cx.quadraticCurveTo(sx*34,by+(SB[0]+SB[1])/2-6,sx*54,by+SB[1]);cx.stroke()}
  cx.beginPath();cx.moveTo(-7,-702);cx.quadraticCurveTo(0,-688,9,-700);cx.lineWidth=5;cx.strokeStyle=C.ink;cx.stroke();
  if(P.bigode){cx.beginPath();cx.moveTo(0,-686);cx.bezierCurveTo(-20,-700,-48,-690,-46,-668);cx.bezierCurveTo(-30,-678,-12,-674,0,-678);cx.bezierCurveTo(12,-674,30,-678,46,-668);cx.bezierCurveTo(48,-690,20,-700,0,-686);cx.fillStyle=P.cabelo;cx.fill();contorno(5)}
  const my=-660;cx.lineWidth=6;cx.strokeStyle=C.ink;cx.lineCap='round';
  if(fal){const o=.25+.75*Math.abs(Math.sin(t*15.5)*Math.cos(t*6.1));const w=h==='bravo'?34:26+6*o,hh=5+(h==='bravo'?14:20)*o;
    cx.beginPath();cx.ellipse(0,my,w,hh,0,0,7);cx.fillStyle='#6B2A2A';cx.fill();cx.save();cx.clip();cx.fillStyle='#E8787A';cx.beginPath();cx.ellipse(0,my+hh,w*.7,hh*.6,0,0,7);cx.fill();
    if(h==='bravo'){cx.fillStyle='#fff';cx.fillRect(-w,my-hh,w*2,hh*.55)}cx.restore();cx.beginPath();cx.ellipse(0,my,w,hh,0,0,7);contorno(5)}
  else if(h==='feliz'||h==='radiante'){const g=h==='radiante'?1.25:1;cx.beginPath();cx.moveTo(-30*g,my-10);cx.quadraticCurveTo(0,my+36*g,30*g,my-10);cx.closePath();cx.fillStyle='#6B2A2A';cx.fill();
    cx.save();cx.clip();cx.fillStyle='#fff';cx.fillRect(-40,my-14,80,11);cx.fillStyle='#E8787A';cx.beginPath();cx.ellipse(0,my+22*g,16,10,0,0,7);cx.fill();cx.restore();cx.beginPath();cx.moveTo(-30*g,my-10);cx.quadraticCurveTo(0,my+36*g,30*g,my-10);cx.closePath();contorno(5)}
  else if(h==='triste'){cx.beginPath();cx.arc(0,my+20,22,Math.PI*1.2,Math.PI*1.8);cx.stroke()}
  else if(h==='bravo'){cx.beginPath();cx.moveTo(-24,my+4);cx.quadraticCurveTo(0,my-6,24,my+4);cx.stroke()}
  else if(h==='surpreso'){cx.beginPath();cx.ellipse(0,my+2,12,17,0,0,7);cx.fillStyle='#6B2A2A';cx.fill();contorno(5)}
  else if(h==='preocupado'||h==='vergonha'){cx.beginPath();cx.moveTo(-24,my);cx.bezierCurveTo(-10,my-10,8,my+10,24,my-2);cx.stroke()}
  else if(h==='cansado'){cx.beginPath();cx.moveTo(-16,my+2);cx.lineTo(16,my+2);cx.stroke()}
  else{cx.beginPath();cx.arc(0,my-18,24,Math.PI*.22,Math.PI*.78);cx.stroke()}
  if(h==='triste'){cx.fillStyle='rgba(90,170,220,.85)';for(const sx of[-1,1])for(let k=0;k<2;k++){const p=((t*1.1+k*.5+(sx>0?.25:0))%1);cx.globalAlpha=1-p;cx.beginPath();cx.ellipse(sx*42,-706+p*70,6,9,0,0,7);cx.fill()}cx.globalAlpha=1}
  if(h==='preocupado'||h==='vergonha'){const b=Math.sin(t*4)*4;cx.fillStyle='rgba(120,190,230,.95)';cx.beginPath();cx.moveTo(84,-812+b);cx.quadraticCurveTo(100,-786+b,92,-776+b);cx.arc(84,-778+b,10,0,Math.PI);cx.quadraticCurveTo(70,-790+b,84,-812+b);cx.fill();cx.lineWidth=4;cx.strokeStyle=C.ink;cx.stroke()}
  if(h==='bravo'){const p=1+.12*Math.abs(Math.sin(t*8));cx.save();cx.translate(58,-808);cx.scale(p,p);cx.lineWidth=6;cx.strokeStyle=C.red;cx.lineCap='round';
    [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(([a,b])=>{cx.beginPath();cx.arc(a*16,b*16,11,Math.atan2(-b,-a)-.9,Math.atan2(-b,-a)+.9);cx.stroke()});cx.restore()}}
function cabeca(P,t,st){
  for(const sx of[-1,1]){cx.beginPath();cx.ellipse(sx*92,-712,17,25,0,0,7);cx.fillStyle=P.pele;cx.fill();contorno(6)}
  cx.beginPath();cx.moveTo(0,-840);cx.bezierCurveTo(63,-840,95,-793,95,-727);cx.bezierCurveTo(95,-660,57,-611,0,-609);cx.bezierCurveTo(-57,-611,-95,-660,-95,-727);cx.bezierCurveTo(-95,-793,-63,-840,0,-840);cx.closePath();
  cx.fillStyle=P.pele;cx.fill();contorno(7);
  cx.save();cx.clip();cx.fillStyle='rgba(42,38,34,.07)';cx.beginPath();cx.ellipse(40,-650,90,70,0,0,7);cx.fill();cx.restore();
  cabeloFrente(P,t);rosto(P,t,st)}
function corpoPath(){cx.beginPath();cx.moveTo(-34,-602);cx.quadraticCurveTo(-88,-602,-94,-556);cx.lineTo(-82,-352);cx.quadraticCurveTo(0,-334,82,-352);cx.lineTo(94,-556);cx.quadraticCurveTo(88,-602,34,-602);cx.quadraticCurveTo(0,-572,-34,-602);cx.closePath()}
function tronco(P){cx.fillStyle=P.pele;rr(-24,-660,48,84,12);cx.fill();contorno(6);
  corpoPath();cx.fillStyle=P.roupa;cx.fill();cx.save();cx.clip();cx.fillStyle='rgba(42,38,34,.12)';cx.fillRect(40,-620,70,300);cx.fillStyle='rgba(255,255,255,.12)';cx.fillRect(-90,-620,26,300);cx.restore();
  corpoPath();contorno(7);
  if(P.botoes){cx.fillStyle=C.ink;for(let i=0;i<4;i++){cx.beginPath();cx.arc(0,-540+i*48,5,0,7);cx.fill()}cx.beginPath();cx.moveTo(0,-585);cx.lineTo(0,-345);cx.lineWidth=3;cx.strokeStyle='rgba(42,38,34,.4)';cx.stroke()}
  else paw(0,-470,.95,'rgba(255,255,255,.35)')}
function item(tipo,x,y,t){cx.save();cx.translate(x,y);
  if(tipo==='petisco'){bone(18,-6,.5,C.cream,-.5,true)}
  else if(tipo==='celular'){cx.rotate(-.15);rr(-24,-74,48,92,10);cx.fillStyle=C.ink;cx.fill();rr(-18,-66,36,74,6);cx.fillStyle='#8FD3C7';cx.fill()}
  else if(tipo==='bilhete'){cx.rotate(-.04);rr(-82,-70,164,110,8);cx.fillStyle='#FFF6D8';cx.fill();contorno(5);for(let i=0;i<4;i++){cx.fillStyle='rgba(42,38,34,.45)';cx.fillRect(-60,-46+i*22,i===3?70:120,6)}txt('!',58,-40,40,C.red,{w:900,f:'NU'})}
  cx.restore()}
function bracos(P,t,st){const A=alvosPose(st,t);const ord=A.cruz?['R','L']:['L','R'];const maos={};
  for(const k of ord){const sd=k==='L'?-1:1,S=[sd*84,-562];const [E,H]=ik(S,A[k],128,124,sd);
    membro([S,E,H],40,P.pele);const m=[S[0]+(E[0]-S[0])*.6,S[1]+(E[1]-S[1])*.6];membro([S,m],52,P.roupa);
    cx.beginPath();cx.arc(H[0],H[1],25,0,7);cx.fillStyle=P.pele;cx.fill();contorno(6);
    cx.beginPath();cx.arc(H[0]-sd*14,H[1]-12,10,0,7);cx.fill();contorno(5);
    maos[k]=H;if(A.item&&A.item[0]===k)item(A.item[1],H[0],H[1],t)}
  if(A.item&&A.item[0]==='C')item(A.item[1],0,-470,t);
  return {maos,item:A.item}}
// desenha e devolve pontos úteis (cabeça, mãos) em coordenadas do cenário
function persona(id,x,y,s,t,st={}){const P=ELENCO[id]||ELENCO.ana;const d=st.dir||1;const sent=!!st.sentado,oy=sent?122:0;
  const resp=Math.sin(t*2.4+(P.fase||0)*3)*4;const pulo=st.pose==='comemora'?-Math.abs(Math.sin(t*7))*26:0;
  const trem=(st.humor==='bravo'&&st.falando)?Math.sin(t*60)*2.5:0;
  cx.save();cx.translate(x,y);cx.scale(s*d,s);
  cx.fillStyle='rgba(42,38,34,.16)';cx.beginPath();cx.ellipse(0,4,130,20,0,0,7);cx.fill();
  cx.translate(trem,pulo);pernas(P,t,st);
  cx.save();cx.translate(0,oy+resp*.5);if(st.inclina)cx.rotate(st.inclina);
  cabeloAtras(P,t);tronco(P);cx.save();cx.translate(0,resp*.4);cabeca(P,t,st);cx.restore();const br=bracos(P,t,st);cx.restore();cx.restore();
  const W2=(p)=>[x+s*d*p[0],y+s*(p[1]+oy+pulo)];
  return {cabeca:W2([0,-880]),maos:{L:br.maos.L&&W2(br.maos.L),R:br.maos.R&&W2(br.maos.R)},item:br.item}}

// ---------------- cenários ----------------
function piso(y0,c1,c2,tab=true){cx.fillStyle=c1;cx.fillRect(0,y0,W,H-y0);if(tab){cx.strokeStyle=c2;cx.lineWidth=4;for(let i=-8;i<16;i++){cx.beginPath();cx.moveTo(W/2+i*140,y0);cx.lineTo(W/2+i*300,H);cx.stroke()}}
  cx.fillStyle='rgba(42,38,34,.18)';cx.fillRect(0,y0,W,10)}
function janela(x,y,w,h,noite,t){rr(x-14,y-14,w+28,h+28,14);cx.fillStyle='#F4EEE4';cx.fill();contorno(7);
  rr(x,y,w,h,8);const g=cx.createLinearGradient(0,y,0,y+h);if(noite){g.addColorStop(0,'#1B2440');g.addColorStop(1,'#33406B')}else{g.addColorStop(0,'#9FD8F0');g.addColorStop(1,'#DDF2F8')}cx.fillStyle=g;cx.fill();
  cx.save();rr(x,y,w,h,8);cx.clip();if(noite){cx.fillStyle='#FFF1C2';cx.beginPath();cx.arc(x+w*.7,y+h*.28,26,0,7);cx.fill();cx.fillStyle='#1B2440';cx.beginPath();cx.arc(x+w*.7+12,y+h*.28-8,22,0,7);cx.fill();
    for(let i=0;i<8;i++){cx.fillStyle=`rgba(255,255,255,${.4+.4*Math.sin(t*3+i)})`;cx.fillRect(x+rnd(i)*w,y+rnd(i+9)*h*.6,4,4)}}
  else{cx.fillStyle='#fff';[[.3,.3],[.62,.5]].forEach(([a,b],i)=>{const ox=((t*12+i*80)%(w+160))-80;cx.beginPath();cx.ellipse(x+ox,y+h*b,46,18,0,0,7);cx.ellipse(x+ox+30,y+h*b-12,30,18,0,0,7);cx.fill()})}
  cx.fillStyle=noite?'#141A30':'#7DB89A';cx.fillRect(x,y+h*.78,w,h*.22);cx.restore();
  cx.beginPath();cx.moveTo(x+w/2,y);cx.lineTo(x+w/2,y+h);cx.moveTo(x,y+h/2);cx.lineTo(x+w,y+h/2);cx.lineWidth=8;cx.strokeStyle='#F4EEE4';cx.stroke();
  const sw=Math.sin(t*1.5)*6;for(const [cxp,dir] of[[x-30,1],[x+w+30,-1]]){cx.beginPath();cx.moveTo(cxp-40*dir,y-40);cx.lineTo(cxp+60*dir,y-40);cx.quadraticCurveTo(cxp+30*dir+sw,y+h*.5,cxp+50*dir,y+h+40);cx.lineTo(cxp-40*dir,y+h+40);cx.closePath();cx.fillStyle=noite?'#5A3E5E':'#E07A3F';cx.fill();contorno(6)}
  rr(x-60,y-56,w+120,18,9);cx.fillStyle=C.ink;cx.fill()}
function sofa(x,y,s,cor){cx.save();cx.translate(x,y);cx.scale(s,s);
  rr(-260,-250,520,170,50);cx.fillStyle=cor;cx.fill();contorno(8);
  rr(-240,-120,480,90,30);cx.fillStyle=cor;cx.fill();contorno(8);
  cx.beginPath();cx.moveTo(0,-120);cx.lineTo(0,-30);contorno(6);
  for(const sx of[-1,1]){rr(sx*290-50,-170,100,150,40);cx.fillStyle=cor;cx.fill();contorno(8)}
  cx.fillStyle='rgba(255,255,255,.15)';rr(-230,-235,460,30,15);cx.fill();
  for(const sx of[-1,1]){rr(sx*230-10,-30,20,34,6);cx.fillStyle=C.ink;cx.fill()}
  cx.restore()}
function planta(x,y,s,t){cx.save();cx.translate(x,y);cx.scale(s,s);
  for(let i=0;i<6;i++){const a=-Math.PI/2+(i-2.5)*.38+Math.sin(t*1.2+i)*.04;cx.save();cx.rotate(a+Math.PI/2);cx.beginPath();cx.ellipse(0,-120,26,92,0,0,7);cx.fillStyle=i%2?'#3E9A6E':'#2F7D58';cx.fill();contorno(5);cx.restore()}
  cx.beginPath();cx.moveTo(-62,-40);cx.lineTo(62,-40);cx.lineTo(48,60);cx.lineTo(-48,60);cx.closePath();cx.fillStyle='#C2410C';cx.fill();contorno(6);cx.restore()}
function luminaria(x,y,on,t){cx.save();cx.translate(x,y);if(on){const g=cx.createRadialGradient(0,-560,10,0,-500,520);g.addColorStop(0,'rgba(255,214,140,.55)');g.addColorStop(1,'rgba(255,214,140,0)');cx.fillStyle=g;cx.fillRect(-520,-1080,1040,1100)}
  cx.beginPath();cx.moveTo(0,-540);cx.lineTo(0,0);cx.lineWidth=10;cx.strokeStyle=C.ink;cx.stroke();cx.beginPath();cx.ellipse(0,0,60,14,0,0,7);cx.fillStyle=C.ink;cx.fill();
  cx.beginPath();cx.moveTo(-70,-540);cx.lineTo(70,-540);cx.lineTo(44,-640);cx.lineTo(-44,-640);cx.closePath();cx.fillStyle=on?'#FFE3A6':'#F4EEE4';cx.fill();contorno(7);cx.restore()}
function relogioParede(x,y,texto,t){cx.save();cx.translate(x,y);rr(-96,-48,192,96,22);cx.fillStyle=C.ink;cx.fill();rr(-84,-36,168,72,14);cx.fillStyle='#1B1714';cx.fill();
  txt(texto,0,4,50,Math.floor(t*2)%2?'#FF6B5A':'#FF8A7A',{w:900,f:'NU',ls:2});cx.restore()}
function porta(x,y,num,aberta,t){cx.save();cx.translate(x,y);rr(-130,-560,260,560,12);cx.fillStyle='#F4EEE4';cx.fill();contorno(7);
  if(aberta){rr(-110,-540,220,540,6);cx.fillStyle='#2A2622';cx.fill();cx.save();cx.transform(.45,0,0,1,-110,0);rr(0,-540,220,540,6);cx.fillStyle='#A0623A';cx.fill();contorno(7);cx.restore()}
  else{rr(-110,-540,220,540,6);cx.fillStyle='#A0623A';cx.fill();contorno(7);rr(-80,-500,160,200,10);contorno(5);rr(-80,-260,160,200,10);contorno(5);cx.beginPath();cx.arc(80,-270,12,0,7);cx.fillStyle=C.gold;cx.fill();contorno(4)}
  if(num){rr(-46,-640,92,52,10);cx.fillStyle=C.ink;cx.fill();txt(num,0,-612,34,C.gold,{w:900,f:'NU'})}cx.restore()}
function cenarioH(t,tipo,s){const N=tipo==='noite'||tipo==='quarto';const F=1180;
  if(tipo==='rua'){const g=cx.createLinearGradient(0,0,0,F);g.addColorStop(0,'#8ED0EE');g.addColorStop(1,'#E5F4FA');cx.fillStyle=g;cx.fillRect(0,0,W,F);
    for(let i=0;i<3;i++){const ox=((t*14+i*400)%(W+400))-200;cx.fillStyle='#fff';cx.beginPath();cx.ellipse(ox,260+i*110,90,32,0,0,7);cx.ellipse(ox+60,240+i*110,60,34,0,0,7);cx.fill()}
    [[60,560,'#E8B48C'],[300,460,'#CFEAE3'],[560,620,'#FBE3C8'],[820,500,'#E5B23C']].forEach(([x,h,c],i)=>{rr(x,F-h,230,h+20,8);cx.fillStyle=c;cx.fill();contorno(6);
      for(let r=0;r<Math.floor(h/120);r++)for(let k=0;k<2;k++){rr(x+40+k*90,F-h+40+r*120,60,70,6);cx.fillStyle=(r+k+i)%3?'#9FD8F0':'#FFE3A6';cx.fill();contorno(4)}});
    cx.fillStyle='#7DB89A';cx.fillRect(0,F-30,W,60);piso(F+20,'#D8CFC2','rgba(42,38,34,.08)');
    for(const x of[150,930]){cx.fillStyle='#7A5236';rr(x-16,F-260,32,300,10);cx.fill();contorno(6);cx.beginPath();cx.arc(x,F-300,110,0,7);cx.arc(x-70,F-240,80,0,7);cx.arc(x+70,F-240,80,0,7);cx.fillStyle='#3E9A6E';cx.fill();contorno(7)}
    return}
  if(tipo==='corredor'){cx.fillStyle='#CFD8E0';cx.fillRect(0,0,W,F);cx.fillStyle='#B7C4CF';cx.fillRect(0,F-140,W,140);cx.fillStyle='rgba(42,38,34,.2)';cx.fillRect(0,F-146,W,6);
    porta(250,F,s.porta_num||'302',false,t);porta(830,F,s.porta_num2||'301',!!s.porta_aberta,t);
    cx.save();cx.translate(540,520);rr(-30,-20,60,80,14);cx.fillStyle='#FFE3A6';cx.fill();contorno(6);const g=cx.createRadialGradient(0,20,10,0,20,300);g.addColorStop(0,'rgba(255,230,160,.5)');g.addColorStop(1,'rgba(255,230,160,0)');cx.fillStyle=g;cx.fillRect(-300,-280,600,600);cx.restore();
    rr(430,700,220,150,10);cx.fillStyle='#FFF6D8';cx.fill();contorno(6);txt('AVISO',540,740,34,C.red,{w:900,f:'NU',ls:2});for(let i=0;i<3;i++){cx.fillStyle='rgba(42,38,34,.35)';cx.fillRect(460,775+i*22,160,6)}
    piso(F,'#9AA6B0','rgba(255,255,255,.12)');rr(170,F+10,160,40,10);cx.fillStyle='#7A5236';cx.fill();return}
  if(tipo==='cozinha'){cx.fillStyle='#E9F2EE';cx.fillRect(0,0,W,F);cx.strokeStyle='rgba(42,38,34,.08)';cx.lineWidth=3;for(let x=0;x<W;x+=70){cx.beginPath();cx.moveTo(x,560);cx.lineTo(x,F);cx.stroke()}for(let y=560;y<F;y+=70){cx.beginPath();cx.moveTo(0,y);cx.lineTo(W,y);cx.stroke()}
    janela(380,300,320,240,false,t);rr(0,F-330,W,40,8);cx.fillStyle='#F4EEE4';cx.fill();contorno(6);rr(0,F-290,W,290,0);cx.fillStyle='#E07A3F';cx.fill();contorno(6);
    for(let i=0;i<5;i++){rr(20+i*215,F-270,190,250,12);contorno(5);cx.beginPath();cx.arc(20+i*215+170,F-150,8,0,7);cx.fillStyle=C.ink;cx.fill()}
    rr(820,F-760,240,430,24);cx.fillStyle='#F4EEE4';cx.fill();contorno(7);cx.beginPath();cx.moveTo(820,F-600);cx.lineTo(1060,F-600);contorno(5);
    piso(F,'#F4EEE4','rgba(42,38,34,.08)');return}
  const parede=N?'#4A4038':C.peach;cx.fillStyle=parede;cx.fillRect(0,0,W,F);
  cx.fillStyle=N?'rgba(0,0,0,.08)':'rgba(232,145,60,.08)';for(let x=0;x<W;x+=90)cx.fillRect(x,0,40,F);
  cx.fillStyle=N?'#3A322C':'#F4EEE4';cx.fillRect(0,F-40,W,40);
  janela(110,380,280,330,N,t);
  if(tipo==='quarto'){rr(560,F-330,460,200,30);cx.fillStyle='#6B7FA8';cx.fill();contorno(7);rr(600,F-370,160,70,26);cx.fillStyle='#F4EEE4';cx.fill();contorno(6)}
  else{rr(680,430,230,170,10);cx.fillStyle='#F4EEE4';cx.fill();contorno(7);rr(700,450,190,130,6);cx.fillStyle=N?'#5B6E8E':'#9FD8F0';cx.fill();
    paw(795,520,1.2,N?'#3A4A66':C.amb);sofa(700,F+40,1,N?'#6B5A8E':'#2F9C8A');planta(990,F+20,.9,t)}
  if(s.relogio)relogioParede(540,300,s.relogio,t);
  piso(F,N?'#2E2723':'#D9A97A',N?'rgba(255,255,255,.04)':'rgba(42,38,34,.07)');
  cx.fillStyle=N?'rgba(255,255,255,.05)':'rgba(194,65,12,.18)';cx.beginPath();cx.ellipse(540,F+300,440,90,0,0,7);cx.fill();
  if(N)luminaria(80,F+60,true,t)}
// objetos de cena (bagunça, pistas da história)
function objetoH(nome,x,y,t,t0){const k=t0==null?1:pop(t,t0,.45);if(!k)return;cx.save();cx.translate(x,y);cx.scale(k,k);
  if(nome==='poca'){cx.beginPath();cx.ellipse(0,0,110,30,0,0,7);cx.ellipse(70,8,50,18,0,0,7);cx.fillStyle='rgba(229,190,60,.75)';cx.fill();cx.lineWidth=4;cx.strokeStyle='rgba(42,38,34,.35)';cx.stroke();cx.fillStyle='rgba(255,255,255,.6)';cx.beginPath();cx.ellipse(-40,-6,24,6,0,0,7);cx.fill()}
  else if(nome==='almofada'){cx.rotate(.3);rr(-80,-56,160,112,30);cx.fillStyle='#E5B23C';cx.fill();contorno(6);cx.beginPath();cx.moveTo(-20,-56);cx.lineTo(0,-20);cx.lineTo(-24,10);cx.lineTo(4,56);contorno(5);cx.rotate(-.3);
    for(let i=0;i<10;i++){const p=((t*.35+rnd(i))%1);cx.save();cx.translate((rnd(i+3)-.5)*420,-p*520);cx.rotate(Math.sin(t*3+i));cx.globalAlpha=1-p;cx.beginPath();cx.ellipse(0,0,14,30,0,0,7);cx.fillStyle='#fff';cx.fill();cx.lineWidth=3;cx.strokeStyle=C.ink;cx.stroke();cx.restore()}}
  else if(nome==='sapato'){cx.rotate(-.2);cx.beginPath();cx.moveTo(-70,0);cx.quadraticCurveTo(-74,-50,-30,-52);cx.lineTo(10,-30);cx.quadraticCurveTo(70,-24,74,0);cx.closePath();cx.fillStyle='#A0623A';cx.fill();contorno(6);
    cx.fillStyle=C.cream;for(let i=0;i<3;i++){cx.beginPath();cx.arc(40+i*12,-18,7,0,7);cx.fill()}}
  else if(nome==='petisco'){bone(0,0,.9,C.cream,-.2,true)}
  else if(nome==='potinho'){cx.beginPath();cx.moveTo(-70,-40);cx.lineTo(70,-40);cx.lineTo(54,10);cx.lineTo(-54,10);cx.closePath();cx.fillStyle=C.red;cx.fill();contorno(6);txt('THOR',0,-14,26,C.cream,{w:900,f:'NU'})}
  else if(nome==='coracoes'){for(let i=0;i<5;i++){const p=((t*.5+i/5)%1);cx.globalAlpha=1-p;heart((rnd(i)-.5)*240,-p*320,.35+rnd(i+2)*.2,C.red)}cx.globalAlpha=1}
  cx.restore()}
// balão de fala ancorado num ponto (ax,ay = ponta do rabicho)
function balaoH(texto,ax,ay,t,t0,{cor=C.cream,size=46,maxw=560,pensa=false,grito=false,alpha=1}={}){const k=pop(t,t0,.38);if(!k)return;
  const ls=quebrar(texto,size,maxw);const w=Math.min(maxw,Math.max(...ls.map(l=>medir(l,size))))+64,h=ls.length*size*1.18+46;
  const bx=Math.max(w/2+30,Math.min(W-w/2-30,ax)),by=ay-h/2-46;const tx=ax-bx;
  cx.save();cx.globalAlpha=alpha;cx.translate(bx,by);cx.scale(k,k);cx.rotate(Math.sin(t*2+ax)*.008);
  sh('rgba(42,38,34,.25)',0,8);cx.fillStyle=cor;
  if(grito){cx.beginPath();const n=18;for(let i=0;i<=n*2;i++){const a=i/(n*2)*Math.PI*2,r=i%2?1:1.16;const px=Math.cos(a)*(w/2+14)*r,py=Math.sin(a)*(h/2+14)*r;i?cx.lineTo(px,py):cx.moveTo(px,py)}cx.closePath();cx.fill();nosh();contorno(7)}
  else if(pensa){rr(-w/2,-h/2,w,h,h/2);cx.fill();nosh();contorno(7);[[tx*.5,h/2+22,14],[tx*.8,h/2+44,8]].forEach(([a,b,r])=>{cx.beginPath();cx.arc(a,b,r,0,7);cx.fillStyle=cor;cx.fill();contorno(5)})}
  else{const bx0=Math.max(-w/2+40,Math.min(w/2-80,tx*.35-22));
    cx.beginPath();cx.moveTo(-w/2+34,-h/2);cx.arcTo(w/2,-h/2,w/2,h/2,34);cx.arcTo(w/2,h/2,-w/2,h/2,34);cx.lineTo(bx0+44,h/2);cx.lineTo(tx,h/2+42);cx.lineTo(bx0,h/2);cx.arcTo(-w/2,h/2,-w/2,-h/2,34);cx.arcTo(-w/2,-h/2,w/2,-h/2,34);cx.closePath();
    cx.fill();nosh();contorno(7)}
  ls.forEach((l,i)=>txt(l,0,-h/2+23+size*.62+i*size*1.18,size,C.ink,{w:700}));cx.restore()}
