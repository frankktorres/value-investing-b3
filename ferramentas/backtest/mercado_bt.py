"""Mercado point-in-time: rf e π da data de corte, com o prêmio do Ke como PARÂMETRO.

Dataclass PRÓPRIA, deliberadamente sem herdar de motor_financeiras.Mercado. Subclassar seria
destruído em silêncio: `central_ao_ke` (motor_financeiras.py:227) e o caminho de sensibilidade
(:348) reconstroem `Mercado(rf, pi)` por dentro, e a subclasse — com o prêmio dela — sumiria,
voltando aos 5 p.p. sem erro nenhum.

O caminho que funciona já existe nos dois motores e não exige tocá-los: ambos aceitam `ke_nom`
explícito, e o `PREMIO_KE` do módulo se CANCELA no vai-e-volta. Em `central_ao_ke`:

    rf  = (1 + ke_nom)/(1 + π) − 1 − PREMIO_KE        # desconta o prêmio
    mk2 = Mercado(rf, π)
    mk2.ke_real = rf + PREMIO_KE = (1 + ke_nom)/(1 + π) − 1
    mk2.ke_nom  = ke_nom                              # exatamente o que foi passado

Em `valores(emp, mk, ke_nom=K)` o mesmo: `ke_real` é derivado do K passado, e `wacc` mantém
`kd = mk.rf_nom + spread_kd`, de modo que o prêmio move o Ke de EQUITY e não contamina o custo da
dívida — que é precisamente o que a sensibilidade de 3 a 6 p.p. quer medir.

`tests/test_premio_parametrizado.py` prova isso trocando PREMIO_KE e exigindo resultado idêntico,
e prova o limite: `avaliar(emp, mk)`, que não recebe ke_nom, NÃO é prêmio-agnóstico — por isso o
backtest nunca o usa.
"""
from __future__ import annotations

from dataclasses import dataclass

from .config import PADRAO


@dataclass(frozen=True)
class MercadoBT:
    """Régua macro de UMA data de corte, a UM prêmio.

    rf_real: Tesouro IPCA+ sem cupom (NTN-B Principal) de vencimento mais longo à venda na data,
             taxa de fechamento (doutrina §4). Vem do Tesouro Transparente — fatia 9.
    pi:      inflação implícita da curva na data = (1+pré)/(1+IPCA+) − 1, mesmo vértice.
    premio:  o que está sob teste. 0,05 é a régua da casa.
    """
    data: str
    rf_real: float
    pi: float
    premio: float
    titulo_rf: str = ""
    vencimento_rf: str = ""
    fonte: str = ""
    pib_real_lp: float = PADRAO.pib_real_lp

    @property
    def ke_real(self) -> float:
        return self.rf_real + self.premio

    @property
    def ke_nom(self) -> float:
        """O número que se passa aos motores por `ke_nom=`. É a única porta de entrada do prêmio."""
        return (1 + self.ke_real) * (1 + self.pi) - 1

    @property
    def rf_nom(self) -> float:
        return (1 + self.rf_real) * (1 + self.pi) - 1

    @property
    def g_teto(self) -> float:
        """Teto do g perpétuo: inflação + crescimento real de longo prazo da economia (§11.1)."""
        return (1 + self.pi) * (1 + self.pib_real_lp) - 1

    @property
    def fator_graham(self) -> float:
        return (1 / self.ke_real) / 8.5

    def com_premio(self, premio: float) -> "MercadoBT":
        """Mesma data e mesma curva, outro prêmio — a grade de sensibilidade."""
        return MercadoBT(self.data, self.rf_real, self.pi, premio,
                         self.titulo_rf, self.vencimento_rf, self.fonte, self.pib_real_lp)

    def procedencia(self) -> dict[str, object]:
        """Vai como COLUNA do painel, não como log: é o que torna o teste sentinela possível."""
        return {"data_macro": self.data, "rf_real": self.rf_real, "pi": self.pi,
                "premio": self.premio, "titulo_rf": self.titulo_rf,
                "vencimento_rf": self.vencimento_rf, "fonte_macro": self.fonte}
