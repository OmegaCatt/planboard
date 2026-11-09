# Ověření 9. 11. 2026

## Automatické testy

16 Python unittest testů prošlo. Pokrytí: známý malý plán, pořadí podle priority, nepřerušování operace přes směnu, návaznosti, sjednocení překrývajících se výpadků, nulová kapacita, odvolání částečně rozplánované zakázky, čtyři scénáře, neměnnost vstupů, poškozené výsledky a metriky, vysvětlení čekání, CSV a 30 deterministicky generovaných sad. HTTP testy ověřují skutečný výpočet, SQLite historii/mazání, Host/Origin, limit požadavku, neplatnou verzi a nepřístupnost serverových souborů.

## Browser QA

Playwright/Edge, desktop 1440 × 1000 a mobilní šířka 390 px. Prošly čtyři skutečné scénáře, detail operace, uložení do SQLite, návrat k příkladu a obnovení historie, změna kapacity s vymazáním výsledku, viditelné nezařazené zakázky, JSON a CSV průchod, výsledný CSV včetně nezařazených a ochrany textu před vzorci, záměrně zadržené odpovědi výpočtu/obnovení/resetu proti novější editaci, kompaktní řádky na mobilu a nulový počet JavaScript chyb.

Vizuální kontrola odhalila úzké tlačítko Odebrat na mobilu: zalamovalo se po písmenech a zvětšovalo řádek na 158 px. Opraveno minimální šířkou; regrese kontroluje řádky pod 80 px a nepřetékání celé stránky. Tabulky a graf se posouvají uvnitř svého panelu. Aktuální obrázky: preview.png, timeline.png, mobile.png.

## Výsledky fiktivní sady

| Scénář | Zakázky | Nezařazené | Pozdní | Součet zpoždění (pracovní minuty) |
|---|---:|---:|---:|---:|
| Základ | 10 | 0 | 6 | 1800 |
| Výpadek | 10 | 0 | 6 | 2790 |
| Urgentní | 11 | 0 | 7 | 2670 |
| Paralelní kapacita | 10 | 0 | 0 | 0 |

Jednorázové místní měření porovnání pro 200 zakázek: 16,02 ms, 185 nezařazených kvůli záměrně přetíženému pětidennímu horizontu. Měření závisí na zařízení a není kapacitní příslib.

## Hranice

Testy neprokazují globální optimálnost ani úplnou bezpečnost. Nezařazení heuristikou neprokazuje neexistenci jiného pořadí. Model nepokrývá materiál, přestavby strojů, svátky, víkendy, práci přes směnu ani skutečné ERP. SQLite a API jsou místní bez firemního přihlášení. Veřejná běžící služba není nasazená. GitHub Actions ověřily commit bc8541c úspěšně: https://github.com/OmegaCatt/planboard/actions/runs/42683993618.
