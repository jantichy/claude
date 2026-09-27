# -*- coding: utf-8 -*-
"""Převod českého slova „partie“ na „podobjednávka“ se zachováním pádu.

Obě slova jsou ženského rodu, takže se mění jen samo podstatné jméno –
přívlastky, příčestí ani shoda se nedotknou. Tvary se navíc slévají, takže
zbývají tři binární rozhodnutí:

    partie  → podobjednávka (1. j.)   | podobjednávky (2. j., 1./4. mn.)
    partii  → podobjednávce (3., 6.)  | podobjednávku (4.)
    partií  → podobjednávkou (7. j.)  | podobjednávek (2. mn.)
"""
import re

# --- předložky podle pádu, který si vynucují -----------------------------
P2 = {'u','do','z','ze','od','ode','bez','beze','podle','vedle','kolem','během','kromě','místo','okolo','stran'}
P3 = {'k','ke','ku','proti','kvůli','díky','vůči','naproti'}
P4 = {'pro','přes','skrz','mimo'}
P6 = {'v','ve','o','při','po'}
P7 = {'s','se','nad','pod','před','přede','mezi','za'}
# „na“ je 4. i 6. pád, rozhoduje sloveso – řeší se zvlášť

KVANT = {'víc','více','několik','pár','mnoho','málo','tolik','kolik','všech','obou','ostatních','zbylých',
         'dvou','tří','čtyř','pěti','šesti','sedmi','osmi','devíti','deseti','žádných','těch','oněch','jiných'}
CISLO_MN = {'dvě','tři','čtyři','pět','šest','sedm','osm','devět','deset','obě','všechny','ostatní','jednotlivé',
            'zbylé','živé','další','některé','tyhle','tyto','ty','víc','více','čtyři'}

# slovesa a tvary, po kterých následuje předmět ve 4. pádě
SLOVESO_4 = re.compile(r'(vezme|zamyká|zamkne|vystaví|smaže|smazat|obnoví|obnovit|potvrdí|potvrdit|zruší|zrušit|'
    r'vrátí|vrátit|přesune|přesunout|dostane|dostat|nechá|nechat|pustí|pustit|bere|brát|drží|držet|'
    r'najde|najít|označí|označit|zaplatí|zaplatit|dobropisuje|rozdělí|rozdělit|uzavře|uzavřít|'
    r'vyřadí|vyřadit|blokuje|blokovat|odemkne|odemknout|přeskočí|přeskočit|vyzvedne|zapíše|'
    r'ovlivní|ovlivnit|postihne|založí|založit|mění|měnit|hne|hnout|nepustí|nepustit|nevezme)$')

# přívlastek v jednotlivých pádech (ženský rod)
ADJ_1 = re.compile(r'(á|ta|tahle|tato|jedna|žádná|každá|která|kterákoli|táž|celá|sama|samotná|jediná|jiná|nová|ta)$')
ADJ_4_7 = re.compile(r'(ou)$')           # smazanou, celou, touhle – 4. nebo 7.
ADJ_2MN = re.compile(r'(ých|ích|ech)$')  # smazaných, ostatních – 2. mn.
ADJ_23_6 = re.compile(r'(é|ě|í|té|téže|této|oné)$')  # smazané (2. j. / 1.,4. mn.), téže (3., 6.)

SUBST2 = {'stav','číslo','čísla','cena','ceny','zrušení','potvrzení','pořadí','vzniku','vznik','splatnost',
          'doklad','dokladu','doklady','historie','detail','detailu','seznam','seznamu','záložky','záložka',
          'obsah','mailing','mailingy','kontext','kontextu','osa','osy','stránka','stránce','smazání','obnovení',
          'vystavení','zaplacení','expirace','výmaz','položky','účastníci','účastníky','účastník','součet','souhrn',
          'konec','konce','guard','guardy','identifikátor','část','části','většina','polovina','sloupec','pole',
          'úhradu','úhrady','dobropisu','dobropis','fakturu','faktury','zálohovky','zálohovka','platba','platby',
          'objednávka','objednávky','objednávce','akce','události','termín','termínu',
          'token','tokenu','entitu','entita','entity','záložce','záložku','dobropisy','stavem','čísla','id',
          'osu','ose','kontextem','mailingu','dokladem','platbu','platbou','vznikem','smazáním','obnovením',
          'zrušením','potvrzením','vystavením','zaplacením','koncem','začátkem','polovina','zbytek','zbytku'}
# co může stát za podmětem v 1. pádě j. č. (sloveso nebo jmenný tvar příčestí)
SLOVESO_J = {'je','má','není','nemá','vznikne','vznikla','vzniká','zůstane','zůstává','zůstala','dostane','dostala',
 'smí','musí','může','nemůže','bude','byla','bývá','spadne','spadla','odchází','odešla','žije','stojí','existuje',
 'nese','končí','platí','projde','neprojde','drží','patří','visí','leží','čeká','vstoupí','dojde','nejde','ztratí',
 'míří','sedí','zmizí','přijde','vypadá','obnovena','obnovená','smazána','smazaná','potvrzená','potvrzena','zrušena',
 'zaplacená','zaplacena','vystavená','dobropisovaná','nezaplacená','bezplatná','živá','sama','tím','totiž','naopak','padá','vězí','ví','umí','slouží','podrží','zastaví','vrátí','přibyla','přibude',
 'jde','nejde','začíná','překlopí','zamkne','uvolní','ztratí','nezabíjí','spadá','nesahá','nevisí','nezbyla',
 'odešla','vypadla','prošla','neprošla','dorazila','zanikla','zbyla','platila','měla','neměla','mohla','musela',
 'dostávala','zůstávala','nese','sestoupí','odchází','přechází','vstupuje','zaniká','zbývá','trvá','visela','vypadala','dostala','sčítá','nesčítá','zlevnila','nezlevnila','vyjde',
 'nevyjde','skončí','znamená','unese','potřebuje','vyžaduje','projede','vydrží','zůstávala','zapsala',
 'neposlala','zadržela','ukázala','nedostala','nezlevní','nabízí','vystaví','uzavře','padá','čte','ví'}
SLOVESO_MN = {'jsou','mají','nejsou','nemají','vzniknou','vznikají','zůstávají','zůstanou','dostanou','nesou',
 'odcházejí','projdou','žijí','čekají','spadnou','existují','patřily','byly','bývají','obnoveny','smazány',
 'potvrzené','zaplacené','vystavené','dvě','tři','nejsou','neukazují','objevovaly','rozlišovaly','prošly',
 'odcházely','zůstaly','vznikly','existují','visí','leží','čekají','spadaly','stály','byly','nemají',
 'padají','spadnou','dostávají','vypadají','sčítají','nezlevní','projdou','odejdou','zůstávaly'}

# slovesa končící na -á, která by prošla jako přívlastek v 1. pádě
SLOVESA_A = {'má','nemá','dá','nedá','sahá','čeká','vzniká','zůstává','padá','odpovídá','nastává','bývá',
             'zahrnuje','obsahuje','eviduje','drží','nese','vyžaduje','potřebuje','dostává','ztrácí'}

NEJASNE_ADJ = {'její','jejich','první','další','poslední','třetí','jejíž','celé','téže','existující','stejné'}

TOK = re.compile(r'[0-9A-Za-zÁ-Žá-ž_`]+')   # bez pomlčky, ať se kotva #88-…-z-partií rozpadne na slova

VETA = re.compile(r'[.!?:;|)\]]\s+(?=[^a-zá-ž]|$)|\n|„|“|–\s')

def tokens_before(text, i, n=4):
    seg = text[max(0, i-90):i]
    # neber slova z předchozí věty ani z jiné buňky tabulky
    hranice = [m.end() for m in VETA.finditer(seg)]
    if hranice:
        seg = seg[hranice[-1]:]
    return TOK.findall(seg)[-n:]

def tokens_after(text, j, n=7):
    return TOK.findall(text[j:j+90])[:n]

# Uzavřený seznam funkčních slov. Stojí-li vlevo něco jiného, je to skoro vždy
# podstatné jméno („stav partie“, „číslem partie“) a jde o 2. pád jednotného čísla.
FUNKCNI = {'a','i','ale','nebo','ani','že','protože','takže','když','jestli','pokud','kdyby','kdybychom','li',
 'jen','jenom','tedy','proto','přitom','navíc','naopak','se','si','by','bych','ne','nejen','kde','kdy','jak',
 'tak','to','tím','už','ještě','také','taky','pak','potom','teď','nyní','dnes','vždy','nikdy','jestliže',
 'je','jsou','není','nejsou','byla','byly','bude','budou','má','nemá','mají','nemají','smí','musí','může',
 'však','totiž','sice','přece','vlastně','zároveň','naráz','proč','která','které','kterou','jejichž','čím',
 'první','druhá','třetí','každá','tahle','tato','ta','jedna','žádná','všechny','obě','dvě','tři','víc','více',
 'jedné','téže','této','oné','její','jejich','celé','existující','stejné','poslední','další','nějaká','některé',
 'jde','nejde','jdou','šlo','lze','nelze','stačí','zbývá','zůstává','znamená','platí','začíná','končí'}

SLOVESNA_KONCOVKA = re.compile(r'(t|ti|ou|ají|ejí|ují|la|ly|lo|jí|ne|de|še)$')

VYCET = {'doklady','dobropisy','účastníci','účastníky','akce','kategorie','platby','maily','objednávky',
         'doklad','dobropis','účastník','položky','termíny'}

def cislo_podle_tvaru(w):
    """Číslo přísudku podle koncovky: množné má -ejí/-ají/-ou/-ly, jednotné -í/-á/-e/-la."""
    if len(w) < 3: return None
    if w.endswith(('ají','ejí','nou','ou','ly','yly','aly')): return 'mn'
    if w.endswith(('la','lo','í','á','e','ne','de','je')): return 'j'
    return None

def prvni_sloveso(right):
    """Najde první tvar, který rozhodne číslo podmětu – přeskočí předložkovou frázi."""
    for w in right[:7]:
        if w in SLOVESO_MN: return 'mn'
        if w in SLOVESO_J:  return 'j'
        if w in ('a','nebo','ale','ani'): break         # další větný člen, dál se neptáme
    return cislo_podle_tvaru(right[0]) if right else None

def sloveso_vlevo(left):
    for w in reversed(left):
        if w in SLOVESO_MN: return 'mn'
        if w in SLOVESO_J:  return 'j'
        if w.endswith(('ly','aly','ily')) and len(w) > 4: return 'mn'
    return None

def nxt2_sloveso(right):
    """Za „partie se …“ stojí sloveso ve tvaru, který ukazuje na jednotné číslo."""
    if len(right) < 2: return False
    w = right[1]
    return bool(re.search(r'(í|e|á|uje|ne|le|ší)$', w)) and w not in ('nebo','ale','a','i','se','je')

# --- rozhodování o pádu --------------------------------------------------
# Tvary, které se s ničím neslévají, a tedy o nich není co rozhodovat.
INVARIANT = {'partiemi': 'podobjednávkami', 'partiích': 'podobjednávkách',
             'partiím': 'podobjednávkám'}


class Context:
    """Okolí výskytu, ze kterého se pád určuje – vlevo 4 slova, vpravo 7.

    Počítá se jednou pro celý výskyt, protože po něm sahá skoro každé pravidlo:
    `prev` a `prev2` jsou dvě slova vlevo, `nxt` první vpravo, a `left`/`right`
    celá okna pro pravidla, která hledají dál (souřadný člen, přísudek za
    předložkovou frází).
    """

    __slots__ = ('left', 'right', 'prev', 'prev2', 'nxt')

    def __init__(self, text, i, j):
        self.left = [w.lower() for w in tokens_before(text, i)]
        self.right = [w.lower() for w in tokens_after(text, j)]
        self.prev = self.left[-1] if self.left else ''
        self.prev2 = self.left[-2] if len(self.left) > 1 else ''
        self.nxt = self.right[0] if self.right else ''


def resolve(form, text, i, j):
    """Vrátí (náhrada, jistota, pravidlo).

    Rozhoduje se ve **stupních a záleží na jejich pořadí**: každý vrací hotovou
    trojici, nebo `None`, a vyhrává první, který se chytí. Přesunout pravidlo
    mezi stupni proto **není úprava, ale změna chování** – slabší pravidlo by
    předběhlo silnější. Pořadí uvnitř stupně platí ze stejného důvodu.
    """
    if form in INVARIANT:
        return INVARIANT[form], True, 'jednoznačný tvar'
    c = Context(text, i, j)
    if form == 'partií':
        return instrumental_or_genitive(c)
    if form == 'partii':
        return dative_or_accusative(c)
    return nominative_or_genitive(c)


def first_hit(stages, c, fallback):
    """První stupeň, který něco vrátí; nechytí-li se žádný, platí `fallback`."""
    for stage in stages:
        hit = stage(c)
        if hit:
            return hit
    return fallback


# --- partií: 7. pád j. č., nebo 2. pád mn. č. ----------------------------

def instrumental_or_genitive(c):
    """`partií` je „podobjednávkou“ (7. j.), nebo „podobjednávek“ (2. mn.)."""
    if c.prev in P7 or ADJ_4_7.search(c.prev) or c.prev in ('touto', 'toutéž', 'onou', 'samou'):
        return 'podobjednávkou', True, '7. pád j. č.'
    if c.prev in KVANT or ADJ_2MN.search(c.prev):
        return 'podobjednávek', True, '2. pád mn. č.'
    if c.prev in P2 and c.prev2 in KVANT:
        return 'podobjednávek', True, '2. pád mn. č.'
    if c.prev in P2:
        return 'podobjednávek', True, '2. pád mn. č. po předložce'
    return 'podobjednávek', False, 'nejisté'


# --- partii: 3./6. pád, nebo 4. pád -------------------------------------

def dative_or_accusative(c):
    """`partii` je „podobjednávce“ (3., 6.), nebo „podobjednávku“ (4.)."""
    stages = (coordinated_member, case_by_preposition, case_by_modifier)
    hit = first_hit(stages, c, None)
    if hit:
        return hit
    if SLOVESO_4.search(c.prev):
        return 'podobjednávku', True, '4. pád po slovese'
    if c.prev in ('li', 'se', 'nese', 'má', 'obsahuje', 'zahrnuje'):
        return 'podobjednávku', False, '4. pád – předmět'
    return 'podobjednávku', False, 'nejisté'


def coordinated_member(c):
    """Za „ne partii“ se pád přebírá z členu, ke kterému je to souřadné."""
    if c.prev not in ('ne', 'nejen', 'ani'):
        return None
    for w in reversed(c.left[:-1]):
        if w.endswith(('ce', 'ě', 'i', 'ovi')):
            return 'podobjednávce', True, '3. pád podle souřadného členu'
        if w.endswith(('u', 'ku')):
            return 'podobjednávku', True, '4. pád podle souřadného členu'
    return None


def case_by_preposition(c):
    if c.prev in P3:
        return 'podobjednávce', True, '3. pád'
    if c.prev in P6:
        return 'podobjednávce', True, '6. pád'
    if c.prev in P4:
        return 'podobjednávku', True, '4. pád po předložce'
    if c.prev == 'na':
        # v datech je „na partii“ skoro vždy 6. pád („na partii leží, visí, zůstává“)
        if c.nxt in ('navěsit', 'převést', 'přepsat', 'rozdělit', 'navázat',
                     'přenést', 'převede', 'naváže', 'přepíše'):
            return 'podobjednávku', False, '„na“ – 4. pád podle slovesa'
        return 'podobjednávce', True, '6. pád po „na“'
    if c.prev in ('za', 'nad', 'pod', 'mezi', 'před'):
        return 'podobjednávku', True, '4. pád po předložce'
    return None


def case_by_modifier(c):
    if c.prev in NEJASNE_ADJ:
        return ambiguous_modifier(c)
    if ADJ_4_7.search(c.prev) or ADJ_1.search(c.prev):
        return 'podobjednávku', True, '4. pád podle přívlastku'
    # 3. i 6. pád mají týž tvar, takže se rozlišovat nemusí
    if ADJ_23_6.search(c.prev):
        return 'podobjednávce', True, '3. nebo 6. pád podle přívlastku'
    return None


def ambiguous_modifier(c):
    """Přívlastek jako „její“ nebo „první“ pád neodhalí – rozhodne slovo před ním."""
    if c.prev2 in P3 | P6 or c.prev2 == 'na':
        return 'podobjednávce', True, '3. nebo 6. pád podle předložky'
    if c.prev2 in P4 or c.prev2 in ('za',) or SLOVESO_4.search(c.prev2) or c.prev2 in SLOVESA_A:
        return 'podobjednávku', True, '4. pád podle předložky nebo slovesa'
    return 'podobjednávku', False, 'přívlastek nerozlišuje pád'


# --- partie: 1. pád j. č., nebo 2. pád j. č. a 1./4. mn. ----------------

def nominative_or_genitive(c):
    """`partie` je „podobjednávka“ (1. j.), nebo „podobjednávky“ (2. j., 1./4. mn.)."""
    stages = (nom_by_governor, nom_by_modifier, nom_by_enumeration,
              nom_by_right_word, nom_after_prepositional_phrase,
              nom_by_content_word, nom_by_ambiguous_modifier, nom_by_predicate)
    return first_hit(stages, c, ('podobjednávky', False, 'nejisté – 2. pád j. č. nebo množné'))


def nom_by_governor(c):
    """Slovo vlevo, které pád řídí: předložka, kvantifikátor, sloveso, podstatné jméno."""
    if c.prev in P2:
        return 'podobjednávky', True, '2. pád j. č. po předložce'
    if c.prev in CISLO_MN or c.prev in KVANT:
        return 'podobjednávky', True, 'množné číslo'
    if c.prev in SLOVESA_A or SLOVESO_4.search(c.prev):
        return 'podobjednávky', True, '4. pád mn. č. po slovese'   # 4. pád j. č. je „partii“
    if c.prev in SUBST2:
        return 'podobjednávky', True, '2. pád j. č. po podstatném jméně'
    if c.prev in ('na', 'pro', 'přes', 'mezi', 'za', 'nad', 'pod'):
        return 'podobjednávky', True, '4. pád mn. č. po předložce'   # 4. pád j. č. je „partii“
    return None


def nom_by_modifier(c):
    """Přívlastek a zájmeno vlevo. `její` je jediné, které samo o čísle nerozhoduje."""
    if c.prev in ('téže', 'jedné', 'oné', 'této', 'její') and c.nxt not in SLOVESO_MN:
        if c.prev == 'její' and c.nxt in SLOVESO_J:
            return 'podobjednávka', True, '1. pád po přivlastňovacím zájmeně'
        if c.prev != 'její':
            return 'podobjednávky', True, '2. pád j. č. po přívlastku'
    if c.prev == 'li':
        return 'podobjednávka', True, '1. pád v podmínkové větě „-li“'
    if ADJ_1.search(c.prev) and not ADJ_23_6.search(c.prev):
        return 'podobjednávka', True, '1. pád podle přívlastku'
    if ADJ_2MN.search(c.prev):
        return 'podobjednávky', True, 'množné číslo podle přívlastku'
    if ADJ_23_6.search(c.prev):
        return 'podobjednávky', True, '2. pád j. č. nebo mn. č. podle přívlastku'
    return None


def nom_by_enumeration(c):
    """Výčet vpravo a předmět ve 4. pádě mn. č. – jednotné by bylo „partii“."""
    if c.nxt in VYCET or (len(c.right) > 1 and c.right[1] in VYCET
                          and c.nxt in VYCET | {'jejich'}):
        return 'podobjednávky', True, 'výčet ve 4. pádě mn. č.'
    # sloveso vlevo řeší `nom_by_governor`, sem zbývá jen sloveso o slovo dál
    if c.prev2 in ('založí', 'zahrne', 'nese', 'platí'):
        return 'podobjednávky', True, '4. pád mn. č. – jednotné by bylo „partii“'
    if c.prev in ('nejen', 'ne', 'ani') and c.nxt not in SLOVESO_MN:
        return 'podobjednávka', True, 'paralelní větný člen v 1. pádě'
    return None


def nom_by_right_word(c):
    """Číslovka nebo přísudek hned vpravo, tedy shoda s podmětem."""
    if c.nxt in ('jedna', 'jediná', 'žádná', 'tatáž', 'táž', 'sama'):
        return 'podobjednávka', True, '1. pád s číslovkou'
    if c.nxt in SLOVESO_MN or c.nxt in ('jejichž', 'kterým', 'kterých'):
        return 'podobjednávky', True, 'množné číslo'
    if c.nxt in SLOVESO_J or c.nxt in ('která', 'jejíž'):
        return 'podobjednávka', True, '1. pád j. č.'
    return None


def nom_after_prepositional_phrase(c):
    """Přísudek stojí až za předložkovou frází („partie v tomhle stavu zůstává“)."""
    if c.nxt in P2 | P3 | P6 | P7 | P4 or c.nxt in ('bez', 'se', 's'):
        cislo = prvni_sloveso(c.right)
        if cislo == 'j':
            return 'podobjednávka', True, '1. pád – sloveso za předložkovou frází'
        if cislo == 'mn':
            return 'podobjednávky', True, 'množné číslo – sloveso za předložkovou frází'
    if c.nxt == 'se' and nxt2_sloveso(c.right):
        return 'podobjednávka', True, '1. pád – zvratné sloveso'
    return None


def nom_by_content_word(c):
    """Vlevo stojí slovo, které není funkční ani přívlastek – tedy sloveso, nebo jméno."""
    if not c.prev or c.prev in FUNKCNI or c.prev in CISLO_MN or c.prev in KVANT:
        return None
    if ADJ_1.search(c.prev) or ADJ_2MN.search(c.prev) or ADJ_23_6.search(c.prev):
        return None
    if SLOVESNA_KONCOVKA.search(c.prev) and c.prev not in SUBST2:
        return 'podobjednávky', True, '4. pád mn. č. po slovese'
    return 'podobjednávky', True, '2. pád j. č. po podstatném jméně'


def nom_by_ambiguous_modifier(c):
    """Přívlastek, který pád ani číslo neodhalí – rozhoduje okolí, pak přísudek."""
    if c.prev not in NEJASNE_ADJ:
        return None
    if c.prev2 in P2 or c.prev2 in ('jedné', 'téže', 'této', 'oné'):
        return 'podobjednávky', True, '2. pád j. č. po předložce a přívlastku'
    if c.prev2 in CISLO_MN or c.prev2 in KVANT:
        return 'podobjednávky', True, 'množné číslo podle kvantifikátoru'
    if any(SLOVESO_4.search(w) or w in SLOVESA_A for w in c.left):
        return 'podobjednávky', True, '4. pád mn. č. – jednotné by bylo „partii“'
    okoli = prvni_sloveso(c.right) or sloveso_vlevo(c.left)
    if okoli == 'mn':
        return 'podobjednávky', True, 'množné číslo podle přísudku'
    if okoli == 'j':
        return 'podobjednávka', True, '1. pád podle přísudku'
    return 'podobjednávka', False, 'přívlastek nerozlišuje pád'


def nom_by_predicate(c):
    """Poslední záchrana: číslo se odvodí z koncovky přísudku, a jistota se nehlásí."""
    if c.nxt == 'a' and not c.prev:
        return 'podobjednávka', True, '1. pád v souřadném spojení'
    cislo = prvni_sloveso(c.right)
    if cislo == 'j':
        return 'podobjednávka', False, '1. pád podle tvaru přísudku'
    if cislo == 'mn':
        return 'podobjednávky', False, 'množné číslo podle tvaru přísudku'
    if c.prev and cislo_podle_tvaru(c.prev) == 'j' and c.prev not in SUBST2:
        return 'podobjednávka', False, '1. pád podle slovesa vlevo'
    if not c.prev:
        return 'podobjednávka', False, 'začátek věty nebo buňky'
    return None


def velke(s, orig):
    return s[0].upper() + s[1:] if orig[0].isupper() else s

FORMS = re.compile(r'\b([Pp]arti(?:e|i|í|ím|emi|ích))\b')
ADJEKT = re.compile(r'\b([Pp])arti(ov\w*)\b')

def convert(text, report=None, path=''):
    out, last = [], 0
    for m in FORMS.finditer(text):
        form = m.group(1).lower()
        new, sure, rule = resolve(form, text, m.start(), m.end())
        out.append(text[last:m.start()]); out.append(velke(new, m.group(1))); last = m.end()
        if report is not None:
            report.append({'file': path, 'form': m.group(1), 'new': velke(new, m.group(1)),
                           'sure': sure, 'rule': rule,
                           'ctx': text[max(0,m.start()-55):m.end()+55].replace('\n',' ⏎ '),
                           'pos': m.start()})
    out.append(text[last:])
    text = ''.join(out)
    text = ADJEKT.sub(lambda m: m.group(1) + 'odobjednávk' + m.group(2), text)
    return text
