// Alertas (rota #/monitor): quem cruzou a zona de compra ou de venda entre as duas últimas rodadas (monitor/historico.csv).
// Círculo vazado = semana anterior; traço = hoje. Sem botão de ação; cada linha leva à Empresa.
import { h, num, data } from '../fmt.js';
import { reguaMini, cartao, vazio, faixaErro } from '../ui.js';

const LISTAS = [
  ['entraram_compra', 'Entraram na zona de compra'], ['entraram_saida', 'Entraram na zona de venda'],
  ['sairam_compra', 'Saíram da zona de compra'], ['sairam_saida', 'Saíram da zona de venda'],
];

function linhaMon(x, c) {
  // régua do Hall como está (sem régua lá = sem régua aqui); só o P/C vem das rodadas do monitor
  const regua = { ...(c.linhas[x.ticker] || {}), pc: x.pc_atual };
  return h('div', { class: 'mon' },
    h('a', { href: `#/empresa/${x.ticker}` }, h('b', { text: x.ticker })),
    reguaMini(regua, { anterior: x.pc_anterior, cls: 'mr' }),
    h('span', { class: 'r num', title: 'Cotação ÷ preço justo: semana anterior → hoje' }, `${num(x.pc_anterior)}× → ${num(x.pc_atual)}×`,
      x.novo ? h('span', { class: 'tag n', text: 'novo' }) : null, x.removido ? h('span', { class: 'tag n', text: 'saiu da lista' }) : null));
}

export function telaMonitor(c) {
  const contexto = 'Alertas · semana';
  const titulo = h('h1', { class: 'h1', text: 'Alertas da semana' });
  if (c.estado.erros.monitor) return { contexto, nos: [titulo, faixaErro(c.estado.erros.monitor)] };
  const m = c.estado.monitor;
  if (!m || !m.rodada) return { contexto, nos: [titulo, vazio('Sem rodada de alertas ainda.', m && m.aviso ? m.aviso : 'Os alertas são gerados às sextas.')] };
  const nos = [
    h('div', {}, titulo, h('p', { class: 'sub', text: m.rodada_anterior
      ? `Rodada de ${data(m.rodada)} (cotação de ${data(m.pregao)}) contra a de ${data(m.rodada_anterior)}. Números = cotação ÷ preço justo, antes → agora.`
      : `Primeira rodada (${data(m.rodada)}): ainda não há semana anterior para comparar.` })),
    m.aviso ? faixaErro(m.aviso) : null,
    // só as listas com alguém: quatro cartões vazios eram ruído
    LISTAS.some(([k]) => m[k].length)
      ? h('div', { class: 'grid2' }, LISTAS.filter(([k]) => m[k].length).map(([k, rot]) => cartao({ titulo: rot, lead: m[k].length === 1 ? '1 ação' : `${m[k].length} ações` },
        m[k].map((x) => linhaMon(x, c)))))
      : vazio('Nenhuma ação mudou de zona nesta semana.', 'Ninguém entrou nem saiu da zona de compra ou de venda.'),
    h('details', { class: 'semmud' }, h('summary', { text: `Sem mudança: ${m.sem_mudanca} ações` }),
      h('p', { class: 'small', text: `${m.sem_mudanca} de ${m.tickers} papéis ficaram na mesma zona.` }),
      m.novos.length ? h('p', { class: 'small', text: `Novos nesta rodada: ${m.novos.join(', ')}.` }) : null,
      m.removidos.length ? h('p', { class: 'small', text: `Fora desta rodada: ${m.removidos.join(', ')}.` }) : null),
  ];
  return { contexto, nos };
}
