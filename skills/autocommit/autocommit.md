# Autocommit

Pravidla, která platí v projektu se zapnutým autocommitem. Importuje si je sekce `## Autocommit` v projektovém `CLAUDE.md`, kterou tam zapsal `/autocommit` – v projektu bez té sekce tenhle soubor neplatí a nenačte se.

- **Commituj po každé zásadní ucelené změně** – ne po každém dílčím kroku, ale po každém logickém celku.
- **Má-li repozitář nastavený git remote, po commitu hned pushuj.** Remote ověřuj `git remote get-url origin`, ne `git remote` – to vypíše `origin` i u sekce bez adresy, třeba z globálního `~/.gitconfig`, a push pak v každé odpovědi selže.
