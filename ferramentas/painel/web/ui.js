// Componentes da tela v0.2: palavra, nota de fonte, régua, sparkline, cartões e estados.
// Nenhuma conta de valuation: compra, saída, P/C e central chegam prontos do contrato (`dados/contrato/`). A régua só
// converte um fator já pronto (P/C, 0,70×, 1,30×…) em posição na escala visual fixa que o próprio contrato declara.
import { h, s, num, mult, pct, rs, sinal, ok, TRACO, OCULTO } from './fmt.js';

// ------------------------------------------------------------------------------ palavra
export const PALAVRAS = {
  BARATA: { cls: 'barata', rot: 'BARATA' },
  RADAR: { cls: 'radar', rot: 'RADAR' },
  JUSTA: { cls: 'justa', rot: 'JUSTA' },
  CARA: { cls: 'cara', rot: 'CARA' },
  NAO_CONCLUSIVO: { cls: 'nc', rot: 'NÃO CONCLUSIVO' },
};
export const ORDEM_PALAVRAS = ['BARATA', 'RADAR', 'JUSTA', 'CARA', 'NAO_CONCLUSIVO'];

export function chip(palavra, tam = '') {
  const p = PALAVRAS[palavra];
  if (!p) return h('span', { class: `chip chip-erro ${tam}`, text: 'ERRO' });
  return h('span', { class: `chip chip-${p.cls} ${tam}` }, h('i', { class: `gl gl-${p.cls}`, 'aria-hidden': 'true' }), p.rot);
}

// ------------------------------------------------------------------------------ nota de fonte
const NOME_NOTA = {
  A: 'Nota A: oficial (CVM, B3)', B: 'Nota B: primária com ressalva',
  C: 'Nota C: agregador ou não conferido — menos firme', '—': 'Sem fonte',
};
export const firme = (n) => n === 'A' || n === 'B';

export function nota(n) {
  const k = n === 'A' || n === 'B' || n === 'C' ? n : 'x';
  return h('span', { class: `nt nt-${k}`, title: NOME_NOTA[k === 'x' ? '—' : k], 'aria-label': NOME_NOTA[k === 'x' ? '—' : k],
    text: k === 'x' ? TRACO : k });
}

/** Número com nota: cinza e sublinhado pontilhado quando a nota não embasa decisão (C ou sem fonte). */
export function valor(texto, n, { comNota = true, cls = '' } = {}) {
  const fraco = !firme(n) || texto === TRACO;
  return h('span', { class: `vn ${cls}` }, h('span', { class: fraco ? 'num v-w' : 'num', text: texto }), comNota ? nota(texto === TRACO ? '—' : n) : null);
}

/** Valor pessoal (R$ da carteira, peso): vira "•••" com Ocultar valores. */
export function pessoal(texto, ocultar, cls = '') {
  return ocultar
    ? h('span', { class: `num pes ${cls}`, 'aria-label': 'valor oculto', text: OCULTO })
    : h('span', { class: `num ${cls}`, text: texto });
}

export const RF_TEXTO = { Sim: 'sim', 'Não': 'não', Empate: 'empate' };
export function rendaFixa(linha) {
  const t = RF_TEXTO[linha.vence_rf] || TRACO;
  return h('span', { class: 'vn', title: linha.vence_rf_criterio ? `Supera a renda fixa? Critério: ${linha.vence_rf_criterio}` : 'sem fonte' },
    h('span', { class: t === TRACO ? 'v-w' : '', text: t }), nota(t === TRACO ? '—' : linha.vence_rf_nota));
}

// ------------------------------------------------------------------------------ régua
let ESCALA = null;   // [início, fim] da escala visual, em múltiplos do central — vem de hall.fatores.escala_regua
let FATORES = null;
export function configurar(fatores) { FATORES = fatores; ESCALA = fatores.escala_regua; }
export function fatores() { return FATORES; }

/** Fator (múltiplo do central, já pronto) → posição % na escala visual. Fora da escala: preso na borda, com sinal. */
export function posicao(f, borda = 2) {
  if (!ok(f) || !ESCALA) return null;
  const x = ((f - ESCALA[0]) / (ESCALA[1] - ESCALA[0])) * 100;
  const fora = f > ESCALA[1] ? '>' : f < ESCALA[0] ? '<' : null;      // "fora" pela escala, não pela borda visual
  return { x: Math.min(Math.max(x, borda), 100 - borda), fora };
}

const pctCss = (x) => `${x}%`;
export const foraCls = (p) => (!p || !p.fora ? '' : p.fora === '<' ? ' fora esq' : ' fora');

function semRegua(linha, cls) {
  const txt = linha.regua_suspensa ? 'faixas suspensas até veredito novo'
    : (linha.palavra === 'NAO_CONCLUSIVO' ? 'sem preço justo' : 'sem faixas');
  return h('div', { class: `reg-nc ${cls}`, text: txt });
}

export function temRegua(linha) {
  return ok(linha.compra) && ok(linha.saida) && ok(linha.central) && ok(linha.fator_saida) && !linha.regua_suspensa;
}

/** Régua mini: faixa de compra, losango do central, faixa de saída, traço do preço de hoje (P/C do motor). */
export function reguaMini(linha, { anterior = null, cls = '' } = {}) {
  if (!temRegua(linha)) return semRegua(linha, cls);
  const xc = posicao(FATORES.compra, 0).x, xs = posicao(linha.fator_saida, 0).x, x1 = posicao(1, 0).x;
  const p = posicao(linha.pc);
  const fraca = !firme(linha.central_nota);
  const rotulo = `Faixas: cotação ${ok(linha.pc) ? `${num(linha.pc)}× o preço justo` : 'sem preço'}; compra até ${mult(FATORES.compra)}, `
    + `venda a partir de ${mult(linha.fator_saida)} do preço justo${p && p.fora ? '; cotação fora da escala' : ''}`
    + (anterior !== null ? `; semana anterior ${num(anterior)}×` : '');
  const filhos = [
    h('i', { class: 'reg-z reg-zb', style: { left: '0', width: pctCss(xc) } }),
    h('i', { class: 'reg-z reg-zc', style: { left: pctCss(xs), right: '0' } }),
    h('i', { class: 'reg-t', style: { left: pctCss(xc) } }),
    h('i', { class: 'reg-t', style: { left: pctCss(xs) } }),
    h('i', { class: 'reg-c', style: { left: pctCss(x1) } }),
  ];
  const pa = anterior !== null ? posicao(anterior) : null;
  if (pa) filhos.push(h('i', { class: 'reg-o', style: { left: pctCss(pa.x) } }));
  if (p) filhos.push(h('i', { class: `reg-p${foraCls(p)}`, style: { left: pctCss(p.x) } }));
  return h('div', { class: `reg ${fraca ? 'fraca' : ''} ${cls}`, role: 'img', 'aria-label': rotulo, title: rotulo }, filhos);
}

/** Régua grande da Empresa ("Faixas de preço"): rótulos com os valores em R$ que o motor deu. */
export function reguaGrande(linha) {
  if (!temRegua(linha)) return semRegua(linha, 'grande');
  const xc = posicao(FATORES.compra, 0).x, xs = posicao(linha.fator_saida, 0).x, x1 = posicao(1, 0).x;
  const p = posicao(linha.pc, 1);
  const lb = (x, cima, valorTxt, rot) => h('span', {        // perto da borda o rótulo cresce para dentro
    class: `lb ${cima ? 'cima' : ''} ${x > 85 ? 'dir' : x < 15 ? 'esq' : ''}`,
    style: { left: pctCss(x) },
  }, h('b', { class: 'num', text: valorTxt }), rot);
  return h('div', {
    class: `bigreg ${firme(linha.central_nota) ? '' : 'fraca'}`, role: 'img',
    'aria-label': `Faixas: cotação ${rs(linha.preco)}, compra até ${rs(linha.compra)}, preço justo ${rs(linha.central)}, venda a partir de ${rs(linha.saida)}`,
  },
  h('i', { class: 'track' }),
  h('span', { class: 'z zb', style: { left: '0', width: pctCss(xc) }, text: 'zona de compra' }),
  h('span', { class: 'z zc', style: { left: pctCss(xs), right: '0' }, text: 'zona de venda' }),
  h('i', { class: 'tick', style: { left: pctCss(xc) } }),
  h('i', { class: 'tick', style: { left: pctCss(xs) } }),
  h('i', { class: 'cd', style: { left: pctCss(x1) } }),
  p ? h('i', { class: `px${foraCls(p)}`, style: { left: pctCss(p.x) } }) : null,
  p ? lb(p.x, true, num(linha.preco), p.fora ? `cotação · ${num(linha.pc)}× o preço justo, fora da escala` : 'cotação') : null,
  lb(xc, false, num(linha.compra), 'compra até'),
  lb(x1, false, num(linha.central), 'preço justo'),
  lb(xs, false, num(linha.saida), 'venda a partir de'));
}

/** Margem de segurança (Graham) = 1 − P/C, com o P/C pronto do motor. Positiva = cotação abaixo do preço justo. */
export function margem(linha) {
  const m = ok(linha.pc) ? 1 - linha.pc : null;
  const fraca = !firme(linha.central_nota);
  const tom = m === null ? '' : m >= 0 ? ' mg-pos' : ' mg-neg';
  return h('span', { class: `num mg${tom}${fraca ? ' v-w' : ''}`,
    title: m === null ? 'sem preço justo' : `Cotação ÷ preço justo = ${num(linha.pc)}× · margem = 1 − ${num(linha.pc)}${fraca ? ' · preço justo sem fonte A/B' : ''}`,
    text: sinal(m) });
}

// ------------------------------------------------------------------------------ gráficos pequenos
export function sparkline(serie) {
  if (!Array.isArray(serie) || serie.length < 2) return h('span', { class: 'v-w small', text: TRACO });
  const vs = serie.map((p) => p[1]);
  const mn = Math.min(...vs), mx = Math.max(...vs), amp = mx - mn || 1;
  const d = vs.map((v, i) => `${i ? 'L' : 'M'}${((i / (vs.length - 1)) * 84).toFixed(1)} ${(21 - ((v - mn) / amp) * 18).toFixed(1)}`).join(' ');
  return s('svg', { class: 'sp', viewBox: '0 0 84 24', role: 'img',
    'aria-label': `Cotação semanal de ${serie[0][0]} a ${serie[serie.length - 1][0]}: de ${num(vs[0])} a ${num(vs[vs.length - 1])}` },
  s('path', { d }));
}

// ------------------------------------------------------------------------------ blocos
export function cartao({ titulo, lead, id, cls = '' }, ...filhos) {
  return h('section', { class: `card ${cls}`, id, 'aria-labelledby': id ? `${id}-t` : null },
    titulo ? h('h2', { id: id ? `${id}-t` : null, text: titulo }) : null,
    lead ? h('p', { class: 'lead', text: lead }) : null, filhos);
}

export function stat(cap, ...valorEtc) {
  return h('div', { class: 'stat' }, h('div', { class: 'cap', text: cap }), h('div', { class: 'v' }, valorEtc));
}

export function kv(pares) {
  return h('div', { class: 'kv' }, pares.flatMap(([k, v]) => [h('span', { class: 'small', text: k }), h('span', { class: 'r' }, v)]));
}

export function vazio(titulo, texto, acao = null) {
  return h('div', { class: 'box vazio', role: 'status' }, h('b', { text: titulo }), texto ? h('p', { class: 'small', text: texto }) : null, acao);
}

export function carregando(linhas = 4) {
  return h('div', { class: 'box carregando', role: 'status', 'aria-label': 'Carregando' },
    Array.from({ length: linhas }, () => h('i', { class: 'ld' })));
}

export function faixaErro(texto) {
  return h('div', { class: 'banner', role: 'alert' }, h('span', { class: 'ico', 'aria-hidden': 'true', text: '!' }), h('span', { text: texto }));
}

export function faixaInfo(rotulo, itens) {
  if (!itens || !itens.length) return null;
  return h('details', { class: 'avisos' }, h('summary', { text: `${rotulo} (${itens.length})` }),
    h('ul', {}, itens.map((t) => h('li', { text: t }))));
}

export { num, mult, pct, rs, TRACO };
