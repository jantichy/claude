#!/usr/bin/env python3
"""Progress bar + ETA pro běžící whisper přepis (skill /transcript).

Čte log, do kterého transcribe.sh píše délky souborů (`### DURATION N SECONDS`),
značky `### START zaznam-N HH:MM:SS` / `### DONE zaznam-N HH:MM:SS` a whisper píše
časové značky segmentů (`[HH:MM:SS ...]`).

Usage:
    progress.py <logfile>                 # délky si načte z logu (### DURATION)
    progress.py <logfile> N=SECONDS ...   # délky lze i předat ručně
"""
import re
import sys
from datetime import datetime


def hms_to_s(h, m, s):
    return int(h) * 3600 + int(m) * 60 + int(s)


def main():
    if len(sys.argv) < 2:
        print("usage: progress.py <logfile> [N=SECONDS ...]")
        return
    logfile = sys.argv[1]
    dur = {}
    for pair in sys.argv[2:]:
        n, sec = pair.split("=")
        dur[n] = float(sec)

    with open(logfile, encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()

    if not dur:  # délky z logu
        for ln in lines:
            m = re.search(r"### DURATION (\d+) ([\d.]+)", ln)
            if m:
                dur[m.group(1)] = float(m.group(2))

    started, done = [], set()
    first_start_clock = None
    last_pos = 0

    for ln in lines:
        m = re.search(r"### START zaznam-(\d+) (\d\d):(\d\d):(\d\d)", ln)
        if m:
            started.append(m.group(1))
            clk = hms_to_s(m.group(2), m.group(3), m.group(4))
            if first_start_clock is None:
                first_start_clock = clk
            last_pos = 0
            continue
        m = re.search(r"### DONE zaznam-(\d+)", ln)
        if m:
            done.add(m.group(1))
            last_pos = 0
            continue
        m = re.match(r"\[(\d\d):(\d\d):(\d\d)", ln)
        if m:
            last_pos = hms_to_s(m.group(1), m.group(2), m.group(3))

    total = sum(dur.values())
    done_audio = sum(dur.get(n, 0) for n in done)
    running = next((n for n in reversed(started) if n not in done), None)
    cur = last_pos if running else 0
    processed = min(done_audio + cur, total)
    remaining = max(0.0, total - processed)
    pct = processed / total if total else 0

    now = datetime.now()
    now_clk = now.hour * 3600 + now.minute * 60 + now.second
    eta_txt, rate_txt = "—", "—"
    if first_start_clock is not None:
        elapsed = now_clk - first_start_clock
        if elapsed < 0:
            elapsed += 24 * 3600
        if elapsed > 0 and processed > 0:
            rate = processed / elapsed
            rate_txt = f"{rate:.1f}× realtime"
            if remaining > 0:
                eta = remaining / rate
                eta_txt = f"~{int(eta // 60)} min {int(eta % 60)} s"
            else:
                eta_txt = "hotovo"

    width = 30
    fill = int(round(pct * width))
    bar = "█" * fill + "░" * (width - fill)

    def mmss(sec):
        return f"{int(sec // 60)}:{int(sec % 60):02d}"

    n_files = len(dur)
    if remaining == 0:
        status = "HOTOVO"
    else:
        status = f"běží soubor {running}/{n_files}"
    print(f"  [{bar}] {pct * 100:5.1f}%")
    print(f"  {mmss(processed)} / {mmss(total)} min   (zbývá {mmss(remaining)})")
    print(f"  {status}  •  hotové: {len(done)}/{n_files}  •  tempo: {rate_txt}  •  ETA: {eta_txt}")


if __name__ == "__main__":
    main()
