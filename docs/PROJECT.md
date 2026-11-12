# Snadné vyzkoušení - 12. 11. 2026

Základní Windows návod je na začátku README; řešení potíží a volitelné předpoklady v docs/SPUSTENI.md. Netechnický návštěvník může začít existující veřejnou ukázkou. Ověření čisté kopie a hranice testu jsou v docs/QA.md. Jádro aplikace se touto dokumentační úpravou nemění.

# UX-1 až UX-7 – 11. 11. 2026

Operace se v rozhraní zobrazují česky: Řezání, Montáž a Balení. Strojové klíče cut/assembly/pack v JSON/CSV zůstávají stabilní kvůli kompatibilitě. Vlastní neznámé názvy se zobrazí tak, jak byly zadané.

Všech sedm aplikací má první přístupný dialog a stálé ovládání nápovědy v hlavičce. Playwright ověřuje skutečný první vstup, obě části, GitHub odkaz, Tab/Shift+Tab, Escape, návrat fokusu, potvrzení po reloadu a mobil. CompanyAtlas čeká s přihlášením na zavření úvodu; hlavička se testuje po přihlášení. Legacy pracovní průchody pokračují po skutečném zavření úvodu. Aktuální commit, CI a přesný rozsah ověření této etapy jsou vedené v hlavním Portfolio_PROGRESS.md; starší zápisy níže jsou historické.

# Aktuální rozsah a kontrola 10. 11. 2026

Aktuální funkce, technologie, API, způsob použití, firemní zavedení a omezení jsou v [README](../README.md). Znovu prošlo 16 Python testů a odpovídající skutečný browser průchod desktop/mobil. Jde o fiktivní portfolio projekt. Výsledky a případné opravy jsou v [QA](QA.md).

Předchozí ověřený kód bf4e96d: [úspěšné GitHub Actions](https://github.com/OmegaCatt/planboard/actions/runs/42687367558). Nový commit této revize má vlastní CI; aktuální stav je v hlavním protokolu portfolia. Níže uvedené historické plány nejsou seznam nehotových funkcí.

<details>
<summary>Historická projektová rozhodnutí a průběžné etapy</summary>

# PlanBoard – PB-1 až PB-10

Navazuje na schválený plán rozvoje portfolia. Cílem je ukázat rozbor provozního procesu, práci s omezeními a ověřování výsledku pro role IT konzultanta, plánování a technické analýzy.

Implementace: Python plánovač a nezávislý kontrolor, 10 fiktivních zakázek, 3 typy pracovišť, tabulkové vstupy, čtyři porovnávané scénáře, detail čekání, časová osa, CSV/JSON a SQLite historie. Přidaná kapacita je další kompatibilní pracoviště. Výsledek se přepočítává a změna vstupů jej zneplatní. Jednoduché světlé UI bez dekorativních AI prvků.

Rozhodnutí: pracovní čas používá pět 480minutových dnů, operace se nevejde přes směnu a zakázka se přijme do plánu celá. Heuristika používá prioritu, termín a ID; samostatný kontrolor nepoužívá plánovač ani vyhledávač slotů. Nezařazené zakázky zůstávají viditelné. Jiné pořadí může dát jiný výsledek.

Ověření a naměřené výsledky jsou v QA.md. Další možné rozšíření podle skutečné zpětné vazby: různé směny podle dne, přestavby, více operací a zdrojová integrace. Nepřidávat je předem jako hotové schopnosti. Veřejná služba by vyžadovala samostatnou identitu, provozní limity a další kontrolu.

PB-10: samostatný CSV přehled výsledků se znovu počítá z validovaných vstupů, zachovává nezařazené zakázky a důvody. Generační kontrola chrání nejen výpočet, ale i pomalé obnovení JSON/SQLite, import CSV a reset ukázky. Browser regrese zadržuje skutečné odpovědi výpočtu/obnovení/resetu a ověřuje zachování novější editace.


</details>
