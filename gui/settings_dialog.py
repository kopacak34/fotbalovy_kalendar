import tkinter as tk
from tkinter import ttk, colorchooser, messagebox


class SettingsDialog(tk.Toplevel):
    """
    Dialogové okno pro nastavení vzhledu aplikace a dalších preferencí.

    Umožňuje uživateli měnit barvy různých prvků kalendáře a aplikace,
    a také nastavit počet dní dopředu pro zobrazování připomínek událostí.
    Změny lze uložit nebo zrušit, případně obnovit výchozí nastavení.
    """
    def __init__(self, parent, settings_manager, on_save_callback=None):
        """
        Inicializuje SettingsDialog.

        Args:
            parent (tk.Widget): Rodičovské okno.
            settings_manager (SettingsManager): Instance správce nastavení pro načítání
                                                a ukládání hodnot.
            on_save_callback (callable, optional): Funkce, která se zavolá po úspěšném
                                                      uložení nastavení. Výchozí je None.
        """
        super().__init__(parent)
        self.transient(parent) # Dialog bude vždy nad rodičovským oknem
        self.settings_manager = settings_manager
        self.on_save_callback = on_save_callback

        self.title("Nastavení vzhledu")
        self.resizable(False, False) # Pevná velikost okna
        self.grab_set() # Zajistí, že dialog je modální

        # Načteme všechny aktuální hodnoty nastavení pro úpravy v tomto dialogu
        self.current_settings_values = self.settings_manager.get_all_settings()

        # Proměnná pro Spinbox (musí být atributem instance, aby byla dostupná v _save_settings)
        self.reminder_days_var = tk.IntVar(
            value=self.current_settings_values.get("reminder_days_ahead",
                                                 self.settings_manager.DEFAULT_SETTINGS.get("reminder_days_ahead", 2))
        )

        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self._cancel) # Co se stane při zavření křížkem
        self.wait_window(self) # Počká, dokud se dialog nezavře

    def _create_widgets(self):
        """
        Vytvoří a uspořádá všechny widgety v dialogovém okně nastavení.
        """
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Sekce pro barvy kalendáře ---
        ttk.Label(main_frame, text="Barvy kalendáře:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        self.color_pickers_preview_labels = {} # Pro uložení labelů s náhledy barev

        # Přidání jednotlivých výběrů barev pro kalendář
        self._add_color_picker(main_frame, 1, "Den s událostí (pozadí):", "calendar_event_day_bg")
        self._add_color_picker(main_frame, 2, "Vybraný den (pozadí):", "calendar_selected_day_bg")
        self._add_color_picker(main_frame, 3, "Vybraný den s událostí (pozadí):", "calendar_selected_event_day_bg")
        self._add_color_picker(main_frame, 4, "Dny v kalendáři (písmo):", "calendar_day_fg")
        # Můžeme přidat i barvu pro normální dny, pokud je to žádoucí
        self._add_color_picker(main_frame, 4, "Normální den (pozadí):", "calendar_normal_day_bg", row_offset=1)


        # --- Sekce pro obecná nastavení vzhledu ---
        ttk.Label(main_frame, text="Obecné:", font=("Arial", 12, "bold")).grid(
            row=5, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))
        self._add_color_picker(main_frame, 6, "Pozadí aplikace:", "main_window_bg")

        # --- Sekce pro nastavení připomínek ---
        ttk.Label(main_frame, text="Připomínky:", font=("Arial", 12, "bold")).grid(
            row=7, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))

        ttk.Label(main_frame, text="Zobrazit události na:").grid(row=8, column=0, sticky=tk.W, padx=5, pady=3)

        # Spinbox pro výběr počtu dní (0 až 7)
        reminder_spinbox = ttk.Spinbox(main_frame, from_=0, to=7, textvariable=self.reminder_days_var, width=5, wrap=True, state="readonly")
        reminder_spinbox.grid(row=8, column=1, padx=5, pady=3, sticky=tk.W)
        ttk.Label(main_frame, text="dní dopředu (0 = jen dnes)").grid(row=8, column=2, sticky=tk.W, padx=5, pady=3)


        # --- Tlačítka pro ovládání dialogu ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=(20, 0))

        save_button = ttk.Button(button_frame, text="Uložit", command=self._save_settings)
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = ttk.Button(button_frame, text="Zrušit", command=self._cancel)
        cancel_button.pack(side=tk.LEFT, padx=10)

        default_button = ttk.Button(button_frame, text="Výchozí", command=self._reset_to_defaults)
        default_button.pack(side=tk.LEFT, padx=10)

    def _add_color_picker(self, parent_frame, row, label_text, setting_key, row_offset=0):
        """
        Pomocná metoda pro přidání řádku s výběrem barvy.

        Vytvoří popisek, náhled barvy a tlačítko pro výběr barvy.

        Args:
            parent_frame (ttk.Frame): Rodičovský rámec, do kterého se prvky přidají.
            row (int): Číslo řádku v mřížce `parent_frame`.
            label_text (str): Text popisku pro výběr barvy.
            setting_key (str): Klíč nastavení, který tato barva reprezentuje.
            row_offset (int): Posun řádku pro případné přidání dalšího prvku pod tento.
        """
        actual_row = row + row_offset
        ttk.Label(parent_frame, text=label_text).grid(row=actual_row, column=0, sticky=tk.W, padx=5, pady=3)

        # Získání počáteční barvy pro náhled
        initial_color_for_preview = self.current_settings_values.get(
            setting_key,
            self.settings_manager.DEFAULT_SETTINGS.get(setting_key, "#ffffff") # Výchozí bílá, pokud nic není
        )

        color_preview = tk.Label(parent_frame, text="      ", bg=initial_color_for_preview, relief=tk.SUNKEN,
                                 borderwidth=1)
        color_preview.grid(row=actual_row, column=1, padx=5, pady=3, sticky=tk.EW)

        pick_button = ttk.Button(parent_frame, text="Vybrat barvu",
                                 command=lambda sk=setting_key, cp=color_preview: self._pick_color(sk, cp))
        pick_button.grid(row=actual_row, column=2, padx=5, pady=3)

        # Uložení reference na náhledový label pro pozdější aktualizaci
        self.color_pickers_preview_labels[setting_key] = color_preview

    def _pick_color(self, setting_key, color_preview_label):
        """
        Otevře standardní dialog pro výběr barvy a aktualizuje náhled a dočasnou hodnotu.

        Args:
            setting_key (str): Klíč nastavení, pro který se barva vybírá.
            color_preview_label (tk.Label): Label zobrazující náhled barvy.
        """
        # Pro výběr barvy použijeme aktuální hodnotu z self.current_settings_values
        initial_color = self.current_settings_values.get(
            setting_key,
            self.settings_manager.DEFAULT_SETTINGS.get(setting_key) # Výchozí z SettingsManager
        )
        # Otevření dialogu pro výběr barvy
        color_code = colorchooser.askcolor(title=f"Vyberte barvu pro {setting_key}", initialcolor=initial_color)

        if color_code and color_code[1]: # color_code[1] je hex kód barvy, např. '#RRGGBB'
            # Aktualizujeme hodnotu v našem dočasném slovníku (neukládáme hned do SettingsManager)
            self.current_settings_values[setting_key] = color_code[1]
            # Aktualizujeme barvu náhledového labelu
            color_preview_label.config(bg=color_code[1])

    def _update_all_color_previews(self):
        """
        Aktualizuje všechny náhledy barev podle hodnot v `self.current_settings_values`.

        Používá se například po resetu na výchozí hodnoty.
        """
        for key, preview_label in self.color_pickers_preview_labels.items():
            color_to_set = self.current_settings_values.get(
                key,
                self.settings_manager.DEFAULT_SETTINGS.get(key, "#ffffff") # Výchozí bílá
            )
            if color_to_set: # Ujistíme se, že máme platnou barvu
                preview_label.config(bg=color_to_set)

    def _save_settings(self):
        """
        Uloží aktuálně nastavené hodnoty (z `self.current_settings_values` a `self.reminder_days_var`)
        do `SettingsManager`, zavolá `on_save_callback` (pokud existuje) a zavře dialog.
        """
        # Uložení barev a dalších nastavení, která jsou ve slovníku current_settings_values
        for key, value in self.current_settings_values.items():
            # Klíče, které nejsou pro barvy (jako reminder_days_ahead), se zde neukládají,
            # protože reminder_days_ahead se ukládá samostatně níže.
            # Můžeme zpřesnit podmínku, pokud by current_settings_values obsahovalo i jiné typy nastavení.
            if key in self.settings_manager.DEFAULT_SETTINGS: # Ukládáme jen známé klíče
                 self.settings_manager.update_setting(key, value)


        # Uložení nastavení připomínek ze Spinboxu
        self.settings_manager.update_setting("reminder_days_ahead", self.reminder_days_var.get())

        self.settings_manager.save_settings() # Fyzické uložení do souboru

        if self.on_save_callback:
            self.on_save_callback() # Zavolání callbacku pro aktualizaci GUI v hlavním okně

        self.destroy() # Zavření dialogu

    def _cancel(self):
        """
        Zavře dialog bez uložení jakýchkoli změn.
        """
        self.destroy()

    def _reset_to_defaults(self):
        """
        Obnoví hodnoty ve formuláři na výchozí (z `SettingsManager.DEFAULT_SETTINGS`)
        a aktualizuje náhledy barev a hodnotu Spinboxu.
        Samotné uložení výchozích hodnot proběhne až po kliknutí na "Uložit".
        """
        if messagebox.askyesno("Obnovit výchozí",
                               "Opravdu chcete obnovit všechna nastavení na výchozí hodnoty?\n"
                               "(Změny se projeví až po uložení)",
                               parent=self):
            # Obnovíme self.current_settings_values na kopii DEFAULT_SETTINGS
            self.current_settings_values = self.settings_manager.DEFAULT_SETTINGS.copy()
            # Aktualizujeme náhledy barev
            self._update_all_color_previews()
            # Aktualizujeme hodnotu Spinboxu
            self.reminder_days_var.set(
                self.current_settings_values.get("reminder_days_ahead",
                                                 self.settings_manager.DEFAULT_SETTINGS.get("reminder_days_ahead", 2))
            )