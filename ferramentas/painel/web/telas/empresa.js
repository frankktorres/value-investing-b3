// Empresa: relatório de um ticker como o motor gravou (contrato v0.2). Régua, métodos, sensibilidade pré-calculada,
// premissas, qualitativo, riscos, proventos e fontes. Nada é recalculado: a posição no eixo é só leitura visual.
import { h, num, pct, mult, rs, data, ok, TRACO } from '../fmt.js';
import {
  chip, nota, valor, pessoal, firme, rendaFixa, reguaGrande, margem, posicao, foraCls, temRegua, cartao, stat, kv, vazio,
  carregando, faixaErro, faixaInfo, fatores, PALAVRAS,
} from '../ui.js';

const SECOES = [
  ['valuation', 'Preço justo'], ['sensibilidade', 'Sensibilidade'], ['qualitativo', 'Fundamentos'],
  ['riscos', 'Riscos'], ['proventos', 'Dividendos'], ['premissas', 'Premissas'], ['fontes', 'Fontes'],
];
// nome do método como aparece nos sites brasileiros (o motor grava o nome técnico)
const APELIDO = {
  DDM: 'Modelo de Gordon (DDM)', DCF: 'Fluxo de caixa descontado (DCF)', Graham: 'Graham (preço justo)', Bazin: 'Bazin (preço teto)',
};
const nomeMetodo = (n) => APELIDO[n] || n;

function fmtUnidade(v, unidade) {
  if (typeof v === 'string') return v;
  if (unidade === 'R$') return num(v);
  if (unidade === '%') return pct(v);
  if (unidade === 'x') return mult(v);
  return ok(v) ? num(v, Number.isInteger(v) ? 0 : 2) : TRACO;
}

function cabecalho(cab, c) {
  const flags = [
    cab.fora_do_hall ? h('span', { class: 'tag n', title: 'Não passa no filtro de qualidade: o veredito é só referência', text: 'fora do filtro' }) : null,
    cab.velho ? h('span', { class: 'tag', text: `cotação antiga · ${cab.dias_defasagem} d` }) : null,
  ];
  return h('div', { class: 'head' },
    h('div', { class: 'id' },
      h('div', { class: 'tl' }, h('span', { class: 'tkr', text: cab.ticker }), h('span', { class: 'nome', text: cab.nome || '' })),
      h('div', { class: 'meta' }, chip(cab.palavra, 'lg'),
        h('span', { text: `${cab.setor ? `${cab.setor} · ` : ''}veredito de ${data(cab.data_palavra)} · cotação de ${data(cab.ultimo_pregao)}`, title: cab.origem }), flags)),
    h('div', { class: 'stats' },
      stat('Cotação', h('small', { text: 'R$' }), valor(num(cab.preco), cab.preco_nota)),
      stat('Preço justo', h('small', { text: 'R$' }), cab.regua_suspensa ? h('span', { class: 'v-w', text: TRACO }) : valor(num(cab.central), cab.central_nota)),
      stat('Margem de segurança', margem(cab)),
      stat('DY sustentável', valor(pct(cab.yield_sust), cab.yield_nota)),
      stat('Supera a RF?', rendaFixa(cab))));
}

function cardRegua(cab) {
  const f = fatores();
  return h('section', { class: 'card', id: 'regua', 'aria-label': 'Faixas de preço' },
    h('div', { class: 'cap', text: `Faixas de preço · R$ por ação · compra até ${mult(f.compra)} e venda a partir de ${mult(f.saida)} do preço justo (${mult(f.saida_qualidade)} com exceção de qualidade)` }),
    h('div', { class: 'xs' }, h('div', { style: { minWidth: '560px', paddingTop: '22px' } }, reguaGrande(cab))),
    cab.palavra_motor ? h('p', { class: 'small', text: `O cálculo de hoje dá ${PALAVRAS[cab.palavra_motor] ? PALAVRAS[cab.palavra_motor].rot : cab.palavra_motor}; o veredito vigente só muda com uma análise nova.` }) : null);
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
      title: `${nomeMetodo(m.nome)}: ${rs(m.base)}${p.fora ? ' (fora da escala)' : ''}` }) : null;
  })()) : h('div', { class: 'pl' });
  const fraco = !firme(m.nota) || !ok(m.base);
  return h('div', { class: 'mrow' },
    h('div', { class: 'nm' }, h('b', { text: nomeMetodo(m.nome) }), nota(ok(m.base) ? m.nota : '—'),
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
    ...(temRegua(cab) ? [[cab.pc, 'cotação'], [f.compra, 'compra'], [1, 'justo'], [cab.fator_saida, 'venda']] : [[1, 'justo']]).map(([fat, rot]) => {
      const p = ok(fat) ? posicao(fat, 3) : null;
      return p ? h('span', { class: 'ax', style: { left: `${p.x}%`, bottom: rot === 'cotação' ? '26px' : '4px' }, text: rot }) : null;
    })) : h('div', { class: 'pl' }, h('span', { class: 'small', text: 'sem preço justo firme: só os valores' }));
  const corpo = [
    h('div', { class: 'mrow h' }, h('div', { class: 'cap', text: 'Entram no preço justo' }), eixo, h('div', { class: 'cap r', text: 'R$ por ação (faixa)' })),
    ...centrais.map((m) => linhaMetodo(m, cab, comEixo)),
    h('div', { class: 'grp cap', text: 'Só informativos · não entram no preço justo' }),
    ...infos.map((m) => linhaMetodo(m, cab, comEixo)),
  ];
  const ind = emp.indicadores.length ? h('div', { class: 'ind' }, emp.indicadores.flatMap((i) => [
    h('span', {}, h('b', { text: i.nome }), i.descricao ? h('span', { class: 'small', text: ` — ${i.descricao}` }) : null),
    valor(fmtUnidade(i.base, i.unidade), i.nota)])) : null;
  return cartao({ titulo: 'Preço justo por método', id: 'valuation',
    lead: 'Cada ponto é o valor por ação de um método, no mesmo eixo das faixas. Ponto cheio = entra no preço justo; vazado = só informativo.' },
  h('div', { class: 'xs' }, h('div', { style: { minWidth: '640px' } }, corpo)), ind);
}

// ------------------------------------------------------------------------------ sensibilidade
const TOM = { bem_acima: 'up2', acima: 'up1', abaixo: 'dn1', bem_abaixo: 'dn2' };
const TOM_TEXTO = { bem_acima: 'cotação na zona de compra', acima: 'acima da cotação', abaixo: 'abaixo da cotação', bem_abaixo: 'cotação na zona de venda' };

function cardSensibilidade(emp) {
  const s = emp.sensibilidade;
  if (!s) return cartao({ titulo: 'Sensibilidade do preço justo', id: 'sensibilidade' }, vazio('Sem grade de sensibilidade', 'O motor não gravou a grade para este ticker (sem fonte).'));
  const grade = h('div', { class: 'sens', style: { gridTemplateColumns: `96px repeat(${s.colunas.length}, minmax(64px, 1fr))` }, role: 'table', 'aria-label': s.titulo },
    h('div', { class: 'linha', role: 'row' },
      h('div', { class: 'hd', role: 'columnheader', text: `${s.eixo_linha} ↓ · ${s.eixo_coluna} →` }),
      s.colunas.map((col) => h('div', { class: 'hd', role: 'columnheader', text: col }))),
    s.linhas.map((rot, i) => h('div', { class: 'linha', role: 'row' },
      h('div', { class: 'hd', role: 'rowheader', text: rot }),
      s.valores[i].map((v, j) => {
        const base = s.base && s.base[0] === i && s.base[1] === j;
        const tom = TOM_TEXTO[s.classe[i][j]] || 'sem cotação de hoje';
        return h('div', { class: `cell num ${TOM[s.classe[i][j]] || ''}${base ? ' base' : ''}`, role: 'cell',
          title: `${rot} × ${s.colunas[j]}: ${num(v)} · ${tom}${base ? ' · caso-base' : ''}`,
          'aria-label': `${num(v)}, ${tom}${base ? ', caso-base' : ''}`, text: num(v) });
      }))));
  return cartao({ titulo: 'Sensibilidade do preço justo', id: 'sensibilidade', lead: `${s.titulo}. Contorno grosso = caso-base; grade calculada pelo motor.` },
    h('div', { class: 'xs' }, grade),
    h('div', { class: 'lg' },
      h('span', {}, h('i', { class: 'sw up2' }), 'cotação na zona de compra'), h('span', {}, h('i', { class: 'sw up1' }), 'acima da cotação'),
      h('span', {}, h('i', { class: 'sw dn1' }), 'abaixo da cotação'), h('span', {}, h('i', { class: 'sw dn2' }), 'cotação na zona de venda')));
}

// ------------------------------------------------------------------------------ premissas, qualitativo, riscos
function cardPremissas(emp) {
  const ps = emp.premissas;
  return cartao({ titulo: 'Premissas', id: 'premissas', lead: 'Escolhas de julgamento por trás do preço justo (método, não dado). Hachurado = julgamento.' },
    ps.length ? h('div', { class: 'xs' }, h('div', { style: { minWidth: '480px' } },
      h('div', { class: 'prem h' }, ['Premissa', 'Valor', 'Tipo', 'Fonte'].map((t) => h('span', { class: 'cap', text: t }))),
      ps.map((p) => h('div', { class: `prem${p.tipo === 'julgamento' ? ' j' : ''}` },
        h('span', { text: p.nome }), h('span', { class: 'small', text: p.valor || TRACO }),
        h('span', {}, h('span', { class: p.tipo === 'julgamento' ? 'tag j' : 'tag n', text: p.tipo })),
        nota(p.nota || '—')))))
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
  return cartao({ titulo: 'Fundamentos', id: 'qualitativo', lead: 'Notas e indicadores por tema, sempre com a fonte. Não é nota de compra.' },
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
  return cartao({ titulo: 'Riscos', id: 'riscos', lead: 'Alertas de risco: "dispara" = o critério foi atingido.' },
    r.itens.length ? h('div', { class: 'risk' }, r.itens.flatMap((x) => [
      h('span', {}, x.nome, h('span', { class: 'small', text: ` · ${fmtUnidade(x.valor, x.unidade)}` }), nota(x.nota)),
      x.disparou ? h('span', { class: 'tag', text: 'dispara' }) : h('b', { text: 'ok' })])) : vazio('Sem bandeiras', 'O motor não gravou bandeiras.'),
    r.texto.map((t) => h('p', { class: 'small', text: t.replace(/\*\*/g, '') })));
}

// ------------------------------------------------------------------------------ lateral
function cardLeitura(emp) {
  const cab = emp.cabecalho, l = emp.leitura, f = fatores();
  return h('section', { class: 'card', 'aria-label': 'Resumo' },
    h('div', { class: 'cap', text: 'Resumo' }),
    h('div', { style: { margin: '10px 0' } }, chip(cab.palavra, 'lg')),
    kv([
      ['Cotação ÷ preço justo', h('span', { class: `num${firme(cab.central_nota) ? '' : ' v-w'}`, text: mult(cab.pc) })],
      ['Compra até · venda a partir de', h('span', { class: 'num', text: temRegua(cab) ? `${mult(f.compra)} · ${mult(cab.fator_saida)}` : TRACO })],
      ['Métodos no preço justo', h('span', { class: 'num', text: `${l.metodos_central} de ${l['metodos_r$']}` })],
      ['Com fonte A ou B', h('span', { class: 'num', text: `${l.central_com_fonte_ab} de ${l.metodos_central}` })],
      ['Supera a renda fixa?', rendaFixa(cab)],
    ]),
    h('p', { class: 'small', text: `Renda fixa: ${cab.vence_rf_criterio || 'sem fonte'}. O veredito descreve a cotação contra o preço justo. Não é recomendação.` }),
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
  return cartao({ titulo: 'Dividendos e JCP', id: 'proventos', lead: 'Proventos em R$ por ação, por ano da data-com.' },
    grafico,
    h('div', { style: { marginTop: '12px' } }, kv([
      par('DPA sustentável', p.dpa_sustentavel, (v) => rs(v)),
      par('Payout', p.payout, (v) => pct(v, 0)),
      par('DY sustentável', p.yield_sust, (v) => pct(v)),
      par('Exercícios com provento', p.exercicios_com_provento, (v) => (typeof v === 'string' ? v : num(v, 0))),
      par('Anos seguidos pagando', p.anos_seguidos, (v) => `${num(v, 0)}${p.anos_seguidos.minimo ? '+' : ''}`),
      par('Prazo da data-com ao pagamento (meses)', p.defasagem_meses, (v) => num(v, 1)),
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
  return cartao({ titulo: 'Fontes dos dados', id: 'fontes', lead: `Relatório de ${data(emp.data_relatorio)} · cotação de ${data(c.estado.hall.cotacao_em)}. Só A e B embasam decisão.` },
    fs.map((f) => h('div', { class: 'src' }, h('span', { text: f.nome }), h('span', { class: 'small num', text: `${f.data ? data(f.data) : 'sem data'} · ${f.n_numeros} nº` }), nota(f.nota))),
    emp.fontes.length > fs.length ? h('p', { class: 'small', text: `+ ${emp.fontes.length - fs.length} fontes com menos números.` }) : null);
}

// ------------------------------------------------------------------------------ tela
export function telaEmpresa(c, tk) {
  if (!tk) {
    return { contexto: 'Empresa', nos: [vazio('Nenhuma empresa escolhida', 'Abra uma empresa pela lista de ações (clique no ticker) ou pela busca.', h('a', { class: 'btn', href: '#/hall', text: 'Ver ações' }))] };
  }
  const contexto = `Ações / ${tk}`;
  const crumb = h('div', { class: 'crumb' }, h('a', { href: '#/hall', text: 'Ações' }), ` / ${tk}`);
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
    faixaInfo('Avisos do modelo', emp.avisos),
    cardRegua(cab),
    h('div', { class: 'cols' },
      h('div', { class: 'main' }, cardValuation(emp), cardSensibilidade(emp), cardQualitativo(emp), cardRiscos(emp), cardPremissas(emp)),
      h('div', { class: 'aside' }, cardLeitura(emp), cardProventos(emp), cardCarteira(tk, c), cardFontes(emp, c))),
  ];
  return { contexto, nos };
}
