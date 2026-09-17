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

let inputFormat = DateFormatter()
inputFormat.dateFormat = "yyyy-MM-dd"
// `en_US_POSIX` schválně, i když jde o česká data: bez pevného locale čte
// DateFormatter pevný formát kalendářem uživatele, takže v locale s jiným než
// gregoriánským kalendářem (thajský buddhistický, japonský) vyjde jiný rok.
// Je to doporučený postup Applu pro formát, který se nemá řídit uživatelem.
inputFormat.locale = Locale(identifier: "en_US_POSIX")
inputFormat.timeZone = TimeZone.current
guard let startDay = inputFormat.date(from: args[1]), let endDay = inputFormat.date(from: args[2]) else {
    FileHandle.standardError.write("data musí být ve tvaru YYYY-MM-DD\n".data(using: .utf8)!)
    exit(2)
}
// Konec dne, ne půlnoc: schůzka od 16:00 posledního dne období by jinak vypadla.
let periodEnd = Calendar.current.date(byAdding: .day, value: 1, to: endDay)!

let store = EKEventStore()
let accessDone = DispatchSemaphore(value: 0)
var granted = false
var problem: String?

store.requestFullAccessToEvents { ok, error in
    granted = ok
    problem = error?.localizedDescription
    accessDone.signal()
}
// Bez čekání by proces skončil dřív, než uživatel stihne dialog odklepnout.
accessDone.wait()

guard granted else {
    let reason = problem ?? "přístup ke Kalendáři není povolený"
    FileHandle.standardError.write("""
    \(reason)
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

let events = store.events(matching: store.predicateForEvents(withStart: startDay, end: periodEnd, calendars: nil))
let output: [[String: Any]] = events.map { e in
    // `isCurrentUser` u účtů přidaných přes CalDAV nefunguje – vrací false u všech
    // a odmítnuté schůzky by pak vypadaly jako konané. Titul kalendáře je u těchhle
    // účtů rovnou mailová adresa, takže se účast hledá podle ní a `isCurrentUser`
    // slouží jen jako záloha.
    let me = (e.attendees ?? []).first {
        mail($0).caseInsensitiveCompare(e.calendar.title) == .orderedSame || $0.isCurrentUser
    }
    return [
        "title": e.title ?? "",
        "start": iso.string(from: e.startDate),
        "end": iso.string(from: e.endDate),
        // Minuty, ne sekundy: nikdo neúčtuje po vteřinách a v JSONu se to hůř čte.
        "minutes": Int(e.endDate.timeIntervalSince(e.startDate) / 60),
        "all_day": e.isAllDay,
        "calendar": e.calendar.title,
        "location": e.location ?? "",
        // Účastníci prozradí, komu schůzka patří, i když to není v názvu.
        "attendees": (e.attendees ?? []).map(mail),
        // Odmítnutá schůzka se nekonala a nálezem být nesmí.
        "declined": me?.participantStatus == .declined,
        "notes": e.notes ?? "",
    ]
}

let json = try JSONSerialization.data(withJSONObject: output, options: [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes])
FileHandle.standardOutput.write(json)
