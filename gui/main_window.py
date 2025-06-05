import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .event_dialog import EventDialog
from .settings_dialog import SettingsDialog
from core.event_manager import EventManager
from core.data_handler import DataHandler
from core.thematic_content_manager import ThematicContentManager
from core.settings_manager import SettingsManager
from .calendar_widget import CalendarWidget
from .event_list_panel import EventListPanel
from datetime import date, timedelta
import csv
import random
from core.pdf_exporter import PDFExporter


class MainWindow:
    """
    Hlavní okno aplikace Fotbalový Kalendář.

    Tato třída sestavuje celé uživatelské rozhraní, inicializuje všechny
    potřebné manažery (pro události, data, tematický obsah, nastavení)
    a propojuje jejich funkcionalitu s GUI prvky.
    """

    def __init__(self, master):
        """
        Inicializuje hlavní okno aplikace.

        Args:
            master (tk.Tk): Kořenový Tkinter objekt.
        """
        self.master = master
        master.title("Fotbalový Kalendář")
        master.geometry("950x750")

        self.style = ttk.Style()
        try:
            # Pokus o nastavení preferovaného TTK tématu pro modernější vzhled
            current_theme = self.style.theme_use()
            print(f"Původní TTK téma: {current_theme}")
            new_theme_to_try = 'clam'  # 'clam', 'alt', 'default', 'vista', 'xpnative'
            print(f"Zkouším nastavit TTK téma na: {new_theme_to_try}")
            self.style.theme_use(new_theme_to_try)
            print(f"Nové TTK téma: {self.style.theme_use()}")
        except tk.TclError as e:
            print(f"Nepodařilo se nastavit téma '{new_theme_to_try}': {e}. Používá se výchozí.")

        # Inicializace manažerů
        self.settings_manager = SettingsManager()
        self.data_handler = DataHandler("data/events.json")
        self.event_manager = EventManager()
        self.thematic_content_manager = ThematicContentManager("data/thematic_content.json")
        self.current_thematic_category_for_next = None  # Pro sledování poslední zobrazené náhodné kategorie

        self.currently_selected_date = None  # Datum aktuálně vybrané v kalendáři

        # Reference na hlavní rámce a panely
        self.main_frame = None
        self.event_list_panel = None  # Reference na panel se seznamem událostí

        self._apply_initial_background()
        self._create_menu()
        self.create_widgets()
        self.load_events()
        self.display_daily_thematic_info()
        self._check_upcoming_events()  # Zkontroluje a zobrazí připomínky při startu

    def _apply_initial_background(self):
        """Aplikuje počáteční barvu pozadí na hlavní okno a definuje styly pro rámce."""
        main_bg = self.settings_manager.get_setting("main_window_bg")
        if main_bg:
            self.master.config(bg=main_bg)
            # Definice stylů pro ttk.Frame, které budou používány v aplikaci
            self.style.configure("App.TFrame", background=main_bg)
            self.style.configure("LeftPanel.TFrame", background=main_bg)
            self.style.configure("RightPanel.TFrame", background=main_bg)

    def _create_menu(self):
        """Vytvoří hlavní menu aplikace."""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Soubor", menu=file_menu)
        file_menu.add_command(label="Nastavení vzhledu...", command=self._open_settings_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Export CSV...", command=self._export_events_csv)
        file_menu.add_command(label="Export PDF...", command=self._export_events_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Konec", command=self.master.quit)

    def _open_settings_dialog(self):
        """Otevře dialogové okno pro nastavení vzhledu."""
        SettingsDialog(self.master, self.settings_manager, on_save_callback=self._apply_ui_settings_update)

    def _apply_ui_settings_update(self):
        """
        Aplikuje změny uživatelských nastavení na relevantní části GUI.

        Tato metoda je volána jako callback po uložení změn v dialogu nastavení.
        Aktualizuje vzhled kalendáře a barvy pozadí hlavních rámců.
        """
        # Aktualizace kalendáře
        if hasattr(self, 'calendar_widget'):
            self.calendar_widget.apply_new_settings(self.settings_manager.get_all_settings())

        # Aktualizace pozadí hlavního okna a rámců
        main_bg = self.settings_manager.get_setting("main_window_bg")
        if main_bg:
            self.master.config(bg=main_bg)
            self.style.configure("App.TFrame", background=main_bg)
            self.style.configure("LeftPanel.TFrame", background=main_bg)
            self.style.configure("RightPanel.TFrame", background=main_bg)

            # Překonfigurování existujících rámců, aby se změna stylu projevila
            if self.main_frame: self.main_frame.configure(style="App.TFrame")
            if hasattr(self, 'left_panel_ref') and self.left_panel_ref:
                self.left_panel_ref.configure(style="LeftPanel.TFrame")
                if self.event_list_panel:  # EventListPanel si styl nastavuje sám, ale můžeme ho "šťouchnout"
                    self.event_list_panel.configure(style="LeftPanel.TFrame")
            if hasattr(self, 'right_panel_ref') and self.right_panel_ref:
                self.right_panel_ref.configure(style="RightPanel.TFrame")
        # Zde by se mohly přidat další aktualizace GUI prvků dle potřeby

    def create_widgets(self):
        """Vytvoří a uspořádá všechny hlavní widgety v okně."""
        self.main_frame = ttk.Frame(self.master, padding="10", style="App.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Levý panel (kontejner pro kalendář a seznam událostí) ---
        self.left_panel_ref = ttk.Frame(self.main_frame, width=320, style="LeftPanel.TFrame")
        self.left_panel_ref.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.left_panel_ref.pack_propagate(False)  # Zabrání smrštění panelu podle obsahu

        # Kalendář
        self.calendar_widget = CalendarWidget(
            self.left_panel_ref,
            self.event_manager,
            self.on_calendar_date_selected,
            initial_settings=self.settings_manager.get_all_settings()
        )
        self.calendar_widget.pack(fill=tk.X, pady=(10, 5), ipady=5) # ipady pro vnitřní padding

        # Panel se seznamem událostí a filtry
        event_list_callbacks = {
            'open_add_event': self.open_add_event_dialog,
            'open_edit_event': self.open_edit_event_dialog,
            'remove_event': self.remove_event_by_id,
            'update_event_details': self._update_event_details_text
        }
        self.event_list_panel = EventListPanel(self.left_panel_ref, self.event_manager, event_list_callbacks)
        self.event_list_panel.pack(fill=tk.BOTH, expand=True, pady=5)

        # --- Pravý panel (pro detaily události a tematický obsah) ---
        self.right_panel_ref = ttk.Frame(self.main_frame, style="RightPanel.TFrame")
        self.right_panel_ref.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(self.right_panel_ref, text="Detaily / Tematický obsah", font=("Arial", 14, "bold")).pack(pady=10)

        # Rámec pro detail vybrané události
        self.event_details_frame = ttk.LabelFrame(self.right_panel_ref, text="Detail události", height=200)
        self.event_details_frame.pack(fill=tk.X, pady=5)
        self.event_details_text = tk.Text(self.event_details_frame, height=8, state=tk.DISABLED, wrap=tk.WORD,
                                          font=("Arial", 9))
        self.event_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Rámec pro tematický obsah
        self.thematic_content_frame = ttk.LabelFrame(self.right_panel_ref, text="Fotbalové info dne")
        self.thematic_content_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.thematic_content_text = tk.Text(self.thematic_content_frame, height=10, wrap=tk.WORD, state=tk.DISABLED,
                                             font=("Arial", 9), padx=5, pady=5)
        # Definice tagů pro formátování textu v tematickém obsahu
        self.thematic_content_text.tag_configure("bold_red", font=("Arial", 10, "bold"), foreground="red")
        self.thematic_content_text.tag_configure("title", font=("Arial", 10, "bold", "underline"), spacing1=5,
                                                 spacing3=5)
        self.thematic_content_text.tag_configure("heading", font=("Arial", 9, "bold"), spacing1=3, spacing3=3)
        self.thematic_content_text.tag_configure("normal_text", font=("Arial", 9))
        self.thematic_content_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        thematic_buttons_frame = ttk.Frame(self.thematic_content_frame)
        thematic_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        self.refresh_thematic_button = ttk.Button(thematic_buttons_frame, text="Obnovit info dne",
                                                  command=self.display_daily_thematic_info)
        self.refresh_thematic_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.next_thematic_button = ttk.Button(thematic_buttons_frame, text="Další náhodné",
                                               command=self.display_next_random_thematic_info)
        self.next_thematic_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    def on_calendar_date_selected(self, selected_date):
        """
        Obsluha události výběru data v kalendáři.

        Aktualizuje `currently_selected_date` a předá vybrané datum
        do `event_list_panel` pro filtrování seznamu událostí.

        Args:
            selected_date (date | None): Objekt `date` reprezentující vybraný den,
                                         nebo None, pokud byl výběr zrušen (např. změnou měsíce).
        """
        self.currently_selected_date = selected_date
        if self.event_list_panel:
            self.event_list_panel.filter_by_date(selected_date)

    def open_add_event_dialog(self):
        """Otevře dialog pro přidání nové události."""
        dialog = EventDialog(self.master, self.event_manager, self.save_and_refresh_events)
        # Pokud je v kalendáři vybráno datum, předvyplníme ho v dialogu
        if self.currently_selected_date:
            dialog.date_entry.insert(0, self.currently_selected_date.strftime("%Y-%m-%d"))

    def open_edit_event_dialog(self, event_id_to_edit):
        """
        Otevře dialog pro úpravu existující události.

        Args:
            event_id_to_edit (str): ID události, která má být upravena.
        """
        if not event_id_to_edit:
            messagebox.showwarning("Chyba", "Nebylo vybráno ID události k úpravě.", parent=self.master)
            return
        event_to_edit = self.event_manager.get_event(event_id_to_edit)
        if event_to_edit:
            EventDialog(self.master, self.event_manager, self.save_and_refresh_events, event_to_edit=event_to_edit)
        else:
            messagebox.showerror("Chyba", "Vybranou událost se nepodařilo načíst pro úpravu.", parent=self.master)

    def save_and_refresh_events(self, event_processed=None, is_edit=False):
        """
        Uloží aktuální stav událostí do souboru a obnoví zobrazení v GUI.

        Tato metoda je volána jako callback po úspěšném přidání nebo úpravě
        události v `EventDialog`.

        Args:
            event_processed (Event, optional): Objekt Event, který byl právě zpracován (přidán/upraven).
                                               Používá se pro zobrazení informační zprávy.
            is_edit (bool): True, pokud se jednalo o úpravu události, False pro přidání.
        """
        success = self.data_handler.save_data(self.event_manager.get_all_events_data())
        if success and event_processed:
            action_text = "upravena" if is_edit else "přidána"
            messagebox.showinfo(f"Událost {action_text}",
                                f"Událost '{event_processed.title}' byla úspěšně {action_text}.", parent=self.master)
        elif not success:
            messagebox.showerror("Chyba ukládání", "Nepodařilo se uložit data událostí.", parent=self.master)

        # Obnovení zobrazení
        if self.event_list_panel:
            self.event_list_panel.refresh_event_list()  # Aktualizuje seznam událostí
        if hasattr(self, 'calendar_widget'):
            self.calendar_widget.update_display()  # Aktualizuje zvýraznění v kalendáři

    def load_events(self):
        """Načte události z datového souboru a zobrazí je."""
        events_data = self.data_handler.load_data()
        if events_data:
            self.event_manager.load_events_from_data(events_data)

        # Po načtení zobrazíme všechny události a aktualizujeme kalendář
        if self.event_list_panel:
            self.event_list_panel.show_all_events_in_list()
        if hasattr(self, 'calendar_widget'):
            self.calendar_widget.update_display()

    def remove_event_by_id(self, event_id_to_remove):
        """
        Odebere událost na základě jejího ID.

        Zobrazí potvrzovací dialog před samotným odebráním.
        Po úspěšném odebrání uloží změny a obnoví GUI.

        Args:
            event_id_to_remove (str): ID události k odebrání.
        """
        if not event_id_to_remove:
            messagebox.showwarning("Chyba", "Nebylo vybráno ID události k odebrání.", parent=self.master)
            return

        event_to_remove = self.event_manager.get_event(event_id_to_remove)
        if event_to_remove and messagebox.askyesno("Potvrdit odebrání",
                                                   f"Opravdu chcete odebrat událost '{event_to_remove.title}'?",
                                                   parent=self.master):
            if self.event_manager.remove_event(event_id_to_remove):
                # Po úspěšném odebrání z manageru, uložíme a obnovíme
                # Použijeme event_processed pro zobrazení info zprávy, is_edit=False je zde irelevantní
                # pro logiku save_and_refresh, ale může ovlivnit text zprávy.
                # Můžeme zvážit samostatnou zprávu o odebrání.
                self.save_and_refresh_events() # Jednodušší je zavolat bez parametrů, pokud nechceme specifickou zprávu
                messagebox.showinfo("Odebráno", f"Událost '{event_to_remove.title}' byla úspěšně odebrána.", parent=self.master)
            else:
                messagebox.showerror("Chyba", "Nepodařilo se odebrat událost z manageru.", parent=self.master)
        elif not event_to_remove:
            messagebox.showerror("Chyba", "Událost k odebrání nebyla nalezena.", parent=self.master)

    def _update_event_details_text(self, text_content):
        """
        Aktualizuje text v poli pro zobrazení detailů události.

        Args:
            text_content (str): Text, který má být zobrazen.
        """
        self.event_details_text.config(state=tk.NORMAL)
        self.event_details_text.delete("1.0", tk.END)
        self.event_details_text.insert(tk.END, text_content)
        self.event_details_text.config(state=tk.DISABLED)

    def _parse_and_insert_thematic_content(self, text_content):
        """
        Parzuje a vkládá tematický obsah do textového pole s formátováním.

        Používá předdefinované tagy ("title", "heading", "normal_text")
        pro stylování různých částí textu.

        Args:
            text_content (str): Surový text tematického obsahu.
        """
        self.thematic_content_text.config(state=tk.NORMAL)
        self.thematic_content_text.delete("1.0", tk.END)

        lines = text_content.split('\n')
        first_line = True  # Příznak pro speciální formátování prvního řádku
        for line in lines:
            if not line.strip(): # Přeskočíme prázdné řádky na začátku
                if self.thematic_content_text.index(tk.END).split('.')[0] == '1' and \
                   self.thematic_content_text.index(tk.END).split('.')[1] == '0':
                    continue
            applied_tag = "normal_text" # Výchozí tag
            if first_line and line.strip():
                # Jednoduchá heuristika pro detekci titulku (obsahuje dvojtečku, kratší než 30 znaků před ní)
                if ":" in line and len(line.split(":")[0]) < 30:
                    parts = line.split(":", 1)
                    self.thematic_content_text.insert(tk.END, parts[0] + ":\n", "title")
                    if len(parts) > 1 and parts[1].strip():
                        self.thematic_content_text.insert(tk.END, parts[1].strip() + "\n", "normal_text")
                    first_line = False
                    continue
                else: # Pokud to není titulek dle heuristiky, ale je to první řádek, použijeme "heading"
                    applied_tag = "heading"
                first_line = False
            # Detekce klíčových slov pro "heading" tag
            elif "Pravidlo:" in line or "Nadpis:" in line:
                applied_tag = "heading"
            elif "Kdy se trestá:" in line or "Příklad:" in line:
                applied_tag = "heading"

            self.thematic_content_text.insert(tk.END, line + "\n", applied_tag)
        self.thematic_content_text.config(state=tk.DISABLED)

    def display_daily_thematic_info(self):
        """Zobrazí tematickou informaci pro aktuální den."""
        today = date.today()
        daily_info = self.thematic_content_manager.get_daily_info(today)
        self._parse_and_insert_thematic_content(daily_info)
        self.current_thematic_category_for_next = None # Reset pro další náhodný výběr

    def display_next_random_thematic_info(self):
        """Zobrazí náhodnou tematickou informaci z dostupné kategorie."""
        available_categories = self.thematic_content_manager.get_available_random_categories()
        if not available_categories:
            self._parse_and_insert_thematic_content("Žádné další kategorie k zobrazení.")
            return

        # Výběr kategorie, která nebyla zobrazena jako poslední (pokud je více možností)
        if self.current_thematic_category_for_next and len(available_categories) > 1:
            possible_next_categories = [cat for cat in available_categories if
                                        cat != self.current_thematic_category_for_next]
            chosen_category = random.choice(
                possible_next_categories) if possible_next_categories else self.current_thematic_category_for_next
        else:
            chosen_category = random.choice(available_categories)

        self.current_thematic_category_for_next = chosen_category
        info = self.thematic_content_manager.get_random_info_from_category(chosen_category)

        if info:
            category_title = chosen_category.replace("_", " ").capitalize()
            self._parse_and_insert_thematic_content(f"{category_title}:\n{info}")
        else:
            self._parse_and_insert_thematic_content("Nepodařilo se načíst další informaci.")

    def _check_upcoming_events(self):
        """
        Zkontroluje nadcházející události a zobrazí připomínku, pokud nějaké jsou.

        Počet dní dopředu pro kontrolu se načítá z uživatelských nastavení.
        """
        today = date.today()
        upcoming_events = []
        # Načtení počtu dní pro připomínku z nastavení
        days_ahead_setting = self.settings_manager.get_setting("reminder_days_ahead")

        for i in range(days_ahead_setting + 1):  # +1 aby zahrnovalo i dnešek
            target_date = today + timedelta(days=i)
            events_on_day = self.event_manager.get_events_for_date(target_date)
            if events_on_day:
                upcoming_events.extend(events_on_day)

        if upcoming_events:
            upcoming_events.sort(key=lambda e: (e.date, e.time_str if e.time_str else "24:00")) # Seřazení
            reminder_text_parts = ["Nadcházející události:"]
            for event in upcoming_events:
                day_diff = (event.date - today).days
                date_str = "Dnes" if day_diff == 0 else (
                    "Zítra" if day_diff == 1 else f"Za {day_diff} dní ({event.date.strftime('%d.%m.')})")
                time_str = event.time_str if event.time_str else "--:--"
                reminder_text_parts.append(f"- {date_str}, {time_str}: {event.title} ({event.event_type})")
            messagebox.showinfo("Připomínka událostí", "\n".join(reminder_text_parts), parent=self.master)

    def _export_events_csv(self):
        """Exportuje všechny události do souboru CSV."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV soubory", "*.csv"), ("Všechny soubory", "*.*")],
            title="Uložit události jako CSV"
        )
        if not filepath:  # Uživatel zrušil dialog
            return

        all_events = sorted(self.event_manager.get_all_events(),
                            key=lambda e: (e.date, e.time_str if e.time_str else "24:00"))
        if not all_events:
            messagebox.showinfo("Export", "Nejsou žádné události k exportu.", parent=self.master)
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Název', 'Datum', 'Čas', 'Typ', 'Detaily', 'Štítky']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for event in all_events:
                    writer.writerow({
                        'ID': event.id,
                        'Název': event.title,
                        'Datum': event.date.strftime("%Y-%m-%d"),
                        'Čas': event.time_str,
                        'Typ': event.event_type,
                        'Detaily': event.details,
                        'Štítky': ", ".join(event.tags)  # Štítky jako string oddělený čárkou
                    })
            messagebox.showinfo("Export", f"Události úspěšně exportovány do {filepath}", parent=self.master)
        except IOError as e:
            messagebox.showerror("Chyba exportu", f"Chyba při zápisu do souboru: {e}", parent=self.master)
        except Exception as e:
            messagebox.showerror("Chyba exportu", f"Došlo k neočekávané chybě při exportu: {e}", parent=self.master)

    def _export_events_pdf(self):
        """Exportuje všechny události do souboru PDF."""
        # Kontrola dostupnosti ReportLab
        if not PDFExporter.is_reportlab_available():
            messagebox.showerror("Chyba exportu PDF",
                                 "Knihovna ReportLab není k dispozici.\n"
                                 "Export do PDF nelze provést.",
                                 parent=self.master)
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF soubory", "*.pdf"), ("Všechny soubory", "*.*")],
            title="Uložit události jako PDF"
        )
        if not filepath:  # Uživatel zrušil dialog
            return

        all_events = self.event_manager.get_all_events() # Zde není potřeba řadit, PDFExporter to dělá interně
        if not all_events:
            messagebox.showinfo("Export PDF", "Nejsou žádné události k exportu.", parent=self.master)
            return

        exporter = PDFExporter(all_events)
        try:
            if exporter.export(filepath):
                messagebox.showinfo("Export PDF", f"Události úspěšně exportovány do {filepath}", parent=self.master)
            else:
                # Chyba by měla být vypsána do konzole z PDFExporter
                messagebox.showerror("Chyba exportu PDF",
                                     "Nepodařilo se vygenerovat PDF soubor. Zkontrolujte konzoli pro detaily.",
                                     parent=self.master)
        except Exception as e:
            messagebox.showerror("Chyba exportu PDF",
                                 f"Došlo k neočekávané chybě při exportu PDF: {e}",
                                 parent=self.master)