// Monitor semanal: quem cruzou a faixa de compra ou de saída entre as duas últimas rodadas (monitor/historico.csv).
// Círculo vazado = semana anterior; traço = hoje. Sem botão de ação; cada linha leva à Empresa.
import { h, num, data } from '../fmt.js';
import { reguaMini, cartao, vazio, faixaErro } from '../ui.js';

const LISTAS = [
  ['entraram_compra', 'Entraram na faixa de compra'], ['entraram_saida', 'Entraram na faixa de saída'],
  ['sairam_compra', 'Saíram da faixa de compra'], ['sairam_saida', 'Saíram da faixa de saída'],
];

function linhaMon(x, c) {
  // régua do Hall como está (sem régua lá = sem régua aqui); só o P/C vem das rodadas do monitor
  const regua = { ...(c.linhas[x.ticker] || {}), pc: x.pc_atual };
  return h('div', { class: 'mon' },
    h('a', { href: `#/empresa/${x.ticker}` }, h('b', { text: x.ticker })),
    reguaMini(regua, { anterior: x.pc_anterior, cls: 'mr' }),
    h('span', { class: 'r num' }, `${num(x.pc_anterior)} → ${num(x.pc_atual)}`,
      x.novo ? h('span', { class: 'tag n', text: 'novo' }) : null, x.removido ? h('span', { class: 'tag n', text: 'saiu do hall' }) : null));
}

export function telaMonitor(c) {
  const contexto = 'Monitor · semana';
  const titulo = h('h1', { class: 'h1', text: 'Monitor semanal' });
  if (c.estado.erros.monitor) return { contexto, nos: [titulo, faixaErro(c.estado.erros.monitor)] };
  const m = c.estado.monitor;
  if (!m || !m.rodada) return { contexto, nos: [titulo, vazio('Sem rodada do monitor ainda.', m && m.aviso ? m.aviso : 'O monitor roda às sextas.')] };
  const nos = [
    h('div', {}, titulo, h('p', { class: 'sub', text: m.rodada_anterior
      ? `Rodada de ${data(m.rodada)} (pregão ${data(m.pregao)}) contra a de ${data(m.rodada_anterior)}. P/C anterior → atual.`
      : `Primeira rodada (${data(m.rodada)}): ainda não há semana anterior para comparar.` })),
    m.aviso ? faixaErro(m.aviso) : null,
    h('div', { class: 'grid2' }, LISTAS.map(([k, rot]) => cartao({ titulo: rot, lead: `${m[k].length} papel(éis)` },
      m[k].length ? m[k].map((x) => linhaMon(x, c)) : h('p', { class: 'small', text: 'Nenhum papel nesta semana.' })))),
    h('details', { class: 'semmud' }, h('summary', { text: `Sem mudança: ${m.sem_mudanca} papéis` }),
      h('p', { class: 'small', text: `${m.sem_mudanca} de ${m.tickers} papéis ficaram do mesmo lado da régua.` }),
      m.novos.length ? h('p', { class: 'small', text: `Novos nesta rodada: ${m.novos.join(', ')}.` }) : null,
      m.removidos.length ? h('p', { class: 'small', text: `Fora desta rodada: ${m.removidos.join(', ')}.` }) : null),
  ];
  return { contexto, nos };
}
