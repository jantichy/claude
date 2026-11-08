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
WEEKDAY_NAMES = "pondělí úterý středa čtvrtek pátek sobota neděle".split()
BAR = 30

# Co uživatel nenapsal, ale vložil: delší vložený text a obrázek stojí v promptu jen jako značka.
PASTED = re.compile(r"\[(?:Pasted text #\d+[^\]]*|Image #\d+)\]")

# Zásahy, kterými uživatel řídí Clauda – z transcriptů, takže za odhadnutý den neúplné.
INTERVENTIONS = ("decision", "interrupt", "rejection")

# Pauza po nočním promptu, od které je to spánek, ne přestávka.
SLEEP = timedelta(hours=3)

# Normostrana – ať se dá napsaný text představit.
PAGE = 1800


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


def period_hours(members, data) -> float:
    return sum(data.hours.get(d, 0) for d in members)


def time_row(label, members, data) -> str:
    total = period_hours(members, data)
    active = [d for d in members if data.hours.get(d, 0) > 0]
    mark = "~" if any(d in data.guessed for d in members) else ""
    per_active = number(total / len(active)) if active else "–"
    return (
        f"| {label} | {mark}{number(total)} "
        f"| {mark}{number(total / len(members))} | {mark}{per_active} "
        f"| {len(active)} z {len(members)} |"
    )


def table(days, data, granularity) -> list:
    rows = [
        "| Období | Hodiny | Ø na kalendářní den | Ø na aktivní den | Aktivní dny |",
        "|---|---:|---:|---:|---:|",
    ]
    for key, members in sorted(groups(days, granularity).items()):
        rows.append(time_row(period_label(key, granularity), members, data))
    return rows + [time_row("**Celkem**", days, data)]


def prompt_figures(members, data):
    """(napsané znaky, Ø znaků na prompt) za skupinu dnů; příkazy do průměru nejdou."""
    inside = set(members)
    texts = [text for at, text in data.prompts if at.date() in inside]
    written = [typed(t) for t in texts if not is_command(t) and typed(t)]
    average = sum(written) / len(written) if written else None
    return sum(typed(t) for t in texts), average


def commit_count(members, data) -> int:
    return sum(data.commits.get(d, 0) for d in members)


def attention_row(label, members, data) -> str:
    figures = [lower_bound(members, data, (k,)) for k in INTERVENTIONS]
    written, average = prompt_figures(members, data)
    shown = number(average, 0) if average is not None else "–"
    return (
        f"| {label} | {' | '.join(figures)} "
        f"| {per_hour(members, data, INTERVENTIONS)} | {count(commit_count(members, data))} "
        f"| {count(written)} | {shown} |"
    )


def attention(days, data, granularity) -> list:
    rows = [
        "| Období | Rozhodnutí | Přerušení | Zamítnutí | Zásahů na hodinu "
        "| Commity | Napsaných znaků | Ø znaků na prompt |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key, members in sorted(groups(days, granularity).items()):
        rows.append(attention_row(period_label(key, granularity), members, data))
    return rows + [attention_row("**Celkem**", days, data)]


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
    return rows + [f"| **Celkem** | {len(days)} | |"]


def weekday_averages(days, hours) -> dict:
    totals, counts = defaultdict(float), defaultdict(int)
    for day in days:
        totals[day.weekday()] += hours.get(day, 0)
        counts[day.weekday()] += 1
    return {w: totals[w] / counts[w] for w in counts}


def weekdays(days, hours) -> list:
    averages = weekday_averages(days, hours)
    peak = max(averages.values())
    rows = ["| Den v týdnu | Ø hodin | |", "|---|---:|---|"]
    for w in sorted(averages):
        rows.append(
            f"| {WEEKDAYS[w]} | {number(averages[w])} | {bar(averages[w], peak)} |"
        )
    # Průměr přes všechny dny, ne průměr sedmi řádků – dnů v týdnu nemusí být v období stejně.
    overall = sum(hours.get(d, 0) for d in days) / len(days)
    return rows + [f"| **Celkem** | {number(overall)} | |"]


def two_hour_slots(measured, days) -> dict:
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
    return slots


def day_hours(slots) -> list:
    if not slots:
        return []
    peak = max(slots.values())
    rows = ["| Hodina dne | Hodin celkem | |", "|---|---:|---|"]
    for slot in range(12):
        rows.append(
            f"| {2 * slot}–{2 * slot + 2} | {number(slots[slot])} | {bar(slots[slot], peak)} |"
        )
    return rows + [f"| **Celkem** | {number(sum(slots.values()))} | |"]


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


# Zajímavosti jsou věty ke sdílení: první osoba bez rodu, aby seděly každému, kdo skill
# pustí, a slova místo značek – čtenář na sociální síti `~` ani `≥` neprečte.


def plural(n: int, one: str, few: str, many: str) -> str:
    return one if n == 1 else few if 2 <= n <= 4 else many


def pages(chars: int) -> str:
    n = round(chars / PAGE)
    return f"{count(n)} {plural(n, 'normostrana', 'normostrany', 'normostran')}"


def worded(text: str) -> str:
    """Číslo z tabulky jako slovo do věty: `≥` je „nejméně“, `~` „zhruba“."""
    return text.replace("≥", "nejméně ").replace("~", "zhruba ")


def about(members, data) -> str:
    return "zhruba " if any(d in data.guessed for d in members) else ""


def full_date(day: date) -> str:
    return f"{WEEKDAY_NAMES[day.weekday()]} {czech_date(day)}"


def unit(granularity: str) -> str:
    return {"month": "měsíc", "week": "týden"}[granularity]


def summary(days, data) -> list:
    total = period_hours(days, data)
    active = [d for d in days if data.hours.get(d, 0) > 0]
    span = f"{len(days)} {plural(len(days), 'den', 'dny', 'dní')}"
    return [
        f"- V Claude Code mám za sebou {about(days, data)}{number(total)} h za {span} "
        f"({czech_date(days[0])} – {czech_date(days[-1])}): v průměru "
        f"{number(total / len(days))} h denně včetně víkendů, ve dnech s prací "
        f"({len(active)} z {len(days)}) {number(total / len(active))} h."
    ]


def period_sentences(days, data, granularity) -> list:
    grouped = groups(days, granularity)
    if granularity == "day" or len(grouped) < 2:
        return []
    key, members = max(grouped.items(), key=lambda g: period_hours(g[1], data))
    hours = period_hours(members, data)
    label = period_label(key, granularity)
    return [
        f"- Nejsilnější {unit(granularity)}: {label} – {about(members, data)}{number(hours)} h, "
        f"tedy {number(hours / len(members))} h denně včetně víkendů."
    ]


def record_sentences(days, data) -> list:
    top = max(days, key=lambda d: data.hours.get(d, 0))
    rows = [
        f"- Nejdelší den: {full_date(top)} – {about([top], data)}"
        f"{number(data.hours.get(top, 0))} h v Claude Code."
    ]
    block = longest_block(data.measured, days)
    if block:
        start, end = (x.astimezone(ZONE) for x in block)
        rows.append(
            f"- Nejdelší souvislý blok: {number((end - start).total_seconds() / 3600)} h "
            f"bez pauzy delší než 20 minut ({czech_date(start.date())}, "
            f"{start:%H:%M}–{end:%H:%M})."
        )
    streak, streak_end = longest_streak(days, data.hours)
    if streak > 1:
        streak_start = streak_end - timedelta(days=streak - 1)
        rows.append(
            f"- {streak} {plural(streak, 'den', 'dny', 'dní')} v řadě bez jediného volného dne "
            f"({czech_date(streak_start, False)} – {czech_date(streak_end)})."
        )
    return rows


def rhythm_sentences(days, data, slots) -> list:
    averages = weekday_averages(days, data.hours)
    best = max(averages, key=averages.get)
    weekend = [d for d in days if d.weekday() >= 5]
    rows = [
        f"- Nejsilnější den v týdnu: {WEEKDAY_NAMES[best]} s průměrem {number(averages[best])} h"
        + (
            f", o víkendu v průměru {number(period_hours(weekend, data) / len(weekend))} h."
            if weekend
            else "."
        )
    ]
    total = sum(slots.values())
    if total:
        evening = sum(slots[s] for s in (0, 1, 2, 10, 11))
        peak = max(slots, key=slots.get)
        rows.append(
            f"- Večer a v noci (20–6 h) padá {number(100 * evening / total, 0)} % času, "
            f"nejsilnější dvouhodinovka dne je {2 * peak}–{2 * peak + 2} h."
        )
    return rows


def busiest_period(days, data, granularity, kinds):
    grouped = groups(days, granularity)
    if granularity == "day" or len(grouped) < 2:
        return None
    key, members = max(
        grouped.items(),
        key=lambda g: sum(
            data.counts[d][k] for d in g[1] for k in kinds if d in data.counts
        ),
    )
    return period_label(key, granularity), worded(lower_bound(members, data, kinds))


def top_day(days, data, kind):
    busiest = max(days, key=lambda d: data.counts[d][kind] if d in data.counts else 0)
    return busiest, data.counts[busiest][kind] if busiest in data.counts else 0


def decision_sentences(days, data, granularity) -> list:
    total = lower_bound(days, data, ("decision",))
    if total in ("–", "0"):
        return []
    sentence = (
        f"- {worded(total).capitalize()} rozhodnutí – odpovědí na Claudovy otázky "
        f"s nabídnutými variantami, tedy {per_hour(days, data, ('decision',))} za hodinu práce"
    )
    best = busiest_period(days, data, granularity, ("decision",))
    if best:
        sentence += f"; nejvíc za {unit(granularity)} {best[0]} ({best[1]})"
    rows = [sentence + "."]
    day, value = top_day(days, data, "decision")
    if value:
        rows.append(
            f"- Rekord: {count(value)} rozhodnutí za jediný den ({full_date(day)})."
        )
    return rows


def intervention_sentences(days, data) -> list:
    interrupts = lower_bound(days, data, ("interrupt",))
    rejections = lower_bound(days, data, ("rejection",))
    if interrupts == "–":
        return []
    return [
        f"- Zastavení Clauda klávesou Esc: {worded(interrupts)}×, zamítnutých akcí "
        f"{worded(rejections)}×; i s rozhodnutími {per_hour(days, data, INTERVENTIONS)} "
        "zásahů za hodinu práce."
    ]


def work_sentences(days, data, granularity) -> list:
    rows = []
    commits_total = commit_count(days, data)
    if commits_total:
        sentence = f"- {count(commits_total)} commitů"
        grouped = groups(days, granularity)
        if granularity != "day" and len(grouped) > 1:
            key, members = max(grouped.items(), key=lambda g: commit_count(g[1], data))
            sentence += (
                f", nejvíc za {unit(granularity)} {period_label(key, granularity)} "
                f"({count(commit_count(members, data))})"
            )
        rows.append(sentence + ".")
    written, average = prompt_figures(days, data)
    if written:
        rows.append(
            f"- Do promptů napsáno {count(written)} znaků, zhruba "
            f"{pages(written)}; průměrný prompt má "
            f"{number(average, 0)} znaků."
        )
    return rows


def prompt_trend(days, data, granularity) -> list:
    grouped = sorted(groups(days, granularity).items())
    averages = [(key, prompt_figures(members, data)[1]) for key, members in grouped]
    averages = [(k, a) for k, a in averages if a is not None]
    if granularity == "day" or len(averages) < 2:
        return []
    (first, start), (last, end) = averages[0], averages[-1]
    verb = "zkrátil" if end < start else "prodloužil"
    return [
        f"- Průměrný prompt se {verb} z {number(start, 0)} znaků "
        f"({period_label(first, granularity)}) na {number(end, 0)} "
        f"({period_label(last, granularity)})."
    ]


def fun_sentences(days, data) -> list:
    rows = []
    agreed = lower_bound(days, data, ("agreement",))
    rate = per_hour(days, data, ("agreement",))
    if agreed not in ("–", "0") and rate not in ("–", "0,0"):
        every = 1 / float(rate.replace(",", "."))
        rows.append(
            f"- Claude mi řekl „máš pravdu“ {worded(agreed)}×, zhruba jednou "
            f"za {number(every)} h práce."
        )
    inside = set(days)
    prompts = [(at, t) for at, t in data.prompts if at.date() in inside and t.strip()]
    if not prompts:
        return rows
    # Příkazy harnessu (`exit`, `/clear`) by první místa obsadily vždycky a nic by neřekly.
    common = Counter(
        " ".join(t.lower().split()) for _, t in prompts if not is_command(t)
    ).most_common(3)
    if common:
        quoted = ", ".join(f"„{t[:40]}“ ({count(n)}×)" for t, n in common)
        rows.append(f"- Nejčastější prompty: {quoted}.")
    longest_at, longest = max(prompts, key=lambda p: typed(p[1]))
    rows.append(
        f"- Nejdelší napsaný prompt: {count(typed(longest))} znaků "
        f"({czech_date(longest_at.date())}), tedy {number(typed(longest) / PAGE)} normostrany."
    )
    return rows + night(prompts)


def night(prompts) -> list:
    ends = bedtimes(prompts)
    if not ends:
        return []
    latest = max(ends, key=lambda at: at.time())
    after_two = len({at.date() for at in ends if at.hour >= 2})
    return [
        f"- Nejpozdější konec práce: {latest:%-H:%M} ráno (noc z "
        f"{czech_date(latest.date() - timedelta(days=1), False)} na "
        f"{czech_date(latest.date())}); nocí s prací po půlnoci {len(ends)}, "
        f"z toho {after_two} {plural(after_two, 'skončila', 'skončily', 'skončilo')} "
        "až po druhé hodině."
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


def highlights(days, data, granularity, slots) -> list:
    return [
        *summary(days, data),
        *period_sentences(days, data, granularity),
        *record_sentences(days, data),
        *rhythm_sentences(days, data, slots),
        *decision_sentences(days, data, granularity),
        *intervention_sentences(days, data),
        *work_sentences(days, data, granularity),
        *prompt_trend(days, data, granularity),
        *fun_sentences(days, data),
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
    slots = two_hour_slots(data.measured, days)
    out = [
        f"## Čas v Claude Code – {czech_date(first)} až {czech_date(last)}",
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
        "### Rozložení",
        "",
        *histogram(days, data.hours),
        "",
        *weekdays(days, data.hours),
        "",
        *day_hours(slots),
        *footnote(days, data),
        "",
        "### Zajímavosti",
        "",
        *highlights(days, data, granularity, slots),
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
