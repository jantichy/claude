#!/usr/bin/env python3
"""Kalibrace tempa přepisu pro skill /transcript.

Drží ~/.whisper-models/rate.json se skutečně naměřeným tempem (× realtime)
zvlášť pro každý model. Výchozí hodnoty jsou naměřené na Apple M1; po každém
běhu se posouvají k realitě daného stroje.

Usage:
    rate.py get <model>                      # tempo v × realtime
    rate.py eta <model> <audio_seconds>      # odhad běhu, "MM:SS"
    rate.py update <model> <audio_s> <wall_s>
"""
import json
import os
import sys

RATE_FILE = os.path.expanduser("~/.whisper-models/rate.json")

# Výchozí tempo (× realtime) do doby, než se naměří vlastní. Apple M1, 31 min zvuku.
DEFAULTS = {"turbo": 5.4, "large-v3": 1.67}
FALLBACK = 2.0

# Váha nového měření. Nižší = pomalejší, stabilnější kalibrace.
ALPHA = 0.35

# Kratší běhy do kalibrace nepouštíme: u nich dominuje načtení modelu (jednotky
# sekund) a tempo vyjde nesmyslně nízké. Ověřeno – 25s vzorek srazil naměřených
# 5,96x realtime na 4,75x.
MIN_AUDIO_S = 120


def as_float(value):
    """Tolerantní převod – shell v české locale umí poslat desetinnou čárku."""
    return float(str(value).replace(",", "."))


def load():
    try:
        with open(RATE_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def rate_for(model):
    entry = load().get(model)
    if isinstance(entry, dict) and isinstance(entry.get("rate"), (int, float)) and entry["rate"] > 0:
        return float(entry["rate"])
    return DEFAULTS.get(model, FALLBACK)


def mmss(seconds):
    seconds = int(round(seconds))
    return f"{seconds // 60}:{seconds % 60:02d}"


def update(model, audio_s, wall_s):
    if audio_s < MIN_AUDIO_S or wall_s <= 0:
        return
    measured = audio_s / wall_s
    data = load()
    entry = data.get(model) if isinstance(data.get(model), dict) else {}
    old = entry.get("rate")
    n = int(entry.get("n", 0)) if str(entry.get("n", 0)).isdigit() else 0
    if isinstance(old, (int, float)) and old > 0 and n > 0:
        new = (1 - ALPHA) * float(old) + ALPHA * measured
    else:
        new = measured
    data[model] = {"rate": round(new, 3), "n": n + 1, "last": round(measured, 3)}
    os.makedirs(os.path.dirname(RATE_FILE), exist_ok=True)
    tmp = RATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, RATE_FILE)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__.strip())
        return 1
    cmd = args[0]
    if cmd == "get" and len(args) == 2:
        print(f"{rate_for(args[1]):.2f}")
    elif cmd == "eta" and len(args) == 3:
        print(mmss(as_float(args[2]) / rate_for(args[1])))
    elif cmd == "update" and len(args) == 4:
        update(args[1], as_float(args[2]), as_float(args[3]))
    else:
        print(__doc__.strip())
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
