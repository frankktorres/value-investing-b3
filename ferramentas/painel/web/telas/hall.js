// Hall: uma palavra por empresa (a VIGENTE, do veredito gravado ou do golden) e a régua da doutrina.
// O traço é o preço de hoje (COTAHIST) e o P/C de hoje é informativo: nada aqui recalcula palavra.
import { h, num, pct, mult, TRACO } from '../fmt.js';
import {
  PALAVRAS, ORDEM_PALAVRAS, chip, nota, valor, pessoal, firme, rendaFixa, reguaMini, sparkline, vazio, faixaErro,
} from '../ui.js';

const ABAS = [{ id: 'todas', rot: 'TODAS' }, ...ORDEM_PALAVRAS.map((p) => ({ id: p, rot: PALAVRAS[p].rot }))];
const ORDENS = [
  { id: 'pc', rot: 'P/C (menor primeiro)' },
  { id: 'yield', rot: 'DY sustentável (maior primeiro)' },
  { id: 'ticker', rot: 'Ticker' },
  { id: 'velho', rot: 'Dado mais velho' },
];
const COLS = ['Empresa', 'Palavra', 'Régua', 'Preço R$', 'Compra', 'Central', 'Saída', 'P/C', 'DY sust.', 'Renda fixa', 'Preço 12m', 'Carteira'];
const DIREITA = new Set([3, 4, 5, 6, 7, 8, 11]);

function ordenar(lista, ordem) {
  const fim = (v) => (typeof v === 'number' ? v : Infinity);
  const dy = (e) => (typeof e.yield_sust === 'number' ? e.yield_sust : -Infinity);   // sem DY no fim
  const por = {
    pc: (a, b) => fim(a.pc) - fim(b.pc) || a.ticker.localeCompare(b.ticker),
    yield: (a, b) => dy(b) - dy(a) || a.ticker.localeCompare(b.ticker),
    ticker: (a, b) => a.ticker.localeCompare(b.ticker),
    velho: (a, b) => (b.dias_defasagem ?? -1) - (a.dias_defasagem ?? -1) || a.ticker.localeCompare(b.ticker),
  };
  return [...lista].sort(por[ordem] || por.pc);
}

function filtrar(empresas, vista, busca) {
  const q = busca.toLowerCase();
  return empresas.filter((e) => (vista.filtro === 'todas' || e.palavra === vista.filtro)
    && (!vista.soAB || firme(e.central_nota))
    && (!q || e.ticker.toLowerCase().includes(q) || (e.nome || '').toLowerCase().includes(q)));
}

function celula(i, ...filhos) {
  return h('div', { role: 'cell', class: `c c${i}${DIREITA.has(i) ? ' r' : ''}` }, filhos);
}

function linha(e, c) {
  const cart = c.carteiraPorTk[e.ticker];
  const fracoCentral = !firme(e.central_nota);
  const sub = (txt) => h('span', { class: 'sb', text: txt });
  const nomeLinha = [e.nome || '', e.setor, e.origem].filter(Boolean).join(' · ');
  const tags = [
    e.velho ? h('span', { class: 'tag', title: `Último pregão há ${e.dias_defasagem} dias (mais de ${c.estado.hall.dias_velho})`, text: 'velho' }) : null,
    e.fora_do_hall ? h('span', { class: 'tag n', title: 'Falha o filtro de qualidade: a palavra é só referência', text: 'fora do hall' }) : null,
  ];
  if (e.erro) {
    return h('div', { role: 'row', class: 'row erro' },
      celula(0, h('a', { class: 'tk', href: `#/empresa/${e.ticker}` }, h('b', { text: e.ticker }), h('span', { text: 'não montou' }))),
      celula(1, chip(null)),
      h('div', { role: 'cell', class: 'c span-erro small', text: e.erro }));
  }
  return h('div', { role: 'row', class: `row${e.velho ? ' velho' : ''}` },
    celula(0, h('a', { class: 'tk', href: `#/empresa/${e.ticker}` }, h('b', { text: e.ticker }), h('span', { class: 'dim', text: nomeLinha })), ...tags),
    celula(1, chip(e.palavra), e.palavra_motor ? sub(`motor hoje: ${PALAVRAS[e.palavra_motor] ? PALAVRAS[e.palavra_motor].rot : e.palavra_motor}`) : null),
    celula(2, reguaMini(e)),
    celula(3, valor(num(e.preco), e.preco_nota)),
    celula(4, h('span', { class: `num dim${fracoCentral ? ' v-w' : ''}`, text: num(e.compra) })),
    celula(5, e.regua_suspensa
      ? [h('span', { class: 'v-w', text: TRACO }), sub('régua suspensa')]
      : [valor(num(e.central), e.central_nota), sub(`${e.metodos_central} de ${e.metodos_total} métodos`)]),
    celula(6, h('span', { class: `num dim${fracoCentral ? ' v-w' : ''}`, text: num(e.saida) }),
      e.fator_saida ? sub(e.fator_saida > c.estado.hall.fatores.saida ? `exc. ${mult(e.fator_saida)}` : mult(e.fator_saida)) : null),
    celula(7, h('b', { class: `num${fracoCentral ? ' v-w' : ''}`, text: num(e.pc) })),
    celula(8, valor(pct(e.yield_sust), e.yield_nota)),
    celula(9, rendaFixa(e)),
    celula(10, sparkline(e.serie_12m)),
    celula(11, cart ? pessoal(pct(cart.peso), c.ocultar) : h('span', { class: 'small', text: TRACO })));
}

function cabecalho() {
  return h('div', { role: 'row', class: 'row th' }, COLS.map((t, i) => h('div', { role: 'columnheader', class: `cap c c${i}${DIREITA.has(i) ? ' r' : ''}`, text: t })));
}

function legenda() {
  const amostra = h('div', { class: 'reg leg', 'aria-hidden': 'true' },
    h('i', { class: 'reg-z reg-zb', style: { left: '0', width: '30%' } }), h('i', { class: 'reg-c', style: { left: '50%' } }),
    h('i', { class: 'reg-z reg-zc', style: { left: '72%', right: '0' } }), h('i', { class: 'reg-p', style: { left: '20%' } }));
  const f = c_fatores();
  return h('div', { class: 'legend' },
    h('span', { class: 'it' }, amostra, h('span', {}, 'faixa de compra · central · faixa de saída · ', h('b', { text: 'traço = preço de hoje' }),
      ` (escala ${pct(f.escala_regua[0], 0)}–${pct(f.escala_regua[1], 0)} do central; compra ${mult(f.compra)}, saída ${mult(f.saida)} ou ${mult(f.saida_qualidade)} com exceção de qualidade)`)),
    h('span', { class: 'it' }, nota('A'), 'oficial (CVM, B3)'),
    h('span', { class: 'it' }, nota('B'), 'primária com ressalva'),
    h('span', { class: 'it' }, nota('C'), 'agregador · ', h('span', { class: 'v-w', text: 'menos firme' })),
    h('span', { class: 'it' }, nota('—'), 'sem fonte'),
    h('span', { class: 'it small', text: 'Só A e B embasam decisão.' }));
}

let FAT = null;
const c_fatores = () => FAT;

export function telaHall(c) {
  const hl = c.estado.hall;
  FAT = hl.fatores;
  const vista = c.estado.hallVista;
  const todas = hl.empresas;
  const cont = { todas: todas.length };
  for (const p of ORDEM_PALAVRAS) cont[p] = todas.filter((e) => e.palavra === p).length;

  const abas = h('div', { class: 'tabs', role: 'group', 'aria-label': 'Filtrar por palavra' }, ABAS.map((a) => h('button', {
    type: 'button', class: `tab tab-${a.id === 'todas' ? 'todas' : PALAVRAS[a.id].cls}`, 'aria-pressed': String(vista.filtro === a.id),
    onclick: () => { vista.filtro = vista.filtro === a.id && a.id !== 'todas' ? 'todas' : a.id; c.render(); },
  },
  a.id === 'todas' ? h('span', { class: 'cap', text: 'TODAS' }) : chip(a.id),
  h('span', {}, h('span', { class: 'n num', text: String(cont[a.id]) }),
    a.id === 'todas' ? null : h('span', { class: 'p', text: pct(cont[a.id] / cont.todas, 0) })))));

  const dist = h('div', { class: 'dist', role: 'img', 'aria-label': ORDEM_PALAVRAS.map((p) => `${PALAVRAS[p].rot} ${cont[p]}`).join(', ') },
    ORDEM_PALAVRAS.filter((p) => cont[p]).map((p) => h('i', { class: `seg seg-${PALAVRAS[p].cls}`, style: { flexGrow: String(cont[p]) }, title: `${PALAVRAS[p].rot}: ${cont[p]}` })));

  const lista = ordenar(filtrar(todas, vista, c.estado.busca), vista.ordem);

  const toolbar = h('div', { class: 'toolbar' },
    h('label', {}, 'Ordenar por', h('select', {
      onchange: (ev) => { vista.ordem = ev.target.value; c.render(); },
    }, ORDENS.map((o) => h('option', { value: o.id, selected: vista.ordem === o.id, text: o.rot })))),
    h('label', {}, h('input', { type: 'checkbox', checked: vista.soAB, onchange: (ev) => { vista.soAB = ev.target.checked; c.render(); } }),
      'Só central com fonte A ou B'),
    h('span', { class: 'grow', text: `Exibindo ${lista.length} de ${todas.length}` }));

  const corpo = lista.length
    ? lista.map((e) => linha(e, c))
    : [vazio('Nenhuma empresa com esse filtro.', c.estado.busca ? `Busca: "${c.estado.busca}".` : 'Tente tirar "Só central com fonte A ou B" ou trocar a aba.',
      h('button', { type: 'button', class: 'btn', onclick: () => { Object.assign(vista, { filtro: 'todas', soAB: false }); c.estado.busca = ''; document.getElementById('busca').value = ''; c.render(); }, text: 'Limpar filtros' }))];

  const nos = [
    h('div', {}, h('h1', { class: 'h1', text: 'Hall' }),
      h('p', { class: 'sub', text: `${todas.length} empresas, uma palavra cada. A palavra compara o preço com a régua: compra, central (dos métodos marcados como central) e saída. Não é recomendação.` })),
    ...hl.avisos.map((a) => faixaErro(a)),
    h('div', { class: 'tabs-wrap' }, abas, dist),
    toolbar,
    h('div', { class: 'tbl' }, h('div', { class: 'tbl-in', role: 'table', 'aria-label': 'Hall: empresas, palavra e régua', 'aria-rowcount': String(lista.length + 1) },
      cabecalho(), h('div', { class: 'scroll', role: 'rowgroup' }, corpo)), legenda()),
  ];
  return { contexto: `Hall · ${todas.length} empresas`, nos };
}
