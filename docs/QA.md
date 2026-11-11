# Regrese UX-1b – rychlé zavření a reload

První Linux main CI odhalilo závod: potvrzení úvodu v události close se někdy nestihlo zapsat před reloadem. Nyní se zapisuje synchronně v Escape/cancel a tlačítkách před zavřením; close je záložní cesta. Původní neúspěšný běh zůstává v Actions. Browser test stále provádí okamžitý reload, očekávání nebylo oslabeno ani přidán čekací čas.

# UX-1 až UX-7 – 11. 11. 2026

Místně ověřené unit testy: **16 Python**.

Operace se v rozhraní zobrazují česky: Řezání, Montáž a Balení. Strojové klíče cut/assembly/pack v JSON/CSV zůstávají stabilní kvůli kompatibilitě. Vlastní neznámé názvy se zobrazí tak, jak byly zadané.

Všech sedm aplikací má první přístupný dialog a stálé ovládání nápovědy v hlavičce. Playwright ověřuje skutečný první vstup, obě části, GitHub odkaz, Tab/Shift+Tab, Escape, návrat fokusu, potvrzení po reloadu a mobil. CompanyAtlas čeká s přihlášením na zavření úvodu; hlavička se testuje po přihlášení. Legacy pracovní průchody pokračují po skutečném zavření úvodu. Aktuální commit, CI a přesný rozsah ověření této etapy jsou vedené v hlavním Portfolio_PROGRESS.md; starší zápisy níže jsou historické.

# Opakované ověření 10. 11. 2026

**16 Python testů prošlo.** Znovu spuštěné prohlížečové QA ověřilo skutečný pracovní postup na dočasných fiktivních podkladech, desktop i mobil a JavaScript chyby. Nová kontrola zopakovala běžné i připravené chybové toky. Původní počet testů zůstává beze změny.

Ověřený předchozí commit bf4e96d: [GitHub Actions](https://github.com/OmegaCatt/planboard/actions/runs/42687367558); dostupnost jeho artefaktů byla ověřena. Aktuální revize dokumentace/oprav je kontrolována novým CI. Jeho přesný commit a výsledek jsou v hlavním Portfolio_PROGRESS.md. Staré věty o čekající publikaci v rozbaleném archivu platily jen pro dobu daného zápisu.

<details>
<summary>Historické výsledky, původní metriky a omezení</summary>

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


</details>
