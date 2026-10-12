/* Mascote real do produto (copiado da página de vendas do Meu Cão Obedece) */
var E={};
var PELOS=[
 ['#F0B872','#D89A50','#FFEBD2'],['#E8DCC8','#C9B79A','#FFF6E8'],
 ['#C98A5A','#A66A3E','#F5DCC0'],['#8A7B6E','#6B5D52','#E5DCD2'],
 ['#3A332E','#26211D','#D9D0C6'],['#F5F0E6','#D8D0C0','#FFFCF5'],
 ['#D96B3A','#B04E22','#FFDCC2'],['#6B4A32','#4E3423','#E8CDB0'],
 ['#C0C6CC','#9AA1A8','#EEF1F4'],['#E8B4C4','#C98CA0','#FFF0F4']
];
var COLEIRAS=['#E8913C','#2F9C8A','#D9503A','#6C5CC4','#E5B23C','#3A82D9','#2A2622','#E86A9E'];
var ORELHAS=['Caída','Em pé','Curta','Dobrada'];
var CORPOS=[
 {n:'Médio',    larg:1.00, alt:1.00, cab:1.00},
 {n:'Salsicha', larg:1.20, alt:0.78, cab:0.94},
 {n:'Robusto',  larg:1.24, alt:1.02, cab:1.12},
 {n:'Pequeno',  larg:0.84, alt:0.82, cab:1.10},
 {n:'Esguio',   larg:0.80, alt:1.12, cab:0.90}
];
var FOCINHOS=[
 {n:'Médio',   w:37, h:27, y:101, nz:9.5},
 {n:'Curto',   w:30, h:23, y:98,  nz:9},
 {n:'Longo',   w:46, h:24, y:107, nz:8.5},
 {n:'Achatado',w:34, h:19, y:95,  nz:10}
];
var OLHARES=['Normal','Bravo','Sonolento','Alegre'];
var RABOS=['Curvo','Reto','Curto','Enrolado'];
var MANCHAS=['Liso','Malhado','Olho preto','Barriga clara'];

/* ═══════ MASCOTE ═══════ */
function orelhaPath(tipo,lado,cor,T){
  var s=lado, A=function(n){return n.toFixed(1)};
  if(tipo===1){ /* Em pé */
    return '<path d="M'+A(110+s*54)+' 48'+
      ' C'+A(110+s*58)+' 6 '+A(110+s*82)+' -4 '+A(110+s*88)+' 26'+
      ' C'+A(110+s*92)+' 54 '+A(110+s*78)+' 76 '+A(110+s*60)+' 78 Z"'+
      ' fill="'+cor+'" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
  }
  if(tipo===2){ /* Curta */
    return '<path d="M'+A(110+s*52)+' 46'+
      ' C'+A(110+s*74)+' 40 '+A(110+s*88)+' 56 '+A(110+s*84)+' 78'+
      ' C'+A(110+s*80)+' 94 '+A(110+s*60)+' 94 '+A(110+s*54)+' 78 Z"'+
      ' fill="'+cor+'" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
  }
  if(tipo===3){ /* Dobrada */
    return '<path d="M'+A(110+s*52)+' 44'+
      ' C'+A(110+s*78)+' 42 '+A(110+s*94)+' 62 '+A(110+s*86)+' 80'+
      ' C'+A(110+s*98)+' 92 '+A(110+s*92)+' 116 '+A(110+s*68)+' 122'+
      ' C'+A(110+s*58)+' 106 '+A(110+s*56)+' 68 '+A(110+s*52)+' 52 Z"'+
      ' fill="'+cor+'" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
  }
  /* Caída — longa, desce abaixo do queixo, por fora do crânio */
  return '<path d="M'+A(110+s*54)+' 42'+
    ' C'+A(110+s*84)+' 44 '+A(110+s*98)+' 76 '+A(110+s*92)+' 112'+
    ' C'+A(110+s*88)+' 136 '+A(110+s*66)+' 142 '+A(110+s*58)+' 124'+
    ' C'+A(110+s*64)+' 94 '+A(110+s*60)+' 62 '+A(110+s*54)+' 48 Z"'+
    ' fill="'+cor+'" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
}
function rabop(tipo,x,y,cor,T){
  /* nasce na garupa e vai para TRÁS (esquerda), afinando na ponta */
  var A=function(n){return n.toFixed(1)};
  if(tipo===1){ /* Reto — erguido para trás */
    return '<path d="M'+A(x+4)+' '+A(y+9)+
      ' C'+A(x-12)+' '+A(y+2)+' '+A(x-28)+' '+A(y-18)+' '+A(x-36)+' '+A(y-44)+
      ' L'+A(x-27)+' '+A(y-47)+
      ' C'+A(x-20)+' '+A(y-22)+' '+A(x-8)+' '+A(y-6)+' '+A(x+7)+' '+A(y-1)+' Z"'+
      ' fill="'+cor+'" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
  }
  if(tipo===2){ /* Curto — tocinho */
    return '<path d="M'+A(x+4)+' '+A(y+9)+
      ' C'+A(x-8)+' '+A(y+5)+' '+A(x-18)+' '+A(y-3)+' '+A(x-22)+' '+A(y-15)+
      ' L'+A(x-13)+' '+A(y-19)+
      ' C'+A(x-10)+' '+A(y-8)+' '+A(x-4)+' '+A(y-2)+' '+A(x+7)+' '+A(y-1)+' Z"'+
      ' fill="'+cor+'" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
  }
  if(tipo===3){ /* Enrolado — curva sobre a garupa */
    return '<path d="M'+A(x+4)+' '+A(y+8)+
      ' C'+A(x-16)+' '+A(y+4)+' '+A(x-33)+' '+A(y-10)+' '+A(x-31)+' '+A(y-28)+
      ' C'+A(x-30)+' '+A(y-40)+' '+A(x-16)+' '+A(y-44)+' '+A(x-11)+' '+A(y-34)+
      ' L'+A(x-19)+' '+A(y-30)+
      ' C'+A(x-21)+' '+A(y-35)+' '+A(x-24)+' '+A(y-32)+' '+A(x-23)+' '+A(y-26)+
      ' C'+A(x-22)+' '+A(y-14)+' '+A(x-10)+' '+A(y-4)+' '+A(x+7)+' '+A(y-1)+' Z"'+
      ' fill="'+cor+'" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
  }
  /* Curvo — padrão, sobe em arco para trás */
  return '<path d="M'+A(x+6)+' '+A(y+13)+
    ' C'+A(x-18)+' '+A(y+6)+' '+A(x-36)+' '+A(y-12)+' '+A(x-36)+' '+A(y-40)+
    ' L'+A(x-22)+' '+A(y-43)+
    ' C'+A(x-23)+' '+A(y-17)+' '+A(x-10)+' '+A(y-2)+' '+A(x+9)+' '+A(y+2)+' Z"'+
    ' fill="'+cor+'" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
}
function olhosp(tipo,T,tem,vivo){
  var s='';
  if(tem('oculosAviador')){
    s+='<path d="M58 58 L162 58" stroke="#E5B23C" stroke-width="5"/>';
    s+='<path d="M60 56 C60 42 106 42 106 58 C106 80 64 82 60 62 Z" fill="#2A3A55" stroke="#E5B23C" stroke-width="4.5" stroke-linejoin="round"/>';
    s+='<path d="M160 56 C160 42 114 42 114 58 C114 80 156 82 160 62 Z" fill="#2A3A55" stroke="#E5B23C" stroke-width="4.5" stroke-linejoin="round"/>';
    s+='<path d="M106 58 L114 58" stroke="#E5B23C" stroke-width="4.5"/>';
    s+='<path d="M68 54 L82 49 M122 52 L136 47" stroke="#FFFFFF" stroke-width="3.5" opacity=".6" stroke-linecap="round"/>';
    return s;
  }
  if(tipo===3){ /* Alegre — olhos fechados em arco */
    s+='<path d="M66 70 C75 54 93 54 102 70" fill="none" stroke="'+T+'" stroke-width="6" stroke-linecap="round"/>';
    s+='<path d="M118 70 C127 54 145 54 154 70" fill="none" stroke="'+T+'" stroke-width="6" stroke-linecap="round"/>';
    return s;
  }
  var ry = tipo===2 ? 11 : 19;   /* sonolento fecha um pouco */
  var rx = 16;
  var pr = tipo===2 ? 8 : 11;    /* pupila grande, como nas referências */
  var cy = tipo===2 ? 64 : 66;
  [[84,-1],[136,1]].forEach(function(e){
    var cx=e[0], L=e[1];
    s+='<ellipse cx="'+cx+'" cy="'+cy+'" rx="'+rx+'" ry="'+ry+'" fill="#FFFFFF" stroke="'+T+'" stroke-width="5"/>';
    s+='<circle cx="'+(cx+L*1.5)+'" cy="'+(cy+2)+'" r="'+pr+'" fill="'+T+'"/>';
    s+='<circle cx="'+(cx+L*1.5-3.5)+'" cy="'+(cy-3)+'" r="'+(pr*0.42).toFixed(1)+'" fill="#FFFFFF"/>';
    s+='<circle cx="'+(cx+L*1.5+3.5)+'" cy="'+(cy+5)+'" r="'+(pr*0.2).toFixed(1)+'" fill="#FFFFFF" opacity=".85"/>';
  });
  if(tipo===1){ /* Bravo — sobrancelha franzida */
    s+='<path d="M62 40 C72 34 90 38 98 46" fill="none" stroke="'+T+'" stroke-width="7" stroke-linecap="round"/>';
    s+='<path d="M158 40 C148 34 130 38 122 46" fill="none" stroke="'+T+'" stroke-width="7" stroke-linecap="round"/>';
  }
  if(tipo===2) s+='<path d="M68 56 L100 56 M120 56 L152 56" stroke="'+T+'" stroke-width="5" stroke-linecap="round"/>';
  if(tem('oculos')){
    s+='<circle cx="84" cy="'+cy+'" r="24" fill="none" stroke="'+T+'" stroke-width="5"/>';
    s+='<circle cx="136" cy="'+cy+'" r="24" fill="none" stroke="'+T+'" stroke-width="5"/>';
    s+='<path d="M108 '+cy+' L112 '+cy+'" stroke="'+T+'" stroke-width="5"/>';
  }
  return s;
}
function rabofrente(tipo,x,y,cor,T){
  var A=function(n){return n.toFixed(1)}, d;
  if(tipo===1)      d='M'+A(x)+' '+A(y)+' L'+A(x+34)+' '+A(y-46);
  else if(tipo===2) d='M'+A(x)+' '+A(y)+' C'+A(x+14)+' '+A(y-6)+' '+A(x+20)+' '+A(y-16)+' '+A(x+18)+' '+A(y-26);
  else if(tipo===3) d='M'+A(x)+' '+A(y)+' C'+A(x+30)+' '+A(y-4)+' '+A(x+42)+' '+A(y-28)+' '+A(x+24)+' '+A(y-38)+' C'+A(x+14)+' '+A(y-42)+' '+A(x+10)+' '+A(y-30)+' '+A(x+20)+' '+A(y-28);
  else              d='M'+A(x)+' '+A(y)+' C'+A(x+26)+' '+A(y-4)+' '+A(x+38)+' '+A(y-22)+' '+A(x+34)+' '+A(y-48);
  return '<path d="'+d+'" fill="none" stroke="'+T+'" stroke-width="19" stroke-linecap="round"/>'
       + '<path d="'+d+'" fill="none" stroke="'+cor+'" stroke-width="11" stroke-linecap="round"/>';
}
function mascote(op){
  op=op||{};
  function g(k,d){ return op[k]!==undefined?op[k]:(E[k]!==undefined?E[k]:d); }
  var p=PELOS[g('pelo',0)]||PELOS[0];
  var col=COLEIRAS[g('coleira',0)]||COLEIRAS[0];
  var or=g('orelha',0), cp=CORPOS[g('corpo',0)]||CORPOS[0];
  var fo=FOCINHOS[g('focinho',0)]||FOCINHOS[0];
  var ol=g('olhar',0), rb=g('rabo',0), mc=g('mancha',0);
  var itens=op.itens||[], vivo=!!op.vivo;
  var tem=function(id){return itens.indexOf(id)>=0};
  var T='#2A2622', escuro=p[1], A=function(n){return n.toFixed(1)};

  /* corpo sentado, de frente */
  var hw=50*cp.larg, CHAO=226, ty=CHAO-96*cp.alt, esc=cp.cab;
  var X=function(f){return A(110+hw*f)}, bh=CHAO-ty;
  var Y=function(f){return A(ty+bh*f)};

  function anim(tipo,vals,dur){
    if(!vivo) return '';
    return '<animateTransform attributeName="transform" attributeType="XML" type="'+tipo+
      '" values="'+vals+'" dur="'+dur+'" repeatCount="indefinite" calcMode="spline" '+
      'keyTimes="0;0.5;1" keySplines="0.42 0 0.58 1;0.42 0 0.58 1"/>';
  }

  var s='<svg viewBox="0 0 220 250" xmlns="http://www.w3.org/2000/svg">';
  if(tem('aura')){
    s+='<circle cx="110" cy="140" r="118" fill="#E5B23C" opacity="0.15"/>';
    s+='<circle cx="110" cy="140" r="98" fill="#E5B23C" opacity="0.13"/>';
  }
  if(tem('capa')) s+='<path d="M'+X(-0.9)+' '+Y(0.06)+' C'+X(-1.25)+' '+Y(0.5)+' '+X(-1.15)+' '+(CHAO+6)+' '+X(-0.95)+' '+(CHAO+8)+' L'+X(0.95)+' '+(CHAO+8)+' C'+X(1.15)+' '+(CHAO+6)+' '+X(1.25)+' '+Y(0.5)+' '+X(0.9)+' '+Y(0.06)+' Z" fill="#2C3E70" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
  s+='<ellipse cx="110" cy="'+(CHAO+10)+'" rx="'+A(hw*1.1)+'" ry="8" fill="'+T+'" opacity="0.09"/>';

  /* rabo ao lado, como na v8 */
  var rx0=+X(0.9), ry0=+Y(0.42);
  s+='<g>'+anim('rotate','-13 '+A(rx0)+' '+A(ry0)+';13 '+A(rx0)+' '+A(ry0)+';-13 '+A(rx0)+' '+A(ry0),'0.5s')
    + rabofrente(rb,rx0,ry0,escuro,T) + '</g>';

  /* tronco */
  s+='<g>'+anim('translate','0 0;0 -2.4;0 0','2.9s');
  s+='<path d="M110 '+Y(-0.06)
    +' C'+X(0.5)+' '+Y(-0.06)+' '+X(0.86)+' '+Y(0.22)+' '+X(0.92)+' '+Y(0.56)
    +' C'+X(0.98)+' '+Y(0.86)+' '+X(0.84)+' '+CHAO+' '+X(0.54)+' '+CHAO
    +' L'+X(-0.54)+' '+CHAO
    +' C'+X(-0.84)+' '+CHAO+' '+X(-0.98)+' '+Y(0.86)+' '+X(-0.92)+' '+Y(0.56)
    +' C'+X(-0.86)+' '+Y(0.22)+' '+X(-0.5)+' '+Y(-0.06)+' 110 '+Y(-0.06)+' Z" fill="'+p[0]+'" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
  if(mc===1){
    s+='<ellipse cx="'+X(-0.44)+'" cy="'+Y(0.46)+'" rx="'+A(hw*0.28)+'" ry="'+A(bh*0.18)+'" fill="'+escuro+'" opacity=".8"/>';
    s+='<ellipse cx="'+X(0.5)+'" cy="'+Y(0.7)+'" rx="'+A(hw*0.22)+'" ry="'+A(bh*0.14)+'" fill="'+escuro+'" opacity=".8"/>';
  }
  if(mc===3) s+='<ellipse cx="110" cy="'+Y(0.74)+'" rx="'+A(hw*0.6)+'" ry="'+A(bh*0.3)+'" fill="'+p[2]+'" opacity=".85"/>';

  if(tem('peitoral')){
    s+='<path d="M'+X(-0.58)+' '+Y(0.1)+' C'+X(-0.3)+' '+Y(0.28)+' '+X(0.3)+' '+Y(0.28)+' '+X(0.58)+' '+Y(0.1)
      +' L'+X(0.68)+' '+Y(0.3)+' C'+X(0.32)+' '+Y(0.5)+' '+X(-0.32)+' '+Y(0.5)+' '+X(-0.68)+' '+Y(0.3)+' Z" fill="#8A5A32" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
    s+='<circle cx="110" cy="'+Y(0.44)+'" r="6" fill="#F5C451" stroke="'+T+'" stroke-width="3"/>';
  }
  if(tem('mochila')){
    s+='<rect x="'+X(0.86)+'" y="'+Y(0.2)+'" width="30" height="38" rx="7" fill="#8A5A32" stroke="'+T+'" stroke-width="5"/>';
    s+='<rect x="'+A(+X(0.86)+6)+'" y="'+A(+Y(0.2)+9)+'" width="18" height="12" rx="3" fill="#C08850" stroke="'+T+'" stroke-width="4"/>';
  }
  if(tem('coleteTatico')){
    s+='<path d="M110 '+Y(0.02)+' C'+X(0.66)+' '+Y(0.02)+' '+X(0.9)+' '+Y(0.3)+' '+X(0.9)+' '+Y(0.6)+' L'+X(0.9)+' '+Y(0.92)+' L'+X(-0.9)+' '+Y(0.92)+' L'+X(-0.9)+' '+Y(0.6)+' C'+X(-0.9)+' '+Y(0.3)+' '+X(-0.66)+' '+Y(0.02)+' 110 '+Y(0.02)+' Z" fill="#4A5240" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
    s+='<path d="M110 '+Y(0.04)+' L110 '+Y(0.92)+'" stroke="'+T+'" stroke-width="4"/>';
    s+='<rect x="'+X(-0.7)+'" y="'+Y(0.48)+'" width="'+A(hw*0.42)+'" height="'+A(bh*0.22)+'" rx="4" fill="#5C6650" stroke="'+T+'" stroke-width="4"/>';
    s+='<rect x="'+X(0.28)+'" y="'+Y(0.48)+'" width="'+A(hw*0.42)+'" height="'+A(bh*0.22)+'" rx="4" fill="#5C6650" stroke="'+T+'" stroke-width="4"/>';
  }
  if(tem('insignia')) s+='<path d="M'+X(-0.24)+' '+Y(0.28)+' L'+X(0.24)+' '+Y(0.28)+' L'+X(0.24)+' '+Y(0.5)+' L110 '+Y(0.6)+' L'+X(-0.24)+' '+Y(0.5)+' Z" fill="#C9A227" stroke="'+T+'" stroke-width="4.5" stroke-linejoin="round"/>';
  if(tem('farda')){
    s+='<path d="M110 '+Y(0.02)+' C'+X(0.7)+' '+Y(0.02)+' '+X(0.92)+' '+Y(0.3)+' '+X(0.92)+' '+Y(0.62)+' L'+X(0.92)+' '+Y(0.96)+' L'+X(-0.92)+' '+Y(0.96)+' L'+X(-0.92)+' '+Y(0.62)+' C'+X(-0.92)+' '+Y(0.3)+' '+X(-0.7)+' '+Y(0.02)+' 110 '+Y(0.02)+' Z" fill="#1F3566" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
    s+='<path d="M'+X(-0.34)+' '+Y(0.04)+' L110 '+Y(0.44)+' L'+X(0.34)+' '+Y(0.04)+' L'+X(0.54)+' '+Y(0.14)+' L'+X(0.16)+' '+Y(0.68)+' L'+X(-0.16)+' '+Y(0.68)+' L'+X(-0.54)+' '+Y(0.14)+' Z" fill="#FFFFFF" stroke="'+T+'" stroke-width="4" stroke-linejoin="round"/>';
    s+='<path d="M110 '+Y(0.44)+' L'+X(0.2)+' '+Y(0.56)+' L'+X(0.12)+' '+Y(0.96)+' L'+X(-0.12)+' '+Y(0.96)+' L'+X(-0.2)+' '+Y(0.56)+' Z" fill="#8E2437" stroke="'+T+'" stroke-width="4" stroke-linejoin="round"/>';
  }
  if(tem('dragonas')){
    s+='<path d="M'+X(-1.28)+' '+Y(0.12)+' L'+X(-0.6)+' '+Y(0.02)+' L'+X(-0.56)+' '+Y(0.22)+' L'+X(-1.24)+' '+Y(0.32)+' Z" fill="#E5B23C" stroke="'+T+'" stroke-width="4.5" stroke-linejoin="round"/>';
    s+='<path d="M'+X(1.28)+' '+Y(0.12)+' L'+X(0.6)+' '+Y(0.02)+' L'+X(0.56)+' '+Y(0.22)+' L'+X(1.24)+' '+Y(0.32)+' Z" fill="#E5B23C" stroke="'+T+'" stroke-width="4.5" stroke-linejoin="round"/>';
  }
  if(tem('faixa')) s+='<path d="M'+X(-0.9)+' '+Y(0.2)+' L'+X(0.9)+' '+Y(0.84)+' L'+X(0.78)+' '+Y(1.0)+' L'+X(-0.98)+' '+Y(0.36)+' Z" fill="#E5B23C" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
  s+='</g>';

  /* patinhas da frente */
  if(tem('botas')){
    s+='<rect x="'+A(+X(-0.5)-14)+'" y="'+(CHAO-22)+'" width="28" height="26" rx="7" fill="#3E3A34" stroke="'+T+'" stroke-width="5"/>';
    s+='<rect x="'+A(+X(0.5)-14)+'" y="'+(CHAO-22)+'" width="28" height="26" rx="7" fill="#3E3A34" stroke="'+T+'" stroke-width="5"/>';
  } else {
    s+='<ellipse cx="'+X(-0.5)+'" cy="'+(CHAO-8)+'" rx="18" ry="11" fill="'+p[2]+'" stroke="'+T+'" stroke-width="5"/>';
    s+='<ellipse cx="'+X(0.5)+'" cy="'+(CHAO-8)+'" rx="18" ry="11" fill="'+p[2]+'" stroke="'+T+'" stroke-width="5"/>';
  }

  /* ═══ CABEÇA ═══ */
  var hy=ty-54*esc;
  s+='<g transform="translate(110,'+A(hy)+') scale('+A(esc)+') translate(-110,-76)">';
  s+='<g>'+anim('rotate','-2.4 110 128;2.4 110 128;-2.4 110 128','3.6s');
  s+='<g>'+anim('rotate','0 64 54;7 64 54;0 64 54','2.9s')+orelhaPath(or,-1,escuro,T)+'</g>';
  s+='<g>'+anim('rotate','0 156 54;-7 156 54;0 156 54','3.2s')+orelhaPath(or,1,escuro,T)+'</g>';
  s+='<ellipse cx="110" cy="76" rx="63" ry="57" fill="'+p[0]+'" stroke="'+T+'" stroke-width="5"/>';
  if(mc===2){
    var lum=parseInt(p[0].slice(1,3),16)*0.3+parseInt(p[0].slice(3,5),16)*0.59+parseInt(p[0].slice(5,7),16)*0.11;
    s+='<ellipse cx="84" cy="62" rx="29" ry="28" fill="'+(lum<110?p[2]:escuro)+'" opacity=".85"/>';
  }
  s+='<ellipse cx="110" cy="'+fo.y+'" rx="'+fo.w+'" ry="'+fo.h+'" fill="'+p[2]+'" stroke="'+T+'" stroke-width="5"/>';
  s+='<g>'+anim('translate','0 0;0 3;0 0','1.05s')
    +'<path d="M110 '+(fo.y+fo.h*0.42)+' C'+(110+fo.w*0.3)+' '+(fo.y+fo.h*0.42)+' '+(110+fo.w*0.32)+' '+(fo.y+fo.h*1.05)+' 110 '+(fo.y+fo.h*1.2)+' C'+(110-fo.w*0.32)+' '+(fo.y+fo.h*1.05)+' '+(110-fo.w*0.3)+' '+(fo.y+fo.h*0.42)+' 110 '+(fo.y+fo.h*0.42)+' Z" fill="#FF97A6" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/></g>';
  s+='<ellipse cx="110" cy="'+(fo.y-fo.h*0.42)+'" rx="'+(fo.w*0.38).toFixed(1)+'" ry="'+(fo.h*0.36).toFixed(1)+'" fill="'+T+'"/>';
  s+='<ellipse cx="'+(110-fo.w*0.14).toFixed(1)+'" cy="'+(fo.y-fo.h*0.56).toFixed(1)+'" rx="'+(fo.w*0.1).toFixed(1)+'" ry="'+(fo.h*0.09).toFixed(1)+'" fill="#FFFFFF" opacity=".5"/>';
  s+='<path d="M110 '+(fo.y-fo.h*0.06)+' L110 '+(fo.y+fo.h*0.22)
    +' M110 '+(fo.y+fo.h*0.22)+' C'+(110-fo.w*0.22)+' '+(fo.y+fo.h*0.6)+' '+(110-fo.w*0.46)+' '+(fo.y+fo.h*0.46)+' '+(110-fo.w*0.5)+' '+(fo.y+fo.h*0.16)
    +' M110 '+(fo.y+fo.h*0.22)+' C'+(110+fo.w*0.22)+' '+(fo.y+fo.h*0.6)+' '+(110+fo.w*0.46)+' '+(fo.y+fo.h*0.46)+' '+(110+fo.w*0.5)+' '+(fo.y+fo.h*0.16)+'" fill="none" stroke="'+T+'" stroke-width="4.5" stroke-linecap="round"/>';
  s+=olhosp(ol,T,tem,vivo);
  if(tem('capacete')){
    s+='<path d="M52 66 C52 18 168 18 168 66 L168 50 C168 6 52 6 52 50 Z" fill="#4A5240" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
    s+='<path d="M52 52 C52 12 168 12 168 52" fill="#4A5240" stroke="'+T+'" stroke-width="5"/>';
    s+='<rect x="100" y="10" width="20" height="14" rx="4" fill="#6E7A5E" stroke="'+T+'" stroke-width="4"/>';
  }
  if(tem('coroa')){
    s+='<path d="M64 32 L64 -8 L88 16 L110 -14 L132 16 L156 -8 L156 32 Z" fill="#F5C451" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
    s+='<circle cx="110" cy="12" r="6" fill="#8E2437" stroke="'+T+'" stroke-width="3"/>';
    s+='<path d="M64 28 L156 28" stroke="'+T+'" stroke-width="4"/>';
  }
  s+='</g></g>';

  /* coleira no pescoço */
  if(!tem('farda')){
    s+='<path d="M'+X(-0.72)+' '+Y(0.02)+' L'+X(0.72)+' '+Y(0.02)+' L'+X(0.72)+' '+Y(0.14)+' L'+X(-0.72)+' '+Y(0.14)+' Z" fill="'+col+'" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
    s+='<circle cx="110" cy="'+Y(0.24)+'" r="10" fill="#F5C451" stroke="'+T+'" stroke-width="5"/>';
  }
  if(tem('plaquinha')) s+='<path d="M'+X(-0.2)+' '+Y(0.16)+' L'+X(0.2)+' '+Y(0.16)+' L'+X(0.14)+' '+Y(0.36)+' L'+X(-0.14)+' '+Y(0.36)+' Z" fill="#F5C451" stroke="'+T+'" stroke-width="4.5" stroke-linejoin="round"/>';
  if(tem('bandana')) s+='<path d="M'+X(-0.74)+' '+Y(0.0)+' L'+X(0.74)+' '+Y(0.0)+' L110 '+Y(0.44)+' Z" fill="#C4443A" stroke="'+T+'" stroke-width="5" stroke-linejoin="round"/>';
  if(tem('apito')) s+='<path d="M110 '+Y(0.14)+' L110 '+Y(0.32)+'" stroke="'+T+'" stroke-width="4"/><rect x="98" y="'+Y(0.3)+'" width="24" height="15" rx="4" fill="#C0C4CC" stroke="'+T+'" stroke-width="4"/>';
  var med = tem('medOuro')?'#E5B23C':(tem('medPrata')?'#C0C4CC':(tem('medBronze')?'#C97F3F':null));
  if(med) s+=medalha(+X(0.42),+Y(0.42),med);
  s+='</svg>';
  return s;
}
function medalha(x,y,cor){
  var T='#2A2622';
  return '<path d="M'+(x-8)+' '+(y-22)+' L'+x+' '+(y-6)+' L'+(x+8)+' '+(y-22)+'" fill="#D9503A" stroke="'+T+'" stroke-width="4" stroke-linejoin="round"/>'+
    '<circle cx="'+x+'" cy="'+y+'" r="14" fill="'+cor+'" stroke="'+T+'" stroke-width="5"/>'+
    '<circle cx="'+x+'" cy="'+y+'" r="6" fill="none" stroke="'+T+'" stroke-width="2.5"/>';
}
function pataSVG(cor){
  return '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><g fill="'+(cor||'#E8913C')+'">'+
   '<ellipse cx="22" cy="42" rx="9" ry="12"/><ellipse cx="40" cy="28" rx="10" ry="13"/>'+
   '<ellipse cx="60" cy="28" rx="10" ry="13"/><ellipse cx="78" cy="42" rx="9" ry="12"/>'+
   '<ellipse cx="50" cy="68" rx="24" ry="21"/></g></svg>';
}

/* ═══════ APETRECHOS ═══════ */
var ITENS=[
 {d:1,id:'bandana',n:'Bandana',s:1},{d:2,id:'peitoral',n:'Peitoral de couro',s:1},
 {d:3,id:'plaquinha',n:'Plaquinha',s:1},{d:4,id:'mochila',n:'Mochila',s:1},
 {d:5,id:'oculos',n:'Óculos',s:1},{d:6,id:'medBronze',n:'Medalha de bronze',s:1},
 {d:7,id:'faixa',n:'Faixa de Aventureiro',s:1},
 {d:8,id:'coleteTatico',n:'Colete tático',s:2},{d:9,id:'bolsos',n:'Bolsos laterais',s:2},
 {d:10,id:'botas',n:'Botas',s:2},{d:11,id:'apito',n:'Apito de comando',s:2},
 {d:12,id:'capacete',n:'Capacete',s:2},{d:13,id:'medPrata',n:'Medalha de prata',s:2},
 {d:14,id:'insignia',n:'Insígnia de Guardião',s:2},
 {d:15,id:'farda',n:'Farda de almirante',s:3},{d:16,id:'dragonas',n:'Dragonas douradas',s:3},
 {d:17,id:'oculosAviador',n:'Óculos aviador',s:3},{d:18,id:'capa',n:'Capa de comando',s:3},
 {d:19,id:'medOuro',n:'Medalha de ouro',s:3},{d:20,id:'coroa',n:'Coroa',s:3},
 {d:21,id:'aura',n:'AURA LENDÁRIA',s:3}
];
var SKINS=[
 {s:1,nome:'Aventureiro',desc:'Semana 1 · Fundação',dias:7},
 {s:2,nome:'Guardião',desc:'Semana 2 · Controle',dias:14},
 {s:3,nome:'Lendário',desc:'Semana 3 · Vida Real',dias:21}
];
/* cada semana é um TRAJE curado — não a soma de tudo */
var VESTE={
 1:['peitoral','bandana','plaquinha','mochila','oculos'],
 2:['coleteTatico','capacete','botas','apito','insignia'],
 3:['farda','dragonas','oculosAviador','capa','coroa']
};
function medalhasAte(n){
  var r=[];
  if(n>=19) r.push('medOuro');
  else if(n>=13) r.push('medPrata');
  else if(n>=6) r.push('medBronze');
  if(n>=21) r.push('aura');
  return r;
}
function itensAte(n){
  if(n<=0) return [];
  var sem=Math.min(3,Math.ceil(n/7)), r=medalhasAte(n);
  for(var i=0;i<ITENS.length;i++)
    if(ITENS[i].d<=n && ITENS[i].s===sem && VESTE[sem].indexOf(ITENS[i].id)>=0) r.push(ITENS[i].id);
  return r;
}
function itensSkin(s){
  var r=VESTE[s].slice();
  r.push(s===3?'medOuro':(s===2?'medPrata':'medBronze'));
  if(s>=3) r.push('aura');
  return r;
}

