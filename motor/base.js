// Motor de Reels — Meu Cão Obedece. Utilitários, camadas e ícones (tudo determinístico: render(t)).
const W=1080,H=1920;let cx;
const C={cream:'#FDF7EE',ink:'#2A2622',amb:'#E8913C',amb2:'#F4A65A',teal:'#1F7A6C',teal2:'#2F9C8A',red:'#C2410C',gold:'#E5B23C',peach:'#FBE3C8',mint:'#CFEAE3',fur:'#F0B872',fur2:'#D89A50'};
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const lerp=(a,b,t)=>a+(b-a)*t;
const eo=t=>1-Math.pow(1-cl(t),3);
const eio=t=>{t=cl(t);return t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2};
const eIn=t=>Math.pow(cl(t),3);
const back=t=>{t=cl(t);const c1=1.9,c3=c1+1;return 1+c3*Math.pow(t-1,3)+c1*Math.pow(t-1,2)};
const spring=(t,f=11,d=6)=>t<=0?0:1-Math.exp(-d*t)*Math.cos(f*t);
function rnd(s){const x=Math.sin(s*127.1+311.7)*43758.5453;return x-Math.floor(x)}
function rr(x,y,w,h,r){cx.beginPath();cx.roundRect(x,y,w,h,r)}
const boil=(t,s=0)=>{const f=Math.floor(t*10);return (rnd(f*7.3+s)-.5)*4};
const IMG={};let GRAIN=null;
async function carregar(){for(const k in SVGS){const im=new Image();im.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(SVGS[k]);await im.decode();IMG[k]=im}
  GRAIN=document.createElement('canvas');GRAIN.width=GRAIN.height=512;const g=GRAIN.getContext('2d');const d=g.createImageData(512,512);
  for(let i=0;i<d.data.length;i+=4){const v=rnd(i*.37)*255;d.data[i]=d.data[i+1]=d.data[i+2]=v;d.data[i+3]=255}g.putImageData(d,0,0)}
function dog(k,x,y,s,rot=0,sq=0){const im=IMG[k]||IMG.normal;if(!im)return;const w=440*s,h=w*282/220;
  cx.save();cx.translate(x,y);cx.rotate(rot);cx.scale(1+sq,1-sq);cx.drawImage(im,-w/2,-h*0.93,w,h);cx.restore()}
function txt(s,x,y,size,col,{w=700,f='FR',al='center',stroke=null,sw=0,ls=0}={}){
  cx.font=`${w} ${size}px ${f}`;cx.textAlign=al;cx.textBaseline='middle';cx.letterSpacing=ls+'px';
  if(stroke){cx.lineJoin='round';cx.lineWidth=sw;cx.strokeStyle=stroke;cx.strokeText(s,x,y)}
  cx.fillStyle=col;cx.fillText(s,x,y);cx.letterSpacing='0px'}
function medir(s,size,w=700,f='FR'){cx.font=`${w} ${size}px ${f}`;return cx.measureText(s).width}
// texto que encolhe pra caber na largura
function txtFit(s,x,y,size,col,maxw,o={}){const m=medir(s,size,o.w||700,o.f||'FR');const k=Math.min(1,maxw/m);cx.save();cx.translate(x,y);cx.scale(k,k);txt(s,0,0,size,col,o);cx.restore()}
// quebra em linhas
function quebrar(s,size,maxw,w=700,f='FR'){const ws=s.split(' ');const ls=[];let cur='';for(const p of ws){const tt=cur?cur+' '+p:p;if(medir(tt,size,w,f)>maxw&&cur){ls.push(cur);cur=p}else cur=tt}if(cur)ls.push(cur);return ls}
function sh(c='rgba(42,38,34,.28)',b=0,oy=12){cx.shadowColor=c;cx.shadowBlur=b;cx.shadowOffsetY=oy}
function nosh(){cx.shadowColor='transparent';cx.shadowBlur=0;cx.shadowOffsetY=0}
function pop(t,t0,dur=.5){return t<t0?0:back((t-t0)/dur*1.4)}
function sp(t,t0,f=12,d=6.5){return spring(t-t0,f,d)}
// ---------- formas ----------
function paw(x,y,s,col,rot=0){cx.save();cx.translate(x,y);cx.rotate(rot);cx.scale(s,s);cx.fillStyle=col;
  cx.beginPath();cx.ellipse(0,10,22,18,0,0,7);cx.fill();[[-24,-14],[-8,-28],[10,-28],[26,-14]].forEach(([a,b])=>{cx.beginPath();cx.ellipse(a,b,8,10,0,0,7);cx.fill()});cx.restore()}
function bone(x,y,s,col,rot=0,stroke=false){cx.save();cx.translate(x,y);cx.rotate(rot);cx.scale(s,s);cx.beginPath();
  cx.roundRect(-40,-11,80,22,8);[[-42,-12],[-42,12],[42,-12],[42,12]].forEach(([a,b])=>{cx.moveTo(a+14,b);cx.arc(a,b,14,0,7)});
  cx.fillStyle=col;cx.fill();if(stroke){cx.lineWidth=6/s;cx.strokeStyle=C.ink;cx.stroke()}cx.restore()}
function heart(x,y,s,col){cx.save();cx.translate(x,y);cx.scale(s,s);cx.fillStyle=col;cx.beginPath();cx.moveTo(0,30);cx.bezierCurveTo(-90,-36,-42,-96,0,-50);cx.bezierCurveTo(42,-96,90,-36,0,30);cx.fill();cx.restore()}
function contorno(w=10){cx.lineWidth=w;cx.strokeStyle=C.ink;cx.lineJoin='round';cx.lineCap='round';cx.stroke()}
// ---------- ícones (desenhados, tamanho base ~220px, centro 0,0) ----------
const ICONES={
 sino(t){cx.save();cx.rotate(Math.sin(t*30)*.18*Math.max(0,Math.sin(t*2.5)));cx.fillStyle=C.gold;cx.beginPath();cx.moveTo(-90,60);cx.quadraticCurveTo(-90,-110,0,-110);cx.quadraticCurveTo(90,-110,90,60);cx.lineTo(115,85);cx.lineTo(-115,85);cx.closePath();cx.fill();contorno(12);
   cx.fillStyle=C.ink;cx.beginPath();cx.arc(0,110,26,0,7);cx.fill();cx.beginPath();cx.arc(0,-122,16,0,7);cx.fill();cx.fillStyle='rgba(255,255,255,.45)';cx.beginPath();cx.ellipse(-45,-20,12,40,.3,0,7);cx.fill();cx.restore()},
 osso(t){bone(0,0,2.2,C.cream,-.3+Math.sin(t*3)*.08,true)},
 moeda(t){cx.save();cx.scale(Math.abs(Math.cos(t*2))*.25+.75,1);cx.fillStyle=C.gold;cx.beginPath();cx.arc(0,0,110,0,7);cx.fill();contorno(12);cx.beginPath();cx.arc(0,0,82,0,7);cx.lineWidth=6;cx.strokeStyle='rgba(42,38,34,.4)';cx.stroke();txt('R$',0,6,90,C.ink);cx.restore()},
 casa(t){cx.fillStyle=C.amb;cx.beginPath();cx.moveTo(-120,-10);cx.lineTo(0,-120);cx.lineTo(120,-10);cx.closePath();cx.fill();contorno(12);rr(-95,-10,190,130,10);cx.fillStyle=C.cream;cx.fill();contorno(12);rr(-28,40,56,80,8);cx.fillStyle=C.teal;cx.fill();contorno(8);
   heart(50,20,.32,C.red)},
 relogio(t){cx.fillStyle=C.cream;cx.beginPath();cx.arc(0,0,115,0,7);cx.fill();contorno(12);for(let i=0;i<12;i++){const a=i/12*Math.PI*2;cx.beginPath();cx.moveTo(Math.cos(a)*90,Math.sin(a)*90);cx.lineTo(Math.cos(a)*100,Math.sin(a)*100);contorno(6)}
   const a1=t*2.4,a2=t*.4;cx.beginPath();cx.moveTo(0,0);cx.lineTo(Math.sin(a1)*75,-Math.cos(a1)*75);contorno(10);cx.beginPath();cx.moveTo(0,0);cx.lineTo(Math.sin(a2)*50,-Math.cos(a2)*50);contorno(14);cx.fillStyle=C.amb;cx.beginPath();cx.arc(0,0,14,0,7);cx.fill()},
 coracao(t){const k=1+.08*Math.max(0,Math.sin(t*7));cx.save();cx.scale(k,k);heart(0,20,1.35,C.red);cx.beginPath();cx.moveTo(0,60);cx.bezierCurveTo(-120,-30,-56,-110,0,-48);cx.bezierCurveTo(56,-110,120,-30,0,60);contorno(12);cx.restore()},
 lampada(t){cx.save();const g=.5+.5*Math.sin(t*5);cx.fillStyle=`rgba(229,178,60,${.25*g})`;cx.beginPath();cx.arc(0,-30,150,0,7);cx.fill();cx.fillStyle=C.gold;cx.beginPath();cx.arc(0,-40,85,Math.PI*.8,Math.PI*2.2);cx.lineTo(35,60);cx.lineTo(-35,60);cx.closePath();cx.fill();contorno(12);
   rr(-40,60,80,50,10);cx.fillStyle=C.mint;cx.fill();contorno(10);cx.restore()},
 bola(t){cx.save();cx.rotate(t*2);cx.fillStyle=C.red;cx.beginPath();cx.arc(0,0,105,0,7);cx.fill();contorno(12);cx.beginPath();cx.arc(-150,0,140,-.6,.6);cx.lineWidth=12;cx.strokeStyle=C.cream;cx.stroke();cx.beginPath();cx.arc(150,0,140,Math.PI-.6,Math.PI+.6);cx.stroke();cx.restore()},
 guia(t){cx.save();cx.lineWidth=18;cx.strokeStyle=C.teal;cx.lineCap='round';cx.beginPath();cx.moveTo(-110,-110);cx.bezierCurveTo(-20,-150+Math.sin(t*3)*20,40,40,80,60);cx.stroke();cx.lineWidth=6;cx.strokeStyle=C.ink;cx.stroke();
   cx.beginPath();cx.ellipse(95,80,55,40,.4,0,7);cx.lineWidth=22;cx.strokeStyle=C.red;cx.stroke();cx.lineWidth=6;cx.strokeStyle=C.ink;cx.stroke();cx.fillStyle=C.gold;cx.beginPath();cx.arc(-115,-115,24,0,7);cx.fill();contorno(6);cx.restore()},
 calendario(t){rr(-115,-100,230,210,20);cx.fillStyle=C.cream;cx.fill();contorno(12);rr(-115,-100,230,60,{upperLeft:20,upperRight:20,lowerLeft:0,lowerRight:0});cx.fillStyle=C.red;cx.fill();contorno(12);
   for(let i=0;i<9;i++){const x=-70+(i%3)*70,y=0+Math.floor(i/3)*42;const on=i<Math.floor(cl(t/1.2)*9)+1;cx.fillStyle=on?C.teal:'rgba(42,38,34,.15)';rr(x-22,y-14,44,30,8);cx.fill()}},
 megafone(t){cx.save();cx.rotate(-.3);cx.fillStyle=C.amb;cx.beginPath();cx.moveTo(-90,-30);cx.lineTo(70,-100);cx.lineTo(70,100);cx.lineTo(-90,30);cx.closePath();cx.fill();contorno(12);rr(-130,-34,44,68,10);cx.fillStyle=C.ink;cx.fill();
   cx.lineCap='round';for(let i=0;i<3;i++){const p=((t*1.5)+i/3)%1;cx.globalAlpha=1-p;cx.beginPath();cx.arc(80,0,40+p*90,-.6,.6);cx.lineWidth=10;cx.strokeStyle=C.ink;cx.stroke()}cx.restore()},
 pata(t){paw(0,10,3.4,C.amb,Math.sin(t*2)*.1)},
 alvo(t){[110,78,46].forEach((r,i)=>{cx.fillStyle=i%2?C.cream:C.red;cx.beginPath();cx.arc(0,0,r,0,7);cx.fill();contorno(10)});cx.save();const p=eo(t/0.6);cx.translate(lerp(160,6,p),lerp(-160,-6,p));cx.rotate(-Math.PI/4);rr(-8,-90,16,110,6);cx.fillStyle=C.ink;cx.fill();cx.restore()},
 cerebro(t){cx.save();const k=1+.04*Math.sin(t*4);cx.scale(k,k);cx.fillStyle='#F2B8C6';[[-50,-30,70],[30,-45,68],[60,20,62],[-40,35,62],[0,0,60]].forEach(([x,y,r])=>{cx.beginPath();cx.arc(x,y,r,0,7);cx.fill()});
   cx.beginPath();[[-50,-30,70],[30,-45,68],[60,20,62],[-40,35,62]].forEach(([x,y,r])=>{cx.moveTo(x+r,y);cx.arc(x,y,r,0,7)});contorno(10);cx.beginPath();cx.moveTo(0,-90);cx.bezierCurveTo(-20,-30,20,30,0,95);contorno(8);cx.restore()},
 focinho(t){cx.fillStyle=C.fur;cx.beginPath();cx.ellipse(0,20,140,110,0,0,7);cx.fill();contorno(12);cx.fillStyle=C.ink;cx.beginPath();cx.ellipse(0,-20,62,44,0,0,7);cx.fill();
   cx.fillStyle=C.fur2;cx.beginPath();cx.ellipse(-22,-22,12,9,0,0,7);cx.ellipse(22,-22,12,9,0,0,7);cx.fill();for(let i=0;i<3;i++){const p=((t*.9)+i/3)%1;cx.globalAlpha=(1-p)*.8;cx.fillStyle=C.teal2;cx.beginPath();cx.arc(-30+i*30+Math.sin(p*8)*10,-80-p*120,10+p*10,0,7);cx.fill()}cx.globalAlpha=1},
 porta(t){rr(-85,-140,170,280,14);cx.fillStyle=C.fur2;cx.fill();contorno(12);rr(-60,-110,120,100,8);cx.lineWidth=6;cx.strokeStyle='rgba(42,38,34,.35)';cx.stroke();cx.fillStyle=C.gold;cx.beginPath();cx.arc(50,10,14,0,7);cx.fill();contorno(5)},
 escudo(t){cx.fillStyle=C.teal;cx.beginPath();cx.moveTo(0,-125);cx.lineTo(105,-85);cx.quadraticCurveTo(105,60,0,125);cx.quadraticCurveTo(-105,60,-105,-85);cx.closePath();cx.fill();contorno(12);
   cx.beginPath();cx.moveTo(-40,0);cx.lineTo(-10,32);cx.lineTo(48,-30);cx.lineWidth=20;cx.strokeStyle=C.cream;cx.lineCap='round';cx.lineJoin='round';cx.stroke()},
 x(t){cx.fillStyle=C.red;cx.beginPath();cx.arc(0,0,105,0,7);cx.fill();contorno(12);cx.lineWidth=26;cx.lineCap='round';cx.strokeStyle=C.cream;cx.beginPath();cx.moveTo(-42,-42);cx.lineTo(42,42);cx.moveTo(42,-42);cx.lineTo(-42,42);cx.stroke()},
 check(t){cx.fillStyle=C.teal2;cx.beginPath();cx.arc(0,0,105,0,7);cx.fill();contorno(12);cx.lineWidth=26;cx.lineCap='round';cx.lineJoin='round';cx.strokeStyle=C.cream;cx.beginPath();cx.moveTo(-46,4);cx.lineTo(-12,38);cx.lineTo(50,-30);cx.stroke()},
 sofa(t){rr(-130,-40,260,110,30);cx.fillStyle=C.teal;cx.fill();contorno(12);rr(-110,-100,220,80,26);cx.fillStyle=C.teal2;cx.fill();contorno(12);rr(-150,-50,50,120,22);cx.fillStyle=C.teal;cx.fill();contorno(10);rr(100,-50,50,120,22);cx.fill();contorno(10)},
};
function icone(nome,x,y,s,t,rot=0){const f=ICONES[nome];if(!f)return;cx.save();cx.translate(x,y);cx.rotate(rot);cx.scale(s,s);sh('rgba(42,38,34,.22)',0,10/s);f(t);nosh();cx.restore()}
// ---------- camadas ----------
function fundoBase(t,c1,c2,cxp=.5,cyp=.4){cx.fillStyle=c1;cx.fillRect(0,0,W,H);
  const x=W*(cxp+.08*Math.sin(t*.7)),y=H*(cyp+.05*Math.cos(t*.55)),r=H*(.55+.05*Math.sin(t*1.1));
  const g=cx.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,c2);g.addColorStop(1,'rgba(0,0,0,0)');cx.fillStyle=g;cx.fillRect(0,0,W,H)}
function grade(t,col,step=90){cx.save();cx.strokeStyle=col;cx.lineWidth=2;const o=(t*20)%step;cx.beginPath();
  for(let x=-step+o;x<W+step;x+=step){cx.moveTo(x,0);cx.lineTo(x,H)}for(let y=-step+o;y<H+step;y+=step){cx.moveTo(0,y);cx.lineTo(W,y)}cx.stroke();cx.restore()}
function listras(t,col,a=.16){cx.save();cx.globalAlpha=a;cx.fillStyle=col;cx.translate(W/2,H/2);cx.rotate(-.5);const off=(t*80)%160;for(let i=-14;i<14;i++)cx.fillRect(i*160+off-1600,-2000,70,4000);cx.restore()}
function pontos(t,col){cx.fillStyle=col;const o=(t*40)%120;for(let y=-120;y<H+120;y+=120)for(let x=-120;x<W+120;x+=120){const r=10+4*Math.sin(t*2+x*.01+y*.01);cx.beginPath();cx.arc(x+((y/120)%2?60:0)+o,y+o,r,0,7);cx.fill()}}
function raios(t,c1,c2){cx.save();cx.translate(W/2,960);cx.rotate(t*.22);for(let i=0;i<16;i++){cx.rotate(Math.PI/8);cx.fillStyle=i%2?c1:c2;cx.beginPath();cx.moveTo(0,0);cx.lineTo(-200,-1500);cx.lineTo(200,-1500);cx.fill()}cx.restore()}
function particulas(t,col,alpha=.35,n=14,seed=1){cx.save();for(let i=0;i<n;i++){const d=.35+rnd(i*3+seed)*.65;
  const x=(rnd(i+seed)*W+Math.sin(t*.6+i)*30*d), y=((rnd(i*7+seed)*(H+300)-t*120*d)%(H+300)+H+300)%(H+300)-150;
  cx.globalAlpha=alpha*d;const k=i%3;if(k===0)paw(x,y,1.1*d+.3,col,rnd(i)*2+t*.3*d);else if(k===1)bone(x,y,.9*d+.2,col,rnd(i+2)*3+t*.4*d);else{cx.fillStyle=col;cx.beginPath();cx.arc(x,y,10*d+4,0,7);cx.fill()}}cx.restore()}
function vinheta(a=.28){const g=cx.createRadialGradient(W/2,H/2,H*.28,W/2,H/2,H*.78);g.addColorStop(0,'rgba(0,0,0,0)');g.addColorStop(1,`rgba(42,38,34,${a})`);cx.fillStyle=g;cx.fillRect(0,0,W,H)}
function grao(t){if(!GRAIN)return;const f=Math.floor(t*30);cx.save();cx.globalAlpha=.07;cx.globalCompositeOperation='overlay';
  const ox=rnd(f)*512,oy=rnd(f+9)*512;for(let x=-512;x<W+512;x+=512)for(let y=-512;y<H+512;y+=512)cx.drawImage(GRAIN,x+ox-256,y+oy-256);cx.restore()}
function lightleak(t,t0,dur=.9){const p=(t-t0)/dur;if(p<0||p>1)return;cx.save();cx.globalCompositeOperation='screen';
  const x=lerp(-300,W+300,eio(p)),g=cx.createRadialGradient(x,H*.35,0,x,H*.35,900);g.addColorStop(0,`rgba(244,166,90,${.7*Math.sin(p*Math.PI)})`);g.addColorStop(.5,`rgba(229,178,60,${.28*Math.sin(p*Math.PI)})`);g.addColorStop(1,'rgba(0,0,0,0)');
  cx.fillStyle=g;cx.fillRect(0,0,W,H);cx.restore()}
function flash(t,t0,col='253,247,238',d=.25){const p=(t-t0)/d;if(p<0||p>1)return;cx.fillStyle=`rgba(${col},${(1-p)*.85})`;cx.fillRect(0,0,W,H)}
// fundos nomeados -> {escuro:bool}
const FUNDOS={
 listras(t){fundoBase(t,C.amb,'rgba(253,227,200,.55)',.3,.55);listras(t,C.cream);vinheta(.2)},
 grade(t){fundoBase(t,C.cream,'rgba(207,234,227,.9)');grade(t,'rgba(31,122,108,.12)');particulas(t,C.peach,.8,10,3);vinheta(.16)},
 projeto(t){fundoBase(t,C.teal,'rgba(47,156,138,.9)',.6,.55);grade(t,'rgba(207,234,227,.14)',72);particulas(t,C.mint,.18,10,8);vinheta(.3)},
 pontos(t){fundoBase(t,C.cream,'rgba(251,227,200,.95)',.5,.6);pontos(t,'rgba(232,145,60,.12)');particulas(t,C.peach,1,12,5);vinheta(.16)},
 escuro(t){cx.fillStyle=C.ink;cx.fillRect(0,0,W,H);raios(t,'rgba(229,178,60,.10)','rgba(232,145,60,.06)');particulas(t,C.gold,.12,10,11);vinheta(.3)},
 pessego(t){fundoBase(t,C.peach,'rgba(253,247,238,.9)',.5,.35);listras(t,C.amb2,.12);particulas(t,C.cream,.6,12,7);vinheta(.18)},
 alerta(t){fundoBase(t,C.ink,'rgba(194,65,12,.35)',.5,.55);vinheta(.35)},
};
const ESCUROS=new Set(['projeto','escuro','alerta']);
// ---------- peças ----------
function tag(s,x,y,bg,fg,t,t0,rot=-.05){const k=pop(t,t0,.45);if(!k)return;cx.save();cx.translate(x,y+boil(t,3)*.5);cx.rotate(rot);cx.scale(k,k);
  cx.font='900 40px NU';cx.letterSpacing='4px';const w=cx.measureText(s).width+64;cx.letterSpacing='0px';sh('rgba(42,38,34,.3)',0,8);rr(-w/2,-38,w,76,20);cx.fillStyle=bg;cx.fill();nosh();
  cx.lineWidth=6;cx.strokeStyle=C.ink;cx.stroke();txt(s,0,3,40,fg,{w:900,f:'NU',ls:4});cx.restore()}
function palavra(s,x,y,size,col,t,t0,o={}){const k=t<t0?0:spring(t-t0,13,7);if(!k)return;cx.save();cx.translate(x,y+(1-cl((t-t0)*5))*40);cx.scale(k,k);
  if(o.maxw){const m=medir(s,size,o.w||700,o.f||'FR');const f=Math.min(1,o.maxw/m);cx.scale(f,f)}txt(s,0,0,size,col,o);cx.restore()}
function pilula(s,x,y,size,bg,fg,t,t0,rot=-.04){const k=pop(t,t0,.4);if(!k)return;cx.save();cx.translate(x,y);cx.rotate(rot);cx.scale(k,k);const w=Math.min(960,medir(s,size)+80),h=size*1.38;
  sh();rr(-w/2,-h/2,w,h,h/2);cx.fillStyle=bg;cx.fill();nosh();txtFit(s,0,size*.06,size,fg,w-60);cx.restore()}
function ondas(x,y,t,col,dir=Math.PI,n=4,spd=1.3,maxr=520,spread=.55,w=12){cx.save();cx.lineCap='round';for(let i=0;i<n;i++){const p=((t*spd)+i/n)%1;cx.globalAlpha=(1-p)*.9;cx.lineWidth=w;cx.strokeStyle=col;cx.beginPath();cx.arc(x,y,60+p*maxr,dir-spread,dir+spread);cx.stroke()}cx.restore()}
function confete(t,t0,x,y,n=60){const lt=t-t0;if(lt<0||lt>2.2)return;const cols=[C.amb,C.teal2,C.gold,C.red,C.mint,C.amb2];
  for(let i=0;i<n;i++){const a=rnd(i+t0)*Math.PI*2,v=500+rnd(i*3+t0)*900;const px=x+Math.cos(a)*v*lt,py=y+Math.sin(a)*v*lt*.8+900*lt*lt;
   cx.save();cx.translate(px,py);cx.rotate(lt*8*rnd(i+1));cx.globalAlpha=1-cl((lt-1.4)/.8);cx.fillStyle=cols[i%6];if(i%4===0){cx.beginPath();cx.arc(0,0,9,0,7);cx.fill()}else cx.fillRect(-12,-7,24,14);cx.restore()}}
function carimbo(s,x,y,size,bg,fg,t,t0,rot=-.12){if(t<t0)return;const lt=t-t0;const k=lt<.18?lerp(2.6,1,eo(lt/.18)):1+Math.sin(lt*7)*.02;
  cx.save();cx.translate(x,y);cx.rotate(rot);cx.scale(k,k);cx.globalAlpha=cl(lt/.08);const w=Math.min(900,medir(s,size)+70),h=size*1.4;
  sh('rgba(42,38,34,.35)',0,12);rr(-w/2,-h/2,w,h,22);cx.fillStyle=bg;cx.fill();nosh();cx.setLineDash([22,14]);cx.lineWidth=8;cx.strokeStyle=fg;rr(-w/2+14,-h/2+14,w-28,h-28,14);cx.stroke();cx.setLineDash([]);
  txtFit(s,0,size*.06,size,fg,w-60);cx.restore()}
function pessoa(x,y,s,col){cx.save();cx.translate(x,y);cx.scale(s,s);cx.fillStyle=col;cx.beginPath();cx.arc(0,-70,26,0,7);cx.fill();rr(-30,-38,60,74,26);cx.fill();cx.restore()}
function balao(linhas,x,y,t,t0,{bg=C.cream,fg=C.ink,size=58,w=820}={}){const k=pop(t,t0,.45);if(!k)return;const h=linhas.length*size*1.22+80;cx.save();cx.translate(x,y);cx.scale(k,k);cx.rotate(Math.sin(t*2)*.01);
  sh('rgba(42,38,34,.3)',0,12);rr(-w/2,-h/2,w,h,48);cx.fillStyle=bg;cx.fill();cx.beginPath();cx.moveTo(-w/2+120,h/2-4);cx.lineTo(-w/2+80,h/2+70);cx.lineTo(-w/2+210,h/2-4);cx.fill();nosh();
  rr(-w/2,-h/2,w,h,48);contorno(9);linhas.forEach((l,i)=>txtFit(l,0,-h/2+40+size*.62+i*size*1.22,size,fg,w-70,{w:700}));cx.restore()}
