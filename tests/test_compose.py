"""Regresní testy generátorů archivu `/compose` – tam, kde vada nejde poznat.

Tyhle skripty čtou oficiální exporty ze sociálních sítí a přepisují z nich
archiv v `~/Dev/context/archive/`, ze kterého pak `/compose` destiluje znalostní
bázi autorova psaní. Chyba v nich se neprojeví jako pád, ale jako **archiv, který
vypadá v pořádku a není**: chybí část příspěvků, je rozbitá diakritika, nebo
tweet nese text jiného tweetu. Pozná to jedině ten, kdo si přečte diff přes
tisíce řádků, a ten to nedělá nikdo.

Testují se proto tři místa, kde je vada tichá, ne celé skripty:

1. Oprava mojibake ve facebookovém exportu (kóduje UTF-8 jako latin-1 escapy).
2. Vynechávání čistých retweetů – filtr, který smí vypustit jen to své.
3. Párování plných textů dlouhých tweetů podle času s toleranci ±2 s.

Skripty se pouštějí jako podproces, protože mají kód na úrovni modulu a nedají
se importovat; testuje se tím rovnou to, co se doopravdy spouští.

Spouští se: python3 -m unittest discover -s tests -q

Jen stdlib – `parse_bluesky.py` se proto netestuje, potřebuje `cbor2`.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills" / "compose" / "scripts"


class MojibakeFix(unittest.TestCase):
    """Facebook kóduje UTF-8 jako latin-1 escapy; bez opravy je archiv nečitelný."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="compose-fb-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_script(self, posts):
        src = self.tmp / "posts.json"
        src.write_text(json.dumps(posts, ensure_ascii=False), encoding="utf-8")
        out = self.tmp / "out"
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "gen_facebook_md.py"), str(src), str(out)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        produced = list(out.glob("*.md"))
        self.assertEqual(len(produced), 1, f"čekal jsem jeden soubor, je jich {len(produced)}")
        return produced[0].read_text(encoding="utf-8")

    def test_mojibake_is_fixed(self):
        # "Příliš žluťoučký" v UTF-8 bajtech přečtené jako latin-1 – přesně to,
        # co leží v exportu.
        garbled = "Příliš žluťoučký".encode("utf-8").decode("latin-1")
        self.assertNotIn("Příliš", garbled, "fixture není mojibake, test by neměřil nic")
        text = self.run_script([{"timestamp": 1600000000, "data": [{"post": garbled}]}])
        self.assertIn("Příliš žluťoučký", text)

    def test_fix_keeps_correct_text(self):
        """Opačný směr: text, který mojibake není, musí projít beze změny.

        Je to ta nebezpečnější polovina – rozbitá diakritika v archivu je vidět,
        kdežto oprava, která zkazí správný text, vyrobí tichou škodu tam, kde
        předtím nic nebylo."""
        text = self.run_script([{"timestamp": 1600000000,
                            "data": [{"post": "Příliš žluťoučký kůň úpěl ďábelské ódy"}]}])
        self.assertIn("Příliš žluťoučký kůň úpěl ďábelské ódy", text)


class TweetsNotLostOrMixed(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="compose-tw-"))
        self.data = self.tmp / "data"
        self.data.mkdir()
        self.write_js("account.js", [{"account": {"username": "honza", "accountId": "42"}}])

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_js(self, name, content):
        (self.data / name).write_text(
            f"window.YTD.{name.split('.')[0]}.part0 = " + json.dumps(content, ensure_ascii=False),
            encoding="utf-8")

    def tweet(self, id_str, when, text):
        return {"tweet": {"id_str": id_str, "id": id_str, "created_at": when,
                          "full_text": text, "entities": {}}}

    def run_script(self, tweets, notes=None):
        self.write_js("tweets.js", tweets)
        self.write_js("note-tweet.js", notes or [])
        out = self.tmp / "out"
        out.mkdir(exist_ok=True)
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "gen_twitter_md.py"), str(self.data), str(out)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return "\n".join(p.read_text(encoding="utf-8") for p in sorted(out.glob("*.md")))

    def test_pure_retweet_skipped_own_kept(self):
        text = self.run_script([
            self.tweet("1", "Wed Oct 10 20:19:24 +0000 2018", "RT @nekdo: cizí myšlenka"),
            self.tweet("2", "Wed Oct 10 21:19:24 +0000 2018", "moje vlastní myšlenka"),
        ])
        self.assertIn("moje vlastní myšlenka", text)
        self.assertNotIn("cizí myšlenka", text)

    def test_long_tweet_gets_full_text(self):
        """Export nese u dlouhých tweetů zkrácený text; plný je v note-tweet.js."""
        text = self.run_script(
            [self.tweet("1", "Wed Oct 10 20:19:24 +0000 2018", "zkrácený text…")],
            [{"noteTweet": {"createdAt": "2018-10-10T20:19:24.000Z",
                            "core": {"text": "plný text dlouhého tweetu až do konce"}}}])
        self.assertIn("plný text dlouhého tweetu až do konce", text)
        self.assertNotIn("zkrácený text…", text)

    def test_two_long_tweets_in_same_second_keep_own_text(self):
        """Párování běží podle času s tolerancí ±2 s, takže dva dlouhé tweety
        napsané rychle za sebou – běžné ve vlákně – si můžou vyměnit obsah.

        Je to nejtišší představitelná vada archivu: tweet zůstane na svém místě,
        má správné datum i odkaz, a nese cizí text."""
        text = self.run_script(
            [self.tweet("1", "Wed Oct 10 20:19:24 +0000 2018", "první zkrácený…"),
             self.tweet("2", "Wed Oct 10 20:19:25 +0000 2018", "druhý zkrácený…")],
            [{"noteTweet": {"createdAt": "2018-10-10T20:19:24.000Z",
                            "core": {"text": "PLNÝ TEXT PRVNÍHO"}}},
             {"noteTweet": {"createdAt": "2018-10-10T20:19:25.000Z",
                            "core": {"text": "PLNÝ TEXT DRUHÉHO"}}}])
        self.assertIn("PLNÝ TEXT PRVNÍHO", text)
        self.assertIn("PLNÝ TEXT DRUHÉHO", text)
        self.assertEqual(text.count("PLNÝ TEXT PRVNÍHO"), 1,
                         "jeden z tweetů nese text toho druhého")
        self.assertEqual(text.count("PLNÝ TEXT DRUHÉHO"), 1,
                         "jeden z tweetů nese text toho druhého")

    def test_tweet_without_full_text_takes_no_foreign_one(self):
        """Tweet, který svůj plný text nemá, si nesmí vzít text souseda.

        Přesně tohle se dělo do 14. 9. 2026: párování hledalo plný text v okně
        ±2 s a nekontrolovalo, komu patří. Druhý tweet o vteřinu později svůj
        záznam v note-tweet.js neměl, tak sebral ten sousedův – a ve
        vygenerovaném archivu stál text prvního tweetu dvakrát, zatímco text
        druhého zmizel úplně.

        Správné chování je ponechat zkrácený text: ten je vidět, cizí není.
        """
        text = self.run_script(
            [self.tweet("1", "Wed Oct 10 20:19:24 +0000 2018", "první zkrácený…"),
             self.tweet("2", "Wed Oct 10 20:19:25 +0000 2018", "DRUHÝ MÁ VLASTNÍ KRÁTKÝ TEXT")],
            [{"noteTweet": {"createdAt": "2018-10-10T20:19:24.000Z",
                            "core": {"text": "PLNÝ TEXT PRVNÍHO"}}}])
        self.assertEqual(text.count("PLNÝ TEXT PRVNÍHO"), 1,
                         "text prvního tweetu se objevil i u druhého")
        self.assertIn("DRUHÝ MÁ VLASTNÍ KRÁTKÝ TEXT", text,
                      "druhý tweet přišel o svůj text ve prospěch cizího")

    def test_full_text_goes_to_exact_time_match(self):
        """Přesná shoda má přednost před tolerancí, ať jsou tweety v jakémkoliv
        pořadí. Export je řazený od nejnovějšího, takže na pořadí iterace se
        spolehnout nejde."""
        text = self.run_script(
            [self.tweet("2", "Wed Oct 10 20:19:25 +0000 2018", "druhý zkrácený…"),
             self.tweet("1", "Wed Oct 10 20:19:24 +0000 2018", "první zkrácený…")],
            [{"noteTweet": {"createdAt": "2018-10-10T20:19:24.000Z",
                            "core": {"text": "PATŘÍ PRVNÍMU"}}}])
        self.assertIn("PATŘÍ PRVNÍMU", text)
        self.assertIn("druhý zkrácený…", text,
                      "novější tweet sebral tolerancí text, který přesně patří staršímu")

    def test_export_without_note_tweet_passes(self):
        """Účet, který nikdy nenapsal dlouhý tweet, `note-tweet.js` v exportu nemá.

        Dřív na něm generátor spadl na FileNotFoundError, takže se nevygeneroval
        ani jediný ročník – tedy chybějící nepovinný soubor zlikvidoval celý
        archiv včetně let, která s dlouhými tweety nemají nic společného.
        """
        self.write_js("tweets.js", [
            self.tweet("1", "Wed Oct 10 20:19:24 +0000 2018", "krátká myšlenka"),
        ])
        out = self.tmp / "out"
        out.mkdir(exist_ok=True)
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "gen_twitter_md.py"), str(self.data), str(out)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("krátká myšlenka",
                      "\n".join(f.read_text(encoding="utf-8") for f in out.glob("*.md")))


class BlueskyBrokenRecord(unittest.TestCase):
    """Jeden vadný post nesmí shodit generování všech ročníků.

    `parse_bluesky.py` čte repozitář stažený z PDS a záznam bez `createdAt`
    nebo `uri` z něj vyjít může – poškozeným blokem, nedostaženou částí,
    změnou schématu. Dřív na takovém postu generátor spadl na KeyError ještě
    před zápisem prvního souboru, takže se ztratil celý archiv kvůli jednomu
    záznamu. Správné chování je vadné vynechat, nahlásit a zbytek dopsat.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="compose-bs-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def post(self, ident, when, text):
        uri = f"at://did:plc:honza/app.bsky.feed.post/{ident}"
        return {"uri": uri, "createdAt": when, "text": text,
                "url": f"https://bsky.app/profile/honza.cz/post/{ident}"}

    def run_script(self, posts):
        src = self.tmp / "posts.json"
        src.write_text(json.dumps(posts, ensure_ascii=False), encoding="utf-8")
        out = self.tmp / "out"
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "gen_bluesky_md.py"), str(src), str(out)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return "\n".join(f.read_text(encoding="utf-8") for f in sorted(out.glob("*.md")))

    def test_post_without_createdat_keeps_rest(self):
        broken = self.post("x", "2024-05-01T10:00:00Z", "vadný")
        del broken["createdAt"]
        text = self.run_script([
            self.post("a", "2024-05-01T09:00:00Z", "první dobrý"),
            broken,
            self.post("b", "2024-05-01T11:00:00Z", "druhý dobrý"),
        ])
        self.assertIn("první dobrý", text)
        self.assertIn("druhý dobrý", text)
        self.assertNotIn("vadný", text)

    def test_post_without_uri_keeps_rest(self):
        broken = self.post("y", "2024-05-01T10:00:00Z", "vadný")
        del broken["uri"]
        text = self.run_script([self.post("a", "2024-05-01T09:00:00Z", "dobrý"), broken])
        self.assertIn("dobrý", text)
        self.assertNotIn("vadný", text)


if __name__ == "__main__":
    unittest.main()
