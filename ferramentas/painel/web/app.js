// Casca da tela v0.2: rotas, carga do contrato (dados/contrato/ + dados/privado/carteira.json), tema, Ocultar valores,
// busca e teclado. Só leitura; nada é recalculado aqui.
import { h, data } from './fmt.js';
import { configurar, carregando, faixaErro } from './ui.js';
import { telaHall } from './telas/hall.js';
import { telaEmpresa } from './telas/empresa.js';
import { telaCarteira } from './telas/carteira.js';
import { telaMonitor } from './telas/monitor.js';
import { telaSistema } from './telas/sistema.js';

const VERSAO = 2;
const ARQ = {
  hall: 'dados/contrato/hall.json',
  carteira: 'dados/privado/carteira.json',
  monitor: 'dados/contrato/monitor.json',
  sistema: 'dados/contrato/sistema.json',
  empresa: (tk) => `dados/contrato/empresa/${tk}.json`,
};

const estado = {
  hall: null, carteira: null, monitor: null, sistema: null, empresas: {},
  erros: {}, ocultar: false, busca: '',
  hallVista: { filtro: 'todas', ordem: 'pc', soAB: false },
};

function guardar(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* sem storage: só não lembra */ } }
function lembrar(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

async function ler(caminho) {
  let resp;
  try {
    resp = await fetch(caminho, { cache: 'no-store' });
  } catch (e) {
    return { erro: `Não foi possível ler ${caminho} (${e.message}).` };
  }
  if (resp.status === 404) return { erro: `Não foi possível ler ${caminho}: arquivo ausente. Rode painel --exportar na raiz do projeto.` };
  if (!resp.ok) return { erro: `Não foi possível ler ${caminho}: o servidor respondeu ${resp.status}.` };
  try {
    const j = await resp.json();
    if (j.versao === undefined || j.versao === null) return { erro: `${caminho} não informa a versão do contrato; a tela espera ${VERSAO}. Rode painel --exportar de novo.` };
    if (j.versao !== VERSAO) return { erro: `${caminho} está na versão ${j.versao}; a tela espera ${VERSAO}. Rode painel --exportar de novo.` };
    return { dado: j };
  } catch (e) {
    return { erro: `Não foi possível ler ${caminho}: JSON inválido.` };
  }
}

// ------------------------------------------------------------------------------ tema e privacidade
function aplicarTema(t) {
  document.documentElement.dataset.tema = t;
  document.getElementById('tema-rot').textContent = t === 'escuro' ? 'Modo claro' : 'Modo escuro';
}

function aplicarOcultar(on) {
  estado.ocultar = on;
  document.getElementById('ocultar').setAttribute('aria-pressed', String(on));
}

// ------------------------------------------------------------------------------ rotas
const ROTAS = ['hall', 'empresa', 'carteira', 'monitor', 'sistema'];
function rota() {
  const m = /^#\/([a-z]+)(?:\/([A-Za-z0-9]{4,8}))?\/?$/.exec(location.hash);
  return { id: m ? m[1] : (['', '#', '#/'].includes(location.hash) ? 'hall' : '?'), tk: m && m[2] ? m[2].toUpperCase() : null };
}

export function navegar(hash) { if (location.hash !== hash) location.hash = hash; else render(); }

function marcarMenu(id) {
  for (const a of document.querySelectorAll('.snav a[data-rota]')) {
    const on = a.dataset.rota === id;
    a.classList.toggle('on', on);
    if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
  }
}

function rodape(id) {
  const r = document.getElementById('rodape');
  const base = r.firstElementChild;
  const itens = [base];
  const hl = estado.hall;
  if (hl) {
    itens.push(h('span', {}, 'Cotação ', h('b', { text: data(hl.cotacao_em) })));
    itens.push(h('span', {}, 'Exportado ', h('b', { text: hl.exportado_em ? hl.exportado_em.replace('T', ' ') : '—' })));
  }
  if (id === 'carteira') itens.push(h('span', { text: 'Dados pessoais ficam neste computador.' }));
  r.replaceChildren(...itens);
}

function ctx() {
  const porTk = {};
  for (const p of (estado.carteira && estado.carteira.posicoes) || []) porTk[p.ticker] = p;
  const linhas = {};
  for (const e of (estado.hall && estado.hall.empresas) || []) linhas[e.ticker] = e;
  return { estado, ocultar: estado.ocultar, carteiraPorTk: porTk, linhas, render, navegar, ARQ };
}

let renderizando = null;
export function render() {
  const r = rota();
  const pag = document.getElementById('pagina');
  marcarMenu(r.id);
  rodape(r.id);
  const contexto = document.getElementById('contexto');
  if (estado.erros.hall) {
    contexto.textContent = 'Erro de leitura';
    pag.replaceChildren(faixaErro(estado.erros.hall));
    return;
  }
  if (!estado.hall) {
    pag.replaceChildren(carregando(6));
    return;
  }
  const c = ctx();
  let out;
  if (!ROTAS.includes(r.id)) {                       // hash desconhecido não cai calado no Hall (N9)
    contexto.textContent = 'Página não encontrada';
    pag.replaceChildren(faixaErro(`A página "${location.hash}" não existe. Use o menu ou volte ao Hall (#/hall).`));
    return;
  }
  if (r.id === 'empresa') {
    const tk = r.tk || lembrar('mesa.ultima');
    if (tk && !r.tk) { navegar(`#/empresa/${tk}`); return; }
    if (tk) guardar('mesa.ultima', tk);
    if (tk && !estado.empresas[tk] && !estado.erros[`empresa:${tk}`] && renderizando !== tk) {
      renderizando = tk;
      ler(ARQ.empresa(tk)).then(({ dado, erro }) => {
        renderizando = null;
        if (dado) estado.empresas[tk] = dado; else estado.erros[`empresa:${tk}`] = erro;
        if (rota().tk === tk) render();
      });
    }
    out = telaEmpresa(c, tk);
  } else if (r.id === 'carteira') out = telaCarteira(c);
  else if (r.id === 'monitor') out = telaMonitor(c);
  else if (r.id === 'sistema') out = telaSistema(c);
  else out = telaHall(c);
  contexto.textContent = out.contexto;
  pag.replaceChildren(...out.nos.filter((n) => n !== null && n !== undefined && n !== false));
  if (out.depois) out.depois();
}

// ------------------------------------------------------------------------------ início
function teclado() {
  const busca = document.getElementById('busca');
  let g = 0;
  document.addEventListener('keydown', (ev) => {
    const emCampo = ['INPUT', 'SELECT', 'TEXTAREA'].includes(document.activeElement && document.activeElement.tagName);
    if (ev.key === '/' && !emCampo) { ev.preventDefault(); busca.focus(); busca.select(); return; }
    if (ev.key === 'Escape' && document.activeElement === busca) { busca.value = ''; estado.busca = ''; render(); return; }
    if (emCampo || ev.ctrlKey || ev.metaKey || ev.altKey) return;
    if (ev.key === 'g') { g = Date.now(); return; }
    if (g && Date.now() - g < 1200) {
      const destino = { h: '#/hall', e: '#/empresa', c: '#/carteira', m: '#/monitor' }[ev.key];
      g = 0;
      if (destino) { ev.preventDefault(); navegar(destino); return; }
    }
    if ((ev.key === 'ArrowDown' || ev.key === 'ArrowUp') && rota().id === 'hall') {
      const links = [...document.querySelectorAll('#pagina a.tk')];
      if (!links.length) return;
      ev.preventDefault();
      const i = links.indexOf(document.activeElement);
      const j = ev.key === 'ArrowDown' ? Math.min(i + 1, links.length - 1) : Math.max(i - 1, 0);
      links[i < 0 ? 0 : j].focus();
    }
  });
  busca.addEventListener('input', () => {
    estado.busca = busca.value.trim();
    if (rota().id !== 'hall') navegar('#/hall'); else render();
  });
  busca.addEventListener('keydown', (ev) => {
    if (ev.key !== 'Enter') return;
    const primeiro = document.querySelector('#pagina a.tk');
    if (primeiro) { ev.preventDefault(); location.hash = primeiro.getAttribute('href'); }
  });
}

async function iniciar() {
  const salvo = lembrar('mesa.tema');
  aplicarTema(salvo === 'claro' ? 'claro' : 'escuro');          // escuro é o padrão (HANDOFF §3)
  aplicarOcultar(lembrar('mesa.ocultar') === '1');
  document.getElementById('tema').addEventListener('click', () => {
    const t = document.documentElement.dataset.tema === 'escuro' ? 'claro' : 'escuro';
    aplicarTema(t); guardar('mesa.tema', t);
  });
  document.getElementById('ocultar').addEventListener('click', () => {
    aplicarOcultar(!estado.ocultar); guardar('mesa.ocultar', estado.ocultar ? '1' : '0'); render();
  });
  teclado();
  document.querySelector('.pular').addEventListener('click', (ev) => {   // não troca a rota: só leva o foco ao conteúdo
    ev.preventDefault(); document.getElementById('pagina').focus();
  });
  window.addEventListener('hashchange', () => { render(); document.getElementById('pagina').scrollTop = 0; window.scrollTo(0, 0); });
  render();
  const [hl, ct, mn, sy] = await Promise.all([ler(ARQ.hall), ler(ARQ.carteira), ler(ARQ.monitor), ler(ARQ.sistema)]);
  if (hl.dado && !(hl.dado.fatores && Array.isArray(hl.dado.fatores.escala_regua) && Array.isArray(hl.dado.empresas))) {
    estado.erros.hall = `${ARQ.hall} está incompleto (faltam fatores, escala da régua ou empresas). Rode painel --exportar de novo.`;
  } else if (hl.dado) { estado.hall = hl.dado; configurar(hl.dado.fatores); } else estado.erros.hall = hl.erro;
  if (ct.dado) estado.carteira = ct.dado; else estado.erros.carteira = ct.erro;
  if (mn.dado) estado.monitor = mn.dado; else estado.erros.monitor = mn.erro;
  if (sy.dado) estado.sistema = sy.dado; else estado.erros.sistema = sy.erro;
  render();
}

iniciar();
