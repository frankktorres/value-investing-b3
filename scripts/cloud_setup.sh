#!/usr/bin/env bash
# Preparo da sessão da rotina na nuvem (22/10/2026): a de 22/10 achou o python sem pytest e só descobriu a rede bloqueada
# no meio de uma missão. Idempotente; passo que falha não derruba a sessão (o relatório diz o que faltou).
#   bash scripts/cloud_setup.sh
set -u
cd "$(dirname "$0")/.."
/usr/bin/python3 -m pip install -q -r requirements.txt 2>&1 | grep -v "Running pip as the 'root'" | tail -3 || true
/usr/bin/python3 -m pytest --version || echo "SETUP: pytest indisponível"
command -v node >/dev/null && echo "node $(node --version) (node --check nas telas)" || echo "SETUP: sem node"
# Rede: quais fontes de dados respondem desta sessão. 403/000 = domínio fora da allowlist do ambiente da nuvem:
# registre no relatório e não chute o dado (doutrina: só fonte A/B).
for u in https://dados.cvm.gov.br https://conteudo.cvm.gov.br https://sistemaswebb3-listados.b3.com.br \
         https://www.b3.com.br https://api.bcb.gov.br https://www.gov.br https://www.tesourotransparente.gov.br; do
  c=$(curl -s -o /dev/null -m 10 -w '%{http_code}' "$u" 2>/dev/null); rc=$?
  case $rc in 0) v="responde (HTTP $c)" ;; 56|5|6) v="BLOQUEADO pela rede da nuvem (curl $rc)" ;; *) v="falhou (curl $rc)" ;; esac
  echo "rede ${u#https://} -> $v"
done
