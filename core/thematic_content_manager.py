import json
import os
import random
from datetime import date


class ThematicContentManager:
    """
    Spravuje načítání a poskytování tematického obsahu, jako jsou fotbalové tipy,
    zajímavosti, pravidla nebo historické události vztažené k aktuálnímu datu.

    Obsah je načítán z JSON souboru. Pokud soubor neexistuje nebo je neplatný,
    použije se výchozí obsah definovaný v `DEFAULT_CONTENT`.
    """
    DEFAULT_CONTENT = {
        "fotbalove_tipy": ["Nezapomeňte se před zápasem pořádně rozcvičit!"],
        "zajimavosti": [{"nadpis": "Info", "text": "Fotbal je populární sport."}],
        "pravidla_fotbalu": [{"pravidlo": "Základní pravidlo", "popis": "Hraje se s míčem."}],
        "historicke_udalosti_dne": {
            "MM-DD": {"01-01": "Nový rok, nové fotbalové výzvy!"},
            "YYYY-MM-DD": {}
        }
    }
    DEFAULT_MESSAGE = "Dnes žádné speciální fotbalové info, ale každý den je dobrý pro fotbal!"

    def __init__(self, filepath="data/thematic_content.json"):
        """
        Inicializuje ThematicContentManager.

        Načte tematický obsah ze zadaného souboru nebo použije výchozí.

        Args:
            filepath (str, optional): Cesta k souboru JSON s tematickým obsahem.
                                      Výchozí je "data/thematic_content.json".
        """
        self.filepath = filepath
        self.content = self._load_content()

    def _load_content(self):
        """
        Načte tematický obsah ze souboru JSON.

        Pokud soubor neexistuje, je prázdný, poškozený, nebo má nevalidní strukturu,
        vypíše varování/chybu a vrátí výchozí obsah (DEFAULT_CONTENT).

        Returns:
            dict: Slovník s načteným (nebo výchozím) tematickým obsahem.
        """
        if not os.path.exists(self.filepath):
            print(f"Soubor s tematickým obsahem nenalezen: {self.filepath}. Používám výchozí.")
            return self.DEFAULT_CONTENT
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            # Jednoduchá validace - kontrola existence hlavních klíčů
            if self._validate_content_structure(loaded_data):
                print("Tematický obsah úspěšně načten.")
                return loaded_data
            else:
                print("Struktura tematického obsahu v souboru je nevalidní. Používám výchozí.")
                return self.DEFAULT_CONTENT
        except (json.JSONDecodeError, IOError) as e:
            print(f"Chyba při načítání tematického obsahu z {self.filepath}: {e}. Používám výchozí.")
            return self.DEFAULT_CONTENT

    def _validate_content_structure(self, data):
        """
        Provádí základní validaci struktury načteného tematického obsahu.

        Aktuálně kontroluje pouze, zda jsou načtená data slovníkem.
        Může být rozšířena o detailnější kontroly klíčů a typů.

        Args:
            data (any): Načtená data k validaci.

        Returns:
            bool: True, pokud data projdou základní validací, jinak False.
        """
        # Očekáváme, že data jsou slovník
        if not isinstance(data, dict):
            return False
        # Můžeme přidat kontroly na existenci klíčů, které budeme používat
        # Např. if "fotbalove_tipy" not in data or not isinstance(data["fotbalove_tipy"], list): return False
        # Prozatím necháme validaci volnější, spoléháme na správný formát JSONu.
        return True

    def _format_content_item(self, item):
        """
        Formátuje jednotlivou položku tematického obsahu pro zobrazení.

        Pokud je položka řetězec, vrátí ho beze změny.
        Pokud je položka slovník, pokusí se z něj sestavit formátovaný text
        s využitím klíčů jako "nadpis", "pravidlo", "text", "popis", atd.

        Args:
            item (str | dict): Položka obsahu k formátování.

        Returns:
            str: Formátovaný řetězec pro zobrazení, nebo DEFAULT_MESSAGE v případě neúspěchu.
        """
        if isinstance(item, str):
            return item
        elif isinstance(item, dict):
            parts = []
            if "nadpis" in item:
                parts.append(f"{item['nadpis']}:")
            elif "pravidlo" in item:
                parts.append(f"Pravidlo: {item['pravidlo']}")

            if "text" in item:
                parts.append(item['text'])
            elif "popis" in item:
                parts.append(item['popis'])

            if "kdy_se_tresta" in item:
                parts.append(f"Kdy se trestá: {item['kdy_se_tresta']}")
            if "priklad" in item:
                parts.append(f"Příklad: {item['priklad']}")

            return "\n".join(parts) if parts else self.DEFAULT_MESSAGE
        return self.DEFAULT_MESSAGE

    def get_daily_info(self, today_date: date):
        """
        Získá tematickou informaci pro zadaný den.

        Prioritně hledá událost pro konkrétní rok-měsíc-den (YYYY-MM-DD).
        Pokud není nalezena, hledá událost pro měsíc-den (MM-DD) bez ohledu na rok.
        Pokud ani taková událost není nalezena, vybere náhodnou položku
        z ostatních dostupných kategorií (kromě historických událostí).

        Args:
            today_date (date): Objekt `date` reprezentující aktuální den.

        Returns:
            str: Formátovaná tematická informace pro daný den, nebo DEFAULT_MESSAGE.
        """
        specific_event_for_today = None

        # 1. Zkontroluj historické události pro konkrétní YYYY-MM-DD
        date_str_yyyy_mm_dd = today_date.strftime("%Y-%m-%d")
        if "historicke_udalosti_dne" in self.content and \
                isinstance(self.content["historicke_udalosti_dne"], dict) and \
                "YYYY-MM-DD" in self.content["historicke_udalosti_dne"] and \
                date_str_yyyy_mm_dd in self.content["historicke_udalosti_dne"]["YYYY-MM-DD"]:
            event_data = self.content["historicke_udalosti_dne"]["YYYY-MM-DD"][date_str_yyyy_mm_dd]
            specific_event_for_today = self._format_content_item(event_data)
            if specific_event_for_today != self.DEFAULT_MESSAGE:  # Pokud jsme našli platnou událost
                return f"Na dnešní den ({today_date.strftime('%d.%m.%Y')}):\n{specific_event_for_today}"

        # 2. Zkontroluj historické události pro MM-DD (pokud nebyla nalezena specifická YYYY-MM-DD)
        if not specific_event_for_today or specific_event_for_today == self.DEFAULT_MESSAGE:
            date_str_mm_dd = today_date.strftime("%m-%d")
            if "historicke_udalosti_dne" in self.content and \
                    isinstance(self.content["historicke_udalosti_dne"], dict) and \
                    "MM-DD" in self.content["historicke_udalosti_dne"] and \
                    date_str_mm_dd in self.content["historicke_udalosti_dne"]["MM-DD"]:
                event_data = self.content["historicke_udalosti_dne"]["MM-DD"][date_str_mm_dd]
                formatted_event = self._format_content_item(event_data)
                if formatted_event != self.DEFAULT_MESSAGE:
                    return f"Info k {today_date.strftime('%d.%m.')}:\n{formatted_event}"

        # 3. Pokud nic specifického pro datum, vyber náhodnou kategorii a položku
        available_categories = {
            key: value for key, value in self.content.items()
            if key != "historicke_udalosti_dne" and isinstance(value, list) and value
        }

        if not available_categories:
            return self.DEFAULT_MESSAGE

        chosen_category_key = random.choice(list(available_categories.keys()))
        chosen_item = random.choice(available_categories[chosen_category_key])

        category_title = chosen_category_key.replace("_", " ").capitalize()
        return f"{category_title}:\n{self._format_content_item(chosen_item)}"

    def get_random_info_from_category(self, category_key):
        """
        Vrátí náhodně vybranou formátovanou položku z dané kategorie.

        Kategorie musí existovat v načteném obsahu, být seznamem a nebýt prázdná.

        Args:
            category_key (str): Klíč (název) kategorie, ze které se má vybírat.

        Returns:
            str | None: Formátovaná náhodná položka z kategorie, nebo None,
                        pokud kategorie neexistuje, není seznam, nebo je prázdná.
        """
        if category_key in self.content and isinstance(self.content[category_key], list) and self.content[category_key]:
            item = random.choice(self.content[category_key])
            return self._format_content_item(item)
        return None

    def get_available_random_categories(self):
        """
        Vrátí seznam klíčů kategorií, ze kterých lze náhodně vybírat obsah.

        Vylučuje kategorii "historicke_udalosti_dne" a zahrnuje pouze kategorie,
        které jsou seznamy a nejsou prázdné.

        Returns:
            list[str]: Seznam klíčů dostupných kategorií pro náhodný výběr.
        """
        return [
            key for key, value in self.content.items()
            if key != "historicke_udalosti_dne" and isinstance(value, list) and value
        ]