# /serviceaccount – založení strojového přístupu ke klientským systémům

Když pracujete pro víc klientů a potřebujete se do jejich Analytics nebo Tag Manageru dostat i programově, stojíte před otázkou, pod jakou identitou. Osobní účet je nejpohodlnější a nejhorší: je to jediný klíč, který otevírá data všech klientů naráz. Správná odpověď je samostatný účet pro každou dvojici klient a systém – jenže těch účtů rychle přibývá a bez řádu se v nich za půl roku nikdo nevyzná, protože jejich jméno se po založení nedá změnit.

Tenhle skill takový účet připraví od jména po žádost o přístupy. Zeptá se na pár věcí, zbytek odvodí z toho, na čem zrovna pracujete, a vrátí všechno k rozkopírování.

## Co umí

- Pozná z rozpracovaného projektu, o kterého klienta jde, a nabídne jména účtů podle vaší konvence – včetně toho, jestli má účet vidět na všechny weby klienta, nebo jen na jeden.
- Zeptá se, do kterých systémů má účet vidět, a poskládá výsledné adresy.
- Ke každému účtu napíše lidský název a popis, aby v konzoli i u klienta bylo na první pohled jasné, co ten účet je.
- Ohlídá limit délky, který jde snadno přehlédnout, a řekne, co zkrátil.
- Připraví příkaz, který stažené klíče uklidí z disku do bezpečí a rovnou z nich vyčte identifikátory pro přímý odkaz na každý účet.
- Sepíše žádost pro klienta s konkrétními úrovněmi oprávnění pro každý systém, aby se dala poslat beze změn.
- Nakonec vzniklé účty zapíše do evidence, takže za rok víte, co existuje a kam to vidí.

## Proč zrovna tenhle

- Jméno účtu se po založení **nedá změnit** – oprava znamená založit nový, znovu ho nasdílet ve všech systémech a znovu o to požádat klienta. Skill tlačí na to, aby bylo správně napoprvé.
- Z názvu účtu je vidět **rozsah jeho přístupu**, ne jen ke komu patří. To je informace, kterou jinak musíte lovit v administraci každého systému zvlášť.
- Konvenci nenese skill, ale váš vlastní soubor. Když se rozhodnete jinak, měníte jedno místo a skill se přizpůsobí.
- Klíč se nikdy nenechává ležet ve staženém souboru, odkud se běžně dostane do zálohy nebo omylem do gitu.

## Jak se to používá

Zavolá se v adresáři projektu, na kterém zrovna děláte:

```
/serviceaccount
```

Zeptá se na klienta a systémy a vrátí tabulku účtů plus čtyři kroky k provedení. Mimo projekt mu můžete klienta rovnou napovědět: `/serviceaccount planetum`.

## Ukázka výstupu

| Service account ID | Display name | Description |
|---|---|---|
| `planetum-ga4` | GA4 Planetum | Přístup k měření webu planetum.cz |
| `planetum-gtm` | GTM Planetum | Správa kontejneru webu planetum.cz |

A pod tím kroky: kde účty založit, jak vygenerovat klíče, jediný příkaz na jejich uklizení a hotový text žádosti o přístupy pro klienta.

## Co nedělá

- Účty ani klíče nezakládá – to zůstává za vaším přihlášením do Google Cloudu.
- Do administrace klientských systémů nevolá; přístupy uděluje klient.
- Neřeší přístupy, které už existují. Zakládá nové, revizi stávajících dělá člověk.

## Jak si ho nainstalovat

> Jdi na https://github.com/jantichy/claude/tree/main/skills/serviceaccount
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

**Skill sám o sobě nestačí.** Opírá se o soubor s konvencí, který je součástí soukromé znalostní báze a v repozitáři není – musíte si ho vytvořit. Patří do něj tvar jmen účtů, seznam systémů i s jejich zkratkami, úrovně oprávnění, o které se žádá klient, a pravidlo pro ukládání klíčů. Bez něj se skill odmítne rozjet, což je záměr: vymyšlené jméno účtu je neměnné.

---

### Požadavky a omezení

- **macOS.** Příkaz pro uložení klíčů používá systémovou klíčenku.
- **Účet v Google Cloudu** s právem zakládat service accounty a přístup do systémů, které se mají sdílet.
- **Python 3** kvůli vyčtení identifikátorů ze stažených klíčů.
- Jeden cloud projekt pro všechny účty. Kvóta je sto účtů na projekt a dá se zvýšit; klíčů na jeden účet je nejvýš deset a to je pevný strop.
