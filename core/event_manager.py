from .event import Event
from datetime import date, datetime
import uuid

class EventManager:
    """
    Spravuje kolekci událostí (objektů Event).

    Umožňuje přidávat, upravovat, odebírat a vyhledávat události.
    Události jsou uloženy v paměti ve slovníku pro rychlý přístup podle ID.
    """
    def __init__(self):
        """Inicializuje EventManager s prázdnou kolekcí událostí."""
        self._events = {} # Slovník pro rychlý přístup k událostem podle ID {id: Event_object}

    def add_event(self, title, date_str, time_str, event_type, details="", tags=None):
        """
        Přidá novou událost do kolekce.

        Vytvoří novou instanci Event a uloží ji. Pokud by došlo ke kolizi ID (velmi nepravděpodobné),
        vygeneruje se nové ID.

        Args:
            title (str): Název události.
            date_str (str): Datum události ve formátu "YYYY-MM-DD".
            time_str (str): Čas události ve formátu "HH:MM" (může být prázdný).
            event_type (str): Typ události.
            details (str, optional): Podrobnosti o události. Výchozí je prázdný řetězec.
            tags (list[str], optional): Seznam štítků. Výchozí je None.

        Returns:
            Event | None: Nově vytvořený objekt Event, nebo None v případě chyby při validaci dat.
        """
        try:
            new_event = Event(title, date_str, time_str, event_type, details, tags)
            if new_event.id in self._events:
                 # Mělo by být vzácné díky uuid, ale pro jistotu
                 new_event.id = str(uuid.uuid4())
            self._events[new_event.id] = new_event
            return new_event
        except ValueError as e:
            print(f"Chyba při přidávání události: {e}")
            return None # V případě chyby vrátí None

    def update_event(self, event_id, title, date_str, time_str, event_type, details="", tags=None):
        """
        Upraví existující událost na základě jejího ID.

        Pokud událost s daným ID neexistuje, vypíše chybu a vrátí None.
        Jinak se pokusí vytvořit novou instanci Event s aktualizovanými daty
        (což zahrnuje validaci) a nahradí původní událost.

        Args:
            event_id (str): ID události, která má být upravena.
            title (str): Nový název události.
            date_str (str): Nové datum události ("YYYY-MM-DD").
            time_str (str): Nový čas události ("HH:MM", může být prázdný).
            event_type (str): Nový typ události.
            details (str, optional): Nové podrobnosti.
            tags (list[str], optional): Nový seznam štítků.

        Returns:
            Event | None: Aktualizovaný objekt Event, nebo None pokud událost nebyla nalezena
                          nebo došlo k chybě při validaci nových dat.
        """
        if event_id not in self._events:
            print(f"Chyba při úpravě: Událost s ID {event_id} nenalezena.")
            return None

        try:
            # Vytvoříme novou instanci Event s novými daty pro validaci
            updated_event_candidate = Event(title, date_str, time_str, event_type, details, tags, event_id=event_id)

            # Pokud validace projde, nahradíme starou událost novou
            self._events[event_id] = updated_event_candidate
            return updated_event_candidate
        except ValueError as e:
            print(f"Chyba při úpravě události: {e}")
            return None

    def remove_event(self, event_id):
        """
        Odebere událost z kolekce podle jejího ID.

        Args:
            event_id (str): ID události k odebrání.

        Returns:
            bool: True, pokud byla událost úspěšně odebrána, jinak False (pokud nebyla nalezena).
        """
        if event_id in self._events:
            del self._events[event_id]
            return True
        print(f"Chyba při odebírání: Událost s ID {event_id} nenalezena.")
        return False

    def get_event(self, event_id):
        """
        Vrátí objekt Event na základě jeho ID.

        Args:
            event_id (str): ID hledané události.

        Returns:
            Event | None: Nalezený objekt Event, nebo None, pokud událost s daným ID neexistuje.
        """
        return self._events.get(event_id)

    def get_all_events(self):
        """
        Vrátí seznam všech událostí v kolekci.

        Returns:
            list[Event]: Seznam všech objektů Event.
        """
        return list(self._events.values())

    def get_events_for_date(self, target_date):
        """
        Vrátí seznam událostí pro konkrétní datum.

        Pokud je `target_date` řetězec, pokusí se ho převést na objekt `date`.

        Args:
            target_date (date | str): Datum (objekt `date` nebo řetězec "YYYY-MM-DD"),
                                      pro které se mají události vyhledat.

        Returns:
            list[Event]: Seznam událostí pro zadané datum. V případě neplatného formátu
                         data vrátí prázdný seznam.
        """
        if not isinstance(target_date, date):
             # Pokus o konverzi, pokud dostaneme string
             try:
                 target_date = datetime.strptime(str(target_date), "%Y-%m-%d").date()
             except ValueError:
                 print(f"Chyba: Neplatný formát data pro filtrování: {target_date}")
                 return []

        return [event for event in self._events.values() if event.date == target_date]

    def get_events_by_filter(self, date_filter=None, event_type_filter=None, tag_filter=None):
        """
        Vrátí seznam událostí filtrovaných podle různých kritérií.

        Filtry se aplikují postupně. Pokud je `date_filter` řetězec, pokusí se ho převést.
        Filtr `event_type_filter` se ignoruje, pokud je "Všechny typy".

        Args:
            date_filter (date | str, optional): Datum pro filtrování.
            event_type_filter (str, optional): Typ události pro filtrování.
            tag_filter (str, optional): Štítek, který musí událost obsahovat.

        Returns:
            list[Event]: Seznam událostí, které odpovídají zadaným filtrům.
        """
        filtered_events = self.get_all_events()

        if date_filter:
            # Předpokládáme, že date_filter je objekt date nebo string YYYY-MM-DD
            if not isinstance(date_filter, date):
                 try:
                     date_filter = datetime.strptime(str(date_filter), "%Y-%m-%d").date()
                 except ValueError:
                     print(f"Varování: Neplatný formát data pro filtrování: {date_filter}")
                     date_filter = None # Ignorujeme neplatný filtr

            if date_filter:
                filtered_events = [event for event in filtered_events if event.date == date_filter]

        if event_type_filter and event_type_filter != "Všechny typy": # Předpokládáme "Všechny typy" jako možnost v GUI
            filtered_events = [event for event in filtered_events if event.event_type == event_type_filter]

        if tag_filter:
            # Předpokládáme, že tag_filter je string (jeden tag)
            filtered_events = [event for event in filtered_events if tag_filter in event.tags]

        return filtered_events


    def load_events_from_data(self, events_data):
        """
        Načte události ze seznamu slovníků a nahradí stávající události v manageru.

        Každý slovník v `events_data` je převeden na objekt Event pomocí `Event.from_dict()`.
        V případě chyby při konverzi jednotlivé události je tato přeskočena a je vypsáno varování.

        Args:
            events_data (list[dict]): Seznam slovníků, kde každý slovník reprezentuje jednu událost.
        """
        self._events = {} # Vyčistíme stávající události
        for data in events_data:
            try:
                event = Event.from_dict(data)
                self._events[event.id] = event
            except ValueError as e:
                print(f"Varování: Přeskočena neplatná událost při načítání: {e} - Data: {data}")
            except Exception as e:
                 print(f"Varování: Neočekávaná chyba při načítání události: {e} - Data: {data}")


    def get_all_events_data(self):
        """
        Vrátí seznam slovníků reprezentujících všechny události, vhodný pro uložení.

        Každý objekt Event v kolekci je převeden na slovník pomocí metody `to_dict()`.

        Returns:
            list[dict]: Seznam slovníků, kde každý slovník reprezentuje jednu událost.
        """
        return [event.to_dict() for event in self._events.values()]