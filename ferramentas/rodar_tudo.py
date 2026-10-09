"""Roda os 6 lotes, compara com o golden e imprime 'o que mudou e por quê'.

Uso: python rodar_tudo.py            → só mostra o diff (código de saída 1 se houver mudança)
     python rodar_tudo.py --motivo "…" → além do diff, regrava o golden com o motivo (vai para tests/golden_log.md)
"""
import argparse
import sys
from collections import Counter

import golden
import mercado
import universo


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--motivo", help="regrava o golden com este motivo")
    args = ap.parse_args()
    todos = universo.avaliar_todos()
    atual = {tk: universo.instantaneo(it) for tk, it in sorted(todos.items())}
    palavras = Counter(s["palavra"] for s in atual.values())
    print(f"{len(atual)} tickers · " + " · ".join(f"{k} {v}" for k, v in sorted(palavras.items())))
    # AUD-72: idade do preço e da taxa (regra 3 do 00-CONFIGURACAO), calculada, não escrita à mão
    mv = mercado.dados()
    print(f"mercado de {universo.MK.data} ({mercado.idade_dias(mv['data'])} dias): rf {universo.MK.rf_real:.2%} real, "
          f"{mv['rf_tipo']} · π {universo.MK.pi:.2%}")
    aviso = mercado.aviso_idade(mv["data"])
    if aviso:
        print(aviso)
    try:
        ant = golden.carregar()
    except FileNotFoundError:
        ant = {}
    mud = golden.comparar(ant, atual)
    if not mud:
        print("sem mudanças em relação ao golden.")
    else:
        trocas = [(tk, x, y) for tk, rot, x, y in mud if rot == "palavra"]
        print(f"{len(mud)} mudanças em {len({m[0] for m in mud})} tickers; {len(trocas)} trocas de palavra")
        print(golden.formatar(mud))
        if not args.motivo:
            print("\nPara aceitar: python rodar_tudo.py --motivo \"o que mudou e por quê\"")
    if args.motivo:
        golden.salvar(atual, args.motivo)
        print(f"\ngolden regravado. Motivo: {args.motivo}")
    # AUD-77: células numéricas e marca (S) do 03, e o hall do prompt de sexta, são gerados do motor
    import hall03
    esp = hall03.esperado(todos)
    div = hall03.divergencias(hall03.HALL.read_text(encoding="utf-8"), esp)
    prompt_ok = hall03.bloco_do_prompt(hall03.PROMPT.read_text(encoding="utf-8")) == hall03.lista_prompt(esp)
    if div or not prompt_ok:
        print(f"\n03: {len(div)} célula(s) fora do motor; prompt de sexta {'ok' if prompt_ok else 'DIVERGE'} "
              "→ python hall03.py --corrigir")
    return 1 if mud and not args.motivo else 0


if __name__ == "__main__":
    sys.exit(main())
