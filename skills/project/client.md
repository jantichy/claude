# Klientská složka

Katalog k `SKILL.md`: co se v průběhu mění, když projektový adresář leží pod `~/Projekty`. **Co se do klientských souborů píše, drží kostry v `~/Context`** – `organizations/organizations.md`, *Kostra profilu*, a `business/invoicing.md`, *Soubor klienta*. Tenhle soubor říká jen kdy, kam a v jakém pořadí; kostry neopisuj, načti si je.

**Klient** je organizace, pro kterou se pracuje, ať platí, nebo ne. Jeho složka drží všechno, co se pro něj dělá: profil, u fakturovaného klienta fakturační soubor, dokumenty, drobnosti a podprojekty.

## Rozpoznání

Rozhoduje cesta projektového adresáře, ve worktree layoutu cesta kontejneru:

| Kde leží | Co to je | Co z tohoto souboru platí |
|---|---|---|
| `~/Projekty/<Client>` | **klient** | *Klient* |
| hlouběji pod `~/Projekty/<Client>/` | **podprojekt** klienta | *Podprojekt* |
| jinde | běžný projekt | nic |

Řekni nahlas, co jsi rozpoznal. U klienta, který ještě nemá ve složce `invoicing.md`, se pak **zeptej přes `AskUserQuestion`, jestli se mu fakturuje** (*fakturuje se* / *pracuje se pro něj bez fakturace* / *ani jedno*). Na odpovědi stojí, jestli vznikne fakturační soubor, a ze slugu se nepozná. Kde soubor už je, odpověď dává jeho existence a znovu se neptá.

**Složka vzniká, když je co v ní držet** – pracovní soubory, podklady k přípravě, poznámky k historii spolupráce. **Fakturace o ní nerozhoduje ani jedním směrem:** přímo domluvené školení, ke kterému se nic nepřipravuje ani neeviduje a faktura se pošle ručně, složku nepotřebuje, i když se fakturuje; podobná domluva, ke které se chystají podklady, ji potřebuje; a zakázka, která se vůbec nefakturuje, ji potřebuje kvůli pracovním souborům. Jestli a jak se fakturuje, drží `invoicing.md` ve složce; `/invoicing` vidí jen klienty se složkou, ostatní se fakturují ručně. Odučené běhy eviduje `~/Context/speaking/` bez ohledu na složku. Osobní projekt, který se organizace jen tematicky dotýká, patří do `~/Dev`; organizace bez práce i fakturace má jen profil v `~/Context/organizations/`. Při odpovědi *ani jedno* to řekni a zeptej se, jestli složka opravdu má vzniknout – jinak by se do `~/Projekty` dostaly vlastní věci.

## Klient

### Odchylky od kroků

- **Krok 0:** existuje-li `~/Context/organizations/<client>.md` jako plný profil (ne odkaz podle `organizations.md`, *Klient s vlastní složkou*), je to **převod**. Režim se tím nemění – prázdná složka je dál `create`, rozdělaná `adopt` –, jen v něm *Převod* níž nahradí založení profilu. Ohlas to hned v kroku 0, provádí se to až na místě níž.
- **Krok 1:** složka nese **jméno klienta s velkým počátečním písmenem** (`Acme`, `ABsoft`), zástupně `<Client>` – navrhni ho a nech potvrdit, jak se má psát zbytek jména, rozhoduje uživatel. **Slug je totéž jméno malými písmeny**, bez diakritiky, víc slov spojovníkem (`~/Context/CLAUDE.md`, pojmenování v `organizations/`), zástupně `<client>`: nese ho blok metadat, profil `<client>.md` a odkazy v `~/Context`. Je to jediná složka, jejíž slug se od jména adresáře liší velikostí písmen; revize v kroku 14 to nehlásí jako odchylku.
- **Krok 3:** klientská složka je **vždycky git repozitář**, volba *Nic* se nenabízí. Fakturační soubor nese sazby a dohody, takže **remote smí být jen soukromý** – u GitHubu `--private` bez ptaní na viditelnost.
- **Krok 4:** neptej se, platí jeden pracovní adresář. Podprojekty leží jako podsložky klientské složky a ve worktree layoutu by neměly kam patřit: kořen kontejneru není pracovní strom a v `main/` by chyběly v každé další větvi.
- **Mezi krokem 3 a 5:** založ profil a fakturační soubor (*Profil a fakturační soubor*); existující profil převeď (*Převod*). Až tady, protože repozitář už existuje a krok 13 bude importovat soubor, který je na disku.
- **Krok 8:** do `.gitignore` patří každá podsložka s vlastním repozitářem (*Podprojekt* níž).
- **Krok 11:** složka bez vlastního kódu – profil, dokumenty, analýzy – je typ **Psaní a obsah**; kód leží v podprojektech.
- **Krok 12:** ve složce bez kódu není co spouštět; řekni to podle kroku 12 a `verify.sh --allow` nevypisuj.
- **Krok 13:** místo *Profilu organizace* z `checklists.md` zapiš do `CLAUDE.md` sekci s importem profilu ze složky:

```
## Klient

@<client>.md

Fakturační soubor `invoicing.md` se neimportuje – čte ho jen `/invoicing`.
```

**Proč se `invoicing.md` neimportuje:** sazby a deníky by šly do kontextu každé práce pro klienta a mohly by proklouznout do dokumentu, který jde klientovi.

### Profil a fakturační soubor

1. **Profil `<client>.md`** založ v klientské složce podle *Kostry profilu*. Má ho **každý klient**, u jednorázové zakázky klidně tenký (*Co to je*, *Vztah k Honzovi*, *Lidé*). Ptej se po sekcích, jednu po druhé. Co organizace nemá, se vynechá; co nevíš, označ značkou `*doplnit*` (`organizations.md`, *Co se sem nepíše*) – nevymýšlej. Sekce *Projekty* u klienta odpadá, protože projekty jsou podsložky vedle profilu.
2. **Fakturační soubor `invoicing.md`** založ jen klientovi, kterému se fakturuje, podle *Souboru klienta*. Části, které kostra dovoluje vynechat (*Vzdálený timetracking* u klienta bez vlastního timetrackingu), se řídí kostrou; v ostatních vyplň každé pole, i když je odpovědí `nemá` nebo `nezjištěno`. **Oba deníky založ prázdné** – záznamy v kostře jsou ukázka tvaru, ne obsah. **Identifikátory ve Fakturoidu a v Clockify nikdy neodhaduj ze slugu ani z názvu:** nech si je říct, nebo je dohledej voláním podle `business/invoicing.md`, *Přístupy*. Vymyšlené ID vypadá platně a projeví se až prázdným obdobím. Odběratele, který ve Fakturoidu ještě není, nezakládej – nech pole v *Napojení* `nezjištěno` a v souhrnu řekni, že fakturu klientovi vystavit nepůjde, dokud se nedoplní. Pole *Projekty* je `~/Projekty/<Client>`.
3. **Odkazy v `~/Context`:** do `organizations/<client>.md` a u fakturovaného klienta do `business/invoicing/<client>.md` zapiš odkaz na klientskou složku v tvaru podle `organizations.md`, *Klient s vlastní složkou*.

**Bez `invoicing.md` v klientské složce `/invoicing` klienta nevidí** – hledá jen v `~/Projekty/*/invoicing.md`. Na konci to ověř výpisem toho vzoru.

### Převod

Organizace už má profil v `~/Context`, protože se pro ni dosud nepracovalo, a teď dostává složku. Fakturační soubor se nepřevádí: v `~/Context` leží jen odkaz na klientskou složku, takže se založí podle *Profilu a fakturačního souboru*, bod 2.

1. **Ukaž, co se přesune, a nech to potvrdit jednou otázkou** – originál v `~/Context` se přepíše odkazem a *Zásady* `SKILL.md` přepis bez zeptání nedovolují.
2. **Přesuň obsah, nekopíruj ho:** profil do `<client>.md` v klientské složce, originál v `~/Context` nahraď odkazem. Jsou to dva repozitáře, takže to není `git mv` – historie do převodu zůstává v historii souboru v `~/Context` a odkaz to říká.
3. **Sekce *Projekty* v profilu odpadá**, jakmile v ní nic mimo složku nezbude – osobní projekt, který se organizace jen tematicky dotýká, v ní zůstává.
4. **Najdi odkazy na starou cestu.** `~/Dev` ani `~/Projekty` nejsou repozitáře, ale adresáře repozitářů, a obyčejný `grep` v shellu Claude Code respektuje `.gitignore` a část výskytů nevidí. Projdi proto každý repozitář zvlášť, a to jednou – worktree layout má víc pracovních stromů nad týmž repozitářem a pracovní strom podprojektu může ležet ve třetí úrovni (`~/Projekty/<Client>/<sub>/main`). Výčet adresářů dělá `find`, protože vzor, který se nerozbalí na nic (`~/Projekty/*/` před první klientskou složkou), shodí v `zsh` celý příkaz. **Za `<client>` dosaď slug** – nedosazený vzor nic nenajde a tváří se jako čistý výsledek:

```bash
{ echo ~/Context; echo ~/.claude; find ~/Dev ~/Projekty -mindepth 1 -maxdepth 3 -type d 2>/dev/null; } | while read -r d; do
  [ "$(git -C "$d" rev-parse --show-toplevel 2>/dev/null)" = "$d" ] || continue
  c=$(git -C "$d" rev-parse --path-format=absolute --git-common-dir)
  case " $seen " in *" $c "*) continue ;; esac
  seen="$seen $c"
  git -C "$d" grep --untracked -n -F -e "organizations/<client>.md" | sed "s|^|$d/|"
done
```

   **`@import` starého profilu je nejdůležitější nález:** po převodu by importoval jen odkaz a projekt by o klientovi tiše přestal vědět. Nalezené importy vypiš a **jednou otázkou nabídni jejich přepis** na `@~/Projekty/<Client>/<client>.md` – je to zápis do cizího projektu. Leží-li projekt ve worktree layoutu, do jeho `main/` nezapisuj (`~/.claude/standards/worktree.md`) a vypiš opravu jako úkol pro práci v tom projektu. Ostatní výskyty vypiš k opravě přes `/replace`. Commit zápisu řídí *Zápis mimo projekt* níž.

### Revize

V kroku 14 ověř u klienta navíc:

- profil leží ve složce a `CLAUDE.md` ho importuje; fakturovaný klient má `invoicing.md` a v něm pole *Projekty* s klientskou složkou;
- odkazy v `~/Context/organizations/` a `business/invoicing/` existují a míří sem;
- **každá podsložka s vlastním repozitářem** – má `.git`, adresář i soubor (worktree layout má `.git` jako soubor vedle `.bare/`) – je v `.gitignore`. Byla-li už commitnutá do klientského repozitáře, řádek v `.gitignore` nestačí; nabídni `git rm -r --cached <podsložka>`;
- žádný `CLAUDE.md` v podsložkách profil neimportuje (*Podprojekt*). Podsložka bez vlastního repozitáře je obsah klientského repozitáře a nic dalšího se u ní neověřuje.

Nálezy jdou do tří skupin souhrnu v režimu `update` jako všechny ostatní.

## Podprojekt

- **Rodič musí být nastavený.** Nemá-li `~/Projekty/<Client>/` `CLAUDE.md` s importem profilu, řekni to, doporuč napřed `/project` v klientské složce a **skonči** – podprojekt by neměl profil odkud zdědit a kroky 9 a 10, které přeskakuje, by mu nechaly bez paměťové politiky i autocommitu.
- **Profil neimportuje.** Dědí ho z `~/Projekty/<Client>/CLAUDE.md`, protože Claude Code načítá `CLAUDE.md` všech nadřazených adresářů. Stejně tak dědí paměťovou politiku a autocommit, takže **kroky 9 a 10 se přeskakují** – dědění se v `CLAUDE.md` podprojektu přebít nedá, a co platí u klienta, platí i tady. **Najdeš-li v podprojektu import profilu**, nabídni jeho odstranění – profil by se načetl dvakrát.
- **Vlastní repozitář jen podle kritéria:** podprojekt má vlastní nasazení nebo CI, cizí remote, nebo se předává či sdílí samostatně. Krok 3 se proto ptá napřed na tohle.
  - **Nesplní-li ani jednu podmínku**, patří do klientského repozitáře: krok 3 je *Nic* bez ptaní, kroky 4 a 8 odpadají. Průběžná kontrola se počítá pro repozitář, takže potřebuje-li podprojekt kontrakt příkazů, je to důvod pro vlastní repozitář – zeptej se.
  - **Splní-li některou**, dostane vlastní repozitář (smí i worktree layout) a jeho cestu doplň do `.gitignore` klientské složky. Vlastní remote je soukromý jako u klienta, pokud to není klientův remote.
- **Krok 13:** *Profil organizace* se nepoužije; ostatní doménové checklisty platí jako jinde.

## Zápis mimo projekt

Klientská větev zapisuje i do jiných repozitářů: do `~/Context` (odkazy, převod), do klientského repozitáře z podprojektu (`.gitignore`) a do projektu s opraveným importem. **Platí-li v tom repozitáři autocommit, commitni zápis sám** – platí, má-li sekci `## Autocommit` se zapnutým stavem `CLAUDE.md` v kořeni repozitáře nebo v kterémkoliv nadřazeném adresáři (podprojekt ho dědí od klienta) – jmenovanými cestami, a pushni, má-li remote – jinak ho posbírá autocommit cizí session spolu s něčím nesouvisejícím (`~/.claude/skills/preflight.md`). Nemá-li autocommit, nech zápis v pracovním stromu a v souhrnu řekni, kde leží necommitnutý.
