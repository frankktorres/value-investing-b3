// Tela Hall: uma palavra por empresa (a VIGENTE, do veredito gravado ou do golden) e a régua da doutrina.
// O traço é o preço de hoje (COTAHIST) e o P/C de hoje é informativo: nada aqui recalcula palavra.
import { h, num, data, nota, firme, chip, CLASSE, TRACO } from './fmt.js';

const ORDEM_PALAVRA = ['BARATA', 'RADAR', 'JUSTA', 'CARA', 'NÃO CONCLUSIVO'];
const NA_REGUA = {   // rótulos do monitor_semanal.alerta → texto neutro (não é ordem)
  '≤ COMPRA': 'no preço de compra ou abaixo',
  'perto da compra': 'até 10% acima da compra',
  '≥ SAÍDA': 'na saída ou acima',
  '': 'entre compra e saída',
  'sem palavra': 'sem régua (NÃO CONCLUSIVO)',
  'sem central': 'sem régua',
  'sem preço de hoje': 'sem preço de hoje',
  erro: 'erro ao montar',
};
const ESCALA = [0.5, 1.6];   // régua fixa: 50%..160% do central, igual em todas as linhas

const vista = { filtro: 'todas', ordem: 'pc', soAB: false };

function chave(e) { return e.erro ? 'erro' : (CLASSE[e.palavra] ? e.palavra : 'erro'); }

function ordenar(lista) {
  const fim = (v) => (v === null || v === undefined ? Infinity : v);
  const rank = (e) => { const i = ORDEM_PALAVRA.indexOf(e.palavra); return i < 0 ? 99 : i; };
  const por = {
    pc: (a, b) => fim(a.pc_hoje) - fim(b.pc_hoje) || a.tk.localeCompare(b.tk),
    tk: (a, b) => a.tk.localeCompare(b.tk),
    palavra: (a, b) => rank(a) - rank(b) || fim(a.pc_hoje) - fim(b.pc_hoje),
    data: (a, b) => (a.data_palavra || '9999').localeCompare(b.data_palavra || '9999') || a.tk.localeCompare(b.tk),
  };
  return [...lista].sort(por[vista.ordem] || por.pc);
}

function regua(e) {
  if (e.erro) return h('div', { class: 'reg-nc', text: 'sem régua: o relatório não montou' });
  if (e.compra === null || e.saida === null || !e.central) {
    return h('div', { class: 'reg-nc', text: e.palavra === 'NÃO CONCLUSIVO' ? 'sem central firme · só informativo' : 'sem régua' });
  }
  const [a, b] = ESCALA;
  const lo = e.central * a, hi = e.central * b;
  const pos = (x) => Math.max(0, Math.min(100, ((x - lo) / (hi - lo)) * 100));
  const pc = (x) => `${pos(x)}%`;
  const filhos = [
    h('div', { class: 'reg-z reg-zb', style: { left: '0', width: pc(e.compra) } }),
    h('div', { class: 'reg-z reg-zc', style: { left: pc(e.saida), right: '0' } }),
    h('div', { class: 'reg-t', style: { left: pc(e.compra) } }),
    h('div', { class: 'reg-t', style: { left: pc(e.saida) } }),
    h('div', { class: 'reg-c', style: { left: pc(e.central) } }),
  ];
  let rotulo = `${e.tk}: ${e.palavra}; compra ${num(e.compra)}, central ${num(e.central)}, saída ${num(e.saida)}`;
  if (e.preco_hoje) {
    const fora = e.preco_hoje > hi ? ' fora fora-dir' : (e.preco_hoje < lo ? ' fora fora-esq' : '');
    filhos.push(h('div', { class: `reg-p${fora}`, style: { left: `${Math.max(1, Math.min(99, pos(e.preco_hoje)))}%` } }));
    rotulo += `; preço de hoje ${num(e.preco_hoje)}${fora ? ' (fora da escala)' : ''}`;
  }
  return h('div', { class: 'reg', role: 'img', 'aria-label': rotulo, title: rotulo }, ...filhos);
}

function valor(v, n) {
  return h('span', { class: firme(n) ? null : 'v-w', text: num(v) });
}

function linha(e) {
  if (e.erro) {
    return h('div', { class: 'row erro', role: 'row' },
      h('div', { role: 'cell' }, h('span', { class: 'tk' }, h('b', { text: e.tk }), h('span', { text: e.origem }))),
      h('div', { role: 'cell' }, chip(null)),
      h('div', { role: 'cell', style: { gridColumn: '3 / -1' } }, h('div', { class: 'aviso', text: e.erro })));
  }
  const tags = [];
  if (e.na_carteira) tags.push(h('span', { class: 'tag', title: 'Ticker da carteira (carteira_tickers.json)', text: 'carteira' }));
  if (e.fora_do_hall) tags.push(h('span', { class: 'tag', title: 'Falha filtro de qualidade: a palavra é só referência', text: 'fora do hall' }));
  if (e.dossie) tags.push(h('span', { class: 'tag', title: 'Dossiê gravado: a palavra vigente é a do veredito', text: 'dossiê' }));
  return h('div', { class: 'row', role: 'row' },
    h('div', { role: 'cell' },
      h('a', { class: 'tk', href: `#/empresa/${e.tk}` }, h('b', { text: e.tk }), h('span', { text: e.nome, title: e.nome })),
      ...(e.avisos || []).map((a) => h('div', { class: 'aviso', text: a }))),
    h('div', { role: 'cell' }, chip(e.palavra),
      e.palavra_motor ? h('div', { class: 'small', title: 'Motor de hoje; a vigente só muda com veredito novo', text: `motor hoje: ${e.palavra_motor}` }) : null),
    h('div', { role: 'cell' }, regua(e)),
    h('div', { class: 'r num', role: 'cell' }, num(e.preco_hoje), e.preco_hoje ? nota('A') : null),
    h('div', { class: 'r num', role: 'cell' }, e.compra === null ? TRACO : valor(e.compra, e.nota_central)),
    h('div', { class: 'r num', role: 'cell', title: e.fonte_central || 'sem fonte' },
      valor(e.central, e.nota_central), nota(e.nota_central),
      h('div', { class: 'small', title: 'Métodos com valor que entram na mediana do central', text: `${e.n_central} no central` })),
    h('div', { class: 'r num', role: 'cell' }, e.saida === null ? TRACO : valor(e.saida, e.nota_central),
      e.saida === null ? null : h('div', { class: 'small', text: e.saida_exc ? 'exc. 1,50×' : '1,30×' })),
    h('div', { class: 'r num', role: 'cell', title: 'Preço de hoje ÷ central — informativo' }, h('b', { text: num(e.pc_hoje) })),
    h('div', { role: 'cell', class: 'small' }, NA_REGUA[e.situacao] ?? e.situacao),
    h('div', { class: 'small num', role: 'cell' }, data(e.data_palavra), h('div', {}, ...tags)));
}

export function renderHall(hall, busca, rerender) {
  const todas = hall.empresas;
  const contagem = {};
  for (const e of todas) contagem[chave(e)] = (contagem[chave(e)] || 0) + 1;
  const abas = ['todas', ...ORDEM_PALAVRA.filter((p) => contagem[p]), ...(contagem.erro ? ['erro'] : [])];
  if (!abas.includes(vista.filtro)) vista.filtro = 'todas';

  const q = (busca || '').toLocaleLowerCase('pt-BR');
  let lista = todas.filter((e) => vista.filtro === 'todas' || chave(e) === vista.filtro);
  if (vista.soAB) lista = lista.filter((e) => firme(e.nota_central));
  if (q) lista = lista.filter((e) => e.tk.toLocaleLowerCase('pt-BR').includes(q) || (e.nome || '').toLocaleLowerCase('pt-BR').includes(q));
  lista = ordenar(lista);

  const nHall = todas.filter((e) => !e.dossie).length;
  const nDossie = todas.length - nHall;
  const titulo = h('div', {},
    h('h1', { class: 'h1', text: 'Hall' }),
    h('p', { class: 'sub', text: `${todas.length} empresas (${nHall} do hall e ${nDossie} com dossiê). Uma palavra cada: a vigente — `
      + 'o dossiê gravado vence o hall. O traço na régua é o preço de hoje e o P/C de hoje é informativo; palavra nova só com '
      + 'veredito novo. Nada aqui é ordem de compra ou venda.' }));

  const abasEl = h('div', { class: 'tabs', role: 'group', 'aria-label': 'Filtrar por palavra' },
    ...abas.map((k) => {
      const n = k === 'todas' ? todas.length : contagem[k];
      return h('button', { class: 'tab', type: 'button', 'aria-pressed': String(vista.filtro === k),
        onclick: () => { vista.filtro = k; rerender(); } },
      k === 'todas' ? h('span', { class: 'chip chip-todas', text: 'TODAS' }) : chip(k === 'erro' ? null : k),
      h('span', {}, h('span', { class: 'n num', text: String(n) }),
        h('span', { class: 'p num', text: `${Math.round((n / todas.length) * 100)}%` })));
    }));
  const dist = h('div', { class: 'dist', role: 'img', 'aria-label': 'Distribuição das palavras' },
    ...abas.filter((k) => k !== 'todas').map((k) => h('div', {
      class: `seg-${k === 'erro' ? 'erro' : CLASSE[k]}`, title: `${k}: ${contagem[k]}`,
      style: { width: `${(contagem[k] / todas.length) * 100}%` } })));

  const ordem = h('select', { onchange: (ev) => { vista.ordem = ev.target.value; rerender(); } },
    ...[['pc', 'P/C de hoje (menor primeiro)'], ['palavra', 'Palavra'], ['tk', 'Ticker (A–Z)'], ['data', 'Palavra mais antiga']]
      .map(([v, t]) => h('option', { value: v, selected: vista.ordem === v, text: t })));
  const soAB = h('input', { type: 'checkbox', checked: vista.soAB, onchange: (ev) => { vista.soAB = ev.target.checked; rerender(); } });
  const barra = h('div', { class: 'toolbar' },
    h('label', {}, 'Ordenar por', ordem),
    h('label', { title: 'Só A/B embasa decisão' }, soAB, 'Só central com fonte A ou B'),
    h('span', { class: 'grow num', text: `Exibindo ${lista.length} de ${todas.length}` }));

  const cab = ['Empresa', 'Palavra', 'Régua · compra / central / saída', 'Preço hoje', 'Compra', 'Central', 'Saída', 'P/C hoje', 'Na régua', 'Palavra de'];
  const tabela = h('section', { class: 'tbl', 'aria-label': 'Hall de empresas' },
    h('div', { class: 'tbl-in', role: 'table' },
      h('div', { class: 'row th cap', role: 'row' },
        ...cab.map((c, i) => h('div', { role: 'columnheader', class: i >= 3 && i <= 7 ? 'r' : null, text: c }))),
      ...(lista.length ? lista.map(linha) : [h('div', { class: 'vazio', text: 'Nenhuma empresa com esse filtro.' })])),
    legenda());
  return [titulo, h('div', {}, abasEl, dist), barra, tabela];
}

function legenda() {
  const mini = h('span', { class: 'mini', 'aria-hidden': 'true' },
    h('span', { class: 'reg-z reg-zb', style: { left: '0', width: '18px' } }),
    h('span', { class: 'reg-t', style: { left: '18px' } }),
    h('span', { class: 'reg-c', style: { left: '29px' } }),
    h('span', { class: 'reg-t', style: { left: '45px' } }),
    h('span', { class: 'reg-z reg-zc', style: { left: '45px', right: '0' } }),
    h('span', { class: 'reg-p', style: { left: '12px' } }));
  return h('div', { class: 'legend' },
    h('span', { class: 'it' }, mini, 'faixa de compra · central (losango) · faixa de saída · ', h('b', { text: 'traço = preço de hoje' }),
      ' (escala 50%–160% do central; compra 0,70×, saída 1,30× ou 1,50× com exceção de qualidade)'),
    h('span', { class: 'it' }, nota('A'), 'oficial (CVM, B3)'),
    h('span', { class: 'it' }, nota('B'), 'primária com ressalva'),
    h('span', { class: 'it' }, nota('C'), 'agregador ou não conferido · ', h('span', { class: 'v-w', text: 'menos firme' })),
    h('span', { class: 'it' }, nota('—'), 'sem fonte'),
    h('span', { class: 'it small', text: 'Só A e B embasam decisão.' }));
}
