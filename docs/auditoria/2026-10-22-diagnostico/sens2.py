import sys, json, importlib, dataclasses, statistics
sys.dont_write_bytecode=True
R=r"C:\Users\frank\Documents\VALUE INVESTING\ferramentas"
sys.path.insert(0,R)
import motor_financeiras as mf, motor_nao_financeiras as mn
from motor_financeiras import Mercado
from dataclasses import replace
hall={e['tk']:e for e in json.load(open(R+r"\painel\web\dados\hall.json",encoding='utf-8'))['empresas']}
seen={}
for m in ["lote3_agro","lote4_saude_telecom","lote5_petroleo","lote6_quimica","lote2_energia","lote1_bancos"]:
    mod=importlib.import_module(m)
    for e in mod.EMPRESAS: seen[e.ticker]=e
mk=Mercado(7.06/100,0.0646)
orig=mn.estrutura_de_capital
def variante(modo):
    def f(emp,mk):
        _,ltm=mn.serie(emp.ticker)
        d=mn.divida_liquida(ltm)[0]; dl=mn.divida_liquida(ltm)[2]
        t=mn.aliquota(emp)
        e=emp.preco*emp.n_acoes/1000
        dd = d if modo=='bruta_mercado' else max(dl,0.0)
        if modo=='sem_hamada': prem=0.05
        else: prem=mn.premio_alavancado(dd,e,t)
        return dict(mk=replace(mk,premio=prem),e_peso=e,iteracoes=0,ponto_fixo=True,nota=modo)
    return f
res={}
for modo in ['base','bruta_mercado','liquida_mercado','sem_hamada']:
    mn.estrutura_de_capital = orig if modo=='base' else variante(modo)
    for tk,e in seen.items():
        if isinstance(e,mf.Financeira) or tk not in hall: continue
        try:
            r=mn.avaliar(e,mk); res.setdefault(tk,{})[modo]=(hall[tk]['preco_hoje']/r['central'] if r['central']>0 else None, r['ke_nom_emp'], r['de_peso'])
        except Exception as ex: res.setdefault(tk,{})[modo]=None
for tk,d in sorted(res.items()):
    print(tk,*[("%.2f(Ke%.0f%%,D/E%.2f)"%(v[0],v[1]*100,v[2]) if v and v[0] else "NA") for v in d.values()])
for modo in ['base','bruta_mercado','liquida_mercado','sem_hamada']:
    ok=[d[modo][0] for d in res.values() if d.get(modo) and d[modo][0]]
    print(modo,len(ok),round(statistics.median(ok),2),sum(v<=0.7 for v in ok),sum(v<=0.9 for v in ok),sum(v<=1.1 for v in ok))
