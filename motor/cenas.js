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
   if(s.carimbo)carimbo(s.carimbo,W/2-150,1290,96,C.red,C.cream,t,s.kCar,-.12)}},
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
