"""Regresní testy skriptů `/transcript` – zatím jen těch míst, kde hrozí ztráta dat.

Vstupem téhle vrstvy jsou nahrávky, které často **nejde pořídit znovu**: schůzka,
konzultace, přednáška. Chyba, která přepíše zdroj, se proto neprojeví jako vada
nástroje, ale jako nenávratně ztracený podklad – a `ffmpeg -y` to udělá mlčky
s návratovým kódem 0.

Oba scénáře tady nastaly doopravdy (`/review full`, 14. 9. 2026):

1. Pojistka proti přepsání vlastního vstupu porovnávala **řetězce cest**, takže
   `./rec.wav` a `rec.wav` prošly jako různé soubory. Z 30sekundové nahrávky
   zbylo 4,6 s.
2. Kontrola „výstupy už existují“ neznala příponu `wav`, takže existující WAV
   z dřívějšího běhu se přepsal i ve výchozím režimu `stop`.

Spouští se: python3 -m unittest discover -s tests -q

Jen stdlib. `ffmpeg` se nevyžaduje – kde není, testy se přeskočí nahlas.
"""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIBE = ROOT / "skills" / "transcript" / "transcribe.sh"
FFMPEG = shutil.which("ffmpeg")


class PojistkaProtiPrepsaniZdroje(unittest.TestCase):
    """Převod nesmí zapisovat do souboru, ze kterého čte."""

    def setUp(self):
        if not FFMPEG:
            self.skipTest("ffmpeg není k dispozici, scénář se nedá přehrát")
        self.tmp = Path(tempfile.mkdtemp(prefix="transcript-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def nahravka(self, jmeno, sekund=1):
        cil = self.tmp / jmeno
        subprocess.run([FFMPEG, "-f", "lavfi", "-i", f"sine=frequency=440:duration={sekund}",
                        "-ar", "44100", "-ac", "2", str(cil), "-y"],
                       capture_output=True, check=True)
        return cil

    def logika_vyberu(self, workdir, base, vstup):
        """Tentýž výběr cílového WAV, jaký dělá transcribe.sh při KEEP_WAV=1.

        Vytažený ze skriptu proto, že samotný `transcribe.sh` chce whisper-cli
        a model o velikosti gigabajtu; testovat se má ta podmínka, ne whisper.
        Že se s originálem nerozešla, hlídá `test_skript_porovnava_soubory`.
        """
        skript = f'''
        WORKDIR={workdir}; base={base}; f={vstup}; KEEP_WAV=1
        if [ "$KEEP_WAV" = "1" ]; then wav="$WORKDIR/$base.wav"; else wav="$WORKDIR/.${{base}}.tmp.wav"; fi
        if [ -e "$wav" ] && [ "$wav" -ef "$f" ]; then wav="$WORKDIR/$base.16k.wav"; fi
        printf %s "$wav"
        '''
        return subprocess.run(["bash", "-c", skript], capture_output=True,
                              text=True, check=True, cwd=self.tmp).stdout

    def test_relativni_cesta_zdroj_neznici(self):
        """`./rec.wav` a `rec.wav` je týž soubor, ale jiný řetězec.

        Tohle je ten případ, který pojistku obcházel: porovnání `=` neplatilo,
        cílem převodu se stal vstup a ffmpeg ho ořízl během čtení.
        """
        zdroj = self.nahravka("rec.wav", sekund=30)
        pred = zdroj.stat().st_size
        cil = self.logika_vyberu(".", "rec", "rec.wav")
        self.assertNotEqual(cil, "./rec.wav", "cílem převodu se stal vlastní vstup")
        subprocess.run([FFMPEG, "-y", "-i", "rec.wav", "-ar", "16000", "-ac", "1",
                        "-c:a", "pcm_s16le", cil], capture_output=True, cwd=self.tmp, check=True)
        self.assertEqual(zdroj.stat().st_size, pred,
                         "zdrojová nahrávka se převodem změnila – přišla by o obsah")

    def test_absolutni_cesta_zdroj_neznici(self):
        """Táž situace zapsaná absolutně; tu porovnání řetězců zvládalo,
        takže je to pojistka proti obrácené regresi."""
        zdroj = self.nahravka("rec.wav")
        cil = self.logika_vyberu(str(self.tmp), "rec", str(zdroj))
        self.assertNotEqual(cil, str(zdroj))

    def test_jiny_soubor_se_neprejmenuje(self):
        """Propustit, co propustit má: jde-li o jiný soubor, cíl zůstává `<base>.wav`
        – jinak by každý běh vyráběl zbytečný `.16k.wav` a diarizace by ho nenašla."""
        self.nahravka("rec.m4a")
        self.assertEqual(self.logika_vyberu(".", "rec", "rec.m4a"), "./rec.wav")


class SeznamVystupnichPripon(unittest.TestCase):
    """`wav` musí být mezi příponami, které se nesmí tiše přepsat."""

    def test_skript_zna_priponu_wav(self):
        text = TRANSCRIBE.read_text(encoding="utf-8")
        self.assertRegex(text, r'VYSTUPNI_PRIPONY="[^"]*\bwav\b',
                         "seznam výstupních přípon nezná wav – existující nahrávka se přepíše")

    def test_seznam_stoji_na_jednom_miste(self):
        """Dřív byl opsaný dvakrát a `wav` chyběl v obou kopiích."""
        text = TRANSCRIBE.read_text(encoding="utf-8")
        self.assertNotIn("for ext in txt srt md vtt json", text,
                         "seznam přípon je zase opsaný do smyčky místo odkazu na konstantu")
        self.assertEqual(text.count("for ext in $VYSTUPNI_PRIPONY"), 2)

    def test_skript_porovnava_soubory(self):
        """Pojistka musí porovnávat soubory (`-ef`), ne řetězce cest."""
        text = TRANSCRIBE.read_text(encoding="utf-8")
        self.assertIn('[ "$wav" -ef "$f" ]', text)
        self.assertNotIn('[ "$wav" = "$f" ]', text,
                         "porovnání řetězců je zpátky – relativní cesta pojistku mine")


if __name__ == "__main__":
    unittest.main()
