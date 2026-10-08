// Cenas por tipo. Cada tipo tem prep(s) (calcula tempos-chave e sons) e draw(t,s).
// s.ini/s.fim = início/fim da fala da cena; s.pal = índices das palavras da cena em PAL.
const SFX={whoosh:[],pop:[],boom:[],tick:[],riser:[],sucesso:[],tipo:[],notif:[],sirene:[],doorbell:[],ding:[]};
const CORTES=[];
const T=i=>PAL[i].inicio, TF=i=>PAL[i].fim;
const at=(s,f)=>s.ini+f*(s.fim-s.ini);
const norm=x=>x.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/[^a-z0-9]/g,'');
function kw(s,palavra,frac=.5){const n=norm(palavra);for(const i of s.pal)if(norm(PAL[i].palavra)===n)return T(i);return at(s,frac)}
function ultimaPal(s){return s.pal.length?TF(s.pal[s.pal.length-1]):s.fim}
const CORES_DICA=[C.amb,C.teal,C.red,C.teal2,C.gold];
function titulo(linhas,dest,t,t0,y0,{size=108,dark=false,first=false,stagger=.18,gap=1.2}={}){
  linhas.forEach((l,i)=>{const y=y0+i*size*gap;const tt=first?0:t0+i*stagger;
    if(i===dest){const k=first?(.9+.1*sp(t,0,10,6)):pop(t,tt,.4);if(!k)return;cx.save();cx.translate(W/2,y);cx.rotate(-.035);cx.scale(k,k);const w=Math.min(980,medir(l,size)+90);sh();rr(-w/2,-size*.68,w,size*1.36,size*.68);cx.fillStyle=C.ink;cx.fill();nosh();txtFit(l,0,size*.06,size,C.gold,w-70);cx.restore()}
    else{const k=first?(.9+.1*sp(t,0,10,6)):(t<tt?0:spring(t-tt,13,7));if(!k)return;cx.save();cx.translate(W/2,y+(first?0:(1-cl((t-tt)*5))*40));cx.scale(k,k);
      txtFit(l,0,0,size,dark?C.cream:C.cream,980,{stroke:C.ink,sw:size*.2});cx.restore()}})}
const TIPOS={
 gancho:{prep(s){s.fundo=s.fundo||'listras';s.kCar=s.carimbo?kw(s,s.carimbo_palavra||'',.8):0;if(s.icone==='sino')SFX.doorbell.push(.02);if(s.carimbo)SFX.boom.push(s.kCar);SFX.pop.push(.15)},
  draw(t,s){const first=s.i===0;const ls=s.linhas||[];const size=ls.length>3?92:108;
   if(s.icone){const ix=s.icone_x||250,iy=1060;ondas(ix,iy,t,C.cream,0,4,1.4,420,.7,12);icone(s.icone,ix,iy,.75+.04*Math.sin(t*6),t)}
   const k=first?(.8+.2*sp(t,0,9,6)):sp(t,s.ini,9,6);dog(s.mascote||'bravo',W/2+170,1470+(1-k)*400,1.2,Math.sin(t*(s.mascote==='bravo'?14:3))*.035,Math.max(0,Math.sin(t*12))*.02);
   titulo(ls,s.destaque??-1,t,s.ini,330,{size,first});
   if(s.carimbo)carimbo(s.carimbo,W/2-150,1290,96,C.red,C.cream,t,s.kCar,-.12);
   if(s.parte){const k=first?1:pop(t,s.ini,.4);cx.save();cx.translate(W-200,198);cx.scale(k,k);cx.rotate(.04);rr(-120,-38,240,76,24);cx.fillStyle=C.red;cx.fill();contorno(6);txt('PARTE '+s.parte,0,3,40,C.cream,{w:900,f:'NU',ls:2});cx.restore()}}},
 texto:{prep(s){s.fundo=s.fundo||'pontos';const n=(s.linhas||[]).length;s.kL=(s.linhas||[]).map((_,i)=>at(s,i/Math.max(1,n)*.7));s.kL.forEach(x=>SFX.pop.push(x))},
  draw(t,s){const dark=ESCUROS.has(s.fundo);(s.linhas||[]).forEach((l,i)=>{const y=380+i*128;if(i===s.destaque)pilula(l,W/2,y,100,C.ink,C.gold,t,s.kL[i]);else palavra(l,W/2,y,100,dark?C.cream:C.ink,t,s.kL[i],{maxw:960})});
   if(s.icone)icone(s.icone,W/2-230,1060,.8*pop(t,at(s,.35),.5),t);dog(s.mascote||'normal',s.icone?W/2+170:W/2,1430,s.icone?.95:1.1,Math.sin(t*4)*.04,Math.max(0,Math.sin(t*8))*.02)}},
 dica:{prep(s){s.fundo=s.fundo||'pontos';s.cor=CORES_DICA[(s.n-1)%CORES_DICA.length];s.kOk=Math.max(s.ini+.8,s.fim-.15);SFX.pop.push(s.ini+.1);SFX.sucesso.push(s.kOk)},
  draw(t,s){const tot=s.total||5;tag(`DICA ${s.n}/${tot}`,W/2,320,s.cor,C.cream,t,s.ini-.2,-.04);
   // pips de progresso
   const pw=Math.min(70,760/tot);for(let i=0;i<tot;i++){const x=W/2-(tot-1)*pw/2+i*pw;const on=i<s.n-1||(i===s.n-1&&t>=s.kOk);rr(x-pw*.38,420,pw*.76,22,11);cx.fillStyle=on?s.cor:(i===s.n-1?'rgba(42,38,34,.35)':'rgba(42,38,34,.14)');cx.fill()}
   const lt=t-(s.ini-.25),flip=cl(lt/.45),sx=Math.cos((1-eio(flip))*Math.PI/2);
   cx.save();cx.translate(W/2,950+(1-eio(flip))*60);cx.rotate((1-eio(flip))*.08);cx.scale(Math.max(.02,sx)*(1+.012*Math.sin(t*2)),1);
   sh('rgba(42,38,34,.35)',0,22);rr(-430,-400,860,800,60);cx.fillStyle=C.cream;cx.fill();nosh();contorno(10);
   rr(-430,-400,860,40,{upperLeft:60,upperRight:60,lowerLeft:0,lowerRight:0});cx.fillStyle=s.cor;cx.fill();
   const tl=quebrar(s.titulo,74,780);tl.forEach((l,i)=>txt(l,0,-300+i*86,74,C.ink));const yS=-300+tl.length*86;
   if(s.sub){const sl=quebrar(s.sub,46,760,800,'NU');sl.forEach((l,i)=>txt(l,0,yS-10+i*56,46,s.cor===C.gold?C.teal:s.cor,{w:800,f:'NU'}))}
   txt(String(s.n),-250,200,420,'rgba(42,38,34,.06)');const ki=pop(t,s.ini+.35,.5);if(ki&&s.icone){cx.fillStyle='rgba(232,145,60,.12)';cx.beginPath();cx.arc(0,150,200*ki,0,7);cx.fill();icone(s.icone,0,150,1.35*ki,t)}
   const kd=sp(t,s.ini+.6,9,6);if(kd>0){cx.save();cx.beginPath();cx.rect(-430,-400,860,800);cx.clip();dog(s.mascote||['normal','feliz','dorminhoco'][s.n%3],300,470-kd*110,.55,Math.sin(t*4)*.05);cx.restore()}
   if(t>=s.kOk){const kk=pop(t,s.kOk,.35);cx.save();cx.translate(340,-330);cx.scale(kk,kk);ICONES.check(t);cx.restore()}
   if(sx<.9){cx.fillStyle=`rgba(42,38,34,${(1-sx)*.5})`;rr(-430,-400,860,800,60);cx.fill()}cx.restore();
   confete(t,s.kOk,W/2,820,45)}},
 curiosidade:{prep(s){s.fundo=s.fundo||((s.n||1)%2?'projeto':'grade');s.kN=Math.min(kw(s,s.numero_palavra||'',.25),s.ini+.5);for(let k=0;k<10;k++)SFX.tick.push(s.kN+k*.07);SFX.pop.push(s.ini)},
  draw(t,s){const dark=ESCUROS.has(s.fundo);tag(s.tag||`CURIOSIDADE #${s.n||1}`,W/2,320,dark?C.gold:C.teal,dark?C.ink:C.cream,t,s.ini-.2,.04);
   const kn=pop(t,s.kN,.45);if(kn&&s.numero==null){cx.save();cx.translate(W/2,600);cx.scale(kn,kn);cx.fillStyle=dark?'rgba(207,234,227,.16)':'rgba(232,145,60,.16)';cx.beginPath();cx.arc(0,0,190,0,7);cx.fill();icone(s.icone,0,0,1.15,t);cx.restore()}
   else if(kn){const v=lerp(0,s.numero,eo((t-s.kN)/.8));const fmt=(s.prefixo||'')+(Number.isInteger(s.numero)?Math.round(v).toLocaleString('pt-BR'):v.toFixed(1).replace('.',','))+(s.sufixo||'');
     cx.save();cx.translate(W/2,600);cx.scale(kn,kn);txtFit(fmt,0,0,250,dark?C.cream:C.amb,980,{stroke:C.ink,sw:24});cx.restore()}
   (s.rotulo||[]).forEach((l,i)=>palavra(l,W/2,790+i*84,i?54:76,i?(dark?C.cream:C.ink):(dark?C.gold:C.teal),t,s.kN+.25+i*.2,{maxw:960,stroke:i?null:C.ink,sw:i?0:12,f:i?'NU':'FR',w:i?800:700}));
   const ki=pop(t,s.kN+.5,.5);if(ki&&s.icone&&s.numero!=null){cx.save();cx.globalAlpha=.9;cx.fillStyle=dark?'rgba(207,234,227,.14)':'rgba(232,145,60,.14)';cx.beginPath();cx.arc(W/2,1170,190*ki,0,7);cx.fill();cx.restore();icone(s.icone,W/2,1170,.95*ki,t)}}},
 objecao:{prep(s){s.fundo=s.fundo||'pessego';s.kR=kw(s,s.resposta_palavra||'',.42);SFX.pop.push(s.ini);SFX.boom.push(s.kR)},
  draw(t,s){tag(s.tag||'VOCÊ PENSA:',W/2-230,320,C.red,C.cream,t,s.ini-.2,-.05);pessoa(150,700,1.3,C.ink);
   const ls=quebrar('“'+s.objecao+'”',62,720);balao(ls,W/2+70,560,t,s.ini,{size:62,w:800});
   carimbo(s.resposta||'MITO!',W/2,900,120,s.resposta_cor==='teal'?C.teal:C.red,C.cream,t,s.kR,-.08);
   (s.explica||[]).forEach((l,i)=>palavra(l,W/2,1070+i*80,66,C.ink,t,s.kR+.35+i*.25,{maxw:960}));
   dog(s.mascote||'feliz',870,1450,.55*sp(t,s.kR+.2,9,6),Math.sin(t*5)*.03)}},
 mito:{prep(s){s.fundo=s.fundo||'grade';s.kV=kw(s,s.veredito_palavra||'',.45);SFX.pop.push(s.ini);SFX.boom.push(s.kV)},
  draw(t,s){tag(s.tag||'MITO OU VERDADE?',W/2,320,C.ink,C.gold,t,s.ini-.2,-.03);
   const kc=sp(t,s.ini,9,6);cx.save();cx.translate(W/2,620+(1-kc)*500);cx.rotate((1-kc)*-.15);const ls=quebrar('“'+s.frase+'”',66,760);const h=ls.length*80+90;
   sh();rr(-430,-h/2,860,h,40);cx.fillStyle=C.cream;cx.fill();nosh();contorno(10);ls.forEach((l,i)=>txt(l,0,-h/2+70+i*80,66,C.ink));cx.restore();
   const verd=(s.veredito||'MITO').toUpperCase()==='VERDADE';carimbo(verd?'VERDADE':'MITO',W/2+170,620+ls.length*40+40,110,verd?C.teal:C.red,C.cream,t,s.kV,-.15);
   (s.explica||[]).forEach((l,i)=>palavra(l,W/2,1010+i*80,62,C.ink,t,s.kV+.4+i*.25,{maxw:960}));
   if(s.icone)icone(s.icone,W/2,1290,.7*pop(t,s.kV+.6,.5),t)}},
 virada:{prep(s){s.fundo='alerta';s.kP=kw(s,s.para_palavra||'',.6);SFX.riser.push(Math.max(s.ini,s.kP-3.2));SFX.boom.push(s.kP);SFX.sirene.push(s.kP);CORTES.push([s.kP-.5,s.kP])},
  draw(t,s){const al=t>=s.kP;cx.save();cx.translate(W/2,820);const ang=t*(al?7:2.5);for(let i=0;i<2;i++){cx.save();cx.rotate(ang+i*Math.PI);const g=cx.createLinearGradient(0,0,0,-1500);g.addColorStop(0,`rgba(232,145,60,${al?.55:.22})`);g.addColorStop(1,'rgba(232,145,60,0)');
     cx.fillStyle=g;cx.beginPath();cx.moveTo(0,0);cx.lineTo(-420,-1600);cx.lineTo(420,-1600);cx.closePath();cx.fill();cx.restore()}cx.restore();
   (s.topo||[]).forEach((l,i)=>palavra(l,W/2,330+i*100,80,C.cream,t,s.ini+i*.3,{maxw:960}));
   const wy=640,roll=eio((t-s.kP+.05)/.3);cx.save();cx.beginPath();cx.rect(0,wy-115,W,230);cx.clip();
   const kb=pop(t,s.ini+.4,.35);if(kb){cx.save();cx.translate(W/2,wy-roll*230);cx.scale(kb,kb);txtFit(s.de,0,0,170,C.red,960,{stroke:C.cream,sw:14});
     const sp2=eo((t-(s.kP-.6))/.25);if(sp2>0&&roll<1){const w=Math.min(900,medir(s.de,170));cx.lineCap='round';cx.lineWidth=24;cx.strokeStyle=C.cream;cx.beginPath();cx.moveTo(-w/2,10);cx.lineTo(-w/2+w*sp2,-10);cx.stroke()}cx.restore()}
   if(roll>0){cx.save();cx.translate(W/2,wy+230-roll*230);txtFit(s.para,0,0,160,C.gold,960,{stroke:C.ink,sw:18});cx.restore()}cx.restore();
   const k=sp(t,s.ini,8,5),jit=al?Math.sin(t*60)*5:0;cx.save();cx.translate(jit,0);dog('bravo',W/2,1380+(1-k)*600,1.2,Math.sin(t*(al?18:4))*.04,0);
   const dy=790+(1-k)*600;cx.fillStyle=al&&Math.floor(t*8)%2?C.amb2:C.red;cx.shadowColor=al?'rgba(244,166,90,.9)':'transparent';cx.shadowBlur=al?40:0;
   cx.beginPath();cx.arc(W/2,dy,62,Math.PI,0);cx.lineTo(W/2+62,dy+10);cx.lineTo(W/2-62,dy+10);cx.closePath();cx.fill();nosh();contorno(9);rr(W/2-80,dy+8,160,26,10);cx.fillStyle=C.ink;cx.fill();cx.restore();
   if(al)flash(t,s.kP,'244,166,90',.3)}},
 cta_meio:{prep(s){s.fundo=s.fundo||'pessego';s.kS=(s.selos||[]).map((_,i)=>at(s,.35+i*.15));s.kS.forEach(x=>SFX.pop.push(x));SFX.ding.push(s.ini+.2)},
  draw(t,s){titulo(s.linhas||['QUER ADESTRAR','SEU CÃO EM CASA?'],s.destaque??1,t,s.ini,330,{size:100});
   const kc=pop(t,s.ini+.2,.5);if(kc){cx.save();cx.globalAlpha=.9;cx.fillStyle='rgba(232,145,60,.18)';cx.beginPath();cx.arc(W/2-170,860,200*kc,0,7);cx.fill();cx.restore();icone('casa',W/2-170,860,1.1*kc,t)}
   dog(s.mascote||'feliz',W/2+210,1030,.9*sp(t,s.ini+.3,9,6),Math.sin(t*4)*.04);
   (s.selos||[]).forEach((l,i)=>{const k=pop(t,s.kS[i],.4);if(!k)return;cx.save();cx.translate(W/2+(i-(s.selos.length-1)/2)*320,1170+(i%2)*14);cx.rotate((i%2?.04:-.04));cx.scale(k,k);rr(-150,-48,300,96,48);cx.fillStyle=[C.teal,C.amb,C.red][i%3];cx.fill();contorno(7);txtFit(l,0,4,40,C.cream,260,{w:900,f:'NU'});cx.restore()});
   if(t>at(s,.7)){const p=1+.05*Math.sin(t*8);cx.save();cx.translate(W/2,1330);cx.scale(p,p);pilula(s.link||'LINK NA BIO ↑'.replace(' ↑',''),0,0,64,C.ink,C.gold,t,at(s,.7),0);cx.restore()}}},
 cta_final:{prep(s){s.fundo='escuro';s.kX=kw(s,s.palavra||'XIXI',.3);s.kN=Math.max(s.kX+1,ultimaPal(s)-.4);[0,1,2,3].forEach(k=>SFX.tipo.push(s.kX-.05+k*.09));SFX.pop.push(s.kX+.5);SFX.notif.push(s.kN);SFX.boom.push(s.kX+.05)},
  draw(t,s){const tc=s.kX;(s.linhas||['QUER O PLANO CERTO','PRO SEU CÃO?']).forEach((l,i)=>palavra(l,W/2,330+i*92,i?84:74,i?C.gold:C.cream,t,s.ini+i*.3,{maxw:960}));
   const k=sp(t,s.ini,8,5.5),px=W/2,py=1000+(1-k)*1100,pw=560,ph=860;cx.save();cx.translate(px,py);cx.rotate((1-k)*.25+Math.sin(t*1.3)*.012);
   sh('rgba(0,0,0,.5)',50,30);rr(-pw/2,-ph/2,pw,ph,64);cx.fillStyle='#14110F';cx.fill();nosh();rr(-pw/2+16,-ph/2+16,pw-32,ph-32,50);cx.fillStyle=C.cream;cx.fill();cx.save();cx.clip();
   cx.fillStyle=C.amb;cx.beginPath();cx.arc(-pw/2+70,-ph/2+80,30,0,7);cx.fill();paw(-pw/2+70,-ph/2+84,.55,C.cream);txt('meu_cao_obedece',-pw/2+116,-ph/2+80,30,C.ink,{w:800,f:'NU',al:'left'});
   rr(-pw/2+16,-ph/2+130,pw-32,330,0);cx.fillStyle=C.amb2;cx.fill();dog('lendario',0,-ph/2+450,.62,Math.sin(t*3)*.03);
   txt('Comentários',-pw/2+44,-ph/2+500,30,C.ink,{w:900,f:'NU',al:'left'});
   const word=s.palavra||'XIXI',typed=Math.min(word.length,Math.floor(cl((t-tc+.05)/.36)*(word.length+.999))),sent=t>tc+.5;
   if(sent){const kc=pop(t,tc+.5,.4);cx.save();cx.translate(-pw/2+44,-ph/2+590);cx.scale(kc,kc);cx.fillStyle=C.teal2;cx.beginPath();cx.arc(26,0,26,0,7);cx.fill();txt('você',70,-14,26,C.ink,{w:900,f:'NU',al:'left'});
     txt(word,70,18,40,C.ink,{w:700,al:'left'});cx.restore();const kh=pop(t,tc+.85,.35);if(kh)heart(pw/2-60,-ph/2+590,.3*kh,C.red)}
   rr(-pw/2+36,ph/2-150,pw-72,84,42);cx.fillStyle='#fff';cx.fill();cx.lineWidth=4;cx.strokeStyle='rgba(42,38,34,.2)';cx.stroke();
   if(typed===0||sent)txt('Adicione um comentário...',-pw/2+70,ph/2-107,28,'rgba(42,38,34,.45)',{w:800,f:'NU',al:'left'});
   else{const ss=word.slice(0,typed);txt(ss,-pw/2+70,ph/2-105,40,C.ink,{al:'left'});const w=medir(ss,40);if(Math.floor(t*4)%2){cx.fillStyle=C.amb;cx.fillRect(-pw/2+74+w,ph/2-128,5,46)}}
   const ks=t>tc+.3&&t<tc+.7?1+.25*Math.sin((t-tc-.3)/.4*Math.PI):1;cx.save();cx.translate(pw/2-90,ph/2-108);cx.scale(ks,ks);cx.fillStyle=C.amb;cx.beginPath();cx.arc(0,0,32,0,7);cx.fill();cx.fillStyle=C.cream;cx.beginPath();cx.moveTo(-12,-14);cx.lineTo(16,0);cx.lineTo(-12,14);cx.closePath();cx.fill();cx.restore();
   if(t>s.kN){const kn=eo((t-s.kN)/.4);cx.save();cx.translate(0,-ph/2-80+kn*190);sh('rgba(0,0,0,.25)',20,8);rr(-pw/2+30,-55,pw-60,110,30);cx.fillStyle='#fff';cx.fill();nosh();
     cx.fillStyle=C.amb;cx.beginPath();cx.arc(-pw/2+90,0,32,0,7);cx.fill();paw(-pw/2+90,4,.6,C.cream);txt('Meu Cão Obedece',-pw/2+140,-18,28,C.ink,{w:900,f:'NU',al:'left'});txt(s.notificacao||'Te mandei o teste!',-pw/2+140,18,28,C.teal,{w:800,f:'NU',al:'left'});cx.restore()}
   cx.restore();cx.restore();
   if(t>tc-.2&&t<tc+.9){const p=cl((t-tc+.2)/.5);const fx=px+pw/2-90+lerp(140,0,eo(p)),fy=py+ph/2-108+lerp(220,0,eo(p));cx.save();
     if(t>tc+.3){const r=(t-tc-.3)*200;cx.lineWidth=6;cx.strokeStyle=`rgba(253,247,238,${1-cl((t-tc-.3)/.5)})`;cx.beginPath();cx.arc(fx,fy,20+r,0,7);cx.stroke()}
     cx.fillStyle='rgba(253,247,238,.85)';cx.beginPath();cx.arc(fx,fy,30,0,7);cx.fill();cx.restore()}
   carimbo('COMENTA '+word,W/2,1395,76,C.gold,C.ink,t,s.kN-.2,-.05);if(t>tc)confete(t,tc+.5,W/2,900,70)}},
};
// ---------- cenas de anúncio ----------
Object.assign(TIPOS,{
 checklist:{prep(s){s.fundo=s.fundo||'pessego';const n=(s.itens||[]).length;s.kI=(s.itens||[]).map((_,i)=>at(s,.08+i/Math.max(1,n)*.7));s.kI.forEach(x=>SFX.pop.push(x))},
  draw(t,s){if(s.titulo)palavra(s.titulo,W/2,330,84,C.ink,t,s.ini-.1,{maxw:960});
   (s.itens||[]).forEach((it,i)=>{const k=pop(t,s.kI[i],.4);if(!k)return;const y=520+i*165;cx.save();cx.translate(W/2+(1-k)*-200,y);cx.rotate((i%2?.012:-.012));cx.scale(k,k);
     sh();rr(-430,-64,860,128,34);cx.fillStyle=C.cream;cx.fill();nosh();contorno(8);cx.save();cx.translate(-360,0);cx.scale(.42,.42);(s.marca==='check'?ICONES.check:ICONES.x)(t);cx.restore();
     txtFit(it,40,4,60,C.ink,700,{w:700});cx.restore()});
   if(s.mascote!==null)dog(s.mascote||'bravo',880,1450,.5*sp(t,s.ini+.3,9,6),Math.sin(t*12)*.04)}},
 comparativo:{prep(s){s.fundo=s.fundo||'grade';s.kB=Math.max(s.ini+.8,kw(s,s.barato_palavra||'',.55));SFX.pop.push(s.ini+.1);SFX.boom.push(s.kB)},
  draw(t,s){tag(s.tag||'QUANTO CUSTA?',W/2,320,C.ink,C.gold,t,s.ini-.2,-.03);
   const kA=sp(t,s.ini,9,6),dim=t>s.kB?eo((t-s.kB)/.4):0;
   cx.save();cx.translate(W/2-225,820+(1-kA)*700);cx.rotate(-.03);cx.globalAlpha=1-dim*.35;sh();rr(-200,-260,400,520,40);cx.fillStyle=C.cream;cx.fill();nosh();contorno(9);
   txt(s.caro_titulo||'ADESTRADOR',0,-190,40,C.ink,{w:900,f:'NU',ls:2});pessoa(0,-40,1.1,C.ink);
   txtFit(s.caro,0,80,84,C.red,360);(s.caro_sub?quebrar(s.caro_sub,34,340,800,'NU'):[]).forEach((l,i)=>txt(l,0,150+i*42,34,C.ink,{w:800,f:'NU'}));
   if(dim>0){cx.globalAlpha=1;cx.lineCap='round';cx.lineWidth=18;cx.strokeStyle=C.red;cx.beginPath();cx.moveTo(-150,80);cx.lineTo(-150+300*dim,70);cx.stroke()}cx.restore();
   const kB=pop(t,s.kB,.45);if(kB){cx.save();cx.translate(W/2+225,800);cx.rotate(.03);cx.scale(kB*1.05,kB*1.05);sh('rgba(42,38,34,.35)',0,16);rr(-200,-280,400,560,40);cx.fillStyle=C.teal;cx.fill();nosh();contorno(9);
     txtFit(s.barato_titulo||'MEU CÃO OBEDECE',0,-205,40,C.cream,360,{w:900,f:'NU'});paw(0,-90,1.6,C.gold);txtFit(s.barato,0,60,110,C.gold,360,{stroke:C.ink,sw:14});
     (s.barato_sub?quebrar(s.barato_sub,34,340,800,'NU'):[]).forEach((l,i)=>txt(l,0,150+i*42,34,C.cream,{w:800,f:'NU'}));cx.restore()}
   if(s.rodape)palavra(s.rodape,W/2,1230,58,C.ink,t,s.kB+.5,{maxw:960})}},
 produto:{prep(s){s.fundo=s.fundo||'pontos';s.kS=(s.selos||[]).map((_,i)=>at(s,.3+i*.18));s.kS.forEach(x=>SFX.pop.push(x));SFX.ding.push(s.ini+.3)},
  draw(t,s){(s.linhas||[]).forEach((l,i)=>palavra(l,W/2,320+i*96,i?72:84,i?C.amb:C.ink,t,s.ini+i*.25,{maxw:960,stroke:i?C.ink:null,sw:i?12:0}));
   const k=sp(t,s.ini,8,5.5),pw=500,ph=780,px=W/2,py=1000+(1-k)*900;cx.save();cx.translate(px,py);cx.rotate((1-k)*.2+Math.sin(t*1.3)*.012);
   sh('rgba(42,38,34,.4)',40,24);rr(-pw/2,-ph/2,pw,ph,60);cx.fillStyle='#14110F';cx.fill();nosh();rr(-pw/2+14,-ph/2+14,pw-28,ph-28,48);cx.fillStyle=C.cream;cx.fill();cx.save();cx.clip();
   rr(-pw/2,-ph/2,pw,120,0);cx.fillStyle=C.amb;cx.fill();paw(-pw/2+70,-ph/2+72,.6,C.cream);txt('Meu Cão Obedece',-pw/2+110,-ph/2+72,32,C.cream,{w:900,f:'NU',al:'left'});
   const prog=cl((t-s.ini)/Math.max(1,s.fim-s.ini));const dia=Math.max(1,Math.round(prog*21));
   txt(`Dia ${dia} de 21`,0,-ph/2+170,40,C.ink,{w:900,f:'NU'});rr(-190,-ph/2+205,380,26,13);cx.fillStyle='rgba(42,38,34,.12)';cx.fill();rr(-190,-ph/2+205,Math.max(26,380*dia/21),26,13);cx.fillStyle=C.teal2;cx.fill();
   for(let i=0;i<21;i++){const x=-180+(i%7)*60,y=-ph/2+270+Math.floor(i/7)*60;rr(x-22,y-22,44,44,10);cx.fillStyle=i<dia?C.teal2:'rgba(42,38,34,.1)';cx.fill();if(i<dia){cx.lineWidth=5;cx.strokeStyle=C.cream;cx.lineCap='round';cx.beginPath();cx.moveTo(x-9,y);cx.lineTo(x-2,y+7);cx.lineTo(x+10,y-7);cx.stroke()}}
   dog(prog>.5?'feliz':'normal',0,ph/2-150,.5,Math.sin(t*4)*.04);
   if(prog>.75){const kc=pop(t,at(s,.75),.4);cx.save();cx.translate(0,ph/2-70);cx.scale(kc,kc);rr(-200,-36,400,72,20);cx.fillStyle=C.gold;cx.fill();contorno(5);txt('🏅 Certificado do seu cão'.replace('🏅 ',''),0,3,30,C.ink,{w:900,f:'NU'});cx.restore()}
   cx.restore();cx.restore();
   (s.selos||[]).forEach((l,i)=>{const kk=pop(t,s.kS[i],.4);if(!kk)return;const lado=i%2?1:-1;cx.save();cx.translate(W/2+lado*390,700+i*240);cx.rotate(lado*.06);cx.scale(kk*.85,kk*.85);rr(-150,-46,300,92,46);cx.fillStyle=[C.teal,C.amb,C.red][i%3];cx.fill();contorno(7);txtFit(l,0,4,38,C.cream,260,{w:900,f:'NU'});cx.restore()})}},
 oferta:{prep(s){s.fundo=s.fundo||'escuro';s.kP=Math.min(s.ini+.6,kw(s,s.preco_palavra||'',.2));for(let k=0;k<10;k++)SFX.tick.push(s.kP+k*.06);SFX.boom.push(s.kP+.65);s.kS=(s.selos||[]).map((_,i)=>s.kP+.9+i*.3);s.kS.forEach(x=>SFX.pop.push(x))},
  draw(t,s){palavra(s.topo||'TUDO ISSO POR',W/2,340,80,C.cream,t,s.ini,{maxw:960});
   const kp=pop(t,s.kP,.45);if(kp){const v=Math.round(lerp(0,s.preco||37,eo((t-s.kP)/.6)));cx.save();cx.translate(W/2,620);cx.scale(kp,kp);
     const g=cx.createRadialGradient(0,0,20,0,0,420);g.addColorStop(0,'rgba(229,178,60,.4)');g.addColorStop(1,'rgba(229,178,60,0)');cx.fillStyle=g;cx.fillRect(-500,-400,1000,800);
     txt('R$',-230,-40,90,C.gold,{stroke:C.ink,sw:12});txt(String(v),60,0,300,C.gold,{stroke:C.ink,sw:26});cx.restore()}
   if(s.sub)palavra(s.sub,W/2,840,60,C.cream,t,s.kP+.6,{maxw:960});
   (s.selos||[]).forEach((l,i)=>{const k=pop(t,s.kS[i],.4);if(!k)return;cx.save();cx.translate(W/2,1000+i*130);cx.scale(k,k);rr(-380,-52,760,104,52);cx.fillStyle=i===0?C.teal:'rgba(253,247,238,.12)';cx.fill();contorno(6);
     cx.save();cx.translate(-320,0);cx.scale(.32,.32);(i===0?ICONES.escudo:ICONES.check)(t);cx.restore();txtFit(l,30,4,46,C.cream,600,{w:900,f:'NU'});cx.restore()})}},
 cta_link:{prep(s){s.fundo=s.fundo||'listras';SFX.pop.push(s.ini+.1);SFX.ding.push(s.ini+.5);SFX.boom.push(Math.max(s.ini+.5,ultimaPal(s)-.6))},
  draw(t,s){const botao=s.modo==='botao';(s.linhas||(botao?['TOQUE EM','SAIBA MAIS']:['TOQUE NO','LINK DA BIO'])).forEach((l,i)=>{if(i===1)pilula(l,W/2,330+i*130,100,C.ink,C.gold,t,s.ini+.25);else palavra(l,W/2,330,104,C.cream,t,s.ini,{stroke:C.ink,sw:20,maxw:960})});
   if(!botao){const k=sp(t,s.ini+.2,9,6);cx.save();cx.translate(W/2,780+(1-k)*400);sh();rr(-420,-150,840,300,40);cx.fillStyle=C.cream;cx.fill();nosh();contorno(8);
     cx.fillStyle=C.amb;cx.beginPath();cx.arc(-300,-40,70,0,7);cx.fill();contorno(6);paw(-300,-34,1.1,C.cream);txt('meu_cao_obedece',-200,-70,42,C.ink,{w:900,f:'NU',al:'left'});txt('Adestramento em casa 🐾'.replace(' 🐾',''),-200,-20,32,'rgba(42,38,34,.7)',{w:800,f:'NU',al:'left'});
     const pl=1+.06*Math.sin(t*9);cx.save();cx.translate(-60,70);cx.scale(pl,pl);rr(-170,-34,520,68,34);cx.fillStyle=C.teal;cx.fill();txt('🔗 link na bio'.replace('🔗 ',''),90,3,36,C.cream,{w:900,f:'NU'});cx.restore();
     const r=(t*1.6)%1;cx.globalAlpha=1-r;cx.lineWidth=8;cx.strokeStyle=C.teal;rr(-60-260-r*30,70-34-r*20,520+r*60,68+r*40,40);cx.stroke();cx.globalAlpha=1;cx.restore();
     const b=Math.sin(t*7)*18;cx.save();cx.translate(W/2-60,1010+b);cx.fillStyle=C.ink;cx.beginPath();cx.moveTo(0,-60);cx.lineTo(55,10);cx.lineTo(20,10);cx.lineTo(20,70);cx.lineTo(-20,70);cx.lineTo(-20,10);cx.lineTo(-55,10);cx.closePath();cx.fill();cx.restore()}
   else{const k=sp(t,s.ini+.2,9,6);cx.save();cx.translate(W/2,1180+(1-k)*500);sh();rr(-430,-70,860,140,30);cx.fillStyle=C.ink;cx.fill();nosh();txt('Meu Cão Obedece',-390,0,40,C.cream,{w:900,f:'NU',al:'left'});
     const pl=1+.05*Math.sin(t*9);cx.save();cx.translate(250,0);cx.scale(pl,pl);rr(-140,-42,280,84,20);cx.fillStyle=C.cream;cx.fill();txt('Saiba mais',0,3,40,C.ink,{w:900,f:'NU'});cx.restore();
     const tf=ultimaPal(s)-.8;if(t>tf&&t<tf+1){const p=cl((t-tf)/.4);cx.fillStyle='rgba(253,247,238,.85)';cx.beginPath();cx.arc(250+lerp(160,0,eo(p)),lerp(200,0,eo(p)),30,0,7);cx.fill()}cx.restore()}
   dog(s.mascote||'lendario',W/2+250,botao?1000:1430,botao?.8:.6,Math.sin(t*3)*.04)}},
});
// ---------- TikTok: chamada para o quiz ----------
Object.assign(TIPOS,{
 cta_quiz:{prep(s){s.fundo=s.fundo||'escuro';s.kT=at(s,.3);s.kR=at(s,.55);s.kL=at(s,.75);SFX.pop.push(s.ini+.1,s.kT);SFX.ding.push(s.kT+.3);SFX.sucesso.push(s.kR);SFX.boom.push(s.kL)},
  draw(t,s){(s.linhas||['QUAL É O PERFIL','DO SEU CÃO?']).forEach((l,i)=>palavra(l,W/2,320+i*96,i?84:74,i?C.gold:C.cream,t,s.ini+i*.25,{maxw:960}));
   const k=sp(t,s.ini,8,5.5),pw=560,ph=800,px=W/2,py=960+(1-k)*900;cx.save();cx.translate(px,py);cx.rotate((1-k)*.2+Math.sin(t*1.3)*.012);
   sh('rgba(0,0,0,.5)',40,24);rr(-pw/2,-ph/2,pw,ph,60);cx.fillStyle='#14110F';cx.fill();nosh();rr(-pw/2+14,-ph/2+14,pw-28,ph-28,48);cx.fillStyle=C.cream;cx.fill();cx.save();cx.clip();
   rr(-pw/2,-ph/2,pw,110,0);cx.fillStyle=C.teal;cx.fill();txt('Teste: perfil do seu cão',0,-ph/2+66,32,C.cream,{w:900,f:'NU'});
   const prog=t<s.kR?cl((t-s.ini)/(s.kR-s.ini))*.8:1;rr(-220,-ph/2+140,440,18,9);cx.fillStyle='rgba(42,38,34,.12)';cx.fill();rr(-220,-ph/2+140,Math.max(18,440*prog),18,9);cx.fillStyle=C.amb;cx.fill();
   if(t<s.kR){quebrar(s.pergunta||'Quando a campainha toca, ele…',40,460,900,'NU').forEach((l,i)=>txt(l,0,-ph/2+215+i*50,40,C.ink,{w:900,f:'NU'}));
     (s.opcoes||['Late sem parar','Corre pra porta','Se esconde']).forEach((o,i)=>{const y=-40+i*120,sel=t>s.kT&&i===(s.escolha||0);rr(-230,y-45,460,90,24);cx.fillStyle=sel?C.amb:'#fff';cx.fill();cx.lineWidth=5;cx.strokeStyle=sel?C.ink:'rgba(42,38,34,.2)';cx.stroke();
       txt(String.fromCharCode(65+i),-190,y+2,36,sel?C.cream:C.teal,{w:900,f:'NU'});txtFit(o,30,y+2,36,sel?C.cream:C.ink,340,{w:800,f:'NU'})});
     if(t>s.kT-.3&&t<s.kT+.5){const p=cl((t-s.kT+.3)/.3);const y=-40+(s.escolha||0)*120;cx.fillStyle='rgba(42,38,34,.35)';cx.beginPath();cx.arc(150+lerp(120,0,eo(p)),y+lerp(160,10,eo(p)),30,0,7);cx.fill()}}
   else{const kr=pop(t,s.kR,.45);cx.save();cx.translate(0,40);cx.scale(kr,kr);txt('Seu resultado:',0,-290,40,C.teal,{w:900,f:'NU'});dog(s.mascote||'lendario',0,80,.58,Math.sin(t*3)*.04);
     rr(-220,120,440,96,30);cx.fillStyle=C.gold;cx.fill();contorno(6);txtFit(s.resultado||'CÃO ALARME',0,170,46,C.ink,400);cx.restore()}
   cx.restore();cx.restore();if(t>s.kR)confete(t,s.kR,W/2,900,60);
   if(t>s.kL){const p=1+.05*Math.sin(t*8);cx.save();cx.translate(W/2,1430);cx.scale(p,p);pilula(s.link||'LINK NO PERFIL',0,0,58,C.gold,C.ink,t,s.kL,0);cx.restore()}}},
});
// ---------- História: personagens 2D + cão num cenário, com diálogo dublado ----------
// s._linhas = [{quem,texto,pensa,grito,humor,pose}] (montado pelo reels.py), s.linhas = tempos de cada linha.
if(!SFX.latido)SFX.latido=[];
const PES=1400,ESC=.92,CAO_S=.8;
function linhasH(s){const L=(s._linhas||[]).map((l,j)=>Object.assign({},l,(s.tl||[])[j]||{ini:at(s,j/Math.max(1,(s._linhas||[]).length)),fim:at(s,(j+1)/Math.max(1,(s._linhas||[]).length))}));
  const el=s.elenco||[{quem:'ana',x:330,humor:s.humor}];
  (s.baloes||[]).forEach(b=>{if(b.quem!=='cao'){const t0=b.palavra?kw(s,b.palavra,.3):at(s,b.em??.2);L.push({quem:b.quem==='tutor'?el[0].quem:b.quem,texto:b.texto,pensa:b.pensa,grito:b.grito,ini:t0,fim:t0+1.4,mudo:true})}});
  return L.sort((a,b)=>a.ini-b.ini)}
function tempoDe(s,v,def){return v==null?def:(typeof v==='string'?kw(s,v,.3):at(s,v))}
Object.assign(TIPOS,{
 historia:{prep(s){s.fundo=(s.cenario==='noite'||s.cenario==='quarto')?'escuro':'pessego';s.el=(s.elenco||[{quem:'ana',x:330,humor:s.humor||'normal',pose:s.pose}]).map(e=>Object.assign({x:330,humor:'normal',pose:'parado'},e));
   s.cao=s.cao===false?null:Object.assign({mascote:s.mascote||'normal',x:760,acao:s.som==='latido'?'late':null},s.cao||{});
   s.L=linhasH(s);s.kB=(s.baloes||[]).filter(b=>b.quem==='cao').map(b=>Object.assign({t0:tempoDe(s,b.palavra||b.em,s.ini+.1)},b));
   s.kB.forEach(b=>{SFX.latido.push(b.t0);if(/AU|au/.test(b.texto))SFX.latido.push(b.t0+.32)});
   if(s.cao&&s.cao.acao==='late'&&!s.kB.length)SFX.latido.push(s.ini+.15,s.ini+.47);
   (s.objetos||[]).forEach(o=>{o.t0=o.em==null&&!o.palavra?null:tempoDe(s,o.palavra||o.em,0);if(o.t0!=null)SFX.pop.push(o.t0)});
   if(s.icone){s.kI=at(s,.4);SFX.ding.push(s.kI)}
   if(s.campainha)SFX.doorbell.push(tempoDe(s,s.campainha,s.ini));
   if(s.camera){s.camT=tempoDe(s,s.camera.palavra||s.camera.em,s.ini);SFX.whoosh.push(s.camT-.05)}},
  draw(t,s){
   // câmera
   const z0=1+.045*cl((t-s.a)/Math.max(1,s.fim-s.a+.5));let f=[540,960],z=z0;
   if(s.camera){const k=eio(cl((t-s.camT)/.55));let alvo;
     if(s.camera.foco==='cao'&&s.cao)alvo=[s.cao.x,PES-250];else{const e=s.el.find(e=>e.quem===s.camera.foco)||s.el[0];alvo=[e.x,PES-720*ESC+150]}
     const zt=s.camera.z||1.6;z=lerp(z0,zt,k);f=[lerp(540,alvo[0],k),lerp(960,alvo[1],k)]}
   f[0]=Math.max(540/z,Math.min(W-540/z,f[0]));f[1]=Math.max(960/z,Math.min(H-960/z,f[1]));
   const proj=p=>[W/2+(p[0]-f[0])*z,H/2+(p[1]-f[1])*z];
   cx.save();cx.translate(W/2,H/2);cx.scale(z,z);cx.translate(-f[0],-f[1]);
   cenarioH(t,s.cenario||'sala',s);
   (s.objetos||[]).forEach(o=>objetoH(o.nome,o.x??540,o.y??(PES+30),t,o.t0));
   // quem está falando agora
   const atual=s.L.filter(l=>t>=l.ini-.08&&l.quem!=='narrador').slice(-1)[0];
   const pos={};
   s.el.forEach(e=>{const st={humor:e.humor,pose:e.pose,dir:e.dir,sentado:e.sentado,anda:e.anda,inclina:e.inclina};
     for(const l of s.L)if(l.quem===e.quem&&t>=l.ini-.12){if(l.humor)st.humor=l.humor;if(l.pose&&l.pose!==st.pose){st.posePrev=st.pose;st.pose=l.pose;st.tPose=l.ini-.12}}
     st.falando=s.L.some(l=>l.quem===e.quem&&!l.pensa&&!l.mudo&&t>=l.ini-.04&&t<=l.fim+.04);
     const fx=atual&&atual.quem!==e.quem?(atual.quem==='cao'&&s.cao?s.cao.x:(s.el.find(o=>o.quem===atual.quem)||{x:e.x}).x):(s.cao?s.cao.x:540);
     st.olhar=Math.max(-1,Math.min(1,(fx-e.x)/250))*(e.dir||1);
     pos[e.quem]=persona(e.quem,e.x,PES+(e.y||0),ESC*(e.s||1),t,st)});
   if(s.cao){const c=s.cao,ac=c.acao;let x=c.x,y=PES+20,rot=Math.sin(t*3)*.03,sq=0,fl=c.dir||1;
     if(ac==='late'){x+=Math.sin(t*42)*5;rot=Math.sin(t*14)*.05;sq=Math.max(0,Math.sin(t*10))*.03}
     if(ac==='pula'){y-=Math.abs(Math.sin(t*6))*110;rot=Math.sin(t*6)*.12}
     if(ac==='corre'){const ph=Math.sin(t*2.2);x=540+ph*300;fl=Math.cos(t*2.2)>0?1:-1;y-=Math.abs(Math.sin(t*12))*30}
     if(ac==='senta')sq=.07;
     if(ac==='feliz'){y-=Math.abs(Math.sin(t*5))*24;rot=Math.sin(t*5)*.06}
     const lider=s.el.find(e=>e.pose==='guia');if(lider&&pos[lider.quem]&&pos[lider.quem].maos.R){const m=pos[lider.quem].maos.R;cx.beginPath();cx.moveTo(m[0],m[1]);cx.quadraticCurveTo((m[0]+x)/2,Math.max(m[1],y-200)+90,x,y-CAO_S*440*.62);cx.lineWidth=8;cx.strokeStyle=C.red;cx.stroke()}
     cx.save();cx.translate(x,y);cx.scale(fl,1);dog(c.mascote,0,0,CAO_S*(c.s||1),rot,sq);cx.restore();
     if(ac==='late'||s.kB.some(b=>t>=b.t0&&t<b.t0+.9))ondas(x+fl*120,y-CAO_S*440*.78,t,C.amb,fl>0?-.35:Math.PI+.35,3,1.6,220,.5,10);
     if(ac==='dorme'){for(let i=0;i<3;i++){const p=((t*.5+i/3)%1);cx.globalAlpha=1-p;txt('z',x+60+p*80,y-380-p*160,40+i*10,C.cream,{w:900,f:'NU',stroke:C.ink,sw:8})}cx.globalAlpha=1}
     pos.cao={cabeca:[x,y-CAO_S*440*1.12]}}
   (s.objetos||[]).filter(o=>o.frente).forEach(o=>objetoH(o.nome,o.x??540,o.y??(PES+60),t,o.t0));
   cx.restore();
   if(s.cenario==='noite'||s.cenario==='quarto'){cx.fillStyle='rgba(20,18,40,.12)';cx.fillRect(0,0,W,H)}
   vinheta(.2);
   // balões: só o último de cada personagem, no máximo 2 na tela
   const vis=[];const ult={};s.L.forEach((l,j)=>{if(l.quem!=='narrador'&&t>=l.ini-.08)ult[l.quem]=j});
   Object.values(ult).sort((a,b)=>a-b).slice(-2).forEach(j=>vis.push(s.L[j]));
   vis.forEach(l=>{const p=pos[l.quem];if(!p)return;const [ax,ay]=proj(p.cabeca);const el=s.el.find(e=>e.quem===l.quem)||{};
     balaoH(l.texto,ax+(el.x<540?40:-40),Math.max(560,ay),t,l.ini-.08,{pensa:!!l.pensa,grito:!!l.grito,size:l.size||(l.texto.length>40?40:46),cor:l.pensa?'#EEF6F4':C.cream})});
   s.kB.forEach(b=>{if(!pos.cao||t<b.t0)return;const bl=s.kB.filter(x=>x.t0<=t).slice(-1)[0];if(bl!==b)return;const [ax,ay]=proj(pos.cao.cabeca);balaoH(b.texto,ax,Math.max(560,ay),t,b.t0,{grito:b.grito!==false,cor:C.gold,size:b.size||52})});
   if(s.icone&&t>=s.kI){const ki=pop(t,s.kI,.5);icone(s.icone,W-150,600,.5*ki,t)}
   if(s.quando){const k=pop(t,s.ini-.15,.4)*(1-eIn(cl((t-s.ini-2.8)/.35)));if(k>.01){cx.save();cx.translate(W/2,330);cx.rotate(-.03);cx.scale(k,k);const w=medir(s.quando,54,900,'NU')+70;sh();rr(-w/2,-45,w,90,24);cx.fillStyle=C.ink;cx.fill();nosh();txt(s.quando,0,4,54,C.gold,{w:900,f:'NU',ls:3});cx.restore()}}
   if(s.titulo)palavra(s.titulo,W/2,455,70,C.ink,t,s.ini+.2,{maxw:960})}},
 // ---------- conversa de grupo no celular (mensagens dubladas) ----------
 chat:{prep(s){s.fundo=s.fundo||'grade';s.L=linhasH(s).filter(l=>l.quem!=='narrador');s.L.forEach(l=>SFX.notif.push(l.ini-.12))},
  draw(t,s){const pw=820,ph=1300,y0=930;cx.save();cx.translate(W/2,y0+(1-sp(t,s.a,9,7))*300);cx.rotate(-.02);
   sh('rgba(42,38,34,.35)',0,18);rr(-pw/2-22,-ph/2-22,pw+44,ph+44,70);cx.fillStyle=C.ink;cx.fill();nosh();
   rr(-pw/2,-ph/2,pw,ph,52);cx.fillStyle='#EDE6DA';cx.fill();cx.save();rr(-pw/2,-ph/2,pw,ph,52);cx.clip();
   cx.fillStyle='rgba(42,38,34,.05)';for(let i=0;i<30;i++)paw(-pw/2+rnd(i)*pw,-ph/2+rnd(i+40)*ph,.7,'rgba(42,38,34,.05)',rnd(i+7)*3);
   // cabeçalho
   cx.fillStyle=C.teal;cx.fillRect(-pw/2,-ph/2,pw,190);cx.beginPath();cx.arc(-pw/2+90,-ph/2+118,46,0,7);cx.fillStyle=C.cream;cx.fill();paw(-pw/2+90,-ph/2+122,1,C.teal);
   txt(s.grupo||'Condomínio Bloco B',-pw/2+160,-ph/2+100,40,C.cream,{w:900,f:'NU',al:'left'});txt(s.membros||'48 participantes',-pw/2+160,-ph/2+148,28,'rgba(253,247,238,.8)',{w:800,f:'NU',al:'left'});
   // mensagens (as mais recentes empurram as antigas pra cima)
   const NOMES=Object.assign({sindica:'Síndica Márcia',vizinho:'Seu Jorge (301)',ana:'Você',joao:'João (204)',bia:'Bia (101)',carla:'Carla (402)',pedro:'Pedro (103)'},s.nomes||{});
   const CORN={sindica:C.red,vizinho:'#B7791F',joao:'#7A4FD0',bia:C.teal,carla:'#C2410C',pedro:'#2F7D58'};
   const bl=[];let yy=0;s.L.forEach(l=>{if(t<l.ini-.75)return;const eu=l.quem==='ana'||l.eu;const ls=quebrar(l.texto,36,520,800,'NU');const h=ls.length*46+(eu?40:84);bl.push({l,eu,ls,h,y:yy});yy+=h+24});
   const tot=yy,area=ph-260;const off=Math.max(0,tot-area);
   cx.translate(0,-ph/2+220-off);
   bl.forEach(({l,eu,ls,h,y})=>{const typing=t<l.ini-.05;const k=typing?1:sp(t,l.ini-.05,12,7);const w=typing?140:Math.max(...ls.map(x=>medir(x,36,800,'NU')),eu?0:medir(NOMES[l.quem]||l.quem,28,900,'NU'))+60;
     const x=eu?pw/2-30-w:-pw/2+30;cx.save();cx.translate(x+(eu?w:0),y);cx.scale(k,k);cx.translate(-(eu?w:0),0);
     sh('rgba(42,38,34,.15)',0,4);rr(0,0,w,typing?70:h,24);cx.fillStyle=eu?'#D3F2E6':'#fff';cx.fill();nosh();
     if(typing){for(let i=0;i<3;i++){cx.fillStyle=`rgba(42,38,34,${.3+.4*Math.max(0,Math.sin(t*9-i))})`;cx.beginPath();cx.arc(42+i*28,35,9,0,7);cx.fill()}}
     else{let ty=30;if(!eu){txt(NOMES[l.quem]||l.quem,30,30,28,CORN[l.quem]||C.teal,{w:900,f:'NU',al:'left'});ty=74}
       ls.forEach((x,i)=>txt(x,30,ty+i*46,36,C.ink,{w:800,f:'NU',al:'left'}));txt(l.hora||'02:'+String(10+Math.floor(l.ini)%50).padStart(2,'0'),w-20,h-18,22,'rgba(42,38,34,.45)',{w:800,f:'NU',al:'right'})}
     cx.restore()});
   cx.restore();cx.restore();
   if(s.quando){const k=pop(t,s.ini-.15,.4);if(k){cx.save();cx.translate(W/2,250);cx.rotate(-.03);cx.scale(k,k);const w=medir(s.quando,50,900,'NU')+70;rr(-w/2,-42,w,84,24);cx.fillStyle=C.ink;cx.fill();txt(s.quando,0,4,50,C.gold,{w:900,f:'NU',ls:3});cx.restore()}}}},
});
