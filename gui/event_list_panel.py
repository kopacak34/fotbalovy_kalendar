import tkinter as tk
from tkinter import ttk


class EventListPanel(ttk.Frame):
    """
        Panel pro zobrazení seznamu událostí s možnostmi filtrování a správy.

        Obsahuje Listbox pro zobrazení událostí, ovládací prvky pro filtrování
        podle typu události a štítku, a tlačítka pro přidání, úpravu a odebrání
        událostí. Komunikuje s hlavním oknem (nebo jiným rodičem) pomocí
        slovníku `callbacks`.
        """
    def __init__(self, master, event_manager, callbacks):
        """
                Inicializuje EventListPanel.

                Args:
                    master (tk.Widget): Rodičovský widget.
                    event_manager (EventManager): Instance správce událostí pro získávání
                                                  a filtrování dat událostí.
                    callbacks (dict): Slovník callback funkcí pro interakci s rodičovským
                                      widgetem. Očekávané klíče:
                                      'open_add_event': Funkce pro otevření dialogu pro přidání události.
                                      'open_edit_event': Funkce pro otevření dialogu pro úpravu události (přijímá ID).
                                      'remove_event': Funkce pro odebrání události (přijímá ID).
                                      'update_event_details': Funkce pro aktualizaci zobrazení detailů události (přijímá text).
        """
        super().__init__(master, style="LeftPanel.TFrame")
        self.event_manager = event_manager
        self.callbacks = callbacks

        self.active_listbox_event_ids = []
        self._current_event_filter = {}

        self._create_widgets()

    def _create_widgets(self):
        """
                Vytvoří a uspořádá všechny widgety v panelu.
        """
        container_frame = ttk.Frame(self)
        container_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        filter_frame = ttk.Frame(container_frame)
        filter_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        ttk.Label(filter_frame, text="Filtr typu:").pack(side=tk.LEFT, padx=(0, 5))
        self.event_type_filter_var = tk.StringVar()
        event_types = ["Všechny typy"] + ["Zápas (Ligový)", "Zápas (Pohár)", "Zápas (Přátelský)", "Trénink",
                                          "Sledování TV", "Schůzka", "Jiné"]
        self.event_type_filter_combo = ttk.Combobox(filter_frame, textvariable=self.event_type_filter_var,
                                                    values=event_types, state="readonly", width=12)
        self.event_type_filter_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.event_type_filter_combo.set("Všechny typy")
        self.event_type_filter_combo.bind("<<ComboboxSelected>>", self._apply_filter_gui_event)

        ttk.Label(filter_frame, text="Štítek:").pack(side=tk.LEFT, padx=(5, 5))
        self.tag_filter_entry = ttk.Entry(filter_frame, width=10)
        self.tag_filter_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.tag_filter_entry.bind("<Return>", self._apply_filter_gui_event)

        show_all_button = ttk.Button(filter_frame, text="Vše", command=self.show_all_events_in_list)
        show_all_button.pack(side=tk.LEFT, padx=(5, 0))

        self.events_listbox_frame = ttk.LabelFrame(container_frame, text="Události")
        self.events_listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.events_listbox = tk.Listbox(self.events_listbox_frame, height=8)
        self.events_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.events_listbox.bind('<<ListboxSelect>>', self._on_event_select_in_listbox)

        scrollbar = ttk.Scrollbar(self.events_listbox_frame, orient=tk.VERTICAL, command=self.events_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.events_listbox.config(yscrollcommand=scrollbar.set)

        buttons_frame_list = ttk.Frame(self)
        buttons_frame_list.pack(fill=tk.X, pady=(5, 0))

        add_event_button = ttk.Button(buttons_frame_list, text="Přidat", command=self.callbacks['open_add_event'])
        add_event_button.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        self.edit_event_button = ttk.Button(buttons_frame_list, text="Upravit", command=self._handle_edit_request,
                                            state=tk.DISABLED)
        self.edit_event_button.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        self.remove_event_button = ttk.Button(buttons_frame_list, text="Odebrat", command=self._handle_remove_request,
                                              state=tk.DISABLED)
        self.remove_event_button.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

    def _handle_edit_request(self):
        """
                Zpracuje požadavek na úpravu vybrané události.
                Získá ID vybrané události a zavolá příslušný callback.
        """
        selected_id = self._get_selected_event_id()
        if selected_id and 'open_edit_event' in self.callbacks:
            self.callbacks['open_edit_event'](selected_id)

    def _handle_remove_request(self):
        """
                Zpracuje požadavek na odebrání vybrané události.
                Získá ID vybrané události a zavolá příslušný callback.
        """
        selected_id = self._get_selected_event_id()
        if selected_id and 'remove_event' in self.callbacks:
            self.callbacks['remove_event'](selected_id)

    def _get_selected_event_id(self):
        """
                Získá ID události aktuálně vybrané v listboxu.

                Returns:
                    str | None: ID vybrané události, nebo None, pokud nic není vybráno
                                nebo pokud výběr neodpovídá platnému ID.
        """
        selected_indices = self.events_listbox.curselection()
        if not selected_indices:
            return None
        selected_index = selected_indices[0]
        if 0 <= selected_index < len(self.active_listbox_event_ids):
            return self.active_listbox_event_ids[selected_index]
        return None

    def _apply_filter_gui_event(self, event=None):
        """
                Aplikuje filtry na základě aktuálních hodnot z GUI prvků (Combobox, Entry).
                Poté obnoví seznam událostí.

                Args:
                    event (tk.Event, optional): Událost, která metodu spustila (např. výběr z Comboboxu).
                                                Není přímo využívána, ale je vyžadována signaturou bind.
        """
        selected_type = self.event_type_filter_var.get()
        tag_query = self.tag_filter_entry.get().strip()
        self._current_event_filter['event_type_filter'] = selected_type if selected_type != "Všechny typy" else None
        self._current_event_filter['tag_filter'] = tag_query if tag_query else None
        self.refresh_event_list()

    def filter_by_date(self, date_obj):
        """
                Nastaví nebo zruší filtr podle data a obnoví seznam událostí.
                Při nastavení data resetuje ostatní filtry (typ, štítek).

                Args:
                    date_obj (date | None): Objekt `date` pro filtrování, nebo None pro zrušení
        """
        if date_obj:
            self.event_type_filter_var.set("Všechny typy")
            self.tag_filter_entry.delete(0, tk.END)
            self._current_event_filter = {'date_filter': date_obj}
        else:
            self._current_event_filter = {}
        self.refresh_event_list()

    def show_all_events_in_list(self):
        """
                Zobrazí všechny události v listboxu. Resetuje všechny aktivní filtry
                a obnoví seznam.
        """
        self.event_type_filter_var.set("Všechny typy")
        self.tag_filter_entry.delete(0, tk.END)
        self._current_event_filter = {}
        self.refresh_event_list()
        self.events_listbox_frame.config(text="Všechny události")

    def refresh_event_list(self):
        """
                Obnoví obsah listboxu událostí na základě aktuálně nastavených filtrů.

                Získá události z `event_manager` pomocí `get_events_by_filter`,
                seřadí je, vloží do listboxu a aktualizuje stav tlačítek
                a titulek LabelFrame.
        """
        self.events_listbox.delete(0, tk.END)
        self.active_listbox_event_ids.clear()

        events_to_display = self.event_manager.get_events_by_filter(**self._current_event_filter)

        if self._current_event_filter.get('date_filter'):
            events_to_display.sort(key=lambda e: e.time_str if e.time_str else "24:00")
        else:
            events_to_display.sort(key=lambda e: (e.date, e.time_str if e.time_str else "24:00"))

        filter_description_parts = []
        if self._current_event_filter.get('date_filter'):
            date_filter = self._current_event_filter['date_filter']
            filter_description_parts.append(f"pro {date_filter.strftime('%d.%m.%Y')}")
        if self._current_event_filter.get('event_type_filter'):
            filter_description_parts.append(f"typ '{self._current_event_filter['event_type_filter']}'")
        if self._current_event_filter.get('tag_filter'):
            filter_description_parts.append(f"štítek '{self._current_event_filter['tag_filter']}'")

        if filter_description_parts:
            self.events_listbox_frame.config(text=f"Události ({', '.join(filter_description_parts)})")
        elif not self._current_event_filter:
            self.events_listbox_frame.config(text="Všechny události")
        else:
            self.events_listbox_frame.config(text="Události (filtr aktivní)")

        if not events_to_display:
            self.events_listbox.insert(tk.END, " Žádné události dle filtru. ")
        else:
            for event in events_to_display:
                time_display = event.time_str if event.time_str else "--:--"
                date_prefix = ""
                if not self._current_event_filter.get('date_filter'):
                    date_prefix = f"{event.date.strftime('%d.%m.%y')} "
                self.events_listbox.insert(tk.END, f"{date_prefix}{time_display} - {event.title}")
                self.active_listbox_event_ids.append(event.id)

        self._update_buttons_state()
        if 'update_event_details' in self.callbacks:
            self.callbacks['update_event_details']("")

    def _on_event_select_in_listbox(self, evt_unused):
        """
                Obsluha události výběru položky v listboxu událostí.

                Získá vybranou událost, aktualizuje zobrazení jejích detailů
                prostřednictvím callbacku a aktualizuje stav tlačítek.

                Args:
                    evt_unused (tk.Event): Událost výběru (není přímo využívána).
        """
        selected_id = self._get_selected_event_id()
        if selected_id:
            event = self.event_manager.get_event(selected_id)
            if event and 'update_event_details' in self.callbacks:
                details = f"Název: {event.title}\nDatum: {event.date.strftime('%d.%m.%Y')}\nČas: {event.time_str or 'N/A'}\nTyp: {event.event_type}\nDetaily: {event.details or 'Žádné'}\nŠtítky: {', '.join(event.tags) if event.tags else 'Žádné'}"
                self.callbacks['update_event_details'](details)
        else:
            if 'update_event_details' in self.callbacks:
                self.callbacks['update_event_details']("")
        self._update_buttons_state()

    def _update_buttons_state(self):
        """
                Aktualizuje stav tlačítek "Upravit" a "Odebrat" na základě toho,
                zda je v listboxu vybrána nějaká událost.
        """
        has_selection = bool(self._get_selected_event_id())
        self.edit_event_button.config(state=tk.NORMAL if has_selection else tk.DISABLED)
        self.remove_event_button.config(state=tk.NORMAL if has_selection else tk.DISABLED)