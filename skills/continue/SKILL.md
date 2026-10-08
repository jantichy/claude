---
name: continue
description: Skill se použije, když uživatel zadá "/continue", nebo chce v nové session rovnou navázat na práci přerušenou skillem /break – "pokračuj, kde jsme skončili", "naváž na přerušenou práci", "jedeme dál od přerušení". Najde v docs/todo.md kteréhokoliv worktree repozitáře sekci Přerušený běh, přepne se do adresáře, kde práce leží, a hned provede, co zápis říká v odstavci Jak pokračovat – zavolá uvedený skill, nebo se pustí do první zbývající položky. Je jednoúčelový a rychlý: nic nesbírá, nenačítá standardy a nevolá síť. Na rozdíl od /next, který sestavuje a řadí nabídku ze všeho rozdělaného v projektu, tenhle skill nic nenabízí a navazuje jen na zápis z /break; na rozdíl od /break nic nezapisuje, jen čte.
allowed-tools: [Read, Glob, Grep, Bash, AskUserQuestion, Skill]
---

# Continue

## Co skill dělá

Druhá strana `/break`. Na začátku čisté session najde zápis přerušené práce v sekci `## Přerušený běh`, přepne se tam, kde práce leží, a **okamžitě pokračuje** podle odstavce `**Jak pokračovat:**`, který mu tam `/break` nechal. Jeden příkaz shellu, krátké shrnutí, a práce běží dál.

Režimy ani argument nemá. Tvar zápisu, ze kterého čte, drží `/break` – tenhle skill z něj spoléhá jen na dvě značky: nadpis bloku `### ` uvnitř sekce a odstavec `**Jak pokračovat:**`, jehož první věta je jediná první akce.

## Co skill nedělá

- **Nezapisuje rozdělanou práci.** To dělá `/break`; když zápis chybí nebo je neúplný, nedomýšlí ho z hlavy.
- **Nesestavuje nabídku.** Projít celé `todo.md`, plán, kola, větve a místo v cyklu a vybrat z toho je `/next` – a právě ta šíře je to, co tady nechceme. Není-li na co navázat, odkáže na něj.
- **Nemaže sekci ani běhový soubor.** Kdy se smažou, říká *Jak pokračovat* v zápisu; dělá to až práce, která frontu dojde.
- **Nehlídá, jestli nad větví běží jiná session.** `/break` končí řetězem `/cleanup` → `/clear` v téže session, takže by kontrola hlásila jako obsazenou právě tu, která má pokračovat – a byla by to nejpomalejší část běhu. Druhé okno nad týmž worktree je tedy věc uživatele, ne tohohle skillu.

## Fáze 0 – Příprava

`~/.claude/skills/preflight.md` se **nenačítá**, ani `structure.md` a `lifecycle.md` – kořen projektu i worktree najde příkaz ve *Fázi 1* a stav pracovního stromu, kontrakt a autocommit řeší až práce, na kterou se navazuje, podle pravidel projektu. **Rychlost je tady celé zadání:** každé čtení navíc je čekání, kvůli kterému se nepouští `/next`.

## Fáze 1 – Nalezení zápisu

Pusť z adresáře session **přesně tenhle příkaz**, nic předtím a nic dalšího:

```bash
git worktree list --porcelain | sed -n 's/^worktree //p' | while read -r d; do for f in "$d/docs/todo.md" "$d/todo.md"; do if [ -f "$f" ]; then awk -v f="$f" '/^## Přerušený běh/{print "==> " f; s=1; next} s && /^## /{exit} s' "$f"; fi; done; done
```

Projde všechny worktree repozitáře – ve worktree layoutu tedy i větve vedle té, kde session stojí, a funguje i z kořene kontejneru – a vypíše sekci z každého `todo.md`, které ji má, uvozenou řádkem `==> <cesta>`.

| Výstup | Co dál |
|---|---|
| `fatal: not a git repository` | řekni to a skonči druhou závěrečnou větou |
| prázdný | zápis nikde není; skonči druhou závěrečnou větou a doporuč `/next` |
| jeden blok `### ` | pokračuj *Fází 2* |
| víc bloků `### `, v jedné sekci i napříč worktree | zeptej se přes `AskUserQuestion`, kterým začít – nadpis bloku jako `label`, první věta *Jak pokračovat* jako `description`, v pořadí, ve kterém stojí; žádný neoznačuj za doporučený, pořadí nerozhodl nikdo |

**Sekce bez nadpisu `### `** je zápis ze starší podoby `/break`: ber celou sekci jako jeden blok a odstavec *Jak pokračovat* v ní hledej podle textu. **Chybí-li `**Jak pokračovat:**` úplně**, nehádej – vypiš, co v bloku je, a zeptej se, čím začít.

## Fáze 2 – Navázání

1. **Přepni se do worktree, kde zápis leží** – adresář nad `docs/todo.md` z řádku `==>` (nebo nad `todo.md` u projektu bez `docs/`). Stojí-li session jinde, přejdi tam a řekni to jednou větou; ve worktree layoutu je to jediná věc, kterou nová session jinak nemá odkud vědět.
2. **Přečti blok celý** – výstup příkazu ho už obsahuje, `todo.md` znovu neotevírej. Mimo *Jak pokračovat* nese úvodní větu s tím, **co musí předcházet**: stojí-li tam krok, který se ještě neudělal (uživatel chystal změnu rozhodnutí), zeptej se, jestli proběhl, dřív než začneš – fronta nad neplatným stavem je práce nazmar.
3. **Shrň ve třech až pěti řádcích:** co se přerušilo a kdy, kde to leží, kolik položek zbývá, co předchází a čím se teď pokračuje.
4. **Řekni závěrečnou větu a proveď první akci z *Jak pokračovat*:**
   - **Je to skill** (`/review branch`, `/implement`) → vyvolej ho přes nástroj `Skill` s argumentem ze zápisu. Blok mu neopakuj jako zadání – zbývající položky si přečte z `todo.md` sám, a říká-li zápis, že se s nimi má porovnat výsledek, stojí to v *Jak pokračovat*, ne v tvém shrnutí.
   - **Je to položka nebo krok práce** → načti soubory, na které ta položka odkazuje, a pusť se do ní. Další položky ber v pořadí zápisu; každá nese varianty a doporučení, takže je předkládej tak, jak jsou zapsané, ne od nuly.

Od té chvíle běží běžná práce podle pravidel projektu, ne tenhle skill.

## Fáze 3 – Závěr

Šablona výstupu tu není – výstupem je pokračující práce. Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím; u nalezeného zápisu ji řekni **před** první akcí, potom už běh nekončí, ale přechází:

- `Navazuju na: <nadpis bloku>, pokračuju <skillem / položkou „…“> v <pracovní adresář>.`
- `Navázat není na co – brání tomu: <konkrétní seznam>.`

Druhá věta jmenuje, co se prošlo a proč nic: *„sekce `## Přerušený běh` není v `todo.md` žádného worktree – pro přehled všeho rozdělaného pusť `/next`“*.
