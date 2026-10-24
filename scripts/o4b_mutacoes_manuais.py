"""O4b: reaplica à mão as mutações dos itens 9–20 (docs/oraculo/mutacao-2026-10-23.md) e roda os testes de cada uma.

Uso (rode numa CÓPIA do repo, nunca no checkout de trabalho):  cd ferramentas && python ../scripts/o4b_mutacoes_manuais.py
Cada mutação é aplicada, testada e desfeita; no fim os dois motores são conferidos byte a byte contra a cópia guardada.
Só relatório: nenhum motor fica alterado.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile
M=[
("motor_financeiras.py","ai = ancoras(emp, mk2, emp.roe_lp - dc[\"delta_roe\"])","ai = ancoras(emp, mk2, emp.roe_lp + dc[\"delta_roe\"])",9),
("motor_financeiras.py","a = {k: (1 - dc[\"peso\"]) * a[k] + dc[\"peso\"] * ai[k] for k in a}\n    elif dc[\"tipo\"] == \"fixo\":\n        a = descontar(a, dc[\"pct\"])\n    return median","a = {k: (1 + dc[\"peso\"]) * a[k] + dc[\"peso\"] * ai[k] for k in a}\n    elif dc[\"tipo\"] == \"fixo\":\n        a = descontar(a, dc[\"pct\"])\n    return median",10),
("motor_financeiras.py","a = {k: (1 - dc[\"peso\"]) * a[k] + dc[\"peso\"] * ai[k] for k in a}\n    elif dc[\"tipo\"] == \"fixo\":\n        a = descontar(a, dc[\"pct\"])\n    return median","a = {k: (1 - dc[\"peso\"]) * a[k] - dc[\"peso\"] * ai[k] for k in a}\n    elif dc[\"tipo\"] == \"fixo\":\n        a = descontar(a, dc[\"pct\"])\n    return median",10),
("motor_financeiras.py","if bogle_liq_real >= mk.rf_liq_real + 0.03: rf","if bogle_liq_real >= mk.rf_liq_real - 0.03: rf",11),
("motor_financeiras.py","elif bogle_liq_real >= mk.rf_liq_real + 0.015: rf =","elif bogle_liq_real >= mk.rf_liq_real - 0.015: rf =",12),
("motor_financeiras.py","bogle_real = (1 + bogle_nom) / (1 + pi) - 1","bogle_real = (1 + bogle_nom) / (1 - pi) - 1",13),
("motor_financeiras.py","bogle_real = (1 + bogle_nom) / (1 + pi) - 1","bogle_real = (1 + bogle_nom) * (1 + pi) - 1",13),
("motor_financeiras.py","bogle_real = (1 + bogle_nom) / (1 + pi) - 1","bogle_real = (2 + bogle_nom) / (1 + pi) - 1",13),
("motor_financeiras.py","dpa_sust_liq = dpa_sust_vp * (1 - emp.jcp_share * IR_JCP)","dpa_sust_liq = dpa_sust_vp * (1 + emp.jcp_share * IR_JCP)",14),
("motor_financeiras.py","dpa_sust_liq = dpa_sust_vp * (1 - emp.jcp_share * IR_JCP)","dpa_sust_liq = dpa_sust_vp * (1 - emp.jcp_share / IR_JCP)",14),
("motor_financeiras.py","if emp.cobertura_caixa else None","if emp.cobertura_caixa or True else None",15),
("motor_financeiras.py","if emp.cobertura_caixa else None","if emp.cobertura_caixa and False else None",15),
("motor_financeiras.py","if r[\"palavra\"] == \"NÃO CONCLUSIVO\" or r[\"central\"] <= 0:","if r[\"palavra\"] == \"NÃO CONCLUSIVO\" or r[\"central\"] < 0:",16),
("motor_financeiras.py","if n[\"qualidade\"] < NOTA_QUALIDADE_MINIMA:","if n[\"qualidade\"] <= NOTA_QUALIDADE_MINIMA:",16),
("motor_financeiras.py","if n[\"solidez\"] < 7:","if n[\"solidez\"] <= 7:",16),
("motor_financeiras.py","if r[\"dispersao\"] > 1.8:\n        m.append","if r[\"dispersao\"] >= 1.8:\n        m.append",16),
("motor_financeiras.py","round(r[\"pc\"], 9) > COMPRA_PARCIAL","round(r[\"pc\"], 10) > COMPRA_PARCIAL",17),
("motor_nao_financeiras.py","lo, hi = -0.05, min(0.08,","lo, hi = -0.06, min(0.08,",18),
("motor_nao_financeiras.py","lo, hi = -0.05, min(0.08,","lo, hi = -0.05, min(0.09,",18),
("motor_nao_financeiras.py","[\"wacc_real\"] - 0.002)","[\"wacc_real\"] - 0.003)",18),
("motor_nao_financeiras.py","min(0.08, valores(emp, mk, e_peso=e_peso)","min(0.08, valores(emp, mk, e_peso=None)",18),
("motor_nao_financeiras.py","dcf_base = lambda **kw: descontar({\"b\": valores(emp, mk, e_peso=e_peso, **kw)","dcf_base = lambda **kw: descontar({\"b\": valores(emp, mk, e_peso=None, **kw)",19),
("motor_nao_financeiras.py","lo, hi = 0.0, 0.40","lo, hi = 0.0, 0.41",19),
("motor_nao_financeiras.py","lo, hi = mk.g_teto + 0.003, 0.60","lo, hi = mk.g_teto + 0.004, 0.60",20),
("motor_nao_financeiras.py","lo, hi = mk.g_teto + 0.003, 0.60","lo, hi = mk.g_teto - 0.003, 0.60",20),
("motor_nao_financeiras.py","f = lambda k: central_de(descontar(valores(emp, mk, ke_nom=k, e_peso=e_peso)","f = lambda k: central_de(descontar(valores(emp, mk, ke_nom=k, e_peso=None)",20),
("motor_nao_financeiras.py","        if f(lo) < emp.preco:\n            return None\n        for _ in range(70):","        if f(lo) <= emp.preco:\n            return None\n        for _ in range(70):",20),
("motor_nao_financeiras.py","lo, hi = mk.g_teto + 0.003, 0.60","lo, hi = mk.g_teto + 0.003, 1.60",20),
("motor_nao_financeiras.py","            if f(mid) > emp.preco:\n                lo = mid\n            else:\n                hi = mid\n        return (lo + hi) / 2\n    except","            if f(mid) >= emp.preco:\n                lo = mid\n            else:\n                hi = mid\n        return (lo + hi) / 2\n    except",20),
]
TMP = pathlib.Path(tempfile.mkdtemp())
bak = {f: str(TMP / f) for f in ("motor_financeiras.py", "motor_nao_financeiras.py")}
for f in bak:
    shutil.copy(f, bak[f])
for f,a,b,item in M:
    src=open(bak[f]).read(); assert src.count(a)==1,(item,a,src.count(a))
    open(f,"w").write(src.replace(a,b))
    r=subprocess.run([sys.executable,"-m","pytest","tests/test_o4b_mutantes_parte2.py","-q","-x","-p","no:cacheprovider"],capture_output=True,text=True)
    shutil.copy(bak[f],f)
    print(item, "MORTO" if r.returncode else "SOBREVIVE", b[:70].replace("\n"," "))
for f in bak:
    assert pathlib.Path(f).read_bytes() == pathlib.Path(bak[f]).read_bytes(), f"{f} não foi restaurado"
print("motores restaurados")
