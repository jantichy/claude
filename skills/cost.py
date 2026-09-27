"""Změří, co stojí jeden běh skillu, z transcriptů session.

Použití: `python3 ~/.claude/skills/cost.py <skill> [--since ISO] [--end-marker TEXT]`

Běh se ohraničí od záznamu `<command-name>/<skill></command-name>` po první
odpověď obsahující **marker konce**. Ten se odvozuje ze `skills/<skill>/SKILL.md`
– je to nadpis na prvním řádku posledního bloku kódu, tedy šablona závěrečné
fáze (`## Úklid dokončen`, `## Hotovo`, `## Oponentura hotová`). Odvození jde
přebít `--end-marker`, opakovatelně.

**Běh bez markeru konce se nepočítá a hlásí se to**, protože u něj není jak
poznat, kde skončil. Hranice se navíc uzavírá na vyvolání jiného skillu, ať se
běhu nepřipsala cena toho, co přišlo po něm; příkazy harnessu (`/clear`,
`/compact`, …) hranicí nejsou, protože uprostřed dlouhého běhu nastanou běžně.

Náklady hlavní session a subagentů se sčítají zvlášť – subagenti mají vlastní
transcripty v `<slug>/<session-id>/subagents/`.

Váhy jsou ceny Opus 5 v USD za milion tokenů; číslo tedy není fakturovaná
částka, ale vážený součet tokenů, ve kterém čtení cache váží desetinu vstupu
a výstup pětinásobek.

Srovnává se **po pásmech, a to na dvou osách**, protože medián přes všechna
pásma by srovnával jiné běhy s jinými:

- **velikost transcriptu** – rozhoduje u skillu, jehož vstupem transcript je
  (`/cleanup`), protože cena běhu roste s délkou session;
- **velikost rozsahu** – rozhoduje u skillu, který čte kód a dokumentaci na
  disku (`/review`, `/consistency`, `/oponent`). U `/consistency` vyšlo pásmo
  nejkratších session **dráž** než pásmo nejdelších, tedy obráceně: délka
  session u něj cenu neurčuje a srovnání po první ose porovnává nesrovnatelné.

Rozsah se čte z řádku `Pokrytí:` v závěrečném přehledu, tedy z čísla, které si
skill zapisuje sám. Z disku se vzít nedá – rozsah minulého běhu už neexistuje –
a počet souborů, do kterých běh sáhl, měří vykonanou práci, ne zadání, takže by
srovnání ceny podle něj bylo kruhové. **Běh, který rozsah nevykázal, do pásma
druhé osy nespadne a hlásí se to**; měřené pokrytí vzniklo 27. 9. 2026, takže
starší běhy ho nenesou a zpětně dopočítat nejdou.
"""
import json
import glob
import os
import re
import sys
from datetime import datetime
from collections import defaultdict

P_IN, P_CW, P_CR, P_OUT = 15.0, 18.75, 1.5, 75.0
HARNESS = ('/clear', '/compact', '/resume', '/exit', '/rename', '/config',
           '/cost', '/help', '/model', '/status', '/vim', '/doctor')
CMD = re.compile(r'command-name>(/[a-z-]+)</command-name>')
# `- **Pokrytí panelem:** 12 z 30 souborů rozsahu …`; jednotka je povinná, ať se
# za rozsah nevezme `N/N` kotev ani `X kB z Y kB` transcriptu, což je osa první
SCOPE = re.compile(r'\*\*Pokrytí[^:*\n]{0,24}:\*\*[^\n0-9]{0,24}'
                   r'(\d+)\s+z\s+(\d+)\s+(souborů|sekcí|scénářů)')
KB_BANDS = ('A do300kB', 'B 300-600', 'C 600-1200', 'D nad1200')
SCOPE_BANDS = ('A do10', 'B 10-50', 'C 50-200', 'D nad200')
AXES = (('band', KB_BANDS, 'VELIKOSTI TRANSCRIPTU'),
        ('sband', SCOPE_BANDS, 'VELIKOSTI ROZSAHU'))


def price(u):
    return (u.get('input_tokens', 0) * P_IN
            + u.get('cache_creation_input_tokens', 0) * P_CW
            + u.get('cache_read_input_tokens', 0) * P_CR
            + u.get('output_tokens', 0) * P_OUT) / 1e6


def agg(recs):
    """Sečte volání, tokeny a cenu přes záznamy, které nesou `usage`."""
    tok = defaultdict(int)
    calls = 0
    total = 0.0
    for r in recs:
        u = (r.get('message') or {}).get('usage')
        if not u:
            continue
        calls += 1
        total += price(u)
        for k in ('input_tokens', 'cache_creation_input_tokens',
                  'cache_read_input_tokens', 'output_tokens'):
            tok[k] += u.get(k, 0)
    return calls, dict(tok), total


def txt(r):
    c = (r.get('message') or {}).get('content')
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return ' '.join(b.get('text', '') for b in c if isinstance(b, dict))
    return ''


def band(kb):
    if kb < 300:
        return 'A do300kB'
    if kb < 600:
        return 'B 300-600'
    if kb < 1200:
        return 'C 600-1200'
    return 'D nad1200'


def sband(n):
    """Pásmo podle velikosti rozsahu, nebo None, není-li rozsah znám.

    Hranice jsou **přiznaný odhad, ne fit z dat**: v den vzniku téhle osy
    nenesl měřené pokrytí ani jeden naměřený běh, takže nebylo z čeho je
    odvodit. Ladí se na řádovou představu – jednotky souborů je běh na větvi,
    dvě stě a víc celý repozitář. Po prvních desítkách běhů je přepočítej
    z naměřeného rozdělení a tenhle odstavec přepiš.
    """
    if n is None:
        return None
    if n < 10:
        return 'A do10'
    if n < 50:
        return 'B 10-50'
    if n < 200:
        return 'C 50-200'
    return 'D nad200'


def scope_of(seg):
    """Velikost rozsahu z řádku `Pokrytí:` v přehledu běhu, nebo None.

    Bere se **poslední** výskyt v odpovědích modelu, protože závěrečný přehled
    stojí na konci běhu, kdežto dřív v něm mohl padnout mezivýpis. Čte se jen
    text odpovědi, ne vstupy nástrojů – jinak by se za naměřený rozsah vzala
    šablona ze `SKILL.md`, kterou běh zrovna čte nebo píše.
    """
    found = None
    for r in seg:
        if r.get('type') != 'assistant':
            continue
        for m in SCOPE.finditer(txt(r)):
            found = (int(m.group(2)), m.group(3))
    return found


def end_markers(skill):
    """Odvodí marker konce ze šablony **závěrečné fáze** `SKILL.md`.

    Závěrečná fáze je poslední sekce `## Fáze …` (norma `skills/SKILLS.md`,
    *Povinné sekce a jejich pořadí*); marker je nadpis na prvním řádku prvního
    bloku kódu v ní. **Poslední blok v souboru to není** – za závěrečnou fází
    smí stát přílohová sekce, a `/review` tam má šablonu kapitoly `## Review`,
    která se v konverzaci vyskytne kdekoliv. Bral-li by se poslední blok,
    ohraničil by běh na cizím textu a jeho cena by byla nafouknutá.
    """
    path = os.path.expanduser(f'~/.claude/skills/{skill}/SKILL.md')
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as fh:
        lines = fh.read().splitlines()
    return first_template(lines[last_phase(lines):])


def last_phase(lines):
    """Index posledního nadpisu `## Fáze …`, který nestojí v bloku kódu."""
    inside = False
    at = 0
    for i, line in enumerate(lines):
        if line.startswith('```'):
            inside = not inside
        elif not inside and line.startswith('## Fáze'):
            at = i
    return at


def first_template(lines):
    """První blok kódu, jehož první neprázdný řádek je nadpis `## `."""
    inside = False
    head = None
    for line in lines:
        if line.startswith('```'):
            if inside and head:
                return [head]
            inside = not inside
            head = None
            continue
        if inside and head is None and line.strip():
            head = line.strip() if line.startswith('## ') else ''
    return []


def commands(rec):
    """Slash příkazy vyvolané v jednom záznamu."""
    return CMD.findall(json.dumps(rec.get('message', {}), ensure_ascii=False))


def run_bounds(recs, starts, idx, skill, markers):
    """Konec běhu, který začal na `starts[idx]`, nebo None, není-li marker."""
    i0 = starts[idx]
    nxt = starts[idx + 1] if idx + 1 < len(starts) else len(recs)
    for j in range(i0 + 1, len(recs)):
        if j >= nxt:
            return None
        if recs[j].get('type') == 'assistant' and any(m in txt(recs[j]) for m in markers):
            return j + 1
        other = [c for c in commands(recs[j])
                 if c != f'/{skill}' and c not in HARNESS]
        if other:
            return None
    return None


def load(path):
    recs, raw = [], []
    with open(path, encoding='utf-8', errors='replace') as fh:
        lines = fh.read().splitlines()
    for line in lines:
        try:
            recs.append(json.loads(line))
            raw.append(line)
        except ValueError:
            pass
    return recs, raw


def subagents(path):
    """Transcripty subagentů dané session s časem prvního záznamu."""
    sid = os.path.basename(path)[:-6]
    out = []
    pattern = os.path.join(os.path.dirname(path), sid, 'subagents', 'agent-*.jsonl')
    for sp in glob.glob(pattern):
        sr, _ = load(sp)
        ts = next((r['timestamp'] for r in sr if r.get('timestamp')), None)
        if ts:
            out.append((ts, sr))
    return out


def scan(skill, markers, root='~/.claude/projects'):
    """Všechny dokončené běhy skillu; vrací i počet zahozených bez markeru."""
    runs, dropped = [], 0
    for path in glob.glob(os.path.expanduser(f'{root}/*/*.jsonl')):
        recs, raw = load(path)
        starts = [i for i, r in enumerate(recs) if f'/{skill}' in commands(r)]
        if not starts:
            continue
        subs = subagents(path)
        for idx, i0 in enumerate(starts):
            end = run_bounds(recs, starts, idx, skill, markers)
            if end is None:
                dropped += 1
                continue
            run = measure(recs[i0:end], raw[:i0], subs, path)
            if run:
                runs.append(run)
            else:
                dropped += 1
    runs, duplicates = dedup(runs)
    runs.sort(key=lambda r: r['ts'])
    return runs, dropped + duplicates


def dedup(runs):
    """Zahodí tentýž běh započtený dvakrát, a vrátí kolik jich bylo.

    `/resume` zkopíruje transcript do nové session, takže se běh, který v něm
    stojí, najde v obou souborech. Rozliší se podle projektu, času začátku
    a ceny hlavní session – velikost transcriptu se totiž mezi kopiemi liší,
    takže podle ní to nejde. Bez toho se tentýž běh počítá dvakrát a medián
    se posune k tomu, co je náhodou zkopírované.
    """
    seen = {}
    for r in runs:
        key = (r['proj'], r['ts'], round(r['c'], 6))
        # z dvojice si nech tu s vyšším počtem agentů: kopie po /resume
        # nemusí nést podadresář se subagenty, a chybějící agent je ztráta dat
        if key not in seen or r['na'] > seen[key]['na']:
            seen[key] = r
    return list(seen.values()), len(runs) - len(seen)


def measure(seg, before, subs, path):
    ts0 = next((r['timestamp'] for r in seg if r.get('timestamp')), None)
    ts1 = next((r['timestamp'] for r in reversed(seg) if r.get('timestamp')), None)
    if not ts0:
        return None
    kb = sum(len(x.encode()) for x in before) / 1024
    calls, _, cost_main = agg(seg)
    ag_calls, ag_cost, ag_n = 0, 0.0, 0
    for sts, sr in subs:
        if ts0 <= sts <= (ts1 or ts0):
            ag_n += 1
            a, _, d = agg(sr)
            ag_calls += a
            ag_cost += d
    dur = 0.0
    if ts1:
        def parse(s):
            return datetime.fromisoformat(s.replace('Z', '+00:00'))
        dur = (parse(ts1) - parse(ts0)).total_seconds() / 60
    scope = scope_of(seg)
    return dict(ts=ts0, proj=os.path.basename(os.path.dirname(path)), kb=kb,
                band=band(kb), dur=dur, n=calls, c=cost_main, na=ag_n,
                sn=ag_calls, sc=ag_cost, tot=cost_main + ag_cost,
                scope=scope[0] if scope else None,
                unit=scope[1] if scope else '',
                sband=sband(scope[0] if scope else None))


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else 0


def table(runs, title):
    print(f"\n=== {title} ===")
    print(f"{'kdy':17}{'projekt':24}{'kB':>7}{'rozsah':>8}{'min':>5}{'call':>5}"
          f"{'$main':>8}{'ag':>4}{'agcall':>7}{'$ag':>8}{'$CELK':>8}")
    for r in runs:
        print(f"{r['ts'][:16]:17}{r['proj'][:24]:24}{r['kb']:7.0f}"
              f"{(str(r['scope']) if r['scope'] else '-'):>8}{r['dur']:5.0f}"
              f"{r['n']:5}{r['c']:8.2f}{r['na']:4}{r['sn']:7}{r['sc']:8.2f}{r['tot']:8.2f}")


def missing(runs, key):
    """Kolik běhů na dané ose pásmo nemá – hlásí se, ať medián nelže vzorkem."""
    return sum(1 for r in runs if not r.get(key))


def note(runs, key, title):
    miss = missing(runs, key)
    if miss:
        print(f"  ({miss} z {len(runs)} běhů pásmo podle {title.lower()} nemá – "
              f"rozsah v přehledu nevykázaly)")


def bands(pre, post, key, order, title):
    print(f"\n=== SROVNÁNÍ PO PÁSMECH {title} (medián) ===")
    print(f"{'pásmo':12}{'n před':>7}{'$před':>9}{'min':>6} | "
          f"{'n po':>5}{'$po':>9}{'min':>6} | {'změna $':>9}{'z toho $ag':>11}")
    for b in order:
        pb = [r for r in pre if r[key] == b]
        qb = [r for r in post if r[key] == b]
        if not qb:
            print(f"{b:12}{len(pb):7}{med([r['tot'] for r in pb]):9.2f}"
                  f"{med([r['dur'] for r in pb]):6.0f} |  ---  žádný běh po mezi")
            continue
        mp, mq = med([r['tot'] for r in pb]), med([r['tot'] for r in qb])
        ch = f"{(mq / mp - 1) * 100:+.0f}%" if mp else "?"
        print(f"{b:12}{len(pb):7}{mp:9.2f}{med([r['dur'] for r in pb]):6.0f} | "
              f"{len(qb):5}{mq:9.2f}{med([r['dur'] for r in qb]):6.0f} | "
              f"{ch:>9}{med([r['sc'] for r in qb]):11.2f}")


def share(runs, label):
    if not runs:
        return
    tot = sum(r['tot'] for r in runs)
    ags = sum(r['sc'] for r in runs)
    pct = ags / tot * 100 if tot else 0
    print(f"  {label}: agenti {pct:.1f} % celkových nákladů, "
          f"medián agentů na běh {med([r['na'] for r in runs])}, "
          f"medián $ {med([r['tot'] for r in runs]):.2f}, "
          f"medián min {med([r['dur'] for r in runs]):.0f}")


def parse_args(argv):
    """Vrací (skill, since, markers) nebo None, je-li volání vadné."""
    skill = argv[0].lstrip('/')
    since, markers = None, []
    i = 1
    while i < len(argv):
        if argv[i] == '--since' and i + 1 < len(argv):
            since = argv[i + 1]
            i += 2
        elif argv[i] == '--end-marker' and i + 1 < len(argv):
            markers.append(argv[i + 1])
            i += 2
        else:
            print(f"neznámý argument: {argv[i]}")
            return None
    return skill, since, markers


def report_all(runs):
    table(runs, 'VŠECHNY DOKONČENÉ BĚHY')
    print("\n=== PODÍL AGENTŮ NA CELKU ===")
    share(runs, 'vše')
    for key, order, title in AXES:
        print(f"\n=== PO PÁSMECH {title} (medián) ===")
        for b in order:
            sel = [r for r in runs if r[key] == b]
            if sel:
                print(f"  {b:12} n={len(sel):3}  $ {med([r['tot'] for r in sel]):7.2f}"
                      f"  min {med([r['dur'] for r in sel]):4.0f}"
                      f"  volání {med([r['n'] for r in sel]):4}"
                      f"  agentů {med([r['na'] for r in sel]):3}")
        note(runs, key, title)


def report_since(runs, since):
    pre = [r for r in runs if r['ts'] < since]
    post = [r for r in runs if r['ts'] >= since]
    print(f"MEZ: {since}   před {len(pre)}, po {len(post)}")
    table(post, f"BĚHY PO MEZI ({since})")
    for key, order, title in AXES:
        bands(pre, post, key, order, title)
        note(post, key, title)
    print("\n=== PODÍL AGENTŮ NA CELKU ===")
    share(pre, 'před')
    share(post, 'po  ')


def main(argv):
    if not argv or argv[0].startswith('-'):
        print(__doc__)
        return 2
    parsed = parse_args(argv)
    if not parsed:
        return 2
    skill, since, markers = parsed
    if not markers:
        markers = end_markers(skill)
    if not markers:
        print(f"Marker konce se nepodařilo odvodit ze skills/{skill}/SKILL.md – "
              f"předej ho --end-marker.")
        return 2
    runs, dropped = scan(skill, markers)
    print(f"SKILL: /{skill}   MARKER KONCE: {markers}")
    print(f"BĚHŮ DOKONČENÝCH: {len(runs)}   ZAHOZENO (bez markeru konce "
          f"nebo přerušeno jiným skillem): {dropped}")
    if not runs:
        return 1
    if since:
        report_since(runs, since)
    else:
        report_all(runs)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
