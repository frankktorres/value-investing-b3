// Casca da tela: tema, ocultar valores, busca, rota (#/hall, #/empresa/TK…) e carga do hall.json. Só leitura.
import { h, data } from './fmt.js';
import { renderHall } from './hall.js';

const VERSAO = 1;
const estado = { hall: null, erro: null, busca: '' };

function guardar(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* sem storage: só não lembra */ } }
function lembrar(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

function aplicarTema(t) {
  document.documentElement.dataset.tema = t;
  const b = document.getElementById('tema');
  b.textContent = t === 'escuro' ? 'Claro' : 'Escuro';
  b.setAttribute('aria-pressed', String(t === 'escuro'));
}

function aplicarOcultar(on) {
  document.body.classList.toggle('ocultar', on);
  document.getElementById('ocultar').setAttribute('aria-pressed', String(on));
}

const ROTAS = [
  { id: 'hall', rotulo: 'Hall' },
  { id: 'empresa', rotulo: 'Empresa', fatia: 2 },
  { id: 'carteira', rotulo: 'Carteira', fatia: 3 },
  { id: 'monitor', rotulo: 'Monitor', fatia: 4 },
];

function rota() {
  const m = /^#\/([a-z]+)(?:\/([A-Z0-9]+))?/.exec(location.hash);
  return { id: m ? m[1] : 'hall', tk: m && m[2] ? m[2] : null };
}

function nav(atual) {
  const n = document.getElementById('nav');
  n.replaceChildren(...ROTAS.map((r) => (r.fatia
    ? h('span', { title: `Próxima fatia (${r.fatia}); por ora use o comando` }, r.rotulo, h('small', { text: 'em breve' }))
    : h('a', { href: `#/${r.id}`, class: atual === r.id ? 'on' : null, 'aria-current': atual === r.id ? 'page' : null, text: r.rotulo }))));
}

function faixa() {
  const f = document.getElementById('faixa');
  const base = f.firstElementChild;
  const itens = [base];
  const hl = estado.hall;
  if (hl) {
    itens.push(h('span', {}, 'Cotação ', h('b', { text: data(hl.pregao_hoje) }), hl.dado_velho
      ? h('span', { class: 'tag tag-velho', title: `Último pregão com mais de ${hl.dias_velho} dias`, text: 'velho' }) : null));
    itens.push(h('span', {}, 'Exportado ', h('b', { text: hl.gerado_em.replace('T', ' ') })));
    for (const a of hl.avisos || []) itens.push(h('span', { class: 'tag', text: a }));
  }
  f.replaceChildren(...itens);
}

function estadoTela(titulo, ...linhas) {
  return h('div', { class: 'estado', role: 'status' }, h('h2', { text: titulo }), ...linhas.map((l) => h('p', {}, l)));
}

function render() {
  const r = rota();
  nav(r.id === 'empresa' ? 'hall' : r.id);
  faixa();
  const pag = document.getElementById('pagina');
  if (estado.erro) {
    pag.replaceChildren(estadoTela(estado.erro.titulo, ...estado.erro.linhas));
  } else if (!estado.hall) {
    pag.replaceChildren(estadoTela('Carregando…', 'Lendo dados/hall.json.'));
  } else if (r.id === 'hall') {
    pag.replaceChildren(...renderHall(estado.hall, estado.busca, render));
  } else {
    const alvo = ROTAS.find((x) => x.id === r.id);
    pag.replaceChildren(estadoTela(`${alvo ? alvo.rotulo : 'Tela'}: próxima fatia`,
      r.tk ? h('span', {}, 'Por ora, o relatório completo sai pelo comando ', h('code', { text: `relatorio ${r.tk}` }), ' (PDF em RELATORIOS/).')
           : 'Esta tela ainda não existe; o comando correspondente continua valendo.',
      h('a', { href: '#/hall', text: 'Voltar ao hall' })));
  }
}

async function carregar() {
  try {
    const resp = await fetch('dados/hall.json', { cache: 'no-store' });
    if (resp.status === 404) {
      estado.erro = { titulo: 'Sem dados ainda', linhas: [h('span', {}, 'Rode ', h('code', { text: 'painel --exportar' }), ' na raiz do projeto (ou ', h('code', { text: 'python -m painel.exportar' }), ' em ferramentas/).')] };
    } else if (!resp.ok) {
      estado.erro = { titulo: 'Erro de leitura', linhas: [`dados/hall.json respondeu ${resp.status}.`] };
    } else {
      const hl = await resp.json();
      if (hl.versao !== VERSAO) {
        estado.erro = { titulo: 'Versão dos dados diferente da tela', linhas: [`hall.json versão ${hl.versao}, a tela espera ${VERSAO}. Rode painel --exportar de novo.`] };
      } else {
        estado.hall = hl;
      }
    }
  } catch (e) {
    estado.erro = { titulo: 'Erro de leitura', linhas: [`Não consegui ler dados/hall.json (${e.message}).`] };
  }
  render();
}

function iniciar() {
  const salvo = lembrar('mesa.tema');
  aplicarTema(salvo === 'escuro' || salvo === 'claro' ? salvo
    : (window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'escuro' : 'claro'));
  aplicarOcultar(lembrar('mesa.ocultar') === '1');
  document.getElementById('tema').addEventListener('click', () => {
    const t = document.documentElement.dataset.tema === 'escuro' ? 'claro' : 'escuro';
    aplicarTema(t); guardar('mesa.tema', t);
  });
  document.getElementById('ocultar').addEventListener('click', () => {
    const on = !document.body.classList.contains('ocultar');
    aplicarOcultar(on); guardar('mesa.ocultar', on ? '1' : '0');
  });
  const busca = document.getElementById('busca');
  busca.addEventListener('input', () => { estado.busca = busca.value.trim(); if (rota().id !== 'hall') location.hash = '#/hall'; else render(); });
  document.addEventListener('keydown', (ev) => {
    if (ev.key === '/' && document.activeElement !== busca) { ev.preventDefault(); busca.focus(); }
    else if (ev.key === 'Escape' && document.activeElement === busca) { busca.value = ''; estado.busca = ''; render(); }
  });
  window.addEventListener('hashchange', render);
  render();
  carregar();
}

iniciar();
