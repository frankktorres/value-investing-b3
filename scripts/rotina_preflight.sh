#!/usr/bin/env bash
# Pré-voo da rotina noturna da Mesa (26/11/2026; ideia do pré-voo do UNION, sem regra clínica). Ver docs/ops/rotina/PROTOCOLO.md §0.
# Roda em 2º plano (o comando da sessão na nuvem morre em 10 min):
#   nohup bash scripts/rotina_preflight.sh > /tmp/mesa_prevoo.out 2>&1 &
# Grava SEMPRE o marcador <SAIDA sem .md>.fim com o código: 0 = base verde; 1 = BASE VERMELHA; 2 = AMBIENTE QUEBRADO.
# Bloco do relatório em $MESA_PREVOO (padrão /tmp/mesa_prevoo.md); Python escolhido em <base>_python; rede em <base>_rede.json.
set -u
SAIDA="${MESA_PREVOO:-/tmp/mesa_prevoo.md}"
BASE="${SAIDA%.md}"
FIM="$BASE.fim"
rm -f "$FIM"
FIM_OK=0
CODIGO=2
trap 'if [ "$FIM_OK" = 1 ]; then echo "$CODIGO" > "$FIM"; else echo 2 > "$FIM"; fi' EXIT
trap 'exit 2' TERM HUP INT
: > "$SAIDA"
linha() { printf '%s\n' "$*" >> "$SAIDA"; }
fim() { CODIGO="$1"; FIM_OK=1; cat "$SAIDA"; exit "$1"; }
quebrado() { linha "- **AMBIENTE QUEBRADO:** $*"; fim 2; }

linha "### Pré-voo da noite"
linha "- início (UTC): $(date -u +%Y-%m-%dT%H:%MZ)"
RAIZ="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null)" || RAIZ=""
[ -n "$RAIZ" ] || quebrado "pré-voo fora de um repositório git"
cd "$RAIZ" || quebrado "não entrei em $RAIZ"
if [ "$(git rev-parse --is-shallow-repository 2>/dev/null)" = true ]; then git fetch -q --unshallow origin || true; fi
git fetch -q origin || quebrado "git fetch origin falhou"
linha "- HEAD $(git rev-parse --short HEAD) · origin/master $(git rev-parse --short origin/master 2>/dev/null || echo '?')"

# Python 3.14 por uv (a nuvem traz 3.11); sem uv/download → python3 do sistema, com aviso (as noites de outubro rodaram nele).
LOGUV="${BASE}_uv.log"
: > "$LOGUV"
VENV="${MESA_VENV:-$HOME/venv314}"
e314() { [ -x "$1" ] && "$1" -c 'import sys; sys.exit(sys.version_info[:2] != (3, 14))' 2>/dev/null; }
UV="$(command -v uv 2>/dev/null || true)"
if [ -z "$UV" ]; then
  python3 -m pip install -q --user uv >>"$LOGUV" 2>&1 || python3 -m pip install -q uv >>"$LOGUV" 2>&1 || true
  UV="$(command -v uv 2>/dev/null || true)"
  [ -z "$UV" ] && [ -x "$HOME/.local/bin/uv" ] && UV="$HOME/.local/bin/uv"
fi
if [ -n "$UV" ] && ! e314 "$VENV/bin/python"; then
  "$UV" python install 3.14 >>"$LOGUV" 2>&1 && "$UV" venv -q --clear -p 3.14 "$VENV" >>"$LOGUV" 2>&1 || true
fi
if e314 "$VENV/bin/python"; then
  PY="$VENV/bin/python"
  if [ "${MESA_PREVOO_SEM_INSTALAR:-0}" != 1 ]; then
    if [ -n "$UV" ]; then "$UV" pip install -q -p "$PY" -r requirements.txt >>"$LOGUV" 2>&1 || quebrado "uv pip install falhou (ver $LOGUV)"
    else "$PY" -m pip install -q -r requirements.txt >>"$LOGUV" 2>&1 || quebrado "pip install falhou (ver $LOGUV)"; fi
  fi
else
  PY="$(command -v python3 2>/dev/null || true)"
  [ -n "$PY" ] || quebrado "sem python3 e sem Python 3.14 (ver $LOGUV)"
  linha "- **aviso:** Python 3.14 indisponível (uv/download; ver $LOGUV) → $("$PY" -V 2>&1) do sistema"
  if [ "${MESA_PREVOO_SEM_INSTALAR:-0}" != 1 ]; then
    "$PY" -m pip install -q -r requirements.txt >>"$LOGUV" 2>&1 || quebrado "pip install falhou (ver $LOGUV)"
  fi
fi
"$PY" -c "import pytest, pandas, numpy" >>"$LOGUV" 2>&1 || quebrado "pytest/pandas/numpy não importam em $PY"
printf '%s\n' "$PY" > "${BASE}_python"
linha "- Python: $("$PY" -V 2>&1) ($PY)"

# Sonda de rede: domínios de dados da Mesa + os `fonte:` das missões carimbadas na base.
DOMINIOS="dados.cvm.gov.br conteudo.cvm.gov.br sistemaswebb3-listados.b3.com.br www.b3.com.br api.bcb.gov.br www.gov.br www.tesourotransparente.gov.br"
EXTRA="$(git show origin/master:docs/MISSOES.md 2>/dev/null | grep 'Carimbo (nuvem)' | grep -o 'fonte: *`[^`]*`' \
  | sed 's/.*`\(.*\)`/\1/' | tr ',' ' ' | tr ' ' '\n' | grep -v '^nenhuma$' | grep '\.' | sort -u | tr '\n' ' ')"
REDE="${BASE}_rede.json"
CORPO="${BASE}_corpo.tmp"
printf '{' > "$REDE"
sep=""
resumo=""
for d in $DOMINIOS $EXTRA; do
  c="$(curl -s -o "$CORPO" -m 15 -w '%{http_code}' "https://$d/" 2>/dev/null)"; rc=$?
  if [ "$rc" -ne 0 ] || [ "$c" = 000 ]; then e="BLOQUEADO(curl $rc)"
  elif grep -q host_not_allowed "$CORPO" 2>/dev/null; then e="BLOQUEADO(proxy $c)"
  else e="$c"; fi
  printf '%s"%s": "%s"' "$sep" "$d" "$e" >> "$REDE"; sep=", "
  resumo="$resumo $d=$e"
done
printf '}\n' >> "$REDE"
rm -f "$CORPO"
linha "- rede:$resumo"

# Suíte na base (sem backtest; ~42 testes pulam sem os dados locais — a manhã confere com EXIGIR_DADOS=1).
SUITE="${BASE}_suite.log"
( cd ferramentas && PYTHONHASHSEED=0 CLAUDE_NO_SUITE_LOG=1 timeout 3600 "$PY" -m pytest --ignore=backtest -q -p no:cacheprovider -ra ) > "$SUITE" 2>&1
RC=$?
RESUMO="$(grep -E '[0-9]+ (passed|failed|error)' "$SUITE" | tail -1 | tr -d '=' | sed 's/^ *//')"
linha "- suíte da base: rc $RC · ${RESUMO:-sem resumo} (log $SUITE)"
[ "$RC" -eq 0 ] && { linha "- **VERDE**"; fim 0; }
MOD="$(grep -oE "ModuleNotFoundError: No module named '[^']+'" "$SUITE" | head -1 | sed "s/.*'\(.*\)'/\1/")"
if [ -n "$MOD" ] && ! git ls-files | grep -qE "(^|/)${MOD%%.*}(\.py|/)"; then quebrado "módulo de terceiro ausente: $MOD"; fi
if { [ "$RC" -eq 1 ] || [ "$RC" -eq 2 ]; } && grep -qE '^(FAILED|ERROR) ' "$SUITE"; then
  linha "- **BASE VERMELHA:**"
  grep -E '^(FAILED|ERROR) ' "$SUITE" | head -15 | sed 's/^/  - /' >> "$SAIDA"
  fim 1
fi
quebrado "pytest rc $RC sem falha nomeada (124 = timeout; ver $SUITE)"
