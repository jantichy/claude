# Moje Claude Code konfigurace

Tohle je moje osobní konfigurace [Claude Code](https://docs.claude.com/en/docs/claude-code), kterou tu sdílím pro inspiraci. Třeba tu najdete něco užitečného i pro vaši práci. Budu rád i za jakékoliv vaše nápady a připomínky, napište mi na e-mail [jantichy@jantichy.cz](mailto:jantichy@jantichy.cz)!

Co bych z celého repozitáře vypíchl, aby to neuteklo vaší pozornosti?

## `CLAUDE.md` – hlavní soubor s instrukcemi

Na tomhle souboru je zajímavé hlavně to, že v něm skoro nic není 😉. Většina instrukcí je dekomponovaná do dalších .md souborů. Všimněte si, že mezi nimi rozlišuju ty, které obsahují kritické body společné pro všechny projekty a mají se použít vždy, a ty, které se načtou jen když je to podle situace potřeba. Brutálně se tím šetří kontextové okno.

## `RULES.md` – struktura a pořádek pod kontrolou

Kdo mě zná, tak ví, že jsem hodně citlivý na strukturovanost a čistotu návrhu. [OCD](https://cs.wikipedia.org/wiki/Obsedantn%C4%9B-kompulzivn%C3%AD_porucha) hadr neasi. A opravdu hodně trpím tím, jakých svévolností se dovede Claude v projektu dopustit, když se chvíli nehlídá. Tenhle soubor ho drží na uzdě napříč všemi mými projekty. Vedlejší efekt je, že mu pak většinu věcí stačí říct jenom jednou. A co se nevychytá tady, to dotáhne do dokonalosti skill `/consistency`.

## `/consistency` – ultimátní skill proti bordelu

Kompletní audit projektu na vnitřní konzistenci a pořádek. Spustí Explore agenta, který systematicky projde celý projekt a hledá: sémantické nekonzistence, protichůdné instrukce a zadání, strukturální nekonzistence všeho možného druhu, duplicity a redundance, zapomenuté zbytky po smazaných částech projektu, mrtvý kód a nepoužité závislosti, bezpečnostní nekonzistence, typové nesrovnalosti, drift mezi vrstvami… Následně je kategorizuje od kritických až po kosmetické a jednu po druhé se mnou postupně prochází, se srozumitelným vysvětlením, návrhem řešení a zpětnou verifikací provedených oprav.

## `/autocommit` – každá změna hned do Gitu

Zapne pro daný projekt režim, kdy Claude po každém logickém celku automaticky commituje. A pokud je nastavený remote, taky pushuje. Nehodí se do všech projektů, ale tam, kde mám hromadu rychlých iterací, mi to šetří desítky až stovky commit instrukcí za den.

## `/autoprompt` – ukládá všechny prompty

Zapne pro projekt automatické logování všech mých promptů na jedno snadno přístupné a čitelné místo, do souboru `PROMPTS.md` v rootu projektu. Při zapnutí dokonce backfilluje historii ze session souborů, takže získám kompletní záznam i zpětně. Ač to na první pohled nevypadá, dříve či později to opravdu doceníte. Pro sledování, jak se projekt vyvíjel, pro učení se vlastních anti-patternů v promptech, překvapivě často tam pošlete Clauda, aby si z toho něco zpětně vytahal nebo naučil…

## `statusline.sh` – krásná a užitečná status line

Jednořádková status line, která mi ukazuje všechno, co potřebuju průběžně vidět: aktuální model, zaplnění kontextového okna, čerpání 5hodinového i týdenního limitu, aktuální adresář i stav Gitu. Vizualizace ukazuje čerpání pomocí teploměru, procent i zbývajícího času. Navíc mění barvy, čím je okno plnější nebo limit vyčerpanější, tím jasněji příslušná položka svítí.

![Status line](statusline.png)

## `settings.json` – průběžně laděné permissions

Allowlist/denylist/asklist se snažím držet ve vyváženém poměru „bezpečnost vs. flow“. Cíl je nemuset odklikávat každou trivialitu, ale zároveň nenechat bez kontroly moc bezpečnostních děr. Tohle je vždycky lavírování na hraně a občas tu jdu vědomě lehce za hranu – ve prospěch svého pohodlí a na úkor středně rizikových operací. Takže si to k sobě rozhodně nekopírujte bezhlavě, ale můžete to vzít čistě inspiračně pro porovnání s vlastním nastavením.
