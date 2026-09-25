"""Změří, co stojí jeden běh `/cleanup`, z transcriptů session.

Běh se ohraničí od záznamu `command-name>/cleanup` po první odpověď se
šablonou `Úklid dokončen`; běhy bez toho markeru se nepočítají, protože u nich
není jak poznat, kde skončily. Náklady hlavní session a subagentů se sčítají
zvlášť – subagenti mají vlastní transcripty v `<slug>/<session-id>/subagents/`.

Váhy jsou ceny Opus 5 v USD za milion tokenů; číslo tedy není fakturovaná
částka, ale vážený součet tokenů, ve kterém čtení cache váží desetinu vstupu
a výstup pětinásobek. Srovnává se **po pásmech velikosti transcriptu**, protože
cena úklidu roste s délkou uklízené session až jedenáctinásobně a medián přes
všechna pásma by srovnával jiné běhy s jinými.
"""
import json, glob, os
from datetime import datetime
from collections import defaultdict
P_IN,P_CW,P_CR,P_OUT=15.0,18.75,1.5,75.0
CUT='2026-09-25T16:10'
def cost(u): return (u.get('input_tokens',0)*P_IN+u.get('cache_creation_input_tokens',0)*P_CW+u.get('cache_read_input_tokens',0)*P_CR+u.get('output_tokens',0)*P_OUT)/1e6
def agg(recs):
    t=defaultdict(int);n=0;c=0.0
    for r in recs:
        u=(r.get('message') or {}).get('usage')
        if not u: continue
        n+=1;c+=cost(u)
        for k in ('input_tokens','cache_creation_input_tokens','cache_read_input_tokens','output_tokens'): t[k]+=u.get(k,0)
    return n,dict(t),c
def txt(r):
    c=(r.get('message') or {}).get('content')
    if isinstance(c,str): return c
    if isinstance(c,list): return ' '.join(b.get('text','') for b in c if isinstance(b,dict))
    return ''
def band(kb):
    return 'A do300kB' if kb<300 else 'B 300-600' if kb<600 else 'C 600-1200' if kb<1200 else 'D nad1200'
runs=[]
for path in glob.glob(os.path.expanduser('~/.claude/projects/*/*.jsonl')):
    lines=open(path,encoding='utf-8',errors='replace').read().splitlines()
    recs=[];raw=[]
    for L in lines:
        try: recs.append(json.loads(L)); raw.append(L)
        except Exception: pass
    starts=[i for i,r in enumerate(recs) if 'command-name>/cleanup' in json.dumps(r.get('message',{}),ensure_ascii=False)]
    if not starts: continue
    sid=os.path.basename(path)[:-6]
    subdir=os.path.join(os.path.dirname(path),sid,'subagents')
    subs=[]
    for sp in glob.glob(os.path.join(subdir,'agent-*.jsonl')):
        sr=[]
        for L in open(sp,encoding='utf-8',errors='replace').read().splitlines():
            try: sr.append(json.loads(L))
            except Exception: pass
        sts=next((r['timestamp'] for r in sr if r.get('timestamp')),None)
        if sts: subs.append((sts,sr))
    for si,i0 in enumerate(starts):
        end=len(recs); marker=False
        for j in range(i0+1,len(recs)):
            if si+1<len(starts) and j>=starts[si+1]: end=starts[si+1]; break
            if recs[j].get('type')=='assistant' and ('Úklid dokončen' in txt(recs[j]) or 'Úklid session' in txt(recs[j])):
                end=j+1; marker=True; break
        if not marker: continue
        seg=recs[i0:end]
        ts0=next((r['timestamp'] for r in seg if r.get('timestamp')),None)
        ts1=next((r['timestamp'] for r in reversed(seg) if r.get('timestamp')),None)
        if not ts0: continue
        kb=sum(len(x.encode()) for x in raw[:i0])/1024
        n,t,c=agg(seg)
        sn=0;sc=0.0;na=0
        for sts,sr in subs:
            if ts0<=sts<=(ts1 or ts0):
                na+=1;a,b,d=agg(sr);sn+=a;sc+=d
        f=lambda s: datetime.fromisoformat(s.replace('Z','+00:00'))
        dur=(f(ts1)-f(ts0)).total_seconds()/60 if ts1 else 0
        runs.append(dict(ts=ts0,proj=os.path.basename(os.path.dirname(path)),kb=kb,band=band(kb),
            dur=dur,n=n,c=c,na=na,sn=sn,sc=sc,tot=c+sc))
runs.sort(key=lambda r:r['ts'])
post=[r for r in runs if r['ts']>=CUT]
pre=[r for r in runs if r['ts']<CUT]
def med(xs): xs=sorted(xs); return xs[len(xs)//2] if xs else 0
print(f"POČET BĚHŮ: před {len(pre)}, po {len(post)}\n")
print("=== VŠECHNY BĚHY PO PŘEPISU (25.9. 16:10+) ===")
print(f"{'kdy':17}{'projekt':24}{'kB':>7}{'min':>5}{'call':>5}{'$main':>8}{'ag':>4}{'agcall':>7}{'$ag':>8}{'$CELK':>8}")
for r in post:
    print(f"{r['ts'][:16]:17}{r['proj'][:24]:24}{r['kb']:7.0f}{r['dur']:5.0f}{r['n']:5}{r['c']:8.2f}{r['na']:4}{r['sn']:7}{r['sc']:8.2f}{r['tot']:8.2f}")
print("\n=== SROVNÁNÍ PO PÁSMECH VELIKOSTI TRANSCRIPTU (medián) ===")
print(f"{'pásmo':12}{'n před':>7}{'$před':>9}{'min':>6} | {'n po':>5}{'$po':>9}{'min':>6} | {'změna $':>9}{'z toho $ag':>11}")
for b in ('A do300kB','B 300-600','C 600-1200','D nad1200'):
    pb=[r for r in pre if r['band']==b]; qb=[r for r in post if r['band']==b]
    if not qb: 
        print(f"{b:12}{len(pb):7}{med([r['tot'] for r in pb]):9.2f}{med([r['dur'] for r in pb]):6.0f} |  ---  žádný běh po přepisu")
        continue
    mp,mq=med([r['tot'] for r in pb]),med([r['tot'] for r in qb])
    ch=f"{(mq/mp-1)*100:+.0f}%" if mp else "?"
    print(f"{b:12}{len(pb):7}{mp:9.2f}{med([r['dur'] for r in pb]):6.0f} | {len(qb):5}{mq:9.2f}{med([r['dur'] for r in qb]):6.0f} | {ch:>9}{med([r['sc'] for r in qb]):11.2f}")
print("\n=== PODÍL AGENTŮ NA CELKU ===")
for label,sel in (('před',pre),('po',post)):
    if not sel: continue
    ts=sum(r['tot'] for r in sel); ags=sum(r['sc'] for r in sel)
    print(f"  {label}: agenti {ags/ts*100:.1f} % celkových nákladů, medián agentů na běh {med([r['na'] for r in sel])}")

print("\n=== PÁSMO D (nad 1200 kB) – ROZKLAD, bez přerušeného běhu ===")
pd=[r for r in pre if r['band']=='D nad1200']
qd=[r for r in post if r['band']=='D nad1200' and r['n']>10]
print(f"{'':22}{'před (n=%d)'%len(pd):>14}{'po (n=%d)'%len(qd):>14}{'změna':>10}")
for lab,key in (('$ hlavní session','c'),('$ agenti','sc'),('$ CELKEM','tot'),('volání hl. session','n'),('volání agentů','sn'),('agentů','na'),('délka (min)','dur')):
    a,b=med([r[key] for r in pd]),med([r[key] for r in qd])
    ch=f"{(b/a-1)*100:+.0f}%" if a else "—"
    print(f"{lab:22}{a:14.2f}{b:14.2f}{ch:>10}")
