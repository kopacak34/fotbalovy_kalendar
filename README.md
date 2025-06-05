# Fotbalový Kalendář

Jednoduchá desktopová aplikace pro správu fotbalových událostí, jako jsou zápasy, tréninky a další aktivity. Aplikace umožňuje uživatelům přidávat, upravovat, mazat a prohlížet události v kalendáři a v seznamu. Nabízí také tematický obsah a možnost exportu dat.

## Funkce

*   **Správa událostí:**
    *   Přidávání nových událostí (název, datum, čas, typ, detaily, štítky).
    *   Úprava existujících událostí.
    *   Odebírání událostí.
*   **Zobrazení kalendáře:**
    *   Měsíční pohled na kalendář.
    *   Vizuální zvýraznění dnů s událostmi.
    *   Možnost výběru dne pro zobrazení událostí daného dne.
    *   Navigace mezi měsíci.
*   **Seznam událostí:**
    *   Zobrazení seznamu událostí.
    *   Filtrování událostí podle data (výběrem v kalendáři), typu události a štítků.
    *   Možnost zobrazení všech událostí.
*   **Detaily události:**
    *   Zobrazení podrobných informací o vybrané události.
*   **Tematický obsah:**
    *   Zobrazení "Fotbalového infa dne" – historické události, tipy, zajímavosti nebo pravidla.
    *   Možnost obnovit info dne nebo zobrazit další náhodný tematický obsah.
*   **Nastavení vzhledu:**
    *   Uživatelské přizpůsobení barev kalendáře (den s událostí, vybraný den, písmo).
    *   Nastavení barvy pozadí aplikace.
    *   Nastavení počtu dní dopředu pro připomínky nadcházejících událostí.
*   **Připomínky:**
    *   Automatické upozornění na nadcházející události při startu aplikace.
*   **Export dat:**
    *   Export seznamu událostí do formátu CSV.
    *   Export seznamu událostí do formátu PDF (vyžaduje knihovnu ReportLab).
*   **Perzistence dat:**
    *   Události a uživatelská nastavení jsou ukládána lokálně v JSON souborech.

## Struktura projektu
fotbalovy_kalendar/ ├── core/                   # Hlavní logika aplikace │   ├── data_handler.py │   ├── event.py │   ├── event_manager.py │   ├── pdf_exporter.py │   ├── settings_manager.py │   └── thematic_content_manager.py ├── data/                   # Datové soubory (generované aplikací) │   ├── events.json │   ├── settings.json │   └── thematic_content.json # Příklad souboru s tematickým obsahem ├── gui/                    # Grafické uživatelské rozhraní │   ├── calendar_widget.py │   ├── event_dialog.py │   ├── event_list_panel.py │   ├── main_window.py │   └── settings_dialog.py ├── vendor/                 # Složka pro externí knihovny (např. ReportLab) │   └── reportlab/          # (pokud je ReportLab přidán manuálně) └── main.py                 # Hlavní spouštěcí skript aplikace


## Instalace a spuštění

1.  **Požadavky:**
    *   Python 3.x
    *   Knihovna Tkinter (obvykle součástí standardní instalace Pythonu).
    *   Pro export do PDF je vyžadována knihovna `reportlab`.
        *   Pokud není nainstalována globálně (`pip install reportlab`), ujistěte se, že je umístěna ve složce `vendor/reportlab/` v kořenovém adresáři projektu. Skripty jsou nastaveny tak, aby se pokusily importovat knihovnu z této složky.

2.  **Spuštění aplikace:**
    *   Přejděte do kořenového adresáře projektu `fotbalovy_kalendar`.
    *   Spusťte hlavní skript:
        