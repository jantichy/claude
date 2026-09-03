#!/usr/bin/env python3
"""Vlastní běh pyannote. Spouští ho diarize.sh ve svém venv, ne systémový Python.

Vstup přes proměnné prostředí (DIAR_WAV, DIAR_OUT, DIAR_NSPK, DIAR_MODEL, HF_TOKEN),
aby se nemusely řešit uvozovky kolem cest. Výstup je JSON s úseky bez textu; text
k nim přiřadí merge.py.
"""
import json
import os
import sys


def main():
    wav = os.environ["DIAR_WAV"]
    out = os.environ["DIAR_OUT"]
    nspk = os.environ.get("DIAR_NSPK", "auto")
    model = os.environ.get("DIAR_MODEL", "pyannote/speaker-diarization-3.1")
    token = os.environ["HF_TOKEN"]

    import torch
    from pyannote.audio import Pipeline

    pipeline = Pipeline.from_pretrained(model, use_auth_token=token)
    if pipeline is None:
        # Nastane, když uživatel neodsouhlasil licenci gated modelu na HuggingFace.
        print("Pipeline se nenačetla – nejspíš neodsouhlasená licence modelu.", file=sys.stderr)
        return 1

    # MPS urychlí běh na Apple Silicon; když není, zůstane CPU.
    if torch.backends.mps.is_available():
        pipeline.to(torch.device("mps"))

    kwargs = {}
    if nspk.isdigit() and int(nspk) > 0:
        kwargs["num_speakers"] = int(nspk)

    annotation = pipeline(wav, **kwargs)

    turns = [
        {"start": round(seg.start, 3), "end": round(seg.end, 3), "speaker": speaker}
        for seg, _, speaker in annotation.itertracks(yield_label=True)
    ]
    speakers = sorted({t["speaker"] for t in turns})

    with open(out, "w", encoding="utf-8") as fh:
        json.dump(
            {"num_speakers": len(speakers), "speakers": speakers, "turns": turns},
            fh, ensure_ascii=False, indent=2,
        )
        fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
