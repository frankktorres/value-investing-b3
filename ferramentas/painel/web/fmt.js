// Formatação pt-BR e construção de elementos. Dado entra só por textContent (nunca innerHTML).

const fmtCache = new Map();
function nf(casas) {
  if (!fmtCache.has(casas)) {
    fmtCache.set(casas, new Intl.NumberFormat('pt-BR', { minimumFractionDigits: casas, maximumFractionDigits: casas }));
  }
  return fmtCache.get(casas);
}

export const TRACO = '—';
export const OCULTO = '•••';
export const ok = (v) => typeof v === 'number' && Number.isFinite(v);

export function num(v, casas = 2) { return ok(v) ? nf(casas).format(v) : TRACO; }
export function pct(v, casas = 1) { return ok(v) ? `${nf(casas).format(v * 100)}%` : TRACO; }
export function mult(v, casas = 2) { return ok(v) ? `${nf(casas).format(v)}×` : TRACO; }
export function rs(v, casas = 2) { return ok(v) ? `R$ ${nf(casas).format(v)}` : TRACO; }
/** Percentual com sinal: 0.35 → "+35%"; -1.76 → "-176%". */
export function sinal(v, casas = 0) { return ok(v) ? `${v > 0 ? '+' : ''}${pct(v, casas)}` : TRACO; }

export function compacto(v) {
  // 5100 → "5,1k"; 950 → "950"
  if (!ok(v)) return TRACO;
  return Math.abs(v) >= 1000 ? `${nf(1).format(v / 1000)}k` : nf(0).format(v);
}

export function data(iso) {
  // "2026-10-02" → "02/10/2026"; outra coisa passa como veio
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || '');
  return m ? `${m[3]}/${m[2]}/${m[1]}` : (iso || TRACO);
}

export function diaMes(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || '');
  return m ? `${m[3]}/${m[2]}` : (iso || TRACO);
}

const MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
export function mes(iso) {
  // "2026-11" ou "2026-11-03" → "nov/26"
  const m = /^(\d{4})-(\d{2})/.exec(iso || '');
  return m ? `${MESES[Number(m[2]) - 1]}/${m[1].slice(2)}` : (iso || TRACO);
}

function montar(el, attrs, filhos, svg) {
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === 'class') el.setAttribute('class', v);
    else if (k === 'text') el.textContent = v;
    else if (k === 'style') Object.assign(el.style, v);       // CSSOM: permitido pela CSP (sem style inline no HTML)
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? '' : String(v));
  }
  for (const f of filhos.flat(Infinity)) {
    if (f === null || f === undefined || f === false) continue;
    el.append(f instanceof Node ? f : document.createTextNode(String(f)));
  }
  return el;
}

export function h(tag, attrs, ...filhos) { return montar(document.createElement(tag), attrs, filhos, false); }

const NS = 'http://www.w3.org/2000/svg';
export function s(tag, attrs, ...filhos) { return montar(document.createElementNS(NS, tag), attrs, filhos, true); }
