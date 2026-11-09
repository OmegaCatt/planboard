# PlanBoard – PB-1 až PB-10

Navazuje na schválený plán rozvoje portfolia. Cílem je ukázat rozbor provozního procesu, práci s omezeními a ověřování výsledku pro role IT konzultanta, plánování a technické analýzy.

Implementace: Python plánovač a nezávislý kontrolor, 10 fiktivních zakázek, 3 typy pracovišť, tabulkové vstupy, čtyři porovnávané scénáře, detail čekání, časová osa, CSV/JSON a SQLite historie. Přidaná kapacita je další kompatibilní pracoviště. Výsledek se přepočítává a změna vstupů jej zneplatní. Jednoduché světlé UI bez dekorativních AI prvků.

Rozhodnutí: pracovní čas používá pět 480minutových dnů, operace se nevejde přes směnu a zakázka se přijme do plánu celá. Heuristika používá prioritu, termín a ID; samostatný kontrolor nepoužívá plánovač ani vyhledávač slotů. Nezařazené zakázky zůstávají viditelné. Jiné pořadí může dát jiný výsledek.

Ověření a naměřené výsledky jsou v QA.md. Další možné rozšíření podle skutečné zpětné vazby: různé směny podle dne, přestavby, více operací a zdrojová integrace. Nepřidávat je předem jako hotové schopnosti. Veřejná služba by vyžadovala samostatnou identitu, provozní limity a další kontrolu.

PB-10: samostatný CSV přehled výsledků se znovu počítá z validovaných vstupů, zachovává nezařazené zakázky a důvody. Generační kontrola chrání nejen výpočet, ale i pomalé obnovení JSON/SQLite, import CSV a reset ukázky. Browser regrese zadržuje skutečné odpovědi výpočtu/obnovení/resetu a ověřuje zachování novější editace.
