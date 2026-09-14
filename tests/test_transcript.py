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
3. Táž kontrola pak brala i **vlastní vstupní soubor**, takže WAV na vstupu –
   u spojené schůzky běžný případ, `join.sh` vyrábí právě WAV – běh odmítl
   s hláškou „už tu leží výstup“, přestože kandidát ukazoval sám na sebe.

**Pojistka se od 14. 9. 2026 ověřuje na spuštěném skriptu, ne na opisu.** Dřív
tu byla jen kopie jeho podmínky plus kontrola, že ve skriptu zbyl řetězec `-ef`.
Ta dvojice nechytila nic: stačilo vyřadit podmínku ve skriptu (`&& false`) a
všech šest testů zůstalo zelených, protože hlídaný řetězec v souboru zůstal.
Skutečný běh chce whisper a model o velikosti gigabajtu, takže se obojí
podstrčí – model prázdným souborem v přesměrovaném HOME, whisper stubem.

Spouští se: python3 -m unittest discover -s tests -q

Jen stdlib. `ffmpeg` se nevyžaduje – kde není, testy se přeskočí nahlas.
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIBE = ROOT / "skills" / "transcript" / "transcribe.sh"
JOIN = ROOT / "skills" / "transcript" / "join.sh"
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


class PrirazeniMluvcich(unittest.TestCase):
    """`merge.py` přiřazuje repliky mluvčím podle překryvu – a smí to odmítnout.

    Je to nejtišší vada v celém `/transcriptu`: špatně přiřazená replika vypadá
    v přepisu stejně věrohodně jako správná, takže ji pozná jen ten, kdo na té
    schůzce byl. Skript to řeší dvěma prahy (`MIN_RATIO`, `MIN_MARGIN`) a raději
    nechá mluvčího prázdného, než aby hádal. Bez testu jsou ty prahy jen dvě
    konstanty, které někdo při první nepřiřazené replice zvedne.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util
        cesta = ROOT / "skills" / "transcript" / "merge.py"
        spec = importlib.util.spec_from_file_location("merge_pod_testem", cesta)
        cls.merge = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.merge)

    def replika(self, start, end, text="text"):
        return {"start": start, "end": end, "text": text}

    def usek(self, start, end, speaker):
        return {"start": start, "end": end, "speaker": speaker}

    def test_jasny_prekryv_se_priradi(self):
        cue = self.replika(0, 10)
        turns = [self.usek(0, 10, "SPEAKER_00")]
        self.assertEqual(self.merge.assign(cue, turns), "SPEAKER_00")

    def test_tesny_naskok_zustane_neprirazeny(self):
        """Vítěz pokrývá 70 % repliky, ale druhý 60 % – náskok je desetina.

        Tohle je scénář, na kterém stojí `MIN_MARGIN`: `MIN_RATIO` je splněný,
        takže kdyby druhý práh zmizel, replika by nálepku dostala, přestože je
        rozdíl mezi mluvčími v šumu. Úseky se překrývají schválně – pyannote je
        tak vrací, když dva lidé mluví přes sebe, a to je právě ta chvíle, kdy
        je přiřazení nejméně jisté a zároveň nejvíc svádí.
        """
        cue = self.replika(0, 10)
        turns = [self.usek(0, 7, "SPEAKER_00"), self.usek(3, 9, "SPEAKER_01")]
        self.assertIsNone(self.merge.assign(cue, turns))

    def test_slaby_podil_zustane_neprirazeny(self):
        """Vítěz sice není zpochybněný, ale pokrývá jen polovinu repliky –
        zbytek je ticho nebo nikým nepřiznaný hlas."""
        cue = self.replika(0, 10)
        turns = [self.usek(0, 5, "SPEAKER_00")]
        self.assertIsNone(self.merge.assign(cue, turns))

    def test_zadny_prekryv_zustane_neprirazeny(self):
        cue = self.replika(0, 10)
        turns = [self.usek(20, 30, "SPEAKER_00")]
        self.assertIsNone(self.merge.assign(cue, turns))

    def test_rozdelene_useky_tehoz_mluvciho_se_scitaji(self):
        """Pyannote vrací víc úseků na mluvčího; bez sečtení by dlouhá replika
        přerušená nádechem spadla pod práh a zůstala bez jména."""
        cue = self.replika(0, 10)
        turns = [self.usek(0, 4, "SPEAKER_00"), self.usek(4.5, 10, "SPEAKER_00")]
        self.assertEqual(self.merge.assign(cue, turns), "SPEAKER_00")

    def test_mutace_prahu_nalepku_vyrobi(self):
        """Ověří, že testy výš měří prahy, a ne jen shodu s návratovou hodnotou.

        Každý práh se vypíná ZVLÁŠŤ, a to je tady to podstatné. První verze
        těchhle testů shazovala oba naráz a odmítnutí přičítala `MIN_MARGIN`,
        jenže scénář 55:45 padá na `MIN_RATIO` – druhý práh tak nehlídal nikdo
        a mutace `MIN_MARGIN = 0` neshodila jediný test. Doloženo 14. 9. 2026."""
        puvodni = (self.merge.MIN_RATIO, self.merge.MIN_MARGIN)
        try:
            # Slabý podíl: vypnout MIN_RATIO stačí, aby nálepku dostal.
            self.merge.MIN_RATIO, self.merge.MIN_MARGIN = 0.0, puvodni[1]
            self.assertEqual(
                self.merge.assign(self.replika(0, 10), [self.usek(0, 5, "SPEAKER_00")]),
                "SPEAKER_00", "test slabého podílu neměří MIN_RATIO")

            # Těsný náskok: vypnout MIN_MARGIN stačí, aby nálepku dostal.
            self.merge.MIN_RATIO, self.merge.MIN_MARGIN = puvodni[0], 0.0
            self.assertEqual(
                self.merge.assign(self.replika(0, 10),
                                  [self.usek(0, 7, "SPEAKER_00"), self.usek(3, 9, "SPEAKER_01")]),
                "SPEAKER_00", "test těsného náskoku neměří MIN_MARGIN")
        finally:
            self.merge.MIN_RATIO, self.merge.MIN_MARGIN = puvodni


class MergeEndToEnd(unittest.TestCase):
    """Spojení přepisu s mluvčími nad skutečnými vstupy, přes spuštěný skript."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="merge-test-"))
        self.merge_py = ROOT / "skills" / "transcript" / "merge.py"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_vyrobi_json_i_vtt_se_jmeny(self):
        srt = self.tmp / "a.srt"
        srt.write_text(
            "1\n00:00:00,000 --> 00:00:10,000\nDobrý den.\n\n"
            "2\n00:00:10,000 --> 00:00:20,000\nNazdar.\n\n", encoding="utf-8")
        diar = self.tmp / "d.json"
        diar.write_text(json.dumps({
            "speakers": ["SPEAKER_00", "SPEAKER_01"], "num_speakers": 2,
            "turns": [{"start": 0, "end": 10, "speaker": "SPEAKER_00"},
                      {"start": 10, "end": 20, "speaker": "SPEAKER_01"}],
        }), encoding="utf-8")
        names = self.tmp / "n.json"
        names.write_text(json.dumps({"SPEAKER_00": "Honza"}), encoding="utf-8")

        hotovo = subprocess.run(
            ["python3", str(self.merge_py), str(srt), str(diar),
             str(self.tmp / "out"), "--names", str(names)],
            capture_output=True, text=True)
        self.assertEqual(hotovo.returncode, 0, hotovo.stderr)

        data = json.loads((self.tmp / "out.json").read_text(encoding="utf-8"))
        self.assertEqual([s["speaker"] for s in data["segments"]],
                         ["SPEAKER_00", "SPEAKER_01"])
        self.assertEqual(data["unassigned_segments"], 0)
        vtt = (self.tmp / "out.vtt").read_text(encoding="utf-8")
        self.assertIn("<v Honza>Dobrý den.", vtt)
        self.assertIn("<v SPEAKER_01>Nazdar.", vtt,
                      "nepojmenovaný mluvčí musí zůstat pod svým kódem, ne zmizet")

    def test_neprirazena_replika_zustane_bez_znacky(self):
        """Ve VTT nesmí u nepřiřazené repliky vzniknout prázdné `<v >`."""
        srt = self.tmp / "a.srt"
        srt.write_text("1\n00:00:00,000 --> 00:00:10,000\nKdo to řekl?\n\n", encoding="utf-8")
        diar = self.tmp / "d.json"
        diar.write_text(json.dumps({
            "speakers": ["SPEAKER_00", "SPEAKER_01"], "num_speakers": 2,
            "turns": [{"start": 0, "end": 5.5, "speaker": "SPEAKER_00"},
                      {"start": 5.5, "end": 10, "speaker": "SPEAKER_01"}],
        }), encoding="utf-8")

        hotovo = subprocess.run(
            ["python3", str(self.merge_py), str(srt), str(diar), str(self.tmp / "out")],
            capture_output=True, text=True)
        self.assertEqual(hotovo.returncode, 0, hotovo.stderr)
        data = json.loads((self.tmp / "out.json").read_text(encoding="utf-8"))
        self.assertIsNone(data["segments"][0]["speaker"])
        self.assertEqual(data["unassigned_segments"], 1)
        vtt = (self.tmp / "out.vtt").read_text(encoding="utf-8")
        self.assertNotIn("<v ", vtt)
        self.assertIn("Kdo to řekl?", vtt)


class VstupNeblokujeSamSebe(unittest.TestCase):
    """Kontrola existujících výstupů nesmí zastavit běh kvůli vlastnímu vstupu.

    `VYSTUPNI_PRIPONY` obsahuje `wav`, takže u WAV na vstupu ukazuje kandidát na
    výstup na tentýž soubor, který se má přepisovat. Bez výjimky přes `-ef` každý
    takový běh skončil kódem 3 – a od zavedení `join.sh`, který spojenou schůzku
    vyrábí právě jako WAV, by to byla cesta, kudy se k přepisu vůbec nedá dojít.

    Testují se **oba směry**: že vlastní vstup propustí i že skutečný starší
    výstup pořád zastaví. Falešně propustná kontrola je tu horší než chybějící –
    tiše by přepsala hodinu práce.
    """

    def setUp(self):
        if not FFMPEG:
            self.skipTest("ffmpeg není k dispozici, scénář se nedá přehrát")
        self.tmp = Path(tempfile.mkdtemp(prefix="transcript-vstup-"))
        self.home = self.tmp / "home"
        (self.home / ".whisper-models").mkdir(parents=True)
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
        self.env = dict(os.environ, HOME=str(self.home),
                        PATH=f"{self.bin}:{os.environ['PATH']}", WHISPER_VAD="0")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _wav(self, jmeno, sekund=2):
        cil = self.tmp / jmeno
        subprocess.run([FFMPEG, "-f", "lavfi", "-i", f"sine=frequency=440:duration={sekund}",
                        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(cil), "-y"],
                       capture_output=True, check=True)
        return cil

    def _beh(self, skript=None):
        return subprocess.run(
            ["bash", str(skript or TRANSCRIBE), ".", "log.txt", "rec.wav"],
            cwd=str(self.tmp), env=self.env, capture_output=True, text=True)

    def test_wav_vstup_projde(self):
        """Propustit, co propustit má: jediný kolidující kandidát je vstup sám."""
        zdroj = self._wav("rec.wav")
        pred = zdroj.stat().st_size
        hotovo = self._beh()
        self.assertEqual(hotovo.returncode, 0,
                         f"WAV vstup neprošel kontrolou výstupů: {hotovo.stderr[-400:]}")
        self.assertNotIn("### EXISTING", (self.tmp / "log.txt").read_text(encoding="utf-8"))
        self.assertTrue((self.tmp / "rec.srt").exists(), "přepis nevznikl")
        self.assertEqual(zdroj.stat().st_size, pred, "vstupní WAV se během běhu změnil")

    def test_starsi_vystup_porad_zastavi(self):
        """Zastavit, co zastavit má: `.srt` z dřívějška je cizí soubor, ne vstup."""
        self._wav("rec.wav")
        (self.tmp / "rec.srt").write_text("starý přepis", encoding="utf-8")
        hotovo = self._beh()
        self.assertEqual(hotovo.returncode, 3,
                         "existující .srt měl běh zastavit kódem 3")
        self.assertIn("### EXISTING", (self.tmp / "log.txt").read_text(encoding="utf-8"))
        self.assertEqual((self.tmp / "rec.srt").read_text(encoding="utf-8"), "starý přepis",
                         "starší přepis se přepsal, přestože měl běh skončit")

    def test_mutace_vyjimky_zastavi_vlastni_vstup(self):
        """Vyřadí výjimku ve skriptu a ověří, že se běh OPRAVDU zastaví.

        Bez tohohle by první test mohl být zelený z jiného důvodu – třeba proto,
        že kontrola na `wav` vůbec nesáhla. Mutace to rozhodne: s vyřazenou
        výjimkou musí WAV vstup spadnout na kódu 3.
        """
        kopie = self.tmp / "skill"
        shutil.copytree(TRANSCRIBE.parent, kopie)
        text = TRANSCRIBE.read_text(encoding="utf-8")
        podminka = '      [ "$kand" -ef "$f" ] && continue'
        self.assertEqual(text.count(podminka), 1, "výjimka ve skriptu změnila tvar")
        (kopie / TRANSCRIBE.name).write_text(
            text.replace(podminka, '      [ "$kand" -ef "$f" ] && false && continue'),
            encoding="utf-8")
        self._wav("rec.wav")
        hotovo = self._beh(kopie / TRANSCRIBE.name)
        self.assertEqual(hotovo.returncode, 3,
                         "s vyřazenou výjimkou měl WAV vstup zastavit běh – "
                         "test výš tedy neověřuje to, co si myslí")


class SpojovaniCastiSchuzky(unittest.TestCase):
    """`join.sh` spojuje části jedné schůzky do jedné nahrávky.

    Vstupem jsou nahrávky, které většinou nejde pořídit znovu, takže se hlídají
    tři věci: že se nic nepřepíše, že se nic neztratí a že se neúplný výsledek
    nevydá za hotový. Poslední je nejdůležitější – spojení, které tiše přijde
    o část, by se poznalo až jako záhadně chybějící kus přepisu.
    """

    def setUp(self):
        if not FFMPEG:
            self.skipTest("ffmpeg není k dispozici, scénář se nedá přehrát")
        self.ffprobe = shutil.which("ffprobe")
        if not self.ffprobe:
            self.skipTest("ffprobe není k dispozici")
        self.tmp = Path(tempfile.mkdtemp(prefix="transcript-join-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _cast(self, jmeno, sekund, hz=440, kanaly=2, rate=44100):
        cil = self.tmp / jmeno
        subprocess.run([FFMPEG, "-f", "lavfi", "-i", f"sine=frequency={hz}:duration={sekund}",
                        "-ar", str(rate), "-ac", str(kanaly), str(cil), "-y"],
                       capture_output=True, check=True)
        return cil

    def _delka(self, path):
        out = subprocess.run([self.ffprobe, "-v", "error", "-show_entries",
                              "format=duration", "-of", "csv=p=0", str(path)],
                             capture_output=True, text=True, check=True)
        return float(out.stdout.strip())

    def _join(self, nazev, *casti, env=None):
        return subprocess.run(
            ["bash", str(JOIN), str(self.tmp), nazev, *[str(c) for c in casti]],
            cwd=str(self.tmp), capture_output=True, text=True,
            env=env or dict(os.environ))

    def test_ruzne_formaty_se_spoji_a_zdroje_zustanou(self):
        """Části bývají každá odjinud – m4a z diktafonu vedle wav z jiného zdroje.

        Kdyby se spojovalo beze ztráty (`-c copy`), tenhle případ by spadl nebo
        vyrobil vadné časy; proto se překódovává na 16 kHz mono.
        """
        a = self._cast("a.m4a", 3)
        b = self._cast("b.wav", 5, hz=880, kanaly=1, rate=16000)
        velikosti = (a.stat().st_size, b.stat().st_size)

        hotovo = self._join("spojeno", a, b)
        self.assertEqual(hotovo.returncode, 0, hotovo.stderr)
        out = self.tmp / "spojeno.wav"
        self.assertTrue(out.exists(), "spojený soubor nevznikl")
        self.assertAlmostEqual(self._delka(out), 8.0, delta=1.0,
                               msg="spojený soubor nemá délku součtu částí")
        self.assertEqual((a.stat().st_size, b.stat().st_size), velikosti,
                         "zdrojové části se spojováním změnily")

    def test_existujici_soubor_se_neprepise(self):
        """`ffmpeg -y` přepisuje mlčky, takže to musí odchytit skript."""
        a, b = self._cast("a.wav", 1), self._cast("b.wav", 1, hz=880)
        (self.tmp / "spojeno.wav").write_text("dřívější práce", encoding="utf-8")
        hotovo = self._join("spojeno", a, b)
        self.assertNotEqual(hotovo.returncode, 0, "existující soubor se měl bránit")
        self.assertEqual((self.tmp / "spojeno.wav").read_text(encoding="utf-8"),
                         "dřívější práce", "existující soubor se přepsal")

    def test_ztracena_cast_se_nevyda_za_hotovou(self):
        """Podstrčí `ffprobe`, který u výsledku hlásí nesmyslnou délku.

        Simuluje spojení, které přišlo o část. Skript to musí poznat, skončit
        nenulově a **soubor smazat** – jinak by se s ním dál pracovalo jako
        s úplným. Mutace míří na skutečné porovnání, ne na přítomnost řetězce
        v kódu: kdyby kontrola chyběla, tenhle test zezelená jen zdánlivě.
        """
        a, b = self._cast("a.wav", 3), self._cast("b.wav", 5, hz=880)
        falesny_bin = self.tmp / "fakebin"
        falesny_bin.mkdir()
        stub = falesny_bin / "ffprobe"
        stub.write_text(
            "#!/bin/sh\n"
            "for arg in \"$@\"; do\n"
            "  case \"$arg\" in *spojeno.wav) echo 1.0; exit 0 ;; esac\n"
            "done\n"
            f"exec {self.ffprobe} \"$@\"\n"
        )
        stub.chmod(0o755)
        env = dict(os.environ, PATH=f"{falesny_bin}:{os.environ['PATH']}")

        hotovo = self._join("spojeno", a, b, env=env)
        self.assertNotEqual(hotovo.returncode, 0,
                            "nesouhlasící délka měla běh shodit")
        self.assertFalse((self.tmp / "spojeno.wav").exists(),
                         "neúplný spojený soubor zůstal ležet a tváří se jako hotový")

    def test_cast_bez_zvukove_stopy(self):
        """Video bez zvuku je reálný vstup – převod musí selhat nahlas."""
        a = self._cast("a.wav", 1)
        nemy = self.tmp / "nemy.mp4"
        subprocess.run([FFMPEG, "-f", "lavfi", "-i", "testsrc=duration=1:size=64x64:rate=10",
                        "-an", str(nemy), "-y"], capture_output=True, check=True)
        hotovo = self._join("spojeno", a, nemy)
        self.assertNotEqual(hotovo.returncode, 0, "část bez zvuku měla běh shodit")
        self.assertFalse((self.tmp / "spojeno.wav").exists(),
                         "vznikl spojený soubor, přestože jedna část chybí")

    def test_mene_nez_dve_casti(self):
        """Spojovat jeden soubor nedává smysl a bývá to chyba volajícího."""
        a = self._cast("a.wav", 1)
        self.assertNotEqual(self._join("spojeno", a).returncode, 0)
        self.assertFalse((self.tmp / "spojeno.wav").exists())
