"""Parâmetros da triagem — declarados ANTES da primeira rodada (06/10/2026), com a origem de cada um.

Mudar qualquer número aqui muda o hash impresso no `06`; o hash é a prova de qual régua gerou a fila.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ConfigTriagem:
    # ---- liquidez pela posição do Frank (decisão dele em 06/10/2026: posição típica até R$ 50 mil).
    # Regra de saída: vender a posição inteira em `pregoes_saida` pregões usando no máximo
    # `participacao_max` do volume diário -> volume mínimo = posição ÷ (pregões × participação).
    # O piso efetivo é o MAIOR entre isso e o piso do backtest (R$ 500 mil de 2014-05 corrigidos
    # pelo IPCA, backtest.config.limite_liquidez) — com R$ 50 mil vale o do backtest.
    posicao_tipica: float = 50_000.0
    pregoes_saida: int = 5
    participacao_max: float = 0.10

    # ---- exclusões estruturais (doutrina §8 e §2)
    min_exercicios: int = 7               # PLANO F4: "menos de 7 anos de demonstrações"
    # FCA Situacao_Emissor (normalizado): só a fase operacional passa.
    situacao_ok: tuple[str, ...] = ("fase operacional",)
    # CODBDI do último pregão <= T que denuncia recuperação/sanção (cotahist.BDI_UNIVERSO menos o 02):
    # 05 sancionada pela B3 · 06 concordata · 07 recuperação extrajudicial · 08 recuperação judicial
    # · 09 RAET · 11 intervenção · 58 Chapter 11 e afins.
    codbdi_exclui: tuple[str, ...] = ("05", "06", "07", "08", "09", "11", "58")
    # §8 pelo setor da FCA (chave de backtest.motor.perfil.setor_chave)
    setores_excluidos: tuple[tuple[str, str], ...] = (
        ("educacao", "§8: educação superior privada (receita dependente de crédito estudantil)"),
    )
    # §8 "tecnologia sem lucro": setor da FCA + lucro mediano da janela <= 0
    setores_sem_lucro: tuple[str, ...] = ("comunicacao e informatica",)
    # §8 por ticker — a FCA não separa (aviação cai em "transporte e logística"; resseguro em
    # "seguradoras e corretoras"). Raiz de 4 letras: pega todas as classes.
    raizes_excluidas: tuple[tuple[str, str], ...] = (
        ("AZUL", "§8: aviação"),
        ("GOLL", "§8: aviação"),
        ("IRBR", "§8: resseguro (um evento zera anos de lucro)"),
    )

    # ---- qualidade (PLANO F4, "Qualidade Buffett"); fração da janela válida
    q1_frac: float = 0.70                 # ROIC real > WACC real em >= 7 de 10
    q2_frac: float = 0.80                 # FCO > 0 em >= 8 de 10
    q3_dl_ebitda: float = 2.5
    q4_minimo: float = 1.0                # R$ 1 retido virou >= R$ 1 de valor de mercado
    q4_acoes_variacao: float = 0.10       # ações mudaram > 10% na janela -> pendência
    # Acrescentados após a 1ª rodada de 06/10/2026, por defeito de CONTA, não de resultado: ODPV3
    # distribui ~100% e o retido perto de zero dava "R$ 1 -> R$ −6,93" (razão sem sentido); papel
    # com IPO no meio da janela não tinha preço em D0 e caía em "indet". Declarados no 06.
    q4_materialidade: float = 0.10        # retido < 10% do valor de mercado inicial -> n/a
    q4_min_exercicios: int = 3            # janela com preço mínima após IPO
    # Quebra estrutural (achado do adversário em 06/10/2026: SAUD3 = Odontoprev + incorporação em
    # 2026; os DFPs medem a empresa antiga e o preço a nova). Vai para "avaliar à mão", fora do portão.
    quebra_var_acoes: float = 0.50        # |ações em T ÷ ações em D0 − 1| acima disso
    quebra_ativo: float = 3.0             # ativo do ITR mais novo ÷ ativo do último DFP acima disso
    q5_frac: float = 0.80                 # pagou provento em >= 8 de 10
    max_reprovacoes_q2_q5: int = 1        # Q1 obrigatório e no máximo 1 reprovação entre Q2..Q5

    # ---- preço (sem palavra). Erro do proxy MEDIDO na Etapa 3 (consulta única, PLANO F3):
    # mediana |ΔP/C| = 0,340 nos 41 do golden. Corte = limite de CARA + erro a favor.
    erro_proxy_pc: float = 0.34
    limite_cara: float = 1.10
    disp_confiavel: float = 3.00          # acima disso (ou âncora <= 0) o central rápido não vale
    disp_alerta: float = 1.80
    netnet_fracao: float = 2 / 3          # Graham: preço <= 2/3 do NCAV por ação
    tamanho_fila: int = 20
    # Fila ORDENADA, não cortada (decisão de 06/10/2026, depois da 1ª rodada: com o portão acima só
    # 6 de 104 passam e só 1 fica abaixo do corte de preço). Camada A = passa no portão; camada B =
    # >= `fila_min_ok` testes aprovados, com o que reprovou escrito como pergunta. Mesmo papel do
    # `06` de 07/09 ("entra com >= 5 de 7"): define a fila, nunca o veredito.
    fila_min_ok: int = 3

    # ---- mercado: OS MESMOS do hall (lote1_bancos.MK); um teste confere que não divergem.
    rf_real: float = 0.0706
    pi: float = 0.0646
    premio: float = 0.05
    data_mercado: str = "2026-10-02"
    titulo_rf: str = "Tesouro IPCA+ 15/08/2050 (Tesouro Transparente, dados/mercado.json)"
    aviso_mercado_dias: int = 15          # 00-CONFIGURACAO regra 3

    @property
    def corte_pc(self) -> float:
        return round(self.limite_cara + self.erro_proxy_pc, 4)

    @property
    def volume_minimo_posicao(self) -> float:
        return self.posicao_tipica / (self.pregoes_saida * self.participacao_max)


# Notas do `06` de 07/09/2026 (régua v2.0, triagem manual) — a triagem mecânica NÃO exclui por elas,
# só as mostra ao lado. Texto copiado do arquivo em _historico/2026-10-06 antes da Etapa 4/.
NOTAS_06_ANTIGO: dict[str, str] = {
    "ODPV3": "fila 07/09: o P/L de 14 cabe no valor? Bradesco controlador e canal ao mesmo tempo (V4)",
    "DIRR3": "fila 07/09: dependência do MCMV é moat ou risco político? Free float e tag along",
    "ALUP11": "fila 07/09: repetir o teste TIR real vs IPCA+ que reprovou a Taesa",
    "BRAP4": "fila 07/09: SOTP e desconto de holding, como em ITSA4; mono-ativo",
    "VULC3": "fila 07/09: só paga desde 2020 — o dividendo é política ou humor do dono?",
    "GRND3": "fila 07/09: renda pura sem dívida, mas crescimento zero: é armadilha de caixa?",
    "AXIA3": "descartada 07/09: V2 consumado (MP 579) + contingência do empréstimo compulsório",
    "AURE3": "descartada 07/09: prejuízo pós-AES, dívida alta, sem dividendo relevante",
    "TOTS3": "descartada 07/09: compounder com DY 2–3% (Fisher compraria, carteira de renda não)",
    "RENT3": "descartada 07/09: compounder com DY 2–3% (Fisher compraria, carteira de renda não)",
    "MILS3": "descartada 07/09: compounder com DY 2–3% (Fisher compraria, carteira de renda não)",
    **{t: "reserva 07/09: falhava em preço, histórico curto ou payout não coberto"
       for t in ("MULT3", "ALOS3", "VALE3", "MOTV3", "PASS3", "FESA4", "CURY3", "LREN3", "MDIA3",
                 "GMAT3", "NEOE3")},
}

# Tickers líquidos que a FCA `valor_mobiliario` não liga a nenhum CNPJ (código com lixo: CSN "4030",
# CMIN "25585", BTG "000000", Marfrig "ADR"). CNPJ conferido em 06/10/2026 pelo NOME na FCA 2026
# `geral` (fonte A) contra o NOMRES do COTAHIST. MBRF3 = Marfrig após incorporar a BRF (BRFS3 tem
# fim de negociação 2025-09-22 na FCA). Só entra aqui o que tem nome inequívoco.
IDENTIDADE_MANUAL: dict[str, str] = {
    "CSNA3": "33.042.730/0001-04",    # CIA SIDERURGICA NACIONAL  · NOMRES "SID NACIONAL"
    "CMIN3": "08.902.291/0001-15",    # CSN MINERAÇÃO S.A.        · NOMRES "CSNMINERACAO"
    "BPAC11": "30.306.294/0001-45",   # BCO BTG PACTUAL S.A.      · NOMRES "BTGP BANCO"
    "BPAC3": "30.306.294/0001-45",
    "BPAC5": "30.306.294/0001-45",
    "MBRF3": "03.853.896/0001-40",    # MARFRIG GLOBAL FOODS S.A. · NOMRES "MARFRIG"
}

PADRAO = ConfigTriagem()


def hash_config(cfg: ConfigTriagem = PADRAO) -> str:
    bruto = json.dumps(asdict(cfg), sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(bruto.encode("utf-8")).hexdigest()[:16]
