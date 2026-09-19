# -*- coding: utf-8 -*-
"""Přepíše „partii“ na „podobjednávku“ v dokumentaci a chrání místa, kde je to slovo předmětem řeči."""
import sys, re, glob, json, subprocess
sys.path.insert(0, '/private/tmp/claude-501/-Users-honza-Dev-rezervace/ddbf121e-d275-4737-82cc-8e7489edcb16/scratchpad')
import deklinace as D

CHRANENE = [
    r'\n> \*\*Upřesněno \[§121\][^\n]*\n',                 # poznámka nad §88
    r'\n1\. \*\*Přejmenování úrovní\.\*\*[\s\S]*?(?=\n2\. )',  # §88 bod 1 i s pododrážkami
    r'\n## 121\. [\s\S]*?(?=\n## 122\. )',                 # celé §121
    r'121-partie-se-česky-jmenuje-podobjednávka',           # kotva na nadpis §121
    r'\n- \[ \] \*\*Přejmenovat partii na podobjednávku\.\*\*[^\n]*\n',
]
MASKA = '\x00CHRANENO%d\x00'

def convert_file(text, path, report):
    ulozene = []
    for pat in CHRANENE:
        for m in re.finditer(pat, text):
            ulozene.append(m.group(0))
    for i, blok in enumerate(ulozene):
        text = text.replace(blok, MASKA % i, 1)
    text = D.convert(text, report, path)
    for i, blok in enumerate(ulozene):
        text = text.replace(MASKA % i, blok, 1)
    return text, len(ulozene)

if __name__ == '__main__':
    zapis = '--zapis' in sys.argv
    rep, celkem_chran = [], 0
    for path in sorted(glob.glob('docs/*.md')) + ['README.md', 'CLAUDE.md', 'tests/test_mutations.py']:
        # zdroj se bere z posledního commitu, ne z disku – běh jde tím pádem opakovat
        src = subprocess.run(['git', 'show', f'HEAD:{path}'], capture_output=True, text=True, check=True).stdout
        novy, n = convert_file(src, path, rep)
        celkem_chran += n
        assert '\x00' not in novy, path
        if zapis and novy != src:
            open(path, 'w', encoding='utf-8').write(novy)
    print('nahrazeno:', len(rep), '| jistých:', sum(1 for r in rep if r['sure']),
          '| k revizi:', sum(1 for r in rep if not r['sure']), '| chráněných úseků:', celkem_chran)
    json.dump([r for r in rep if not r['sure']],
              open('/private/tmp/claude-501/-Users-honza-Dev-rezervace/ddbf121e-d275-4737-82cc-8e7489edcb16/scratchpad/nejiste.json','w'),
              ensure_ascii=False)
