import json
import os


class SettingsManager:
    """
    Spravuje načítání a ukládání uživatelských nastavení aplikace.

    Nastavení jsou uložena v souboru JSON. Třída poskytuje výchozí
    hodnoty pro případ, že soubor s nastaveními neexistuje nebo je poškozen.
    Umožňuje získat, aktualizovat a resetovat jednotlivá nastavení.
    """
    DEFAULT_SETTINGS = {
        "calendar_event_day_bg": "lightblue",
        "calendar_selected_day_bg": "yellow",
        "calendar_selected_event_day_bg": "orange",
        "calendar_day_fg": "black",
        "main_window_bg": "#e0e0e0",
        "reminder_days_ahead": 2
    }

    def __init__(self, filepath="data/settings.json"):
        """
        Inicializuje SettingsManager.

        Načte nastavení ze zadaného souboru nebo použije výchozí.

        Args:
            filepath (str, optional): Cesta k souboru JSON s nastaveními.
                                      Výchozí je "data/settings.json".
        """
        self.filepath = filepath
        self.settings = self._load_settings()

    def _load_settings(self):
        """
        Načte nastavení ze souboru JSON.

        Pokud soubor neexistuje nebo dojde k chybě při čtení/parsování,
        vrátí kopii výchozích nastavení (DEFAULT_SETTINGS).
        Načtená nastavení jsou sloučena s výchozími, aby byla zajištěna
        existence všech očekávaných klíčů.

        Returns:
            dict: Slovník s načtenými (nebo výchozími) nastaveními.
        """
        if not os.path.exists(self.filepath):
            print(f"Soubor s nastaveními nenalezen: {self.filepath}. Používám výchozí.")
            return self.DEFAULT_SETTINGS.copy()
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                # Zajistíme, že všechny klíče z DEFAULT_SETTINGS existují
                settings = self.DEFAULT_SETTINGS.copy()
                settings.update(loaded_settings)  # Přepíše výchozí hodnoty načtenými, pokud existují
                return settings
        except (json.JSONDecodeError, IOError) as e:
            print(f"Chyba při načítání nastavení z {self.filepath}: {e}. Používám výchozí.")
            return self.DEFAULT_SETTINGS.copy()

    def save_settings(self):
        """
        Uloží aktuální nastavení do souboru JSON.

        Pokud adresář pro uložení neexistuje, pokusí se ho vytvořit.
        Nastavení jsou uložena s odsazením pro lepší čitelnost.

        Returns:
            bool: True, pokud byla nastavení úspěšně uložena, jinak False.
        """
        try:
            data_dir = os.path.dirname(self.filepath)
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            print(f"Nastavení uložena do {self.filepath}")
            return True
        except IOError as e:
            print(f"Chyba při ukládání nastavení do {self.filepath}: {e}")
            return False

    def get_setting(self, key):
        """
        Vrátí hodnotu nastavení pro daný klíč.

        Pokud klíč v aktuálních nastaveních neexistuje, vrátí hodnotu
        z výchozích nastavení (DEFAULT_SETTINGS). Pokud ani tam klíč není,
        vrátí None (což by nemělo nastat, pokud se používají pouze klíče
        definované v DEFAULT_SETTINGS).

        Args:
            key (str): Klíč požadovaného nastavení.

        Returns:
            any: Hodnota nastavení, nebo None.
        """
        return self.settings.get(key, self.DEFAULT_SETTINGS.get(key))

    def update_setting(self, key, value):
        """
        Aktualizuje hodnotu nastavení pro daný klíč.

        Aktualizace je povolena pouze pro klíče, které jsou definovány
        ve výchozích nastaveních (DEFAULT_SETTINGS), aby se zabránilo
        ukládání neznámých/nechtěných nastavení.

        Args:
            key (str): Klíč nastavení k aktualizaci.
            value (any): Nová hodnota nastavení.
        """
        if key in self.DEFAULT_SETTINGS:  # Povolíme aktualizaci jen pro známé klíče
            self.settings[key] = value
        else:
            print(f"Varování: Pokus o aktualizaci neznámého nastavení '{key}'")

    def get_all_settings(self):
        """
        Vrátí kopii všech aktuálních nastavení.

        Returns:
            dict: Kopie slovníku s aktuálními nastaveními.
        """
        return self.settings.copy()

    def reset_to_defaults(self):
        """
        Obnoví všechna nastavení na výchozí hodnoty (DEFAULT_SETTINGS).

        Po obnovení jsou výchozí nastavení ihned uložena do souboru.
        """
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save_settings()  # Uložíme výchozí nastavení