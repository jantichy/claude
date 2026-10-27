# Doménové checklisty

Katalog ke kroku 13 v `SKILL.md`: jak se na checklisty ptát, co která volba importuje, co předvyplnit podle typu projektu a jak se přidává profil organizace.

Checklistů je víc, než se vejde do jedné otázky – `AskUserQuestion` bere najednou nejvýš čtyři volby (týž strop jako v kroku 11). Ptej se **po kolech z tabulky níž**, všechna s `multiSelect: true`. **Kola se dělí tematicky, ne aby byla plná** – uživatel odpovídá na otázku, ne na seznam, a otázka musí jít položit jednou větou. Volby předvyplň podle typu z kroku 11, ale nech uživatele rozhodnout – vývojářský projekt bývá zároveň web, web bývá zároveň administrace.

| Kolo | Otázka | Volby |
|---|---|---|
| 1 | „Co všechno se v projektu bude dělat s kódem a rozhraním? Když nic, nic nezaškrtávej.“ | Psaní kódu · Webové rozhraní · Administrace / backoffice · Webová analytika a měření |
| 2 | „A co se v něm bude psát a učit? Když nic, nic nezaškrtávej.“ | Psaní českých textů · Česká typografie · Školení a kurzy |
| 3 | „A bude se v něm něco kreslit nebo promítat? Když nic, nic nezaškrtávej.“ | Vizuální tvorba a grafika · Prezentace a slajdy |
| 4 | „A bude se v něm vést nebo posuzovat placená reklama? Když ne, nic nezaškrtávej.“ | Výkonnostní reklama a správa kampaní |

Volbu **Žádný** nikam nedávej – prázdný výběr v `multiSelect` ji nahrazuje. **Nový checklist zařaď do kola, kam tematicky patří**; teprve nevejde-li se do žádného pod strop čtyř voleb, přidej další kolo. Pátá volba do existujícího kola nepatří nikdy.

**Česká typografie je samostatná volba, ne přívažek k psaní textů.** Projekt s českým rozhraním nebo se slajdy sází česky, i když v něm žádný souvislý text nevzniká – a naopak by ho nemělo nic nutit brát si kvůli sazbě celá redakční pravidla.

Přehled všech checklistů i s cílem importu:

| Volba | Import |
|---|---|
| Psaní kódu | `@~/Context/Coding/coding.md` |
| Webové rozhraní | `@~/Context/Web/web.md` |
| Administrace / backoffice | `@~/Context/Web/admin.md` |
| Webová analytika a měření | `@~/Context/Analytics/analytics.md` |
| Výkonnostní reklama a správa kampaní | `@~/Context/Advertising/advertising.md` |
| Psaní českých textů | `@~/Context/Text/text.md` |
| Česká typografie | `@~/Context/Text/typography.md` |
| Školení a kurzy | `@~/Context/Training/training.md` |
| Vizuální tvorba a grafika | `@~/Context/Design/design.md` |
| Prezentace a slajdy | `@~/Context/Design/slides.md` |

`~/Context/Legal/legal.md` se do importů **nedává ze stejného důvodu** – čte se, když se o právní úpravu opírá rozhodnutí, ne při každé práci. Projekt, který právní požadavky nese (lhůty dokladů, povinnosti vůči spotřebiteli, retenční doby), na něj narazí přes `~/.claude/CLAUDE.md`, kde je vedený jako podmíněná doménová znalost.

`~/Context/Coding/quality.md` ani `~/Context/Coding/architecture.md` se do importů **nedávají** – čtou se jen při zakládání projektu, návrhu jeho stavby, revizi a nasazení, ne při každé práci na kódu. Skilly, které je potřebují, si je načtou samy; `coding.md` na oba odkazuje. U architektury nese závaznost navíc věta v sekci `## Typ projektu`, kterou zapisuje krok 11.

U typu **Nasazení webové analytiky** přihraj napevno `Analytics/analytics.md` a `Web/web.md` (analytika se nasazuje do webu a překrývá se s ním v consentu a GDPR) a předvyplň `Text/text.md` i `Text/typography.md`, protože výstupem bývá auditní report nebo dokumentace pro klienta. `Coding/coding.md` nabídni jen tehdy, když se v projektu opravdu píše kód – šablony, serverový endpoint, vlastní CMP.

U typu projektu, kde se připravuje **školení, kurz nebo workshop**, předvyplň `Training/training.md` spolu s `Text/text.md` a `Text/typography.md` – materiály pro účastníky jsou text a řídí se vším trojím. Přihoď i `Design/slides.md`, pokud k tomu vzniká promítaná prezentace.

`Design/slides.md` nabízej i mimo školení – všude, kde se dělá deck: konferenční přednáška, prodejní pitch, prezentace výsledků klientovi. Importuje se **navíc** k `Design/design.md`, ne místo něj.

`worktree.md` se tu nenabízí schválně – importuje se už v kroku 4, když si uživatel zvolí worktree layout.

`Brand/brand.md` se tu nenabízí taky schválně, ale z jiného důvodu: je to **korpus, ne checklist**. Neříká, jak se něco dělá, ale jak to je – a projekt, který píše ven, si ho načte podle potřeby přes `~/.claude/CLAUDE.md`, kde je vedený mezi podmíněnými doménovými znalostmi. Importovat ho natvrdo do každého takového projektu by znamenalo vozit korpus tam, kde stačí sáhnout.

### Profil organizace

**Pod `~/Clients` tenhle odstavec neplatí** – klient má profil ve vlastní složce a podprojekty ho dědí, viz [`client.md`](client.md). Platí jen pro projekt mimo ni, který se organizace týká, ale práce pro ni to není (osobní projekt v `~/Projects`).

Když projekt vzniká **pro konkrétní organizaci**, zeptej se, jestli má profil v `~/Context/Organizations/`, a když ano, přidej ho do importů:

```
@~/Context/Organizations/<organizace>.md
```

**Není to metodika, ale korpus** – kdo v organizaci sedí, kdo co schvaluje, jaké mají systémy. Profil zůstává v knowledge base a projekt na něj jen odkazuje; jedna organizace může mít víc projektů a všechny sdílejí týž profil. Když profil neexistuje a jde o **opakovaný vztah, u kterého je potřeba znát vnitřek organizace**, navrhni jeho založení – kritérium je v `~/Context/Organizations/organizations.md`, sekce *Kdo dostane profil*.

Vybrané zapiš do `CLAUDE.md` jako **tvrdé `@import`y**, ne jako odkazy v běžném textu:

```
## Doménové znalosti

Závazné pro tenhle projekt:

@~/Context/Coding/coding.md
@~/Context/Web/web.md
```

**Proč `@import` a ne odkaz:** `@import` Claude Code při startu session textově rozbalí do kontextu, takže obsah platí vždy. Prozaický odkaz („řiď se souborem X“) je jen instrukce, kterou si model musí sám všimnout a sám se rozhodnout ji splnit – to se v praxi dodržuje nespolehlivě.

Platí to **pro projekt**, kde je doména relevantní pořád. Globální `~/.claude/CLAUDE.md` naopak odkazuje běžným textem schválně – tam se domény střídají a import všech by stál kontext v každé session.

Importuj **jen to, co je pro projekt opravdu relevantní.** Každý import stojí kontext v každé session.

Upozorni uživatele, že při příštím spuštění dostane dialog na schválení externího importu a **musí ho odsouhlasit**.
