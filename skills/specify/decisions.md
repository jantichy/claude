# Rozhodnutí – /specify

Soubor drží rozvahu a doklady skillu `/specify`; za běhu skillu se nečte.

### Brainstorming se i na otevřenou otázku ptá přes `AskUserQuestion`

**Rozhodnuto 6. 11. 2026.** Doloženo během `/specify` 1. 11. 2026: `superpowers:brainstorming` začíná otevřenou otázkou v textu a nabídku variant dává, až když člověk neví. Zadání ze `/specify` mu sice velelo `AskUserQuestion`, ale `~/.claude/standards/rules.md` pouští otázku bez variant v textu, a brainstorming to vzal jako svolení. Uživatel dostal dvě otázky v textu a musel si o nástroj říct sám. Zadání brainstormingu proto výslovně říká, že i otevřená otázka jde přes `AskUserQuestion` s variantami z podkladů a *Other* pro vlastní popis; v textu zůstává jen holá hodnota.

**Zamítnuto:** zúžit výjimku přímo v `rules.md` (samotné nebo spolu se `/specify`). Výjimka tam míří na hodnotu, kterou ví jen uživatel, a sedí; vada vznikla na styku s cizím skillem, který `rules.md` nečte jako svá pravidla, takže oprava patří do jeho zadání. Úprava `rules.md` by navíc stála kontext v každé session.
