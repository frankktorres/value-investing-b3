"""Armadilhas de valor e defeitos estruturais por ticker (doutrina §7 e §9): fonte única dos carimbos que bloqueiam a exceção
da 1ª parcela a 0,80× (`motor_financeiras.entrada_parcial`, "zero armadilhas").

O motor não calcula carimbo: cada um aqui foi escrito na doutrina ou numa ficha, com o lugar onde está. Antes (até 21/10/2026)
só o PDF do lote 6 os passava; o relatório e os PDFs dos lotes 1, 3, 4 e 5 diziam "elegível" sem olhar a ficha.
Os casos da tabela do §7 ("Caso da casa") entram como estão; tirar um exige registrar no `09` por que a armadilha acabou.
"""

DOUTRINA_7 = "01-doutrina §7 (caso da casa)"

CARIMBOS: dict[str, tuple[tuple[str, str], ...]] = {
    "UNIP6": (("dividendo não coberto por caixa (defeito estrutural)", DOUTRINA_7),
              ("ROE inflado por alavancagem", DOUTRINA_7)),
    "LEVE3": (("ROE inflado por alavancagem", DOUTRINA_7),
              ("lucro não recorrente", DOUTRINA_7)),
    "KLBN11": (("dividendo não coberto por caixa (venda de terras)", DOUTRINA_7),),
    "SAPR11": (("lucro não recorrente", DOUTRINA_7),),
    "EGIE3": (("lucro não recorrente (venda da TAG em 2024; repactuação do UBP no 2T26, R$ 1,92 bi bruto)", DOUTRINA_7),),
    "VBBR3": (("múltiplo baixo em topo de ciclo", DOUTRINA_7),),
    "PETR4": (("múltiplo baixo em topo de ciclo", DOUTRINA_7),),
    "BRSR6": (("defeito estrutural (controlador)", "03-hall-de-acoes, fora do hall (05/10)"),),
    "RECV3": (("defeito estrutural: produção em declínio com ROIC abaixo do WACC", "atualizar_hall_lote5.py (lote 5)"),),
}


def de(ticker: str) -> list[str]:
    """Carimbos do ticker no formato que `entrada_parcial(armadilhas=…)` espera (texto + onde está escrito)."""
    return [f"{c} [{f}]" for c, f in CARIMBOS.get(ticker, ())]
