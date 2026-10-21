// Carteira e meta de renda: o que `relatorio.carteira` calculou (via dados/privado/carteira.json, só neste computador).
// Sem projeção, sem data de cruzamento da meta, sem cenários. Ocultar valores troca todo R$ e peso por "•••".
import { h, s, num, pct, rs, compacto, data, diaMes, mes, ok, TRACO } from '../fmt.js';
import { chip, nota, pessoal, reguaMini, cartao, vazio, faixaErro, faixaInfo } from '../ui.js';

function kpi(cap, valorNo, sufixo, notaN, texto, extra = null) {
  return h('section', { class: 'card kpi', 'aria-label': cap },
    h('div', { class: 'cap', text: cap }),
    h('div', { class: 'v' }, valorNo, sufixo ? h('small', { text: sufixo }) : null, notaN ? nota(notaN) : null),
    extra, texto ? h('p', { text: texto }) : null);
}

function evolucao(ct, ocultar) {
  const pts = ct.renda_12m.filter((r) => ok(r.renda_liquida_mensal) && ok(r.pct_meta));
  const W = 800, H = 300, L = 56, R = 16, T = 20, B = 28;
  const emPct = ocultar;                                   // oculto: eixo em % da meta (percentuais continuam)
  const meta = emPct ? 1 : (ct.meta.valor || 0);
  const y = (r) => (emPct ? r.pct_meta : r.renda_liquida_mensal);
  const topo = Math.max(meta, ...pts.map(y)) * 1.1 || 1;
  const X = (i) => L + (pts.length > 1 ? (i / (pts.length - 1)) * (W - L - R) : (W - L - R) / 2);
  const Y = (v) => T + (1 - v / topo) * (H - T - B);
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((f) => f * topo);
  const fmtY = (v) => (emPct ? pct(v, 0) : compacto(v));
  const svg = s('svg', { class: 'svgw', viewBox: `0 0 ${W} ${H}`, role: 'img',
    'aria-label': `Renda mensal estimada em ${pts.length} registro(s) contra a meta${emPct ? ', em % da meta' : ''}` },
  ticks.map((v) => s('line', { class: 'gl2', x1: L, x2: W - R, y1: Y(v), y2: Y(v) })),
  s('line', { class: 'meta', x1: L, x2: W - R, y1: Y(meta), y2: Y(meta) }),
  pts.length > 1 ? s('path', { class: 'serie', d: pts.map((r, i) => `${i ? 'L' : 'M'}${X(i)} ${Y(y(r))}`).join(' ') }) : null,
  pts.map((r, i) => s('circle', { class: 'pt', cx: X(i), cy: Y(y(r)), r: 4 })));
  const eixoY = ticks.map((v) => h('span', { class: 'axl', style: { left: '0', top: `${(Y(v) / H) * 100}%` }, text: fmtY(v) }));
  const eixoX = pts.map((r, i) => h('span', { class: 'axl x', style: { left: `${(X(i) / W) * 100}%`, top: '100%' }, text: data(r.data) }));
  return cartao({ titulo: 'Evolução rumo à meta', id: 'evolucao',
    lead: 'Renda mensal líquida estimada a cada geração do painel (média de 12 meses pela data-com), como calculada pelo motor, contra a meta. Sem projeção.' },
  pts.length ? h('div', { class: 'chart', style: { paddingBottom: '26px' } }, svg, eixoY, eixoX) : vazio('Sem histórico ainda', 'O histórico cresce a cada geração do painel da carteira.'),
  h('div', { class: 'lg' }, h('span', { text: '— renda estimada' }), h('span', { text: `— meta${emPct ? ' (100%)' : ''}` }),
    pts.length === 1 ? h('span', { class: 'small', text: `1 registro (${data(pts[0].data)}): a linha aparece a partir do segundo.` }) : null));
}

function posicoes(ct, c) {
  // com Ocultar, a ordem por peso entregaria o ranking: ordena por ticker
  const lista = [...ct.posicoes].sort(c.ocultar ? (a, b) => a.ticker.localeCompare(b.ticker) : (a, b) => (b.peso || 0) - (a.peso || 0));
  return cartao({ titulo: 'Posição de cada papel na régua', id: 'posicoes',
    lead: `${c.ocultar ? 'Ordem alfabética (valores ocultos)' : 'Ordenado por peso'}. Traço = preço de hoje; losango = central. Palavra e régua do Hall (veredito vigente).` },
  h('div', { class: 'pos h' }, ['Papel', 'Palavra', 'Régua', 'Peso', 'Renda/ano'].map((t, i) => h('span', { class: `cap${i > 2 ? ' r' : ''}`, text: t }))),
  lista.map((p) => {
    const linha = c.linhas[p.ticker] || p;
    return h('div', { class: 'pos' },
      h('a', { href: `#/empresa/${p.ticker}` }, h('b', { text: p.ticker })),
      chip(linha.palavra, 'sm'),
      reguaMini(linha, { cls: 'mr' }),
      h('span', { class: 'r' }, pessoal(pct(p.peso), c.ocultar)),
      h('span', { class: 'r' }, pessoal(rs(p.renda_liquida_ano, 0), c.ocultar)));
  }));
}

function calendario(ct, c) {
  const meses = ct.calendario.filter((m) => /^\d{4}-\d{2}$/.test(m.mes)).slice(-12);
  const semData = ct.calendario.filter((m) => !/^\d{4}-\d{2}$/.test(m.mes));
  const mx = Math.max(0, ...meses.map((m) => m.liquido || 0));
  const aReceber = (m) => m.situacao === 'a receber' || m.situacao === 'parte a receber';
  return cartao({ titulo: 'Calendário de proventos', id: 'calendario',
    lead: 'Mês em que cai o provento líquido da renda de 12 meses. Hachurado = ainda a receber.' },
  meses.length ? [
    h('div', { class: 'cal', role: 'img', 'aria-label': `Proventos líquidos por mês, ${mes(meses[0].mes)} a ${mes(meses[meses.length - 1].mes)}` },
      meses.map((m) => h('div', { class: `m${aReceber(m) ? ' rec' : ''}`, title: `${mes(m.mes)}: ${m.situacao}${m.tickers.length ? ` · ${m.tickers.join(', ')}` : ''}` },
        h('span', { class: 'vv', text: ok(m.liquido) ? (c.ocultar ? '•••' : compacto(m.liquido)) : '' }),
        // com Ocultar, a altura entregaria a proporção entre meses: barra só marca se houve pagamento
        h('i', { style: { height: `${!(mx > 0 && ok(m.liquido)) ? 0 : c.ocultar ? (m.liquido > 0 ? 50 : 0) : (m.liquido / mx) * 100}%` } })))),
    h('div', { class: 'calx' }, meses.map((m) => h('span', { text: mes(m.mes).slice(0, 3) }))),
  ] : vazio('Sem calendário', 'Nenhum provento com data de pagamento na janela.'),
  h('div', { class: 'lg' },
    h('span', {}, h('i', { class: 'd' }), 'Total líquido por mês (R$)'),
    h('span', {}, h('i', { class: 'pr' }), 'a receber'),
    h('span', { class: 'small', text: 'Divisão dividendo × JCP por mês: sem fonte (o motor dá só o total).' }),
    semData.length ? h('span', { class: 'small', text: `Sem data de pagamento: ${semData.map((m) => m.tickers.join(', ')).join('; ')}.` }) : null));
}

const TIPO = { DIVIDENDO: 'Dividendo', 'JRS CAP PROPRIO': 'JCP', JCP: 'JCP', RENDIMENTO: 'Rendimento' };

function pagamentos(ct, c) {
  return cartao({ titulo: 'Próximos pagamentos', id: 'pagamentos', lead: 'Hachurado = data estimada. Datas de pagamento: StatusInvest (nota C).' },
    ct.pagamentos.length ? ct.pagamentos.map((p) => h('div', { class: `pay${p.status === 'estimado' ? ' est' : ''}`, title: p.obs },
      h('span', { class: 'num', text: p.data ? diaMes(p.data) : 'sem data' }),
      h('a', { href: `#/empresa/${p.ticker}` }, h('b', { text: p.ticker })),
      h('span', { text: `${TIPO[p.tipo] || p.tipo}${p.so_statusinvest ? ' · só StatusInvest' : ''}` }),
      h('span', { class: 'r' }, pessoal(rs(p.valor), c.ocultar)),
      nota(p.nota))) : vazio('Nenhum pagamento a receber.', null),
    h('div', { style: { marginTop: '16px' } },
      h('div', { class: 'cap', text: 'Concentração por setor' }),
      h('p', { class: 'small v-w', text: 'Sem fonte: o motor ainda não classifica setor.' })));
}

export function telaCarteira(c) {
  const contexto = 'Carteira · meta de renda';
  const erro = c.estado.erros.carteira;
  const ct = c.estado.carteira;
  const titulo = h('div', {}, h('h1', { class: 'h1', text: 'Carteira e meta de renda' }),
    h('p', { class: 'sub', text: 'Renda estimada de dividendos e JCP, quanto falta para a meta e onde cada papel está na régua.' }));
  if (erro) return { contexto, nos: [titulo, faixaErro(erro)] };
  if (!ct || ct.vazia) {
    return { contexto, nos: [titulo, vazio('Nenhuma posição importada.', 'Coloque o arquivo de posições na pasta local (carteira.local.json) e rode painel --exportar. Nada é enviado para fora.'),
      ct && ct.erro ? h('p', { class: 'small', text: `Motivo: ${ct.erro}` }) : null] };
  }
  const o = c.ocultar;
  const pctMeta = ct.pct_meta.valor;
  const medidor = h('div', { class: 'meter', role: 'img', 'aria-label': `Meta atingida: ${pct(pctMeta, 0)}` },
    h('i', { style: { width: `${ok(pctMeta) ? Math.min(1, Math.max(0, pctMeta)) * 100 : 0}%` } }), h('b', { style: { right: '0' } }));
  const kpis = h('div', { class: 'kpis' },
    kpi('Renda mensal estimada', pessoal(rs(ct.renda_mensal_estimada.valor, 0), o), '/mês', ct.renda_mensal_estimada.nota,
      `Líquida (JCP menos IR), média de 12 meses. Bruta: ${o ? '•••' : rs(ct.renda_mensal_bruta.valor, 0)}/mês.`,
      ct.incompleta ? h('span', { class: 'tag', text: 'incompleta' }) : null),
    kpi('Meta de renda', h('span', { class: 'num', text: pct(pctMeta, 0) }), null, ct.pct_meta.nota, 'Meta definida por você.',
      [h('span', { class: 'small' }, 'de ', pessoal(rs(ct.meta.valor, 0), o), ' por mês'), medidor]),
    kpi('Falta', pessoal(rs(ct.falta.valor, 0), o), '/mês', ct.falta.nota, 'Meta menos renda estimada.'),
    kpi('Papéis', h('span', { class: 'num', text: String(ct.n_papeis) }), null, null, null,
      h('p', {}, 'Patrimônio em ações B3: ', pessoal(rs(ct.patrimonio.valor, 0), o), ' · DY líquido 12m ',
        pessoal(pct(ct.dy_liquido_12m.valor), o), '.')));
  const nos = [
    titulo, kpis,
    faixaInfo('Avisos da carteira', ct.avisos),
    h('div', { class: 'cols cart' },
      h('div', { class: 'main' }, evolucao(ct, o), calendario(ct, c)),
      h('div', { class: 'aside' }, posicoes(ct, c), pagamentos(ct, c))),
    h('p', { class: 'small', text: `Pregão ${data(ct.pregao)} · ${ct.origem}. Nada aqui é ordem de compra ou venda.` }),
  ];
  return { contexto, nos };
}
