import sys, json, importlib
sys.dont_write_bytecode=True
R=r"C:\Users\frank\Documents\VALUE INVESTING\ferramentas"
sys.path.insert(0,R)
import motor_financeiras as mf, motor_nao_financeiras as mn
import mercado
mk=mercado.vigente()
hall={e['tk']:e for e in json.load(open(R+r"\painel\web\dados\hall.json",encoding='utf-8'))['empresas']}
for m in ["lote3_agro","lote4_saude_telecom","lote5_petroleo","lote6_quimica"]:
    mod=importlib.import_module(m)
    for e in mod.EMPRESAS:
        if isinstance(e,mf.Financeira) or e.ticker not in hall: continue
        try:
            r=mn.avaliar(e,mk)
            a,ltm=mn.serie(e.ticker)
            lucro=mn.v(ltm,'lucro_liq',None) if False else None
            print(e.ticker,'aliq %.2f(%s,med %s)'%(r['aliquota'],r['aliquota_regra'],None if r['aliquota_mediana'] is None else round(r['aliquota_mediana'],2)),
                  'g_real',e.g_real,'g1',e.g1_real,'roic %.3f roic_f %s wacc %.3f'%(r['roic'] or 0,None if r['roic_filtro'] is None else round(r['roic_filtro'],3),r['wacc']),
                  'P/Lnorm', None if not r['pl_atual'] else round(r['pl_atual'],1),'EY_epv %.3f'%(r['epv']/e.preco), 'DY %.3f'%r['dy'])
        except Exception as ex: print(e.ticker,'ERR',repr(ex)[:100])
