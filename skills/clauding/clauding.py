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
import re
import sys
from collections import Counter, defaultdict
from types import SimpleNamespace
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

# Co uživatel nenapsal, ale vložil: delší vložený text a obrázek stojí v promptu jen jako značka.
PASTED = re.compile(r"\[(?:Pasted text #\d+[^\]]*|Image #\d+)\]")

# Zásahy, kterými uživatel řídí Clauda – z transcriptů, takže za odhadnutý den neúplné.
INTERVENTIONS = ("decision", "interrupt", "rejection")

# Pauza po nočním promptu, od které je to spánek, ne přestávka.
SLEEP = timedelta(hours=3)


def number(value: float, places: int = 1) -> str:
    # Čte to člověk, takže polovina nahoru, ne k sudému číslu jako `round()`.
    quantum = Decimal(1).scaleb(-places)
    return str(Decimal(str(value)).quantize(quantum, ROUND_HALF_UP)).replace(".", ",")


def count(value: int) -> str:
    # Tisíce odděluje nezlomitelná mezera, ať se číslo nerozdělí na konci řádku.
    return f"{value:,}".replace(",", "\u00a0")


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


def counts_per_day(events) -> dict:
    """Počty zásahů a přitakání po dnech v pražském čase, podle druhu události."""
    days = defaultdict(Counter)
    for at, kind, _, data in events:
        day = days[at.astimezone(ZONE).date()]
        if kind == "decision":
            day["decision"] += len(data)
        elif kind in ("interrupt", "rejection"):
            day[kind] += 1
        elif kind == "claude" and data:
            day["agreement"] += data
    return days


def typed(text: str) -> int:
    """Znaky, které uživatel do promptu napsal, bez delšího vloženého textu a obrázků."""
    return len(PASTED.sub("", text).strip())


def measure() -> SimpleNamespace:
    """Všechno, co výpis potřebuje: čas, odhad, zásahy, commity a prompty po dnech."""
    work = commits()
    events = list(timeline.session_events())
    claude = [at for at, *_ in events]
    history = [(at, text) for at, _, _, text in timeline.history_prompts()]
    prompts = [at for at, _ in history]
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
    commit_days = Counter(
        at.astimezone(ZONE).date() for at in near(work, claude + prompts)
    )
    return SimpleNamespace(
        hours=hours,
        guessed=guessed,
        factor=factor,
        calibrated=len(calibration),
        measured=measured,
        counts=counts_per_day(events),
        commits=commit_days,
        prompts=[(at.astimezone(ZONE), text) for at, text in history],
    )


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


def lower_bound(members, data, kinds):
    """Součet druhů z transcriptů za skupinu dnů jako text.

    Za odhadnutý den chybí transcript aspoň jedné session, takže počet je jen dolní mez
    a nese `≥`; skupina jen z odhadnutých dnů nemá číslo vůbec.
    """
    marked = [d for d in members if d in data.guessed]
    if marked and not any(
        data.hours.get(d, 0) > 0 for d in members if d not in data.guessed
    ):
        return "–"
    total = sum(data.counts[d][k] for d in members for k in kinds if d in data.counts)
    return f"{'≥' if marked else ''}{count(total)}"


def per_hour(members, data, kinds) -> str:
    """Kolik událostí daných druhů připadá na hodinu – jen ze dnů bez odhadu.

    Odhadnuté hodiny proti neúplnému počtu by daly poměr, který neplatí.
    """
    full = [d for d in members if d not in data.guessed]
    hours = sum(data.hours.get(d, 0) for d in full)
    if not hours:
        return "–"
    total = sum(data.counts[d][k] for d in full for k in kinds if d in data.counts)
    return number(total / hours)


def groups(days, granularity) -> dict:
    grouped = defaultdict(list)
    for day in days:
        grouped[period_key(day, granularity)].append(day)
    return grouped


def table(days, data, granularity) -> list:
    rows = [
        "| Období | Hodiny | Ø na kalendářní den | Ø na aktivní den | Aktivní dny |",
        "|---|---:|---:|---:|---:|",
    ]
    for key, members in sorted(groups(days, granularity).items()):
        total = sum(data.hours.get(d, 0) for d in members)
        active = [d for d in members if data.hours.get(d, 0) > 0]
        mark = "~" if any(d in data.guessed for d in members) else ""
        per_active = number(total / len(active)) if active else "–"
        rows.append(
            f"| {period_label(key, granularity)} | {mark}{number(total)} "
            f"| {mark}{number(total / len(members))} | {mark}{per_active} "
            f"| {len(active)} z {len(members)} |"
        )
    return rows


def prompt_figures(members, data):
    """(napsané znaky, Ø znaků na prompt) za skupinu dnů; příkazy do průměru nejdou."""
    inside = set(members)
    texts = [text for at, text in data.prompts if at.date() in inside]
    written = [typed(t) for t in texts if not is_command(t) and typed(t)]
    average = number(sum(written) / len(written), 0) if written else "–"
    return count(sum(typed(t) for t in texts)), average


def attention(days, data, granularity) -> list:
    rows = [
        "| Období | Rozhodnutí | Přerušení | Zamítnutí | Zásahů na hodinu "
        "| Commity | Napsaných znaků | Ø znaků na prompt |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key, members in sorted(groups(days, granularity).items()):
        figures = [lower_bound(members, data, (k,)) for k in INTERVENTIONS]
        written, average = prompt_figures(members, data)
        commits_count = count(sum(data.commits.get(d, 0) for d in members))
        rows.append(
            f"| {period_label(key, granularity)} | {' | '.join(figures)} "
            f"| {per_hour(members, data, INTERVENTIONS)} | {commits_count} "
            f"| {written} | {average} |"
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


def top_day(days, data, kind):
    busiest = max(days, key=lambda d: data.counts[d][kind] if d in data.counts else 0)
    value = data.counts[busiest][kind] if busiest in data.counts else 0
    mark = "≥" if busiest in data.guessed else ""
    return busiest, f"{mark}{count(value)}" if value else None


def time_highlights(days, data) -> list:
    top = max(days, key=lambda d: data.hours.get(d, 0))
    mark = "~" if top in data.guessed else ""
    rows = [
        f"- **Nejdelší den:** {period_label(top, 'day')} – {mark}{number(data.hours.get(top, 0))} h"
    ]
    block = longest_block(data.measured, days)
    if block:
        start, end = (x.astimezone(ZONE) for x in block)
        rows.append(
            f"- **Nejdelší blok v kuse:** {czech_date(start.date())} "
            f"{start:%H:%M}–{end:%H:%M} – {number((end - start).total_seconds() / 3600)} h"
        )
    streak, streak_end = longest_streak(days, data.hours)
    if streak:
        streak_start = streak_end - timedelta(days=streak - 1)
        rows.append(
            f"- **Nejdelší řada dnů po sobě:** {streak} "
            f"({czech_date(streak_start, False)} – {czech_date(streak_end)})"
        )
    return rows


def claude_highlights(days, data) -> list:
    rows = []
    busiest, value = top_day(days, data, "decision")
    if value:
        rows.append(
            f"- **Nejvíc rozhodnutí za den:** {period_label(busiest, 'day')} – {value}"
        )
    agreed = lower_bound(days, data, ("agreement",))
    if agreed not in ("–", "0"):
        rate = per_hour(days, data, ("agreement",))
        rows.append(f"- **Claude ti dal za pravdu:** {agreed}× ({rate} na hodinu)")
    return rows


def bedtimes(prompts) -> list:
    """Konce noční práce: poslední prompt bloku, který skončil mezi půlnocí a šestou.

    Blok jsou prompty bez pauzy delší než `SLEEP`. Blok, který začal až mezi čtvrtou
    a šestou ráno, je brzký začátek dne, ne pozdní konec noci.
    """
    moments = sorted(at for at, _ in prompts)
    ends = []
    start = None
    for at, after in zip(moments, moments[1:] + [None]):
        start = start or at
        if after is not None and after - at < SLEEP:
            continue
        early = 4 <= start.hour < 6 and start.date() == at.date()
        if at.hour < 6 and not early:
            ends.append(at)
        start = None
    return ends


def night(prompts) -> list:
    ends = bedtimes(prompts)
    if not ends:
        return []
    latest = max(ends, key=lambda at: at.time())
    after_two = len({at.date() for at in ends if at.hour >= 2})
    return [
        f"- **Noční sova:** nejpozději jsi skončil v {latest:%H:%M} "
        f"(noc z {czech_date(latest.date() - timedelta(days=1), False)} "
        f"na {czech_date(latest.date())}), po druhé hodině jsi končil {after_two}× "
        f"z {len(ends)} nocí, kdy jsi pracoval po půlnoci"
    ]


def prompt_highlights(days, data) -> list:
    inside = set(days)
    prompts = [(at, t) for at, t in data.prompts if at.date() in inside and t.strip()]
    if not prompts:
        return []
    # Příkazy harnessu (`exit`, `/clear`) by první místa obsadily vždycky a nic by neřekly.
    common = Counter(
        " ".join(t.lower().split()) for _, t in prompts if not is_command(t)
    ).most_common(3)
    quoted = ", ".join(f"„{t[:40]}“ {count(n)}×" for t, n in common)
    longest_at, longest = max(prompts, key=lambda p: typed(p[1]))
    return [
        f"- **Nejčastější prompty:** {quoted}",
        f"- **Nejdelší napsaný prompt:** {czech_date(longest_at.date())} – "
        f"{count(typed(longest))} znaků",
        *night(prompts),
    ]


def footnote(days, data) -> list:
    if not any(d in data.guessed for d in days):
        return []
    return [
        "",
        f"`~` odhad: pro den chybí transcript, spočteno z promptů v `history.jsonl` a z commitů "
        f"× koeficient {number(data.factor, 2)} (změřen na {data.calibrated} dnech s úplnými daty). "
        "Rozložení podle hodiny dne a nejdelší blok jsou jen z dnů bez odhadu. "
        "`≥` u rozhodnutí, přerušení, zamítnutí a přitakání: za odhadnutý den chybí záznamy, "
        "počet je jen dolní mez; poměr na hodinu je jen ze dnů bez odhadu.",
    ]


def report(granularity, since, until) -> str:
    data = measure()
    if not any(h > 0 for h in data.hours.values()):
        return "V transcriptech ani v `history.jsonl` není žádná aktivita."
    first = since or min(d for d, h in data.hours.items() if h > 0)
    last = min(until or date.today(), date.today())
    days = [first + timedelta(days=n) for n in range((last - first).days + 1)]
    if not days:
        return "Zadané období neobsahuje ani jeden den."
    total = sum(data.hours.get(d, 0) for d in days)
    active = sum(1 for d in days if data.hours.get(d, 0) > 0)
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
        *table(days, data, granularity),
        "",
        "### Pozornost a práce",
        "",
        "Zásahy jsou rozhodnutí v dialogu, přerušení klávesou Esc a zamítnutí nástroje dohromady. "
        "Napsané znaky jsou bez delšího vloženého textu a obrázků.",
        "",
        *attention(days, data, granularity),
        "",
        "### Zajímavosti",
        "",
        *time_highlights(days, data),
        *claude_highlights(days, data),
        *prompt_highlights(days, data),
        "",
        *histogram(days, data.hours),
        "",
        *weekdays(days, data.hours),
        "",
        *day_hours(data.measured, days),
        *footnote(days, data),
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
