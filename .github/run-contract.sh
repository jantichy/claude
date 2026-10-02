#!/bin/sh
# Spustí příkazy z kontraktu projektu a skončí nenulově, selhal-li kterýkoliv.
#
# Stojí ve vlastním souboru, ne v těle kroku workflow, kvůli jediné věci:
# takhle se dá spustit a změřit. Textové kontroly nad workflow neuměly poznat,
# že přestalo umět zčervenat – `exit 0`, `continue-on-error`, `|| true`,
# prázdný kontrakt i smazané `set -e` jimi prošly (doloženo 18. 9. 2026
# v jednom z projektů, kde tahle kopie vznikla). `tests/test_ci.py` proto
# pouští obojí: kontrakt ze samých pomlček musí vrátit 0 a kontrakt
# s padajícím příkazem 1.
#
# Volá ho sdílený `.github/workflows/contract.yml` z klonu konfigurační vrstvy,
# takže projekty si ho nenesou – dřív ho měl každý v kopii.
#
# Kontrakt se sem nepíše ani neparsuje podruhé – přebírá se z `verify.sh
# --contract` jako TSV, což je tentýž kód, který příkazy spouští lokálně.

set -e

contract="${1:?použití: run-contract.sh <contract.tsv>}"
[ -r "$contract" ] || { echo "::error::kontrakt $contract nejde přečíst"; exit 1; }

# Absolutní cesta, a to JEŠTĚ PŘED `cd` níž: smyčka čte kontrakt znovu, takže
# relativní cesta by se po přepnutí adresáře nenašla a se `set -e` by skript
# spadl na něčem, co vypadá jako chyba jinde. Dnes to nehrozí (workflow předává
# $RUNNER_TEMP a projekt klíč `cwd` nemá), ale je to past, ne vlastnost.
case "$contract" in
  /*) ;;
  *)  contract="$(cd "$(dirname "$contract")" && pwd)/$(basename "$contract")" ;;
esac

# `cwd` posouvá, kde se příkazy spouštějí – průběžná kontrola ho respektuje,
# takže CI musí taky, jinak by každá pouštěla něco jiného.
cwd=$(awk -F'\t' '$1 == "cwd" { print $2 }' "$contract")
if [ -n "$cwd" ]; then
  cd "$cwd"
fi

# Jmenovaný seznam kroků, které do CI patří. Ne všechny klíče kontraktu:
# `dev` je watch server, který nikdy neskončí, `cwd` není příkaz. Klíč,
# který projekt nemá, se přeskočí nahlas.
status=0
for key in typecheck lint test build e2e audit coverage a11y perf mutation; do
  command=$(awk -F'\t' -v k="$key" '$1 == k { print $2 }' "$contract")
  if [ -z "$command" ]; then
    echo "::notice::$key – není v kontraktu, nekontroluje se"
    continue
  fi
  if [ "$command" = "-" ]; then
    echo "::notice::$key – projekt ho vědomě nemá"
    continue
  fi
  echo "::group::$key"
  if sh -c "$command"; then
    echo "::endgroup::"
  else
    echo "::endgroup::"
    echo "::error::$key selhal"
    status=1
  fi
done
exit $status
