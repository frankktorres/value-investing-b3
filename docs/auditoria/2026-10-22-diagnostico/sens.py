import sys, json, importlib, dataclasses
sys.dont_write_bytecode=True
R=r"C:\Users\frank\Documents\VALUE INVESTING\ferramentas"
sys.path.insert(0,R)
import motor_financeiras as mf, motor_nao_financeiras as mn
from motor_financeiras import Mercado
hall={e['tk']:e for e in json.load(open(R+r"\painel\web\dados\hall.json",encoding='utf-8'))['empresas']}
emps=[]
for m in ["lote1_bancos","lote2_energia","lote3_agro","lote4_saude_telecom","lote5_petroleo","lote6_quimica"]:
    try:
        mod=importlib.import_module(m)
        for e in mod.EMPRESAS: emps.append((m,e))
    except Exception as ex: print("ERRO",m,repr(ex)[:200])
seen={}
for m,e in emps: seen[e.ticker]=(m,e)
print(len(seen))
base=json.load(open(R+r"\mercado_vigente.json",encoding='utf-8'))
def run(rf,pi,prem,label,pcs=(0.70,0.75)):
    mk=Mercado(rf_real=rf,pi=pi,premio=prem) if False else Mercado(rf,pi)
    out={}
    for tk,(m,e) in seen.items():
        h=hall.get(tk)
        if not h: continue
        try:
            if isinstance(e,mf.Financeira):
                mk2=Mercado(rf,pi,premio=prem)
                c=mf.avaliar(e,mk2)['central']
            else:
                old=mn.PREMIO_KE; mn.PREMIO_KE=prem
                try: c=mn.avaliar(e,Mercado(rf,pi,premio=prem))['central']
                finally: mn.PREMIO_KE=old
        except Exception as ex:
            out[tk]=None; continue
        out[tk]=h['preco_hoje']/c if c and c>0 else None
    ok=[v for v in out.values() if v]
    import statistics
    print(label,"n=",len(ok),"med P/C=%.2f"%statistics.median(ok),
      " <=0.70:",sum(v<=0.70 for v in ok)," <=0.90:",sum(v<=0.90 for v in ok)," <=1.10:",sum(v<=1.10 for v in ok),
      " | <=0.75:",sum(v<=0.75 for v in ok))
    return out
rf,pi=base['rf_real'],base['pi']
b=run(rf,pi,0.05,"base")
res={'base':b}
res['rf5.0']=run(0.050,pi,0.05,"rf real 5,0%")
res['rf4.5_pr4']=run(0.045,pi,0.04,"rf 4,5% + prem 4")
res['prem3']=run(rf,pi,0.03,"prem 3pp")
res['pi4']=run(rf,0.04,0.05,"pi=4% (Focus)")
res['ke9']=run(0.045,pi,0.045,"Ke real 9%")
json.dump({k:{t:v for t,v in d.items()} for k,d in res.items()},open("sens_out.json","w"))
for tk in sorted(b): print(tk, *["%.2f"%res[k][tk] if res[k].get(tk) else "NA" for k in res])
