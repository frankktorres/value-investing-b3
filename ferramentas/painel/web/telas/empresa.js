// Empresa: relatório de um ticker como o motor gravou (contrato v0.2). Régua, métodos, sensibilidade pré-calculada,
// premissas, qualitativo, riscos, proventos e fontes. Nada é recalculado: a posição no eixo é só leitura visual.
import { h, num, pct, mult, rs, data, ok, TRACO } from '../fmt.js';
import {
  chip, nota, valor, pessoal, firme, rendaFixa, reguaGrande, posicao, foraCls, temRegua, cartao, stat, kv, vazio,
  carregando, faixaErro, faixaInfo, fatores, PALAVRAS,
} from '../ui.js';

const SECOES = [
  ['valuation', 'Valuation'], ['sensibilidade', 'Sensibilidade'], ['premissas', 'Premissas'],
  ['qualitativo', 'Qualitativo'], ['riscos', 'Riscos'], ['proventos', 'Proventos'], ['fontes', 'Fontes'],
];

function fmtUnidade(v, unidade) {
  if (typeof v === 'string') return v;
  if (unidade === 'R$') return num(v);
  if (unidade === '%') return pct(v);
  if (unidade === 'x') return mult(v);
  return ok(v) ? num(v, Number.isInteger(v) ? 0 : 2) : TRACO;
}

function cabecalho(cab, c) {
  const flags = [
    cab.fora_do_hall ? h('span', { class: 'tag n', text: 'fora do hall' }) : null,
    cab.velho ? h('span', { class: 'tag', text: `velho · ${cab.dias_defasagem} d` }) : null,
  ];
  return h('div', { class: 'head' },
    h('div', { class: 'id' },
      h('div', { class: 'tl' }, h('span', { class: 'tkr', text: cab.ticker }), h('span', { class: 'nome', text: cab.nome || '' })),
      h('div', { class: 'meta' }, chip(cab.palavra, 'lg'),
        h('span', { text: `${cab.origem} · palavra de ${data(cab.data_palavra)} · pregão ${data(cab.ultimo_pregao)}` }), flags)),
    h('div', { class: 'stats' },
      stat('Preço', valor(num(cab.preco), cab.preco_nota), h('small', { text: 'R$' })),
      stat('Central', cab.regua_suspensa ? h('span', { class: 'v-w', text: TRACO }) : valor(num(cab.central), cab.central_nota), h('small', { text: 'R$' })),
      stat('P/C', h('span', { class: `num${firme(cab.central_nota) ? '' : ' v-w'}`, text: num(cab.pc) })),
      stat('DY sust.', valor(pct(cab.yield_sust), cab.yield_nota)),
      stat('Renda fixa', rendaFixa(cab))));
}

function cardRegua(cab) {
  const f = fatores();
  return h('section', { class: 'card', id: 'regua', 'aria-label': 'Régua' },
    h('div', { class: 'cap', text: `Régua · R$ por ação · compra ${mult(f.compra)} e saída ${mult(f.saida)} do central (${mult(f.saida_qualidade)} com exceção de qualidade)` }),
    h('div', { class: 'xs' }, h('div', { style: { minWidth: '560px', paddingTop: '22px' } }, reguaGrande(cab))),
    cab.palavra_motor ? h('p', { class: 'small', text: `O motor hoje diz ${PALAVRAS[cab.palavra_motor] ? PALAVRAS[cab.palavra_motor].rot : cab.palavra_motor}; a palavra vigente só muda com veredito novo.` }) : null);
}

// ------------------------------------------------------------------------------ valuation por método
function linhasVerticais(cab) {
  const f = fatores();
  const v = (fat, cls) => { const p = posicao(fat, 0); return p ? h('i', { class: `vl ${cls}`, style: { left: `${p.x}%` } }) : null; };
  const regua = temRegua(cab);                          // sem compra/saída do motor (NÃO CONCLUSIVO): só o central
  return [regua ? v(f.compra, '') : null, v(1, 'c'), regua ? v(cab.fator_saida, '') : null, regua && ok(cab.pc) ? v(cab.pc, 'p') : null];
}

function linhaMetodo(m, cab, comEixo) {
  const plot = comEixo ? h('div', { class: 'pl' }, linhasVerticais(cab), (() => {
    if (!ok(m.base)) return null;
    const p = posicao(m.base / cab.central, 1);   // posição visual do valor do método na escala do central
    return p ? h('i', { class: `bdot${m.entra_no_central ? '' : ' inf'}${foraCls(p)}`, style: { left: `${p.x}%` },
      title: `${m.nome}: ${rs(m.base)}${p.fora ? ' (fora da escala)' : ''}` }) : null;
  })()) : h('div', { class: 'pl' });
  const fraco = !firme(m.nota) || !ok(m.base);
  return h('div', { class: 'mrow' },
    h('div', { class: 'nm' }, h('b', { text: m.nome }), nota(ok(m.base) ? m.nota : '—'),
      h('span', { class: 'sb', title: m.descricao || m.obs, text: m.descricao || m.obs || '' })),
    plot,
    h('div', { class: 'val' }, h('b', { class: `num${fraco ? ' v-w' : ''}`, text: num(m.base) }),
      h('span', { text: ok(m.base) ? (ok(m.baixo) && ok(m.alto) ? `${num(m.baixo)}–${num(m.alto)}` : 'faixa: sem fonte') : (m.obs || 'sem valor') })));
}

function cardValuation(emp) {
  const cab = emp.cabecalho;
  const comEixo = temRegua(cab) || (ok(cab.central) && !cab.regua_suspensa);
  const centrais = emp.metodos.filter((m) => m.entra_no_central);
  const infos = emp.metodos.filter((m) => !m.entra_no_central);
  const f = fatores();
  const eixo = comEixo ? h('div', { class: 'pl' },
    ...linhasVerticais(cab),
    ...(temRegua(cab) ? [[cab.pc, 'hoje'], [f.compra, 'compra'], [1, 'central'], [cab.fator_saida, 'saída']] : [[1, 'central']]).map(([fat, rot]) => {
      const p = ok(fat) ? posicao(fat, 3) : null;
      return p ? h('span', { class: 'ax', style: { left: `${p.x}%`, bottom: rot === 'hoje' ? '26px' : '4px' }, text: rot }) : null;
    })) : h('div', { class: 'pl' }, h('span', { class: 'small', text: 'sem central firme: só os valores' }));
  const corpo = [
    h('div', { class: 'mrow h' }, h('div', { class: 'cap', text: 'Entram no central' }), eixo, h('div', { class: 'cap r', text: 'Base (faixa)' })),
    ...centrais.map((m) => linhaMetodo(m, cab, comEixo)),
    h('div', { class: 'grp cap', text: 'Só informativos · não entram no central' }),
    ...infos.map((m) => linhaMetodo(m, cab, comEixo)),
  ];
  const ind = emp.indicadores.length ? h('div', { class: 'ind' }, emp.indicadores.flatMap((i) => [
    h('span', {}, h('b', { text: i.nome }), i.descricao ? h('span', { class: 'small', text: ` — ${i.descricao}` }) : null),
    valor(fmtUnidade(i.base, i.unidade), i.nota)])) : null;
  return cartao({ titulo: 'Valuation por método', id: 'valuation',
    lead: 'Cada ponto é o valor-base do método no mesmo eixo da régua. Ponto cheio = entra no central; vazado = só informativo. A faixa baixo–alto por método ainda não sai do motor (sem fonte).' },
  h('div', { class: 'xs' }, h('div', { style: { minWidth: '640px' } }, corpo)), ind);
}

// ------------------------------------------------------------------------------ sensibilidade
const TOM = { bem_acima: 'up2', acima: 'up1', abaixo: 'dn1', bem_abaixo: 'dn2' };
const TOM_TEXTO = { bem_acima: 'preço já na compra', acima: 'acima do preço', abaixo: 'abaixo do preço', bem_abaixo: 'preço na saída' };

function cardSensibilidade(emp) {
  const s = emp.sensibilidade;
  if (!s) return cartao({ titulo: 'Sensibilidade do valor central', id: 'sensibilidade' }, vazio('Sem grade de sensibilidade', 'O motor não gravou a grade para este ticker (sem fonte).'));
  const grade = h('div', { class: 'sens', style: { gridTemplateColumns: `96px repeat(${s.colunas.length}, minmax(64px, 1fr))` }, role: 'table', 'aria-label': s.titulo },
    h('div', { class: 'linha', role: 'row' },
      h('div', { class: 'hd', role: 'columnheader', text: `${s.eixo_linha} ↓ · ${s.eixo_coluna} →` }),
      s.colunas.map((col) => h('div', { class: 'hd', role: 'columnheader', text: col }))),
    s.linhas.map((rot, i) => h('div', { class: 'linha', role: 'row' },
      h('div', { class: 'hd', role: 'rowheader', text: rot }),
      s.valores[i].map((v, j) => {
        const base = s.base && s.base[0] === i && s.base[1] === j;
        const tom = TOM_TEXTO[s.classe[i][j]] || 'sem preço de hoje';
        return h('div', { class: `cell num ${TOM[s.classe[i][j]] || ''}${base ? ' base' : ''}`, role: 'cell',
          title: `${rot} × ${s.colunas[j]}: ${num(v)} · ${tom}${base ? ' · caso-base' : ''}`,
          'aria-label': `${num(v)}, ${tom}${base ? ', caso-base' : ''}`, text: num(v) });
      }))));
  return cartao({ titulo: 'Sensibilidade do valor central', id: 'sensibilidade', lead: `${s.titulo}. Contorno grosso = caso-base.` },
    h('div', { class: 'xs' }, grade),
    h('div', { class: 'lg' },
      h('span', {}, h('i', { class: 'sw up2' }), 'preço já na compra'), h('span', {}, h('i', { class: 'sw up1' }), 'acima do preço'),
      h('span', {}, h('i', { class: 'sw dn1' }), 'abaixo do preço'), h('span', {}, h('i', { class: 'sw dn2' }), 'preço na saída')),
    h('p', { class: 'small' }, h('span', { class: 'tag n', text: 'pré-calculado' }), ' Grade calculada pelo motor. Esta tela só exibe; nada é recalculado aqui.'));
}

// ------------------------------------------------------------------------------ premissas, qualitativo, riscos
function cardPremissas(emp) {
  const ps = emp.premissas;
  return cartao({ titulo: 'Premissas', id: 'premissas', lead: 'Premissas de julgamento do motor (método, não dado). Hachurado = julgamento. Efeito no central: o motor ainda não calcula (sem fonte).' },
    ps.length ? h('div', { class: 'xs' }, h('div', { style: { minWidth: '560px' } },
      h('div', { class: 'prem h' }, ['Premissa', 'Valor', 'Tipo', 'Fonte', 'Efeito ± R$'].map((t, i) => h('span', { class: `cap${i === 4 ? ' r' : ''}`, text: t }))),
      ps.map((p) => h('div', { class: `prem${p.tipo === 'julgamento' ? ' j' : ''}` },
        h('span', { text: p.nome }), h('span', { class: 'small', text: p.valor || TRACO }),
        h('span', {}, h('span', { class: p.tipo === 'julgamento' ? 'tag j' : 'tag n', text: p.tipo })),
        nota(p.nota || '—'), h('span', { class: 'r v-w', text: TRACO })))))
      : vazio('Sem premissas registradas', 'O motor não gravou premissas de julgamento para este ticker.'));
}

function notaEixo(ne) {
  if (!ne || !ok(ne.valor)) return h('p', { class: 'small v-w', text: 'sem nota (sem fonte)' });
  const [lo, hi] = ne.escala || [0, 5];
  const rot = `${num(ne.valor, Number.isInteger(ne.valor) ? 0 : 1)} de ${hi}`;
  if (hi <= 5) {
    return h('div', { class: 'pips', role: 'img', 'aria-label': `Nota ${rot}` },
      Array.from({ length: hi - lo }, (_, i) => h('i', { class: `pip${i < Math.round(ne.valor) - lo ? ' on' : ''}` })),
      h('span', { class: 'w', text: rot }));
  }
  return h('div', { class: 'pips', role: 'img', 'aria-label': `Nota ${rot}` },
    h('div', { class: 'meter q10' }, h('i', { style: { width: `${Math.max(0, Math.min(1, (ne.valor - lo) / (hi - lo))) * 100}%` } })),
    h('span', { class: 'w', text: rot }));
}

function cardQualitativo(emp) {
  return cartao({ titulo: 'Qualitativo', id: 'qualitativo', lead: 'Notas e números que o motor grava por eixo, sempre com a fonte. Não é nota de compra.' },
    h('div', { class: 'qgrid' }, emp.qualitativo.map((q) => h('div', { class: 'q' },
      h('h3', {}, h('span', { text: q.titulo }), q.nota_eixo ? nota(q.nota_eixo.nota) : nota('—')),
      notaEixo(q.nota_eixo),
      q.nota_eixo && q.nota_eixo.fonte ? h('span', { class: 'small', text: `${q.nota_eixo.fonte}${q.nota_eixo.obs ? ` · ${q.nota_eixo.obs}` : ''}` }) : null,
      q.texto.map((t) => h('p', { text: t.replace(/\*\*/g, '') })),
      q.numeros.length ? kv(q.numeros.map((n) => [n.rotulo, valor(fmtUnidade(n.valor, n.unidade), n.nota)])) : null,
      q.avisos.map((a) => h('p', { class: 'small', text: a }))))));
}

function cardRiscos(emp) {
  const r = emp.riscos;
  return cartao({ titulo: 'Riscos e bandeiras', id: 'riscos', lead: 'Bandeiras do motor. Probabilidade e impacto: o motor ainda não gradua (sem fonte).' },
    r.itens.length ? h('div', { class: 'risk' }, r.itens.flatMap((x) => [
      h('span', {}, x.nome, h('span', { class: 'small', text: ` · ${fmtUnidade(x.valor, x.unidade)}` }), nota(x.nota)),
      x.disparou ? h('span', { class: 'tag', text: 'dispara' }) : h('b', { text: 'ok' })])) : vazio('Sem bandeiras', 'O motor não gravou bandeiras.'),
    r.texto.map((t) => h('p', { class: 'small', text: t.replace(/\*\*/g, '') })));
}

// ------------------------------------------------------------------------------ lateral
function cardLeitura(emp) {
  const cab = emp.cabecalho, l = emp.leitura, f = fatores();
  return h('section', { class: 'card', 'aria-label': 'Leitura da régua' },
    h('div', { class: 'cap', text: 'Leitura da régua' }),
    h('div', { style: { margin: '10px 0' } }, chip(cab.palavra, 'lg')),
    kv([
      ['P/C hoje', h('span', { class: `num${firme(cab.central_nota) ? '' : ' v-w'}`, text: num(cab.pc) })],
      ['Compra · saída', h('span', { class: 'num', text: temRegua(cab) ? `${mult(f.compra)} · ${mult(cab.fator_saida)}` : TRACO })],
      ['Métodos no central', h('span', { class: 'num', text: `${l.metodos_central} de ${l['metodos_r$']}` })],
      ['Com fonte A ou B', h('span', { class: 'num', text: `${l.central_com_fonte_ab} de ${l.metodos_central}` })],
      ['Vence a renda fixa?', rendaFixa(cab)],
    ]),
    h('p', { class: 'small', text: `Renda fixa: ${cab.vence_rf_criterio || 'sem fonte'}. A palavra descreve o preço contra a régua. Não é recomendação.` }),
    cab.avisos.map((a) => h('p', { class: 'small', text: a })));
}

function cardProventos(emp) {
  const p = emp.proventos;
  const hist = (p.historico || []).slice(-10);
  const mx = Math.max(0, ...hist.map((x) => x.total || 0));
  const grafico = hist.length && mx > 0 ? [
    h('div', { class: 'hist', role: 'img', 'aria-label': `Proventos por ação, ${hist[0].ano} a ${hist[hist.length - 1].ano}: ${hist.map((x) => `${x.ano} ${num(x.total)}`).join('; ')}` },
      hist.map((x) => h('div', { class: `col${x.parcial ? ' pr' : ''}`, title: `${x.ano}${x.parcial ? ' (parcial)' : ''}: total ${rs(x.total)}, JCP ${rs(x.jcp)}` },
        h('i', { class: 'j', style: { height: `${((x.jcp || 0) / mx) * 100}%` } }),
        h('i', { class: 'd', style: { height: `${((x.dividendos || 0) / mx) * 100}%` } })))),
    h('div', { class: 'yrs' }, hist.map((x) => h('span', { text: `${x.ano.slice(2)}${x.parcial ? 'p' : ''}` }))),
    h('div', { class: 'lg' }, h('span', {}, h('i', { class: 'd' }), 'Dividendos'), h('span', {}, h('i', { class: 'j' }), 'JCP'),
      h('span', {}, h('i', { class: 'pr' }), 'ano parcial'), p.fonte_historico ? h('span', {}, `fonte ${p.fonte_historico.fonte}`, nota(p.fonte_historico.nota)) : null),
  ] : [h('p', { class: 'small v-w', text: hist.length
    ? 'Histórico por exercício: nenhum provento nos anos registrados.'
    : 'Histórico por exercício: sem fonte para este ticker.' })];
  const par = (rot, x, fmtf) => [rot, x ? valor(fmtf(x.valor), x.nota) : h('span', { class: 'v-w', text: TRACO })];
  return cartao({ titulo: 'Proventos', id: 'proventos', lead: 'R$ por ação de hoje, por ano da data-com. Dividendos e JCP empilhados.' },
    grafico,
    h('div', { style: { marginTop: '12px' } }, kv([
      par('DPA sustentável', p.dpa_sustentavel, (v) => rs(v)),
      par('Payout', p.payout, (v) => pct(v, 0)),
      par('DY sustentável', p.yield_sust, (v) => pct(v)),
      par('Exercícios com provento', p.exercicios_com_provento, (v) => (typeof v === 'string' ? v : num(v, 0))),
      par('Anos seguidos com provento (data-com)', p.anos_seguidos, (v) => `${num(v, 0)}${p.anos_seguidos.minimo ? '+' : ''}`),
      par('Defasagem do pagamento (meses)', p.defasagem_meses, (v) => num(v, 1)),
    ])),
    p.avisos.map((a) => h('p', { class: 'small', text: a })));
}

function cardCarteira(tk, c) {
  const pos = c.carteiraPorTk[tk];
  if (!pos) return null;
  return cartao({ titulo: 'Na carteira', lead: 'Dado pessoal, só neste computador.' }, kv([
    ['Peso na carteira', pessoal(pct(pos.peso), c.ocultar)],
    ['Renda líquida por ano', pessoal(rs(pos.renda_liquida_ano), c.ocultar)],
    ['Renda bruta por ano', pessoal(rs(pos.renda_bruta_ano), c.ocultar)],
  ]));
}

function cardFontes(emp, c) {
  const fs = emp.fontes.slice(0, 10);
  return cartao({ titulo: 'Fontes e frescor', id: 'fontes', lead: `Relatório de ${data(emp.data_relatorio)} · cotação de ${data(c.estado.hall.cotacao_em)}. Só A e B embasam decisão.` },
    fs.map((f) => h('div', { class: 'src' }, h('span', { text: f.nome }), h('span', { class: 'small num', text: `${f.n_numeros} nº` }), nota(f.nota))),
    emp.fontes.length > fs.length ? h('p', { class: 'small', text: `+ ${emp.fontes.length - fs.length} fontes com menos números.` }) : null);
}

// ------------------------------------------------------------------------------ tela
export function telaEmpresa(c, tk) {
  if (!tk) {
    return { contexto: 'Empresa', nos: [vazio('Nenhuma empresa escolhida', 'Abra uma empresa pelo Hall (clique no ticker) ou pela busca.', h('a', { class: 'btn', href: '#/hall', text: 'Ir ao Hall' }))] };
  }
  const contexto = `Hall / ${tk} · relatório`;
  const crumb = h('div', { class: 'crumb' }, h('a', { href: '#/hall', text: 'Hall' }), ` / ${tk}`);
  const erro = c.estado.erros[`empresa:${tk}`];
  if (erro) return { contexto, nos: [crumb, faixaErro(erro)] };
  const emp = c.estado.empresas[tk];
  if (!emp) return { contexto, nos: [crumb, carregando(8)] };
  const cab = emp.cabecalho;
  const subnav = h('nav', { class: 'subnav', 'aria-label': 'Seções do relatório' }, SECOES.map(([id, rot]) => h('a', {
    href: `#/empresa/${tk}`, text: rot,
    onclick: (ev) => { ev.preventDefault(); const alvo = document.getElementById(id); if (alvo) alvo.scrollIntoView({ behavior: 'smooth', block: 'start' }); },
  })));
  const nos = [
    crumb, cabecalho(cab, c), subnav,
    faixaInfo('Avisos do motor', emp.avisos),
    cardRegua(cab),
    h('div', { class: 'cols' },
      h('div', { class: 'main' }, cardValuation(emp), cardSensibilidade(emp), cardPremissas(emp), cardQualitativo(emp), cardRiscos(emp)),
      h('div', { class: 'aside' }, cardLeitura(emp), cardProventos(emp), cardCarteira(tk, c), cardFontes(emp, c))),
  ];
  return { contexto, nos };
}
