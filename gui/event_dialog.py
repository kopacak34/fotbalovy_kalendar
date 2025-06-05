import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class EventDialog(tk.Toplevel):
    """
    Dialogové okno pro přidání nebo úpravu události.

    Umožňuje uživateli zadat všechny potřebné informace o události,
    jako je název, datum, čas, typ, detaily a štítky.
    Pokud je dialog otevřen pro úpravu existující události,
    formulář je předvyplněn jejími daty.
    """
    def __init__(self, parent, event_manager, on_success_callback=None, event_to_edit=None):
        """
        Inicializuje EventDialog.

        Args:
            parent (tk.Widget): Rodičovské okno.
            event_manager (EventManager): Instance správce událostí pro ukládání/úpravu.
            on_success_callback (callable, optional): Funkce, která se zavolá po úspěšném
                                                      uložení nebo úpravě události.
                                                      Předá zpracovaný objekt Event a bool `is_edit`.
                                                      Výchozí je None.
            event_to_edit (Event, optional): Objekt Event, který se má upravovat.
                                             Pokud je None, dialog slouží pro přidání nové události.
                                             Výchozí je None.
        """
        super().__init__(parent)
        self.transient(parent) # Dialog bude vždy nad rodičovským oknem
        self.event_manager = event_manager
        self.on_success_callback = on_success_callback
        self.event_to_edit = event_to_edit

        if self.event_to_edit:
            self.title("Upravit událost")
        else:
            self.title("Přidat událost")

        self.geometry("400x380") # Pevná velikost okna
        self.resizable(False, False)
        self.grab_set() # Zajistí, že dialog je modální

        self.create_form()
        if self.event_to_edit:
            self._populate_form_for_edit()

    def _populate_form_for_edit(self):
        """
        Předvyplní formulář daty z události, která se upravuje.

        Tato metoda je volána pouze pokud je `self.event_to_edit` nastaveno.
        """
        if not self.event_to_edit:
            return

        self.title_entry.insert(0, self.event_to_edit.title)
        self.date_entry.insert(0, self.event_to_edit.date.strftime("%Y-%m-%d"))
        self.time_entry.insert(0, self.event_to_edit.time_str or "")
        self.event_type_var.set(self.event_to_edit.event_type)
        self.details_text.insert("1.0", self.event_to_edit.details or "")
        self.tags_entry.insert(0, ", ".join(self.event_to_edit.tags))


    def create_form(self):
        """
        Vytvoří a uspořádá všechny widgety formuláře pro zadávání údajů o události.
        """
        frame = ttk.Frame(self, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        # Název události
        ttk.Label(frame, text="Název:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.title_entry = ttk.Entry(frame, width=40)
        self.title_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)

        # Datum (YYYY-MM-DD)
        ttk.Label(frame, text="Datum (YYYY-MM-DD):", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W,
                                                                                      pady=5, padx=5)
        self.date_entry = ttk.Entry(frame, width=15)
        self.date_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

        # Čas (HH:MM)
        ttk.Label(frame, text="Čas (HH:MM):", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5,
                                                                               padx=5)
        self.time_entry = ttk.Entry(frame, width=10)
        self.time_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)

        # Typ události
        ttk.Label(frame, text="Typ:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        self.event_type_var = tk.StringVar()
        event_types = ["Zápas (Ligový)", "Zápas (Pohár)", "Zápas (Přátelský)", "Trénink", "Sledování TV", "Schůzka",
                       "Jiné"]
        self.event_type_combo = ttk.Combobox(frame, textvariable=self.event_type_var, values=event_types,
                                             state="readonly", width=37)
        self.event_type_combo.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=5)
        if event_types: # Nastavíme výchozí, pokud není předvyplněno
            if not self.event_to_edit or not self.event_to_edit.event_type:
                 self.event_type_combo.current(0)

        # Detaily
        ttk.Label(frame, text="Detaily:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.NW, pady=5,
                                                                           padx=5)
        self.details_text = tk.Text(frame, height=5, width=30) # Standardní tk.Text pro víceřádkový vstup
        self.details_text.grid(row=4, column=1, sticky=tk.EW, pady=5, padx=5)

        # Štítky (jednoduché textové pole, oddělené čárkou)
        ttk.Label(frame, text="Štítky (oddělené čárkou):", font=("Arial", 10, "bold")).grid(row=5, column=0,
                                                                                            sticky=tk.W, pady=5, padx=5)
        self.tags_entry = ttk.Entry(frame, width=40)
        self.tags_entry.grid(row=5, column=1, sticky=tk.EW, pady=5, padx=5)

        # Tlačítka
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=15)

        save_button_text = "Uložit změny" if self.event_to_edit else "Uložit událost"
        save_button = ttk.Button(button_frame, text=save_button_text, command=self.save_event)
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = ttk.Button(button_frame, text="Zrušit", command=self.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)

        frame.columnconfigure(1, weight=1) # Umožní roztažení vstupních polí

    def save_event(self):
        """
        Zpracuje data z formuláře, validuje je a uloží/upraví událost.

        Nejprve získá hodnoty z formulářových polí.
        Provede základní validaci (povinná pole, formát data a času).
        Pokud je validace úspěšná, zavolá příslušnou metodu `event_manager`
        (add_event nebo update_event).
        V případě úspěchu zavolá `on_success_callback` a zavře dialog.
        V případě chyby zobrazí chybovou hlášku.
        """
        title = self.title_entry.get().strip()
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        event_type = self.event_type_var.get().strip()
        details = self.details_text.get("1.0", tk.END).strip() # Získání textu z tk.Text
        tags_str = self.tags_entry.get().strip()
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()] # Rozdělení štítků

        # Validace povinných polí
        if not all([title, date_str, event_type]):
            messagebox.showerror("Chyba", "Název, datum a typ události jsou povinné.", parent=self)
            return

        # Validace formátu data a času
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            if time_str: # Čas je volitelný
                datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Chyba formátu",
                                 "Zadejte datum ve formátu YYYY-MM-DD a čas ve formátu HH:MM (pokud zadáváte).",
                                 parent=self)
            return

        try:
            if self.event_to_edit: # Režim úpravy
                updated_event = self.event_manager.update_event(
                    self.event_to_edit.id, title, date_str, time_str, event_type, details, tags
                )
                if updated_event:
                    if self.on_success_callback:
                        self.on_success_callback(updated_event, is_edit=True)
                    self.destroy()
                else:
                    # Chyba by měla být již ošetřena v EventManager nebo Event,
                    # ale pro jistotu zde může být obecná chybová hláška.
                    messagebox.showerror("Chyba", "Nepodařilo se upravit událost.", parent=self)
            else: # Režim přidání nové události
                new_event = self.event_manager.add_event(title, date_str, time_str, event_type, details, tags)
                if new_event:
                    if self.on_success_callback:
                        self.on_success_callback(new_event, is_edit=False)
                    self.destroy()
                # else: Chyba by měla být ošetřena v EventManager/Event

        except ValueError as e: # Chyby z validace v Event třídě
            messagebox.showerror("Chyba při ukládání", str(e), parent=self)
        except Exception as e: # Neočekávané chyby
            messagebox.showerror("Neočekávaná chyba", f"Došlo k chybě: {e}", parent=self)