# Doménové checklisty

Katalog ke kroku 13 v `SKILL.md`: jak se na checklisty ptát, co která volba importuje, co předvyplnit podle typu projektu a jak se přidává profil organizace.

Checklistů je devět a `AskUserQuestion` bere najednou nejvýš čtyři volby (týž strop jako v kroku 11). Ptej se **ve třech kolech**, všechna s `multiSelect: true`. **Kola se dělí tematicky, ne aby byla plná** – uživatel odpovídá na otázku, ne na seznam, a otázka musí jít položit jednou větou. Volby předvyplň podle typu z kroku 11, ale nech uživatele rozhodnout – vývojářský projekt bývá zároveň web, web bývá zároveň administrace.

| Kolo | Otázka | Volby |
|---|---|---|
| 1 | „Co všechno se v projektu bude dělat s kódem a rozhraním? Když nic, nic nezaškrtávej.“ | Psaní kódu · Webové rozhraní · Administrace / backoffice · Webová analytika a měření |
| 2 | „A co se v něm bude psát a učit? Když nic, nic nezaškrtávej.“ | Psaní českých textů · Česká typografie · Školení a kurzy |
| 3 | „A bude se v něm něco kreslit nebo promítat? Když nic, nic nezaškrtávej.“ | Vizuální tvorba a grafika · Prezentace a slajdy |

Volbu **Žádný** nikam nedávej – prázdný výběr v `multiSelect` ji nahrazuje. **Nový checklist zařaď do kola, kam tematicky patří**; teprve nevejde-li se do žádného pod strop čtyř voleb, přidej další kolo. Pátá volba do existujícího kola nepatří nikdy.

**Česká typografie je samostatná volba, ne přívažek k psaní textů.** Projekt s českým rozhraním nebo se slajdy sází česky, i když v něm žádný souvislý text nevzniká – a naopak by ho nemělo nic nutit brát si kvůli sazbě celý redakční standard.

Přehled všech devíti i s cílem importu:

| Volba | Import |
|---|---|
| Psaní kódu | `@~/Dev/context/coding/coding.md` |
| Webové rozhraní | `@~/Dev/context/web/web.md` |
| Administrace / backoffice | `@~/Dev/context/web/admin.md` |
| Webová analytika a měření | `@~/Dev/context/analytics/analytics.md` |
| Psaní českých textů | `@~/Dev/context/text/text.md` |
| Česká typografie | `@~/Dev/context/text/typography.md` |
| Školení a kurzy | `@~/Dev/context/training/training.md` |
| Vizuální tvorba a grafika | `@~/Dev/context/design/design.md` |
| Prezentace a slajdy | `@~/Dev/context/design/slides.md` |

U typu **Nasazení webové analytiky** přihraj napevno `analytics/analytics.md` a `web/web.md` (analytika se nasazuje do webu a překrývá se s ním v consentu a GDPR) a předvyplň `text/text.md` i `text/typography.md`, protože výstupem bývá auditní report nebo dokumentace pro klienta. `coding/coding.md` nabídni jen tehdy, když se v projektu opravdu píše kód – šablony, serverový endpoint, vlastní CMP.

U typu projektu, kde se připravuje **školení, kurz nebo workshop**, předvyplň `training/training.md` spolu s `text/text.md` a `text/typography.md` – materiály pro účastníky jsou text a řídí se vším trojím. Přihoď i `design/slides.md`, pokud k tomu vzniká promítaná prezentace.

`design/slides.md` nabízej i mimo školení – všude, kde se dělá deck: konferenční přednáška, prodejní pitch, prezentace výsledků klientovi. Importuje se **navíc** k `design/design.md`, ne místo něj.

`worktree.md` se tu nenabízí schválně – importuje se už v kroku 4, když si uživatel zvolí worktree layout.

`brand/brand.md` se tu nenabízí taky schválně, ale z jiného důvodu: je to **korpus, ne checklist**. Neříká, jak se něco dělá, ale jak to je – a projekt, který píše ven, si ho načte podle potřeby přes `~/.claude/CLAUDE.md`, kde je vedený mezi podmíněnými doménovými znalostmi. Importovat ho natvrdo do každého takového projektu by znamenalo vozit korpus tam, kde stačí sáhnout.

### Profil organizace

Když projekt vzniká **pro konkrétní organizaci**, zeptej se, jestli má profil v `~/Dev/context/organizations/`, a když ano, přidej ho do importů:

```
@~/Dev/context/organizations/planetum.md
```

**Není to doménový standard, ale korpus** – kdo v organizaci sedí, kdo co schvaluje, jaké mají systémy. Profil zůstává v knowledge base a projekt na něj jen odkazuje; jedna organizace může mít víc projektů a všechny sdílejí týž profil. Když profil neexistuje a jde o **opakovaný vztah, u kterého je potřeba znát vnitřek organizace**, navrhni jeho založení – kritérium je v `~/Dev/context/organizations/organizations.md`, sekce *Kdo dostane profil*.

Vybrané zapiš do `CLAUDE.md` jako **tvrdé `@import`y**, ne jako prozaické odkazy:

```
## Doménové standardy

Závazné pro tenhle projekt:

@~/Dev/context/coding/coding.md
@~/Dev/context/web/web.md
```

**Proč `@import` a ne odkaz:** `@import` Claude Code při startu session textově rozbalí do kontextu, takže obsah platí vždy. Prozaický odkaz („řiď se souborem X“) je jen instrukce, kterou si model musí sám všimnout a sám se rozhodnout ji splnit – to se v praxi dodržuje nespolehlivě.

Platí to **pro projekt**, kde je doména relevantní pořád. Globální `~/.claude/CLAUDE.md` naopak odkazuje prozaicky schválně – tam se domény střídají a import všech by stál kontext v každé session.

Importuj **jen to, co je pro projekt opravdu relevantní.** Každý import stojí kontext v každé session; `web/web.md` a `web/admin.md` mají dohromady skoro 500 řádků.

Upozorni uživatele, že při příštím spuštění dostane dialog na schválení externího importu a **musí ho odsouhlasit**.
