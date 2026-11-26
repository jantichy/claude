# Formát zdroje prezentace

Zdroj prezentace je jeden soubor Markdownu, `Prezentace.md`. Z něj `build.py` sestaví `.pptx` nad šablonou. Do `.pptx` se nesahá – každá úprava jde sem a prezentace se sestaví znovu.

## Řádky

Text před prvním `## ` se ignoruje, takže úvod souboru smí nést cokoliv. Prázdné řádky se ignorují.

| Řádek | Co je |
|---|---|
| `## <typ> <argumenty>` | začátek slajdu; argumenty jsou slova za typem oddělená mezerou |
| `# <text>` | řádek nadpisu; víc řádků `#` dá víc řádků nadpisu |
| `### <text>` | začátek bloku – karta, velké číslo, buňka mřížky; řádky pod ním patří do bloku až do dalšího `###` |
| `- <text>` | odrážka |
| `<text>` | běžný řádek textu |
| `= <text>` | tmavý pruh, u mřížky pointa pod ní |
| `> <text>` | poznámky řečníka; samotné `>` je prázdný řádek poznámek |

Uvnitř textu:

- **`|`** ručně zalamuje řádek. V tabulce místo toho odděluje buňky.
- **Text v zpětných apostrofech** se sází písmem Roboto Mono. V tabulce se to neděje – apostrofy v ní zůstanou vidět.
- **Pevnou mezeru** za krátkou předložkou, spojkou a číslem doplní generátor sám; do zdroje se nepíše.
- **`DOHLEDAT:`** v poznámkách značí údaj, který ještě chybí nebo se musí ověřit. Generátor ho nehlídá, hledá se grepem.

## Typy slajdů

| Typ | Co nese |
|---|---|
| `title` | `#` titulek, běžné řádky podtitulek |
| `section` | mezislajd – **jen předěl, kterým začíná nová část přednášky**: `#` nadpis, běžné řádky podtitulek. Argument `qr=<adresa>` přidá vpravo dole QR kód na tu adresu |
| `claim` | samostatné sdělení – pointa nebo tvrzení, které má zaznít samo: `#` tvrzení velkým písmem na světlém pozadí, běžné řádky podtitulek. **Na sdělení se nepoužívá `section`** – tmavý mezislajd ohlašuje začátek nové části a publikum by se ve struktuře ztratilo |
| `bullets` | `#` nadpis, pod ním odrážky a běžné řádky |
| `cards` | `#` nadpis a dva bloky `###` – světlá a tmavá karta; v bloku odrážky a běžné řádky. Výšku karet generátor odhadne podle delšího textu |
| `grid` | `#` nadpis a **právě čtyři** bloky `###`, z bloku se bere jen jeho řádek; `=` pointa pod mřížkou. Jiný počet bloků sestavení zastaví |
| `numbers` | `#` nadpis a dva bloky `###` – velké číslo, řádky pod ním popisek; `=` tmavý pruh dole |
| `table` | `#` nadpis, běžné řádky s buňkami oddělenými `\|`; první řádek je záhlaví, první sloupec štítky řádků |
| `image` | `#` nadpis a argument `src=<cesta>` – obrázek vůči adresáři zdroje, vejde se do plochy pod nadpisem celý. Chybí-li soubor, sestavení se zastaví |
| `end` | `#` titulek, běžné řádky odkazy |

## Kresba jedné prezentace

Typ, který není v tabulce výš, je kresba jedné prezentace – schéma, které se ze vzorových slajdů šablony poskládat nedá. Leží vedle zdroje jako `<typ>.py`: jméno malými písmeny, číslicemi a podtržítky, protože je zároveň jménem modulu.

Modul má funkci `render(slide, args)`. Generátor slajd založí, napíše na něj `#` nadpis a kresbě předá slajd z `python-pptx` a argumenty z řádku `##`; kresba kreslí pod nadpis. Odrážky, bloky a pruh se u kresby nepoužijí, poznámky ano.

Kresba je obsah prezentace, ne nástroj: patří k jedné přednášce a stěhuje se s ní.

## Ukázka

```markdown
## section qr=https://example.com/materialy
# Měření bez cookies
Co z dat zbude

## cards
# Dva přístupy
### Server
- data jdou přes vlastní doménu
- `sGTM` před GA4
### Prohlížeč
- data jdou rovnou do GA4
> DOHLEDAT: podíl blokovaných požadavků
```
