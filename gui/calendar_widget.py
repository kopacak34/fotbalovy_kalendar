import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime, date, timedelta


class CalendarWidget(ttk.Frame):
    """
    Widget zobrazující měsíční kalendář s možností výběru dne a zvýraznění událostí.

    Umožňuje navigaci mezi měsíci, výběr konkrétního dne a vizuální
    odlišení dnů s událostmi, vybraného dne a vybraného dne s událostí
    na základě uživatelských nastavení barev.
    """
    def __init__(self, master=None, event_manager=None, on_date_select_callback=None, initial_settings=None):
        """
        Inicializuje CalendarWidget.

        Args:
            master (tk.Widget, optional): Rodičovský widget. Výchozí je None.
            event_manager (EventManager, optional): Instance správce událostí pro zjišťování,
                                                   které dny mají události. Výchozí je None.
            on_date_select_callback (callable, optional): Funkce, která se zavolá při výběru data.
                                                          Předá vybraný objekt `date` nebo None.
                                                          Výchozí je None.
            initial_settings (dict, optional): Slovník s počátečním nastavením vzhledu
                                               (barvy kalendáře). Výchozí je None.
        """
        super().__init__(master)
        self.event_manager = event_manager
        self.on_date_select_callback = on_date_select_callback
        self.settings = initial_settings if initial_settings is not None else {}

        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self._selected_button = None # Odkaz na aktuálně vybrané tk.Button dne
        self._day_buttons = {}     # Slovník {date_obj: tk.Button} pro tlačítka dnů

        self._create_widgets()
        self.display_calendar()

    def apply_new_settings(self, new_settings):
        """
        Aplikuje nová nastavení vzhledu a překreslí kalendář.

        Args:
            new_settings (dict): Slovník s novými hodnotami nastavení.
                                 Očekávají se klíče pro barvy kalendáře.
        """
        self.settings = new_settings if new_settings is not None else {}
        self.display_calendar() # Překreslí kalendář s novými barvami

    def _create_widgets(self):
        """
        Vytvoří základní GUI prvky kalendáře (navigační tlačítka, popisky).
        """
        self.nav_frame = ttk.Frame(self)
        self.nav_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        self.prev_month_button = ttk.Button(self.nav_frame, text="<", command=self._prev_month, width=4)
        self.prev_month_button.pack(side=tk.LEFT, padx=(0, 5))

        self.month_year_label = ttk.Label(self.nav_frame, text="", anchor=tk.CENTER, font='TkDefaultFont 10 bold')
        self.month_year_label.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.next_month_button = ttk.Button(self.nav_frame, text=">", command=self._next_month, width=4)
        self.next_month_button.pack(side=tk.RIGHT, padx=(5, 0))

        # Rámec pro mřížku dnů kalendáře
        self.calendar_grid_frame = ttk.Frame(self)
        self.calendar_grid_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Hlavička s názvy dnů v týdnu
        weekdays = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
        for i, day_name in enumerate(weekdays):
            label = ttk.Label(self.calendar_grid_frame, text=day_name, anchor=tk.CENTER, font='TkDefaultFont 9 bold')
            label.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)

        # Nastavení váhy sloupců pro responzivní chování
        for i in range(7):
            self.calendar_grid_frame.grid_columnconfigure(i, weight=1)

    def display_calendar(self):
        """
        Zobrazí (nebo překreslí) mřížku kalendáře pro aktuálně nastavený měsíc a rok.

        Odstraní stará tlačítka dnů, vygeneruje nová pro aktuální měsíc
        a aplikuje na ně styly pomocí `update_display`.
        """
        # Odstranění starých tlačítek dnů (pokud existují)
        for widget in self.calendar_grid_frame.winfo_children():
            if widget.grid_info()['row'] > 0: # Nechceme odstranit hlavičku s názvy dnů
                widget.destroy()
        self._day_buttons = {}
        self._selected_button = None

        month_name_cz = ["Leden", "Únor", "Březen", "Duben", "Květen", "Červen", "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"]
        self.month_year_label.config(text=f"{month_name_cz[self.current_month-1]} {self.current_year}")


        cal = calendar.Calendar()
        # Nastaví pondělí jako první den týdne
        cal.setfirstweekday(calendar.MONDAY)
        month_days_grid = cal.monthdayscalendar(self.current_year, self.current_month)

        current_row = 1 # Začínáme na řádku 1 (řádek 0 je pro názvy dnů)
        for week_data in month_days_grid:
            self.calendar_grid_frame.grid_rowconfigure(current_row, weight=1)
            for col_index, day_number in enumerate(week_data):
                if day_number != 0: # 0 znamená den mimo aktuální měsíc
                    day_date_obj = date(self.current_year, self.current_month, day_number)
                    day_str_display = str(day_number)

                    # Používáme tk.Button pro snadnější nastavení barev pozadí/popředí
                    day_button = tk.Button(self.calendar_grid_frame, text=day_str_display,
                                           relief=tk.FLAT, # Plochý vzhled
                                           borderwidth=1,
                                           command=lambda d_obj=day_date_obj: self._on_day_click(d_obj),
                                           width=4) # Šířka v textových jednotkách
                    day_button.grid(row=current_row, column=col_index, sticky="nsew", padx=1, pady=1)
                    self._day_buttons[day_date_obj] = day_button
            current_row += 1

        self.update_display() # Aplikuje barvy na nově vytvořená tlačítka

    def _prev_month(self):
        """
        Přepne kalendář na předchozí měsíc a překreslí ho.
        Zavolá `on_date_select_callback` s hodnotou None.
        """
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.display_calendar()
        if self.on_date_select_callback:
            self.on_date_select_callback(None) # Zruší výběr data v externím pohledu

    def _next_month(self):
        """
        Přepne kalendář na následující měsíc a překreslí ho.
        Zavolá `on_date_select_callback` s hodnotou None.
        """
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.display_calendar()
        if self.on_date_select_callback:
            self.on_date_select_callback(None) # Zruší výběr data v externím pohledu

    def _on_day_click(self, selected_date_obj):
        """
        Obsluha události kliknutí na tlačítko dne v kalendáři.

        Aktualizuje vizuální styl vybraného tlačítka a předchozího vybraného tlačítka.
        Zavolá `on_date_select_callback` s nově vybraným datem.

        Args:
            selected_date_obj (date): Objekt `date` reprezentující den, na který bylo kliknuto.
        """
        # Zrušení stylu předchozího vybraného tlačítka
        if self._selected_button:
            previous_date = None
            for d, btn in self._day_buttons.items():
                if btn == self._selected_button:
                    previous_date = d
                    break
            if previous_date:
                self._apply_button_style(self._selected_button, previous_date, is_selected=False)

        # Nastavení nového vybraného tlačítka
        clicked_button = self._day_buttons.get(selected_date_obj)
        if clicked_button:
            self._selected_button = clicked_button
            self._apply_button_style(self._selected_button, selected_date_obj, is_selected=True)

        if self.on_date_select_callback:
            self.on_date_select_callback(selected_date_obj)

    def _apply_button_style(self, button, day_date_obj, is_selected):
        """
        Aplikuje barvy (pozadí a popředí) na dané tlačítko dne.

        Barvy jsou určeny na základě toho, zda den obsahuje událost,
        zda je vybraný, a na základě uživatelských nastavení.

        Args:
            button (tk.Button): Tlačítko dne, na které se má styl aplikovat.
            day_date_obj (date): Objekt `date` reprezentující den tlačítka.
            is_selected (bool): True, pokud je tento den aktuálně vybraný.
        """
        if not button:
            return

        has_event = False
        if self.event_manager:
             events_on_day = self.event_manager.get_events_for_date(day_date_obj)
             has_event = bool(events_on_day)

        # Načtení barev z nastavení s výchozími hodnotami
        default_fg = self.settings.get("calendar_day_fg", "black")
        event_bg = self.settings.get("calendar_event_day_bg", "lightblue")
        selected_bg = self.settings.get("calendar_selected_day_bg", "yellow")
        selected_event_bg = self.settings.get("calendar_selected_event_day_bg", "orange")
        normal_day_bg = self.settings.get("calendar_normal_day_bg", "white") # Přidáno pro normální dny

        fg_color = default_fg

        if is_selected:
            bg_color = selected_event_bg if has_event else selected_bg
        elif has_event:
            bg_color = event_bg
        else:
            bg_color = normal_day_bg # Použije barvu pro normální den

        button.config(fg=fg_color, bg=bg_color)

    def update_display(self):
        """
        Aktualizuje vzhled všech tlačítek dnů v kalendáři.

        Projde všechna zobrazená tlačítka dnů a aplikuje na ně správný styl
        pomocí `_apply_button_style` na základě jejich aktuálního stavu
        (vybraný, má událost atd.) a aktuálních nastavení.
        Tato metoda je volána po `display_calendar` a také externě,
        když se změní data událostí nebo nastavení.
        """
        # Není potřeba znovu načítat event_dates_set, protože _apply_button_style
        # si pro každý den zjišťuje události individuálně.
        # To je sice méně efektivní, pokud by se volalo velmi často pro mnoho dní,
        # ale pro překreslení celého měsíce je to přijatelné a zjednodušuje logiku.

        for day_date_obj, button in self._day_buttons.items():
            is_selected = (button == self._selected_button)
            self._apply_button_style(button, day_date_obj, is_selected)

    def get_selected_date(self):
        """
        Vrací aktuálně vybrané datum v kalendáři.

        Returns:
            date | None: Objekt `date` reprezentující vybraný den,
                         nebo None, pokud žádný den není vybrán.
        """
        if self._selected_button:
            for d_obj, btn in self._day_buttons.items():
                if btn == self._selected_button:
                    return d_obj
        return None
