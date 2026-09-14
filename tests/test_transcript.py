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

**Pojistka se od 14. 9. 2026 ověřuje na spuštěném skriptu, ne na opisu.** Dřív
tu byla jen kopie jeho podmínky plus kontrola, že ve skriptu zbyl řetězec `-ef`.
Ta dvojice nechytila nic: stačilo vyřadit podmínku ve skriptu (`&& false`) a
všech šest testů zůstalo zelených, protože hlídaný řetězec v souboru zůstal.
Skutečný běh chce whisper a model o velikosti gigabajtu, takže se obojí
podstrčí – model prázdným souborem v přesměrovaném HOME, whisper stubem.

Spouští se: python3 -m unittest discover -s tests -q

Jen stdlib. `ffmpeg` se nevyžaduje – kde není, testy se přeskočí nahlas.
"""
import os
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


class SkutecnySkriptChraniZdroj(unittest.TestCase):
    """Pojistka se ověřuje na SPUŠTĚNÉM `transcribe.sh`, ne na opisu jeho podmínky.

    Třída `PojistkaProtiPrepsaniZdroje` výš pouští kopii té podmínky, protože
    skutečný běh chce whisper-cli a model o velikosti gigabajtu. Jenže kopie
    nehlídá skript: 14. 9. 2026 se ukázalo, že stačí vyřadit podmínku ve skriptu
    (`&& false`) a všech šest testů zůstane zelených, protože jediná vazba na
    originál byla kontrola přítomnosti řetězce `-ef` – a ten ve skriptu zbyl.

    Tenhle test tu díru zavírá tím, že whisper i model **podstrčí**: model je
    prázdný soubor v přesměrovaném `HOME`, whisper stub, který jen vyrobí
    očekávané výstupy. Skript tak proběhne celý včetně pojistky.
    """

    def setUp(self):
        if not FFMPEG:
            self.skipTest("ffmpeg není k dispozici, scénář se nedá přehrát")
        self.tmp = Path(tempfile.mkdtemp(prefix="transcript-e2e-"))
        self.home = self.tmp / "home"
        (self.home / ".whisper-models").mkdir(parents=True)
        # Model se jen kontroluje na existenci; stub whisperu ho nečte.
        (self.home / ".whisper-models" / "ggml-large-v3-turbo.bin").write_text("")

        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        stub = self.bin / "whisper-cli"
        stub.write_text(
            "#!/bin/sh\n"
            "of=''\n"
            "while [ $# -gt 0 ]; do\n"
            "  case \"$1\" in -of) of=\"$2\"; shift 2 ;; *) shift ;; esac\n"
            "done\n"
            "[ -n \"$of\" ] || exit 1\n"
            "printf 'přepis\\n' > \"$of.txt\"\n"
            "printf '1\\n00:00:00,000 --> 00:00:01,000\\npřepis\\n\\n' > \"$of.srt\"\n"
        )
        stub.chmod(0o755)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_wav_vstup_v_pracovnim_adresari_prezije(self):
        """Nahrávka je WAV a leží tam, kam se převádí – přesně ten případ,
        kdy ffmpeg bez pojistky otevře vlastní vstup pro zápis a ořízne ho.

        Běží se v režimu `overwrite`, protože ve výchozím `stop` skript skončí
        o krok dřív na kontrole „výstupy už existují“ a k pojistce vůbec nedojde.
        Právě proto je pojistka poslední obrana: uživatel v tomhle režimu řekl
        „přepiš výstupy“, ne „znič mi zdroj“."""
        zdroj = self.tmp / "rec.wav"
        subprocess.run([FFMPEG, "-f", "lavfi", "-i", "sine=frequency=440:duration=10",
                        "-ar", "44100", "-ac", "2", str(zdroj), "-y"],
                       capture_output=True, check=True)
        pred = zdroj.stat().st_size

        env = dict(os.environ,
                   HOME=str(self.home),
                   PATH=f"{self.bin}:{os.environ['PATH']}",
                   WHISPER_VAD="0", WHISPER_KEEP_WAV="1",
                   WHISPER_ON_EXISTING="overwrite")
        # Relativní zápis vstupu i pracovního adresáře: právě ten obcházel
        # porovnání řetězců, protože `./rec.wav` a `rec.wav` je týž soubor.
        hotovo = subprocess.run(["bash", str(TRANSCRIBE), ".", "log.txt", "rec.wav"],
                                cwd=str(self.tmp), env=env, capture_output=True, text=True)

        self.assertEqual(zdroj.stat().st_size, pred,
                         f"zdrojová nahrávka se během běhu změnila – "
                         f"{pred} B → {zdroj.stat().st_size} B; stderr: {hotovo.stderr[-500:]}")


    def test_mutace_pojistky_zdroj_znici(self):
        """Vyřadí pojistku ve skriptu a ověří, že se zdroj OPRAVDU zničí.

        Bez tohohle testu by scénář výš mohl být zelený z docela jiného důvodu –
        třeba proto, že skript skončil dřív, než se k pojistce dostal. Přesně to
        se stalo při jeho psaní: ve výchozím režimu `stop` se běh zastavil na
        kontrole existujících výstupů a test procházel i s vyřazenou pojistkou."""
        # Kopíruje se celý adresář skillu: `transcribe.sh` si sourcuje `common.sh`
        # ze svého vlastního adresáře, takže osamocená kopie by spadla na chybějící
        # závislost a test by „prošel“ ze špatného důvodu. Do repozitáře se přitom
        # nezapisuje nic.
        kopie = self.tmp / "skill"
        shutil.copytree(TRANSCRIBE.parent, kopie)
        poskozeny = kopie / TRANSCRIBE.name
        text = TRANSCRIBE.read_text(encoding="utf-8")
        podminka = '  if [ -e "$wav" ] && [ "$wav" -ef "$f" ]; then'
        self.assertEqual(text.count(podminka), 1, "pojistka ve skriptu změnila tvar")
        poskozeny.write_text(text.replace(podminka, podminka[:-6] + " && false; then"),
                             encoding="utf-8")

        zdroj = self.tmp / "rec.wav"
        subprocess.run([FFMPEG, "-f", "lavfi", "-i", "sine=frequency=440:duration=10",
                        "-ar", "44100", "-ac", "2", str(zdroj), "-y"],
                       capture_output=True, check=True)
        pred = zdroj.stat().st_size

        env = dict(os.environ, HOME=str(self.home),
                   PATH=f"{self.bin}:{os.environ['PATH']}",
                   WHISPER_VAD="0", WHISPER_KEEP_WAV="1",
                   WHISPER_ON_EXISTING="overwrite")
        subprocess.run(["bash", str(poskozeny), ".", "log.txt", "rec.wav"],
                       cwd=str(self.tmp), env=env, capture_output=True, text=True)

        self.assertLess(zdroj.stat().st_size, pred,
                        "poškozená verze zdroj nezničila – scénář výš tedy neměří pojistku")


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
