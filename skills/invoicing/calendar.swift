// Vypíše události z macOS Kalendáře jako JSON – zdroj stop práce pro `/invoicing recover`.
//
// Použití:  swift calendar.swift 2026-05-01 2026-08-31
//
// Čte přes EventKit, takže si vystačí s oprávněním „Kalendáře“ pro terminál a
// nepotřebuje plný přístup k disku. Události vrací včetně délky – to je důvod,
// proč je kalendář nejsilnější zdroj: hodiny se z něj neodhadují, ale čtou.

import EventKit
import Foundation

let args = CommandLine.arguments
guard args.count == 3 else {
    FileHandle.standardError.write("použití: swift calendar.swift <od YYYY-MM-DD> <do YYYY-MM-DD>\n".data(using: .utf8)!)
    exit(2)
}

let vstup = DateFormatter()
vstup.dateFormat = "yyyy-MM-dd"
vstup.timeZone = TimeZone.current
guard let od = vstup.date(from: args[1]), let doDne = vstup.date(from: args[2]) else {
    FileHandle.standardError.write("data musí být ve tvaru YYYY-MM-DD\n".data(using: .utf8)!)
    exit(2)
}
// Konec dne, ne půlnoc: schůzka od 16:00 posledního dne období by jinak vypadla.
let konec = Calendar.current.date(byAdding: .day, value: 1, to: doDne)!

let store = EKEventStore()
let hotovo = DispatchSemaphore(value: 0)
var povoleno = false
var problem: String?

store.requestFullAccessToEvents { ok, chyba in
    povoleno = ok
    problem = chyba?.localizedDescription
    hotovo.signal()
}
// Bez čekání by proces skončil dřív, než uživatel stihne dialog odklepnout.
hotovo.wait()

guard povoleno else {
    let duvod = problem ?? "přístup ke Kalendáři není povolený"
    FileHandle.standardError.write("""
    \(duvod)
    Povol ho v Nastavení systému → Soukromí a zabezpečení → Kalendáře pro svůj terminál.
    """.data(using: .utf8)!)
    exit(1)
}

// Časy se vypisují v **místním pásmu**, ne v UTC. Výchozí `ISO8601DateFormatter`
// jede na GMT, takže by se každý čas rozešel s tím, co má uživatel v kalendáři
// před očima – a porovnání se zprávou z chatu („dáme to ve 12:30“) by tiše
// nesedlo o dvě hodiny. Offset zůstává v řetězci, aby šlo poznat, čí je to čas.
let iso = ISO8601DateFormatter()
iso.formatOptions = [.withInternetDateTime]
iso.timeZone = TimeZone.current

// Mail účastníka bez `mailto:`; u zasedaček je to adresa zdroje, ne člověka.
func mail(_ u: EKParticipant) -> String {
    u.url.absoluteString.replacingOccurrences(of: "mailto:", with: "")
}

let udalosti = store.events(matching: store.predicateForEvents(withStart: od, end: konec, calendars: nil))
let vystup: [[String: Any]] = udalosti.map { e in
    // `isCurrentUser` u účtů přidaných přes CalDAV nefunguje – vrací false u všech
    // a odmítnuté schůzky by pak vypadaly jako konané. Titul kalendáře je u těchhle
    // účtů rovnou mailová adresa, takže se účast hledá podle ní a `isCurrentUser`
    // slouží jen jako záloha.
    let ja = (e.attendees ?? []).first {
        mail($0).caseInsensitiveCompare(e.calendar.title) == .orderedSame || $0.isCurrentUser
    }
    return [
        "nazev": e.title ?? "",
        "od": iso.string(from: e.startDate),
        "do": iso.string(from: e.endDate),
        // Minuty, ne sekundy: nikdo neúčtuje po vteřinách a v JSONu se to hůř čte.
        "minut": Int(e.endDate.timeIntervalSince(e.startDate) / 60),
        "celodenni": e.isAllDay,
        "kalendar": e.calendar.title,
        "misto": e.location ?? "",
        // Účastníci prozradí, komu schůzka patří, i když to není v názvu.
        "ucastnici": (e.attendees ?? []).map(mail),
        // Odmítnutá schůzka se nekonala a nálezem být nesmí.
        "odmitnuta": ja?.participantStatus == .declined,
        "poznamka": e.notes ?? "",
    ]
}

let json = try JSONSerialization.data(withJSONObject: vystup, options: [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes])
FileHandle.standardOutput.write(json)
