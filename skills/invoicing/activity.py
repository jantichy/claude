#!/usr/bin/env python3
# Složí z session logů Clauda a z gitu bloky aktivity od–do – zdroj stop práce pro `/invoicing recover`.
#
# Použití:  python3 activity.py 2026-09-01 2026-09-30 ~/Dev/<project> ~/Projekty/<Client>
#           python3 activity.py --gap 30 2026-09-01 2026-09-30 ~/Dev/<project>
#
# Cesta je **prefix**, ne jeden projekt: `~/Projekty/<Client>` pokryje i všechny
# projekty v jeho podadresářích. Session logy se hledají podle zakódovaného jména cesty
# v `~/.claude/projects/`, takže se najdou i tehdy, když adresář na disku už neexistuje.
# Git se čte jen z cest, které na disku jsou a jsou to repozitáře.
#
# Bloky se dělí podle mezery mezi dvěma sousedními záznamy; delší mezera než `--gap`
# minut blok ukončí. Proud událostí a pravidlo mezery jsou ze `skills/timeline.py`, sdíleného
# s `/clauding` – obě otázky „kolik času v tom bylo“ tak mají jednu odpověď. Výstup je JSON,
# jeden blok na položku, časy v místním pásmu.

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "skills"))
import timeline  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Bloky aktivity ze session logů Clauda a z gitu."
    )
    parser.add_argument(
        "--gap",
        type=int,
        default=int(timeline.GAP.total_seconds() // 60),
        help="mezera v minutách, která ukončí blok (výchozí podle timeline.GAP)",
    )
    parser.add_argument("since", help="od YYYY-MM-DD včetně")
    parser.add_argument("until", help="do YYYY-MM-DD včetně")
    parser.add_argument(
        "paths",
        nargs="+",
        help="cesty k projektům klienta; každá platí i pro podadresáře",
    )
    args = parser.parse_args()

    start = datetime.fromisoformat(args.since).astimezone()
    end = datetime.fromisoformat(args.until).astimezone() + timedelta(days=1)
    gap = timedelta(minutes=args.gap)

    events = []
    for raw in args.paths:
        prefix = Path(raw).expanduser().resolve()
        events += timeline.session_events([prefix], start, end)
        events += timeline.git_events(prefix, start, end)
    events.sort(key=lambda event: event[0])

    blocks = []
    for moment, kind, source, text in events:
        if not blocks or moment - blocks[-1]["_end"] > gap:
            blocks.append(
                {
                    "_start": moment,
                    "_end": moment,
                    "prompts": 0,
                    "claude": 0,
                    "commits": 0,
                    "sources": set(),
                    "first_prompts": [],
                    "commit_subjects": [],
                }
            )
        block = blocks[-1]
        block["_end"] = moment
        block["sources"].add(source)
        if kind == "prompt":
            block["prompts"] += 1
            if len(block["first_prompts"]) < 3:
                block["first_prompts"].append(text)
        elif kind == "commit":
            block["commits"] += 1
            if len(block["commit_subjects"]) < 5:
                block["commit_subjects"].append(text)
        else:
            block["claude"] += 1

    output = []
    for block in blocks:
        start_at, end_at = block.pop("_start"), block.pop("_end")
        output.append(
            {
                "start": start_at.isoformat(timespec="minutes"),
                "end": end_at.isoformat(timespec="minutes"),
                "minutes": round((end_at - start_at).total_seconds() / 60),
                **{
                    key: sorted(value) if isinstance(value, set) else value
                    for key, value in block.items()
                },
            }
        )
    print(
        json.dumps(
            {"gap_minutes": args.gap, "blocks": output}, ensure_ascii=False, indent=1
        )
    )


if __name__ == "__main__":
    main()
