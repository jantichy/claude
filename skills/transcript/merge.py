#!/usr/bin/env python3
"""Spojí časovaný přepis z whisperu s úseky mluvčích z pyannote.

Whisperovy segmenty nekopírují střídání mluvčích, takže se přiřazuje podle
největšího časového překryvu. Když je překryv slabý, mluvčí zůstane nevyplněný –
odhad mluvčího je horší než přiznaná neznalost, protože chybné přiřazení vypadá
v přepisu stejně věrohodně jako správné.

Usage:
    merge.py <srt> <diarization.json> <výstupní_základ> [--names <names.json>]

Vznikne <základ>.json (úseky s mluvčím a textem) a <základ>.vtt (titulky se
značkou <v Jméno>). Pojmenování mluvčích je volitelné; bez něj zůstanou
SPEAKER_00 a spol.
"""
import json
import re
import sys
from pathlib import Path

# Kolik z délky repliky musí připadnout vítězi, aby se přiřadil.
MIN_RATIO = 0.6
# O kolik musí vítěz přeskočit druhého v pořadí. Bez tohohle by rozdělení 55:45
# dostalo nálepku, přestože je to hod mincí.
MIN_MARGIN = 0.2

TIME_RE = re.compile(r"(\d\d):(\d\d):(\d\d)[,.](\d{1,3})")


def parse_time(text):
    m = TIME_RE.search(text)
    if not m:
        return None
    h, mi, s, ms = m.groups()
    return int(h) * 3600 + int(mi) * 60 + int(s) + int(ms.ljust(3, "0")) / 1000


def parse_srt(path):
    """Vrátí [{start, end, text}] – tolerantní k číslování i k prázdným řádkům."""
    cues, block = [], []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            block.append(line)
            continue
        if block:
            cues.append(block)
            block = []
    if block:
        cues.append(block)

    out = []
    for block in cues:
        timing = next((ln for ln in block if "-->" in ln), None)
        if not timing:
            continue
        left, _, right = timing.partition("-->")
        start, end = parse_time(left), parse_time(right)
        if start is None or end is None:
            continue
        idx = block.index(timing)
        text = " ".join(ln.strip() for ln in block[idx + 1:]).strip()
        if text:
            out.append({"start": start, "end": end, "text": text})
    return out


def assign(cue, turns):
    """Mluvčí s největším překryvem, nebo None, když je překryv slabý."""
    span = max(cue["end"] - cue["start"], 1e-6)
    totals = {}
    for turn in turns:
        overlap = min(cue["end"], turn["end"]) - max(cue["start"], turn["start"])
        if overlap > 0:
            totals[turn["speaker"]] = totals.get(turn["speaker"], 0.0) + overlap
    if not totals:
        return None
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    speaker, best = ranked[0]
    second = ranked[1][1] if len(ranked) > 1 else 0.0
    if best / span < MIN_RATIO or (best - second) / span < MIN_MARGIN:
        return None
    return speaker


def to_vtt(segments, names):
    def stamp(value):
        h, rest = divmod(value, 3600)
        m, s = divmod(rest, 60)
        return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"

    lines = ["WEBVTT", ""]
    for seg in segments:
        lines.append(f"{stamp(seg['start'])} --> {stamp(seg['end'])}")
        speaker = seg.get("speaker")
        if speaker:
            lines.append(f"<v {names.get(speaker, speaker)}>{seg['text']}")
        else:
            lines.append(seg["text"])
        lines.append("")
    return "\n".join(lines)


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip())
        return 1
    srt_path, diar_path, out_base = argv[0], argv[1], argv[2]

    names = {}
    if "--names" in argv:
        names = json.loads(Path(argv[argv.index("--names") + 1]).read_text(encoding="utf-8"))

    diar = json.loads(Path(diar_path).read_text(encoding="utf-8"))
    turns = diar.get("turns", [])
    cues = parse_srt(srt_path)

    segments = []
    for cue in cues:
        segments.append({
            "start": round(cue["start"], 3),
            "end": round(cue["end"], 3),
            "speaker": assign(cue, turns),
            "text": cue["text"],
        })

    unassigned = sum(1 for s in segments if s["speaker"] is None)
    payload = {
        "speakers": {s: names.get(s, s) for s in diar.get("speakers", [])},
        "num_speakers": diar.get("num_speakers", 0),
        "unassigned_segments": unassigned,
        "segments": segments,
    }
    Path(out_base + ".json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(out_base + ".vtt").write_text(to_vtt(segments, payload["speakers"]), encoding="utf-8")

    print(f"### MERGESTAT {len(segments)} {unassigned} {payload['num_speakers']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
