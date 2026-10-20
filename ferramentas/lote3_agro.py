"""Lote 3 — Papel e celulose, infraestrutura de mercado e agro · data-base 02/10/2026 · doutrina v2.0.

Demonstrações e ações: CVM (DFP 2016–25 + ITR, LTM até 2T26; SMTO3 exercício abr–mar até mar/2026; ações da composição do
capital do último DFP, `acoes`). Preço: COTAHIST (precos_hall). Proventos (DPA/JCP): B3 por data-com (`proventos_hall`,
nota A — fase 3, fatia 2). P/L histórico: CVM + COTAHIST (`pl_historico.do_hall`, nota A — fase 3, fatia 3; SMTO3 no fechamento de março). Mercado: mesmo do Lote 1 (Tesouro Transparente, ANBIMA, BCB).
P/L histórico só entra no Bogle quando o lucro não é dominado por câmbio/ciclo (B3SA3, SMTO3, SLCE3); nas demais o Bogle
vai sem re-rating — declarado.
"""
import sys

from lote1_bancos import MK
import proventos_hall
from pl_historico import do_hall
from precos_hall import preco
from insumos_a import ACOES_DFP, NAV_SLCE3, registrar
from motor_financeiras import SEM_RAZAO
from motor_nao_financeiras import CVM, SI, Industrial, avaliar

QUAL = lambda moat, gestao, controlador, ciclo, fisher: dict(moat=moat, gestao=gestao, controlador=controlador, ciclo=ciclo, fisher=fisher)


def jcp(tk):
    """Fatia do JCP no provento de 2024–25. Registrado com a nota da B3 quando o DPA/JCP do SI é o da B3 (fase 3, fatia 2);
    as financeiras (ITSA4, EGIE3) seguem na StatusInvest."""
    s = SI[tk]
    tot = sum(s["dpa_por_ano_datacom"].get(a, 0) for a in ("2024", "2025"))
    j = sum(s["jcp_por_ano_datacom"].get(a, 0) for a in ("2024", "2025"))
    share = j / tot if tot else 0.0
    o = proventos_hall.origem(tk, SI)
    return registrar(tk, "jcp_share", share, o) if o else share


def acoes(tk):
    """Ações em circulação (sem tesouraria) do último DFP na CVM; KLBN11 em units (5 ações)."""
    ano = "2026" if tk == "SMTO3" else "2025"
    n = CVM[tk]["anual"][ano]["acoes"]
    if n < 1e7:          # alguns formulários da CVM informam a quantidade em milhares
        n *= 1000
    unit = CVM[tk]["acoes_por_unit"]
    return registrar(tk, "acoes", n / unit, ACOES_DFP(ano, unit))   # fase 3: procedência por campo; o número não muda


# Preços = fechamento oficial (PREULT do COTAHIST) de 02/10/2026, lido do snapshot por precos_hall.preco (fase 3, fatia 3; AUD-67).
# Fase 3, fatia 3 (20/10/2026): NAV da própria SLC no lugar do NAV de terceiro (R$ 27,12, atribuído ao Itaú BBA, origem não
# encontrada pelo verificador-fonte): fato relevante "Portfólio de Terras: Atualização 2026" (15/06/2026, RI/CVM), terras avaliadas
# pela Deloitte (R$ 13,53 bi, terra nua, NBR 14653) líquidas de impostos e da parte dos FIPs + demais itens contábeis de 31/03/2026.
SLCE3_NAV_MI, SLCE3_NAV_ACOES = 13_824, 498_745_930
EMPRESAS = [
    Industrial("SUZB3", "Suzano", "ciclica", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=preco("SUZB3"), n_acoes=acoes("SUZB3"), g_real=0.01, jcp_share=jcp("SUZB3"),
               qualitativo=QUAL(4, 4, 4, 2, 3)),
    Industrial("KLBN11", "Klabin (unit)", "ciclica", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=preco("KLBN11"), n_acoes=acoes("KLBN11"), g_real=0.01, jcp_share=jcp("KLBN11"),
               qualitativo=QUAL(3, 3, 3, 2, 3)),
    Industrial("RANI3", "Irani", "ciclica", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=preco("RANI3"), n_acoes=acoes("RANI3"), g_real=0.01, jcp_share=jcp("RANI3"),
               qualitativo=QUAL(2, 3, 3, 2, 3)),
    Industrial("B3SA3", "B3", "servicos", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=preco("B3SA3"), n_acoes=acoes("B3SA3"), g_real=0.02, jcp_share=jcp("B3SA3"),
               pl_hist=do_hall("B3SA3", acoes("B3SA3")), qualitativo=QUAL(5, 4, 4, 3, 4)),
    Industrial("SMTO3", "São Martinho", "ciclica", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=preco("SMTO3"), n_acoes=acoes("SMTO3"), g_real=0.01, jcp_share=jcp("SMTO3"),
               anos_ciclo=[str(a) for a in range(2017, 2027)], pl_hist=do_hall("SMTO3", acoes("SMTO3"), mes_fim=3), qualitativo=QUAL(3, 4, 4, 2, 3),
               janela_razao="exercício social abr–mar: são os 10 exercícios fechados até mar/2026 (o '2026' da série é abr/2025–mar/2026), "
                            "não uma janela curta"),
    Industrial("KEPL3", "Kepler Weber", "ciclica", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=preco("KEPL3"), n_acoes=acoes("KEPL3"), g_real=0.01, jcp_share=jcp("KEPL3"),
               qualitativo=QUAL(3, 3, 3, 2, 3)),
    Industrial("SLCE3", "SLC Agrícola", "ciclica", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=preco("SLCE3"), n_acoes=acoes("SLCE3"), g_real=0.01, jcp_share=jcp("SLCE3"),
               pl_hist=do_hall("SLCE3", acoes("SLCE3")), reproducao_por_acao=registrar("SLCE3", "reproducao_por_acao", SLCE3_NAV_MI * 1e6 / SLCE3_NAV_ACOES, NAV_SLCE3),
               reproducao_fonte="NAV R$ 13.824 mi ÷ 498.745.930 ações = R$ 27,72/ação (fato relevante SLC de 15/06/2026: terras avaliadas pela Deloitte, demais itens contábeis de 31/03/2026) [A] — o PL contábil registra terra a custo histórico",
               qualitativo=QUAL(3, 4, 4, 2, 3)),
]

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Ke nominal {MK.ke_nom:.2%} | RF real líq {MK.rf_liq_real:.2%}")
    for e in EMPRESAS:
        r = avaliar(e, MK)
        anc = " | ".join(f"{k}: {x:.2f}" for k, x in r["ancoras"].items())
        ki = r["ke_implicito"]; gi = r["g_implicito"]
        print(f"{e.ticker:6} P {e.preco:6.2f} central {r['central']:6.2f} P/C {r['pc']:.2f} {r['palavra']:6} disp {r['dispersao']:.2f} | {anc}")
        print(f"       WACC {r['wacc']:.1%} ROIC {r['roic']:.1%} margem {r['m']:.1%} (p25 {r['op']['m25']:.1%} p75 {r['op']['m75']:.1%}) rec_meio {r['op']['receita_meio']/1e6:.1f}bi "
              f"DL/EBITDA {r['dl_ebitda'] and round(r['dl_ebitda'],2)} norm {r['dl_ebitda_norm'] and round(r['dl_ebitda_norm'],2)} cob {r['cobertura_juros'] and round(r['cobertura_juros'],1)}")
        print(f"       Ke* {ki and f'{ki:.1%}'} g_real* {gi and f'{gi:.1%}'} | Bogle {r['bogle_nom']:.1%} liq real {r['bogle_liq_real']:.1%} RF {r['vence_rf']}/{r['rf_sem_rerating']} | "
              f"OE {r['oe_norm'] and round(r['oe_norm']/1e3)} mi DPA5 {r['dpa5']:.2f} FCFE/ação {r['fcfe_acao']:.2f} coberto {r['coberto']} | "
              f"Z'' {r['altman']:.2f} {r['altman_zona']} F {r['piotroski']} M {r['beneish'] and round(r['beneish'],2)} Sloan {r['sloan']:.1%} | EY {r['ey'] and f'{r[chr(101)+chr(121)]:.1%}'} ROC {r['roc'] and f'{r[chr(114)+chr(111)+chr(99)]:.1%}'} | nota {r['notas']['geral']:.1f}")
