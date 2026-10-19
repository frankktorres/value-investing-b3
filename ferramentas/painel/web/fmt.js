// Formatação pt-BR e construção de elementos. Dado entra só por textContent (nunca innerHTML).

const N2 = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export const TRACO = '—';

export function num(v) {
  return typeof v === 'number' && Number.isFinite(v) ? N2.format(v) : TRACO;
}

export function data(iso) {
  // "2026-10-02" → "02/10/2026"; outra coisa passa como veio
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || '');
  return m ? `${m[3]}/${m[2]}/${m[1]}` : (iso || TRACO);
}

export function h(tag, attrs, ...filhos) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k === 'text') el.textContent = v;
    else if (k === 'style') Object.assign(el.style, v);       // CSSOM: permitido pela CSP (sem style inline no HTML)
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? '' : String(v));
  }
  for (const f of filhos.flat()) {
    if (f === null || f === undefined || f === false) continue;
    el.append(f instanceof Node ? f : document.createTextNode(String(f)));
  }
  return el;
}

const NOME_NOTA = { A: 'Nota A: oficial (CVM, B3)', B: 'Nota B: primária com ressalva', C: 'Nota C: agregador ou não conferido — menos firme', '—': 'Sem fonte' };

export function nota(n) {
  const k = n === 'A' || n === 'B' || n === 'C' ? n : 'x';
  return h('span', { class: `nt nt-${k}`, title: NOME_NOTA[n] || NOME_NOTA['—'], text: k === 'x' ? TRACO : k });
}

export function firme(n) {
  return n === 'A' || n === 'B';
}

// palavra → classe do token
export const CLASSE = { BARATA: 'barata', RADAR: 'radar', JUSTA: 'justa', CARA: 'cara', 'NÃO CONCLUSIVO': 'nc' };

export function chip(palavra) {
  const cls = CLASSE[palavra] || 'erro';
  return h('span', { class: `chip chip-${cls}` }, h('i', { class: `gl gl-${cls}`, 'aria-hidden': 'true' }), palavra || 'ERRO');
}
