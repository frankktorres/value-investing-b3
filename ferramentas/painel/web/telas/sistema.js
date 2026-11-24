// Sistema: a idade de cada dado, o último boletim do monitor e da temporada, o golden e a última suíte de testes.
// Só lê web/dados/contrato/sistema.json; nada é calculado aqui além de formatar. Sem registro = "sem registro", nunca zero.
import { h, data } from '../fmt.js';
import { cartao, vazio, faixaErro } from '../ui.js';

const idade = (d) => (d === null || d === undefined ? 'sem registro' : d === 0 ? 'hoje' : d === 1 ? '1 dia' : `${d} dias`);

function linhaDado(x) {
  return h('div', { class: 'src', title: x.fonte },
    h('span', { text: x.rotulo }),
    h('span', { class: 'small num', text: x.data ? data(x.data) : '—' }),
    h('span', { class: `small${x.data ? '' : ' v-w'}`, text: idade(x.idade_dias) }),
    x.obs ? h('span', { class: 'small', text: x.obs }) : null);
}

function boletim(rot, b) {
  return h('div', { class: 'src' }, h('span', { text: rot }),
    h('span', { class: 'small num', text: b ? data(b.data) : '—' }), h('span', { class: `small${b ? '' : ' v-w'}`, text: b ? b.arquivo : 'sem registro' }));
}

export function telaSistema(c) {
  const contexto = 'Status dos dados';
  const titulo = h('h1', { class: 'h1', text: 'Status dos dados' });
  if (c.estado.erros.sistema) return { contexto, nos: [titulo, faixaErro(c.estado.erros.sistema)] };
  const s = c.estado.sistema;
  if (!s) return { contexto, nos: [titulo, vazio('Sem leitura do sistema.', 'Rode painel --exportar na raiz do projeto.')] };
  const g = s.golden, t = s.suite;
  const nos = [
    h('div', {}, titulo, h('p', { class: 'sub', text: `Idade dos dados em ${data(s.hoje)}. Dado antigo muda a cotação de referência, não o veredito: o veredito só muda com análise nova.` })),
    ...(s.avisos || []).map((a) => faixaErro(a)),
    h('div', { class: 'grid2' },
      cartao({ titulo: 'Idade de cada dado', id: 'dados', lead: 'Data do último registro de cada fonte.' }, s.dados.map(linhaDado)),
      cartao({ titulo: 'Boletins', id: 'boletins', lead: 'Último arquivo em BOLETINS/.' },
        boletim('Alertas da semana', s.boletins.monitor), boletim('Temporada de balanços', s.boletins.temporada))),
    h('div', { class: 'grid2' },
      cartao({ titulo: 'Golden', id: 'golden', lead: 'O estado dos tickers que os testes guardam; só muda com motivo registrado.' },
        g ? [h('div', { class: 'src' }, h('span', { text: 'Última regravação' }), h('span', { class: 'small num', text: g.data ? data(g.data) : '—' }),
              h('span', { class: 'small', text: `${g.tickers} tickers` })),
             h('p', { class: 'small', text: g.motivo || 'sem motivo registrado' })]
          : h('p', { class: 'small v-w', text: 'sem registro' })),
      cartao({ titulo: 'Última suíte de testes', id: 'suite', lead: 'Registro da última suíte completa rodada nesta máquina.' },
        t ? [h('div', { class: 'src' }, h('span', { text: data(t.data) }), h('span', { class: 'small num', text: `${t.passed} passaram` }),
              h('span', { class: 'small', text: `${t.failed} falharam · ${t.skipped} pulados` })),
             t.skipped ? h('p', { class: 'small', text: 'Pulado = teste que precisa de dado fora do git; verde não significa que rodou.' }) : null]
          : h('p', { class: 'small v-w', text: 'sem registro' }))),
  ];
  return { contexto, nos };
}
