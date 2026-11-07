// Anúncio "Prova" do Meu Cão Obedece: dor → não é teimosia → depoimentos dublados → produto → preço → teste grátis.
import React from 'react';
import {AbsoluteFill, Audio, Easing, Img, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame} from 'remotion';
import T from './tempos.json';

type Linha = {ini: number; fim: number; pal: [string, number, number][]};
const TM = T as unknown as Record<string, Linha> & {_total: number};
export const MCO_DUR = Math.ceil(TM._total * 30);
const F = 'Poppins, sans-serif';
const C = {lar: '#F2A33A', esc: '#D96E1B', ama: '#FFC94A', cre: '#FFF7EE', ver: '#2A9D8F', dark: '#1E1A16', verm: '#E5484D'};
const S = staticFile;
const ease = Easing.bezier(0.16, 1, 0.3, 1);
const lin = (f: number, a: number, b: number, x: number, y: number, e = ease) => interpolate(f, [a, b], [x, y], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});
const sp = (f: number, d = 12, s = 140) => spring({frame: f, fps: 30, config: {damping: d, stiffness: s}});
const fr = (s: number) => Math.round(s * 30);
const L = (k: string) => TM[k];
// início (em frames) da palavra n que começa com `w` dentro da fala k
const em = (k: string, w: string, n = 0) => {
  const ps = L(k).pal.filter((p) => p[0].toLowerCase().startsWith(w.toLowerCase()));
  return fr((ps[n] ?? ps[0] ?? L(k).pal[0])[1]);
};

const Fontes = () => (
  <style>{[500, 600, 700, 800, 900].map((w) => `@font-face{font-family:Poppins;font-weight:${w};src:url(${S(`m/poppins-${w}.woff2`)}) format('woff2')}`).join('')}</style>
);

// cena com entrada seca (punch-in), sem fade de saída para não encavalar textos
const Cena: React.FC<{de: number; ate: number; children: React.ReactNode; bg?: string}> = ({de, ate, children, bg}) => {
  const f = useCurrentFrame();
  if (f < de || f >= ate) return null;
  const q = lin(f, de, de + 7, 0, 1);
  return <AbsoluteFill style={{background: bg, transform: `scale(${1.08 - 0.08 * q})`, filter: `blur(${(1 - q) * 10}px)`}}>{children}</AbsoluteFill>;
};

const Clip: React.FC<{src: string; de: number; ini?: number; zoom?: [number, number]; dur: number; pos?: string}> = ({src, de, ini = 0, zoom = [1.05, 1.18], dur, pos = 'center'}) => {
  const f = useCurrentFrame();
  const z = interpolate(f - de, [0, dur], zoom, {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <OffthreadVideo src={S(`m/${src}`)} muted startFrom={fr(ini)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: pos, transform: `scale(${z})`}} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(30,26,22,.35) 0%, rgba(30,26,22,0) 30%, rgba(30,26,22,0) 50%, rgba(30,26,22,.85) 100%)'}} />
    </AbsoluteFill>
  );
};

// legenda karaokê: mostra o trecho de até 4 palavras em volta da palavra falada
const Karaoke: React.FC<{k: string; top?: number; cor?: string; size?: number}> = ({k, top = 1340, cor = '#fff', size = 74}) => {
  const f = useCurrentFrame();
  const t = f / 30;
  const pal = L(k).pal;
  let i = pal.findIndex((p) => t < p[2] + 0.05);
  if (i < 0) i = pal.length - 1;
  if (t < pal[0][1] - 0.1) return null;
  const g = Math.floor(i / 4) * 4;
  const grupo = pal.slice(g, g + 4);
  return (
    <div style={{position: 'absolute', left: 60, right: 60, top, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0 22px', fontFamily: F, fontWeight: 900, fontSize: size, lineHeight: 1.12, letterSpacing: '-0.02em', textTransform: 'uppercase'}}>
      {grupo.map((p, j) => {
        const on = g + j === i;
        const q = sp(f - fr(p[1]), 14, 220);
        return <span key={j} style={{color: on ? C.ama : cor, opacity: t >= p[1] - 0.05 ? 1 : 0.35, transform: `scale(${on ? 1 + 0.06 * q : 1})`, display: 'inline-block', textShadow: '0 6px 0 rgba(0,0,0,.35), 0 0 30px rgba(0,0,0,.4)', WebkitTextStroke: '3px rgba(30,26,22,.85)', paintOrder: 'stroke fill'}}>{p[0]}</span>;
      })}
    </div>
  );
};

const Selo: React.FC<{f: number; txt: string; cor: string; rot?: number; size?: number; style?: React.CSSProperties}> = ({f, txt, cor, rot = -6, size = 64, style}) => {
  const q = sp(f, 9, 260);
  return <div style={{fontFamily: F, fontWeight: 900, fontSize: size, color: '#fff', background: cor, padding: '10px 30px', borderRadius: 18, border: '5px solid #fff', boxShadow: '0 12px 0 rgba(30,26,22,.25), 0 20px 40px rgba(0,0,0,.25)', transform: `rotate(${rot}deg) scale(${q * (1 + (1 - q) * 0.6)})`, opacity: q > 0.02 ? 1 : 0, whiteSpace: 'nowrap', ...style}}>{txt}</div>;
};

const Patas: React.FC<{op?: number}> = ({op = 0.07}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{overflow: 'hidden', opacity: op}}>
      {Array.from({length: 14}).map((_, i) => (
        <svg key={i} viewBox="0 0 100 100" style={{position: 'absolute', width: 120, left: (i * 263) % 1080 - 40, top: ((i * 389) % 1920) + Math.sin(f / 40 + i) * 12, transform: `rotate(${(i * 47) % 360}deg)`}}>
          <ellipse cx="50" cy="66" rx="22" ry="18" fill={C.esc} /><circle cx="24" cy="40" r="10" fill={C.esc} /><circle cx="42" cy="26" r="10" fill={C.esc} /><circle cx="60" cy="26" r="10" fill={C.esc} /><circle cx="77" cy="40" r="10" fill={C.esc} />
        </svg>
      ))}
    </AbsoluteFill>
  );
};

const FundoCreme: React.FC = () => (
  <AbsoluteFill style={{background: C.cre}}>
    <div style={{position: 'absolute', left: -300, top: -260, width: 900, height: 900, borderRadius: '50%', background: 'radial-gradient(circle, rgba(242,163,58,.35), transparent 65%)'}} />
    <div style={{position: 'absolute', right: -320, bottom: -300, width: 1000, height: 1000, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,201,74,.35), transparent 65%)'}} />
    <Patas />
  </AbsoluteFill>
);

const Aviso: React.FC<{escuro?: boolean}> = ({escuro}) => (
  <div style={{position: 'absolute', bottom: 70, left: 0, right: 0, textAlign: 'center', fontFamily: F, fontWeight: 600, fontSize: 26, color: escuro ? 'rgba(255,255,255,.75)' : 'rgba(30,26,22,.55)'}}>Resultados variam de cão para cão.</div>
);

// ---------- cenas ----------
const DORES: [string, string, number, string][] = [['Late', '33.mp4', 0, 'LATE PRA TUDO'], ['Pula', '51.mp4', 1, 'PULA EM QUEM CHEGA'], ['Faz', '11.mp4', 7, 'XIXI NA SALA'], ['Te', '33.mp4', 12, 'TE ARRASTA NA RUA']];

const Dores: React.FC = () => {
  const f = useCurrentFrame();
  const cortes = DORES.map(([w]) => em('n2', w));
  return (
    <>
      {DORES.map(([, src, ini, rot], i) => {
        const de = i === 0 ? fr(L('n2').ini) - 4 : cortes[i] - 3;
        const ate = i < 3 ? cortes[i + 1] - 3 : fr(L('n3').ini) - 2;
        return (
          <Cena key={i} de={de} ate={ate}>
            <Clip src={src} de={de} ini={ini} dur={ate - de} zoom={[1.0, 1.04]} />
            <div style={{position: 'absolute', top: 210, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
              <div style={{fontFamily: F, fontWeight: 800, fontSize: 30, color: '#fff', background: 'rgba(30,26,22,.65)', padding: '10px 22px', borderRadius: 99, letterSpacing: '0.14em'}}>PROBLEMA {i + 1}/4</div>
            </div>
            <div style={{position: 'absolute', top: 330, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}><Selo f={f - de - 2} txt={rot} cor={i % 2 ? C.esc : C.verm} rot={i % 2 ? 4 : -4} size={76} /></div>
          </Cena>
        );
      })}
    </>
  );
};

const Teimoso: React.FC = () => {
  const f = useCurrentFrame();
  const de = fr(L('n3').ini) - 2, nao = em('n3', 'Não'), ele = em('n3', 'Ele', 1), ate = fr(L('d1').ini) - 6;
  const tremor = f >= nao && f < nao + 10 ? Math.sin(f * 3) * 12 : 0;
  return (
    <Cena de={de} ate={ate}>
      <FundoCreme />
      {f < ele && (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', transform: `translateX(${tremor}px)`}}>
          <div style={{fontFamily: F, fontWeight: 700, fontSize: 58, color: C.dark, opacity: lin(f, de + 4, de + 14, 0, 1)}}>Será que ele é</div>
          <div style={{fontFamily: F, fontWeight: 900, fontSize: 170, color: C.dark, letterSpacing: '-0.04em', lineHeight: 1, opacity: lin(f, em('n3', 'teimoso') - 4, em('n3', 'teimoso') + 4, 0, 1), transform: `scale(${0.8 + 0.2 * sp(f - em('n3', 'teimoso'))})`, textDecoration: f >= nao ? `line-through ${C.verm} 18px` : 'none'}}>TEIMOSO?</div>
          <div style={{marginTop: 50}}>{f >= nao && <Selo f={f - nao} txt="NÃO É." cor={C.verm} rot={-8} size={130} />}</div>
        </AbsoluteFill>
      )}
      {f >= ele && (
        <AbsoluteFill style={{alignItems: 'center'}}>
          <div style={{marginTop: 240, width: 820, height: 980, borderRadius: 48, overflow: 'hidden', border: '8px solid #fff', boxShadow: '0 24px 0 rgba(217,110,27,.25), 0 40px 80px rgba(30,26,22,.25)', transform: `rotate(${lin(f, ele, ele + 12, 6, -2)}deg) scale(${sp(f - ele, 13, 150)})`}}>
            <OffthreadVideo src={S('m/59.mp4')} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
          </div>
          <div style={{position: 'absolute', top: 1300, left: 70, right: 70, textAlign: 'center', fontFamily: F, fontWeight: 800, fontSize: 70, lineHeight: 1.12, color: C.dark, letterSpacing: '-0.03em'}}>
            Ele só nunca <span style={{color: '#fff', background: C.lar, padding: '0 16px', borderRadius: 14, display: 'inline-block', transform: `rotate(-2deg) scale(${0.7 + 0.3 * sp(f - em('n3', 'entendeu'), 10, 220)})`}}>entendeu</span> o que você quer.
          </div>
        </AbsoluteFill>
      )}
    </Cena>
  );
};

const DEPS: {k: string; img: string; nome: string; cao: string; frase: string; recorte: number}[] = [
  {k: 'd1', img: 'dep2.jpg', nome: 'Adriana', cao: 'tutora do Theu', frase: 'Falo uma vez e ele obedece', recorte: 0.3},
  {k: 'd2', img: 'dep1.jpg', nome: 'Rafaella', cao: 'tutora da Xena', frase: 'Anda do meu lado sem puxar', recorte: 0.5},
  {k: 'd3', img: 'dep0.jpg', nome: 'Adriano', cao: 'tutor do Rex', frase: 'Parou de fazer xixi na sala', recorte: 0.35},
  {k: 'd4', img: 'dep4.jpg', nome: 'Hugo', cao: 'tutor da Rosquinha', frase: 'Resolvi tudo com R$ 37', recorte: 0.45},
];

const Onda: React.FC<{f: number; ativo: boolean; cor: string}> = ({f, ativo, cor}) => (
  <div style={{display: 'flex', alignItems: 'center', gap: 6, height: 50}}>
    {Array.from({length: 14}).map((_, i) => <div key={i} style={{width: 8, borderRadius: 4, background: cor, height: ativo ? 10 + Math.abs(Math.sin(f / 3 + i * 0.9)) * 40 : 10}} />)}
  </div>
);

const Provas: React.FC = () => {
  const f = useCurrentFrame();
  const de = fr(L('d1').ini) - 8, ate = fr(L('n4').ini) - 4;
  return (
    <Cena de={de} ate={ate}>
      <FundoCreme />
      <div style={{position: 'absolute', top: 150, left: 0, right: 0, textAlign: 'center', fontFamily: F}}>
        <div style={{fontWeight: 800, fontSize: 30, letterSpacing: '0.16em', color: C.esc}}>QUEM JÁ FEZ O PROTOCOLO</div>
        <div style={{fontSize: 54, color: C.ama, letterSpacing: 8, textShadow: '0 4px 0 rgba(217,110,27,.4)'}}>★★★★★</div>
      </div>
      {DEPS.map((d, i) => {
        const a = fr(L(d.k).ini) - (i === 0 ? 8 : 10);
        const b = i < 3 ? fr(L(DEPS[i + 1].k).ini) - 10 : ate;
        if (f < a || f >= b) return null;
        const q = sp(f - a, 14, 120);
        const falando = f / 30 >= L(d.k).ini && f / 30 <= L(d.k).fim;
        const t = f / 30;
        return (
          <AbsoluteFill key={d.k}>
            <div style={{position: 'absolute', left: 90, right: 90, top: 330, height: 640, borderRadius: 36, overflow: 'hidden', background: '#ece5dd', border: '6px solid #fff', boxShadow: '0 22px 0 rgba(217,110,27,.18), 0 40px 80px rgba(30,26,22,.22)', transform: `perspective(1400px) rotateY(${(1 - q) * (i % 2 ? -35 : 35)}deg) translateX(${(1 - q) * (i % 2 ? 300 : -300)}px) rotate(${i % 2 ? 1.5 : -1.5}deg)`, opacity: q}}>
              <Img src={S(`m/${d.img}`)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: `center ${d.recorte * 100}%`, transform: `scale(${1.02 + (f - a) * 0.0008})`}} />
            </div>
            <div style={{position: 'absolute', left: 70, right: 70, top: 1010, background: '#fff', borderRadius: 34, padding: '30px 36px', boxShadow: '0 18px 50px rgba(30,26,22,.15)', transform: `translateY(${(1 - sp(f - a - 6)) * 80}px)`, opacity: sp(f - a - 6)}}>
              <div style={{display: 'flex', alignItems: 'center', gap: 18}}>
                <div style={{width: 74, height: 74, borderRadius: '50%', background: `linear-gradient(135deg,${C.lar},${C.ama})`, color: '#fff', fontFamily: F, fontWeight: 900, fontSize: 36, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{d.nome[0]}</div>
                <div style={{fontFamily: F}}>
                  <div style={{fontWeight: 800, fontSize: 38, color: C.dark}}>{d.nome}</div>
                  <div style={{fontWeight: 600, fontSize: 26, color: '#8a7a68'}}>{d.cao}</div>
                </div>
                <div style={{marginLeft: 'auto'}}><Onda f={f} ativo={falando} cor={C.lar} /></div>
              </div>
              <div style={{marginTop: 18, fontFamily: F, fontWeight: 700, fontSize: 44, lineHeight: 1.25, color: C.dark}}>
                “{L(d.k).pal.map((p, j) => <span key={j} style={{color: t >= p[1] - 0.03 ? C.dark : 'rgba(30,26,22,.22)'}}>{p[0]} </span>)}”
              </div>
            </div>
            <div style={{position: 'absolute', top: 1560, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}><Selo f={f - fr(L(d.k).fim) + 12} txt={'✓ ' + d.frase} cor={C.ver} rot={i % 2 ? 2 : -2} size={42} /></div>
          </AbsoluteFill>
        );
      })}
      <Aviso />
    </Cena>
  );
};

const Fone: React.FC<{children: React.ReactNode; q: number}> = ({children, q}) => (
  <div style={{position: 'absolute', left: 250, top: 330, width: 580, height: 1180, borderRadius: 80, background: C.dark, padding: 18, boxShadow: '0 30px 0 rgba(217,110,27,.22), 0 60px 120px rgba(30,26,22,.35)', transform: `perspective(1600px) rotateY(${(1 - q) * -25}deg) rotateZ(${(1 - q) * 6}deg) translateY(${(1 - q) * 300}px)`, opacity: q}}>
    <div style={{width: '100%', height: '100%', borderRadius: 64, overflow: 'hidden', background: '#fff', position: 'relative'}}>{children}</div>
  </div>
);

const Produto: React.FC = () => {
  const f = useCurrentFrame();
  const de = fr(L('n4').ini) - 4, ate = fr(L('n5').ini) - 3;
  const teste = em('n4', 'teste'), descobre = em('n4', 'descobre'), segue = em('n4', 'segue');
  const q = sp(f - de, 14, 110);
  const chips: [string, number][] = [['📱 Teste de 1 minuto', teste], ['🔎 Diagnóstico na hora', descobre], ['📅 21 dias · 15 min/dia', segue]];
  return (
    <Cena de={de} ate={ate}>
      <FundoCreme />
      <div style={{position: 'absolute', top: 140, left: 0, right: 0, textAlign: 'center', fontFamily: F, fontWeight: 900, fontSize: 82, color: C.dark, letterSpacing: '-0.03em', transform: `scale(${sp(f - de, 12, 160)})`}}>Meu Cão <span style={{color: C.lar}}>Obedece</span></div>
      <Fone q={q}>
        {f < descobre ? <OffthreadVideo src={S('m/quiz_c.mp4')} muted startFrom={30} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top'}} />
          : <Img src={S('m/diagnostico.png')} style={{width: '100%', position: 'absolute', top: lin(f, descobre, descobre + 120, 0, -380)}} />}
      </Fone>
      {f >= segue && <Img src={S('m/site_mascote.png')} style={{position: 'absolute', left: -10, top: 1100, width: 330, transform: `rotate(-8deg) scale(${sp(f - segue, 9, 200)})`, filter: 'drop-shadow(0 20px 20px rgba(30,26,22,.25))'}} />}
      <div style={{position: 'absolute', right: 40, top: 560, display: 'flex', flexDirection: 'column', gap: 26, alignItems: 'flex-end'}}>
        {chips.map(([t, a], i) => {
          const c = sp(f - a, 11, 200);
          return <div key={t} style={{fontFamily: F, fontWeight: 800, fontSize: 36, color: C.dark, background: '#fff', border: `4px solid ${i === 2 ? C.lar : '#fff'}`, padding: '18px 26px', borderRadius: 24, boxShadow: '0 10px 0 rgba(217,110,27,.2), 0 18px 36px rgba(30,26,22,.18)', transform: `translateX(${(1 - c) * 400}px) rotate(${i % 2 ? 2 : -2}deg)`, opacity: c}}>{t}</div>;
        })}
      </div>
      <Karaoke k="n4" top={1580} cor={C.dark} size={56} />
    </Cena>
  );
};

const Preco: React.FC = () => {
  const f = useCurrentFrame();
  const de = fr(L('n5').ini) - 3, toca = em('n5', 'Toca');
  const v = Math.round(lin(f, de + 4, de + 26, 800, 37, Easing.out(Easing.cubic)));
  const checks = ['Pagamento único, sem mensalidade', '7 dias de garantia', 'Acesso na hora, no celular'];
  return (
    <Cena de={de} ate={MCO_DUR}>
      <FundoCreme />
      <div style={{position: 'absolute', top: 190, left: 0, right: 0, textAlign: 'center', fontFamily: F}}>
        <div style={{fontWeight: 700, fontSize: 40, color: '#8a7a68'}}>Adestrador presencial: <span style={{textDecoration: `line-through ${C.verm} 6px`}}>R$ 800</span></div>
        <div style={{fontWeight: 900, fontSize: 250, color: C.lar, letterSpacing: '-0.05em', lineHeight: 1.05, textShadow: `0 14px 0 ${C.esc}`, transform: `scale(${1 + (v === 37 ? 0.06 * Math.max(0, 1 - (f - de - 26) / 10) : 0)})`}}><span style={{fontSize: 110}}>R$</span>{v}</div>
        <div style={{fontWeight: 800, fontSize: 44, color: C.dark, marginTop: 6}}>ou 12x de R$ 3,64</div>
      </div>
      <div style={{position: 'absolute', top: 820, left: 120, right: 120, display: 'flex', flexDirection: 'column', gap: 22}}>
        {checks.map((t, i) => {
          const c = sp(f - de - 24 - i * 8, 12, 200);
          return <div key={t} style={{display: 'flex', alignItems: 'center', gap: 22, fontFamily: F, fontWeight: 700, fontSize: 42, color: C.dark, opacity: c, transform: `translateX(${(1 - c) * -120}px)`}}><span style={{width: 62, height: 62, borderRadius: '50%', background: C.ver, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: 36, flex: 'none'}}>✓</span>{t}</div>;
        })}
      </div>
      {f >= toca - 4 && (
        <div style={{position: 'absolute', top: 1230, left: 90, right: 90, transform: `scale(${sp(f - toca + 4, 9, 200) * (1 + 0.03 * Math.sin(f / 4))})`}}>
          <div style={{background: `linear-gradient(180deg,${C.lar},${C.esc})`, color: '#fff', fontFamily: F, fontWeight: 900, fontSize: 52, textAlign: 'center', padding: '36px 20px', borderRadius: 34, boxShadow: `0 14px 0 #a9520f, 0 30px 60px rgba(217,110,27,.45)`}}>Fazer o teste grátis →</div>
          <div style={{textAlign: 'center', marginTop: 26, fontFamily: F, fontWeight: 700, fontSize: 36, color: C.dark}}>Toca em <b style={{color: C.esc}}>Saiba mais</b> 👇</div>
          <div style={{position: 'absolute', right: 30, top: 70, fontSize: 120, transform: `translate(${lin(f, toca, toca + 14, 120, 0)}px,${lin(f, toca, toca + 14, 160, 0) + (f > toca + 20 ? Math.abs(Math.sin(f / 6)) * -16 : 0)}px)`, opacity: lin(f, toca, toca + 6, 0, 1)}}>👆</div>
        </div>
      )}
      <Aviso />
    </Cena>
  );
};

const Gancho: React.FC = () => {
  const f = useCurrentFrame();
  const ate = fr(L('n2').ini) - 4;
  return (
    <Cena de={0} ate={ate}>
      <Clip src="11.mp4" de={0} ini={0} dur={ate} zoom={[1.0, 1.05]} />
      <div style={{position: 'absolute', top: 230, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 18}}>
        {[0, 1, 2].map((i) => <div key={i} style={{fontFamily: F, fontWeight: 900, fontSize: 64, color: '#fff', background: C.verm, borderRadius: 20, padding: '4px 22px', transform: `rotate(${(i - 1) * 8}deg) scale(${sp(f - em('n1', 'repete') - i * 4, 8, 260)})`, boxShadow: '0 8px 0 rgba(0,0,0,.25)'}}>{['SENTA!', 'SENTA!!', 'SENTAAA!'][i]}</div>)}
      </div>
      {f >= em('n1', 'finge') && <div style={{position: 'absolute', top: 1170, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}><Selo f={f - em('n1', 'finge')} txt="🙉 IGNORADO" cor={C.dark} rot={5} size={70} /></div>}
      <Karaoke k="n1" />
    </Cena>
  );
};

export const McoProva: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: C.dark}}>
      <Fontes />
      <Gancho />
      <Dores />
      {f >= fr(L('n2').ini) - 4 && f < fr(L('n3').ini) - 2 && <Karaoke k="n2" top={1300} />}
      <Teimoso />
      <Provas />
      <Produto />
      <Preco />
      <Audio src={S('m/narracao.wav')} />
    </AbsoluteFill>
  );
};
