#!/usr/bin/env python3
# Spočítá, kolik času se strávilo v Claude Code, po dnech, týdnech nebo měsících, a vypíše
# to jako Markdown pro `/clauding`. Proud událostí a pravidlo mezery bere ze `skills/timeline.py`.
#
# Použití:  python3 clauding.py [day|week|month] [--since YYYY-MM-DD] [--until YYYY-MM-DD]
#
# Den, pro který chybí transcript, se odhadne z promptů v `history.jsonl` a z commitů,
# vynásobených koeficientem změřeným na dnech, kde jsou obě sady dat. Metodika je
# v `SKILL.md`, *Metodika*.

import argparse
import bisect
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path.home() / ".claude" / "skills"))
import timeline  # noqa: E402

ZONE = ZoneInfo("Europe/Prague")
MONTHS = (
    "leden únor březen duben květen červen červenec srpen září říjen listopad prosinec"
).split()
WEEKDAYS = "po út st čt pá so ne".split()
BAR = 30


def number(value: float, places: int = 1) -> str:
    # Čte to člověk, takže polovina nahoru, ne k sudému číslu jako `round()`.
    quantum = Decimal(1).scaleb(-places)
    return str(Decimal(str(value)).quantize(quantum, ROUND_HALF_UP)).replace(".", ",")


def czech_date(day: date, year: bool = True) -> str:
    return f"{day.day}. {day.month}." + (f" {day.year}" if year else "")


def per_day(merged) -> dict:
    """Sekundy na den v pražském čase; interval přes půlnoc se rozdělí."""
    days = defaultdict(float)
    for start, end in merged:
        start, end = start.astimezone(ZONE), end.astimezone(ZONE)
        while start < end:
            midnight = datetime.combine(
                start.date() + timedelta(days=1), datetime.min.time(), ZONE
            )
            stop = min(end, midnight)
            days[start.date()] += (stop - start).total_seconds()
            start = stop
    return days


def commits() -> list:
    """Okamžiky vlastních commitů ze všech repozitářů, ve kterých kdy běžela session."""
    tops = {timeline.repository(Path(d)) for d in timeline.working_dirs()}
    return [
        at
        for top in sorted(t for t in tops if t)
        for at, *_ in timeline.git_events(Path(top), own=True)
    ]


def near(work: list, anchors: list) -> list:
    """Commity do `GAP` od aktivity v Claudovi; ruční práce mimo něj čas v Claudovi není."""
    anchors = sorted(anchors)
    kept = []
    for at in work:
        i = bisect.bisect_left(anchors, at)
        neighbours = anchors[max(i - 1, 0) : i + 1]
        if any(abs(at - a) <= timeline.GAP for a in neighbours):
            kept.append(at)
    return kept


def is_command(text: str) -> bool:
    # Příkaz harnessu (`/resume`, `exit`) v session, která nic nezapsala, transcript nezaloží –
    # jeho chybějící transcript tedy neznamená chybějící data.
    return text.startswith("/") or text.strip() in ("exit", "quit")


def incomplete_days(known: set) -> set:
    """Dny se skutečným promptem ze session, jejíž transcript chybí – ty se odhadují."""
    return {
        at.astimezone(ZONE).date()
        for at, session, _, text in timeline.history_prompts()
        if session not in known and not is_command(text)
    }


def measure():
    """Vrátí (hodiny po dnech, odhadnuté dny, koeficient, počet dnů kalibrace, intervaly)."""
    work = commits()
    claude = [at for at, *_ in timeline.session_events()]
    prompts = [at for at, *_ in timeline.history_prompts()]
    full_intervals = timeline.intervals(claude + near(work, claude))
    full = per_day(full_intervals)
    sparse = per_day(timeline.intervals(prompts + near(work, prompts)))
    guessed = incomplete_days(timeline.transcript_sessions())
    first = min(full) if full else None
    calibration = [
        d for d in set(full) | set(sparse) if first and d >= first and d not in guessed
    ]
    covered_sparse = sum(sparse.get(d, 0) for d in calibration)
    factor = (
        sum(full.get(d, 0) for d in calibration) / covered_sparse
        if covered_sparse
        else 1.0
    )
    hours = {d: full.get(d, 0) / 3600 for d in full}
    for d in guessed:
        # Den, kde chybí jen část sessions, by plná metoda podhodnotila – platí větší z obou.
        hours[d] = max(full.get(d, 0), sparse.get(d, 0) * factor) / 3600
    measured = [
        i for i in full_intervals if i[0].astimezone(ZONE).date() not in guessed
    ]
    return hours, guessed, factor, len(calibration), measured


def period_key(day: date, granularity: str) -> date:
    if granularity == "week":
        return day - timedelta(days=day.weekday())
    if granularity == "month":
        return day.replace(day=1)
    return day


def period_label(key: date, granularity: str) -> str:
    if granularity == "week":
        end = key + timedelta(days=6)
        return f"{czech_date(key, key.year != end.year)} – {czech_date(end)}"
    if granularity == "month":
        return f"{MONTHS[key.month - 1]} {key.year}"
    return f"{WEEKDAYS[key.weekday()]} {czech_date(key)}"


def table(days, hours, guessed, granularity) -> list:
    groups = defaultdict(list)
    for day in days:
        groups[period_key(day, granularity)].append(day)
    rows = [
        "| Období | Hodiny | Ø na kalendářní den | Ø na aktivní den | Aktivní dny |",
        "|---|---:|---:|---:|---:|",
    ]
    for key in sorted(groups):
        members = groups[key]
        total = sum(hours.get(d, 0) for d in members)
        active = [d for d in members if hours.get(d, 0) > 0]
        mark = "~" if any(d in guessed for d in members) else ""
        per_active = number(total / len(active)) if active else "–"
        rows.append(
            f"| {period_label(key, granularity)} | {mark}{number(total)} "
            f"| {mark}{number(total / len(members))} | {mark}{per_active} "
            f"| {len(active)} z {len(members)} |"
        )
    return rows


def bar(value: float, peak: float) -> str:
    return "█" * round(BAR * value / peak) if peak else ""


def histogram(days, hours) -> list:
    buckets = defaultdict(int)
    for day in days:
        value = hours.get(day, 0)
        buckets[-1 if value == 0 else int(value)] += 1
    peak = max(buckets.values())
    rows = ["| Hodin za den | Dnů | |", "|---|---:|---|"]
    for bucket in range(-1, max(buckets) + 1):
        label = "0" if bucket == -1 else f"{bucket}–{bucket + 1}"
        rows.append(f"| {label} | {buckets[bucket]} | {bar(buckets[bucket], peak)} |")
    return rows


def weekdays(days, hours) -> list:
    totals, counts = defaultdict(float), defaultdict(int)
    for day in days:
        totals[day.weekday()] += hours.get(day, 0)
        counts[day.weekday()] += 1
    averages = {w: totals[w] / counts[w] for w in counts}
    peak = max(averages.values())
    rows = ["| Den v týdnu | Ø hodin | |", "|---|---:|---|"]
    for w in sorted(averages):
        rows.append(
            f"| {WEEKDAYS[w]} | {number(averages[w])} | {bar(averages[w], peak)} |"
        )
    return rows


def day_hours(measured, days) -> list:
    """Kolik hodin připadá na každou dvouhodinovku dne; jen dny bez odhadu."""
    slots = defaultdict(float)
    first, last = days[0], days[-1]
    for start, end in measured:
        cursor = start.astimezone(ZONE)
        end = end.astimezone(ZONE)
        while cursor < end:
            stop = min(
                end,
                cursor.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1),
            )
            if first <= cursor.date() <= last:
                slots[cursor.hour // 2] += (stop - cursor).total_seconds() / 3600
            cursor = stop
    if not slots:
        return []
    peak = max(slots.values())
    rows = ["| Hodina dne | Hodin celkem | |", "|---|---:|---|"]
    for slot in range(12):
        rows.append(
            f"| {2 * slot}–{2 * slot + 2} | {number(slots[slot])} | {bar(slots[slot], peak)} |"
        )
    return rows


def longest_streak(days, hours):
    best, run, best_end = 0, 0, None
    for day in days:
        run = run + 1 if hours.get(day, 0) > 0 else 0
        if run > best:
            best, best_end = run, day
    return best, best_end


def longest_block(measured, days):
    first, last = days[0], days[-1]
    inside = [i for i in measured if first <= i[0].astimezone(ZONE).date() <= last]
    return max(inside, key=lambda i: i[1] - i[0], default=None)


def highlights(days, hours, guessed, measured) -> list:
    top = max(days, key=lambda d: hours.get(d, 0))
    mark = "~" if top in guessed else ""
    rows = [
        f"- **Nejdelší den:** {period_label(top, 'day')} – {mark}{number(hours.get(top, 0))} h"
    ]
    block = longest_block(measured, days)
    if block:
        start, end = (x.astimezone(ZONE) for x in block)
        rows.append(
            f"- **Nejdelší blok v kuse:** {czech_date(start.date())} "
            f"{start:%H:%M}–{end:%H:%M} – {number((end - start).total_seconds() / 3600)} h"
        )
    streak, streak_end = longest_streak(days, hours)
    if streak:
        streak_start = streak_end - timedelta(days=streak - 1)
        rows.append(
            f"- **Nejdelší řada dnů po sobě:** {streak} "
            f"({czech_date(streak_start, False)} – {czech_date(streak_end)})"
        )
    return rows


def report(granularity, since, until) -> str:
    hours, guessed, factor, calibrated, measured = measure()
    if not any(h > 0 for h in hours.values()):
        return "V transcriptech ani v `history.jsonl` není žádná aktivita."
    first = since or min(d for d, h in hours.items() if h > 0)
    last = min(until or date.today(), date.today())
    days = [first + timedelta(days=n) for n in range((last - first).days + 1)]
    if not days:
        return "Zadané období neobsahuje ani jeden den."
    total = sum(hours.get(d, 0) for d in days)
    active = sum(1 for d in days if hours.get(d, 0) > 0)
    out = [
        f"## Čas v Claude Code – {czech_date(first)} až {czech_date(last)}",
        "",
        f"**Celkem:** {number(total)} h · Ø {number(total / len(days))} h na kalendářní den"
        + (
            f" · Ø {number(total / active)} h na aktivní den ({active} z {len(days)})"
            if active
            else ""
        ),
        "",
        *table(days, hours, guessed, granularity),
        "",
        "### Zajímavosti",
        "",
        *highlights(days, hours, guessed, measured),
        "",
        *histogram(days, hours),
        "",
        *weekdays(days, hours),
        "",
        *day_hours(measured, days),
    ]
    if any(d in guessed for d in days):
        out += [
            "",
            f"`~` odhad: pro den chybí transcript, spočteno z promptů v `history.jsonl` a z commitů "
            f"× koeficient {number(factor, 2)} (změřen na {calibrated} dnech s úplnými daty). "
            "Rozložení podle hodiny dne a nejdelší blok jsou jen z dnů bez odhadu.",
        ]
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Čas strávený v Claude Code.")
    parser.add_argument(
        "granularity", nargs="?", default="month", choices=("day", "week", "month")
    )
    parser.add_argument("--since", type=date.fromisoformat, help="od YYYY-MM-DD včetně")
    parser.add_argument("--until", type=date.fromisoformat, help="do YYYY-MM-DD včetně")
    args = parser.parse_args()
    print(report(args.granularity, args.since, args.until))


if __name__ == "__main__":
    main()
