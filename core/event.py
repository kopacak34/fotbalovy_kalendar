import uuid
from datetime import datetime, date


class Event:
    """
    Reprezentuje jednu fotbalovou událost.

    Každá událost má unikátní ID, název, datum, volitelný čas, typ,
    volitelné detaily a seznam štítků. Třída zajišťuje validaci
    vstupních dat, zejména formátu data a času, a povinných polí.
    """
    def __init__(self, title, date_str, time_str, event_type, details="", tags=None, event_id=None):
        """
        Inicializuje novou událost.

        Args:
            title (str): Název události. Nesmí být prázdný.
            date_str (str): Datum události ve formátu "YYYY-MM-DD".
            time_str (str): Čas události ve formátu "HH:MM". Může být prázdný.
            event_type (str): Typ události (např. "Zápas", "Trénink"). Nesmí být prázdný.
            details (str, optional): Podrobnější popis události. Výchozí je prázdný řetězec.
            tags (list[str], optional): Seznam štítků pro událost. Výchozí je None, což se převede na prázdný seznam.
            event_id (str, optional): Unikátní ID události. Pokud není poskytnuto, vygeneruje se nové UUID.

        Raises:
            ValueError: Pokud je formát data nebo času neplatný, nebo pokud chybí název či typ události.
        """
        try:
            self.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Neplatný formát data. Použijte YYYY-MM-DD.")

        self.time_str = time_str.strip() if time_str else ""
        if self.time_str:
            try:
                datetime.strptime(self.time_str, "%H:%M").time() # Jen validace formátu
            except ValueError:
                raise ValueError("Neplatný formát času. Použijte HH:MM.")

        self.id = event_id if event_id else str(uuid.uuid4())
        self.title = title.strip()
        self.event_type = event_type.strip()
        self.details = details.strip()
        self.tags = [tag.strip() for tag in (tags if tags is not None else []) if tag.strip()]

        if not self.title:
            raise ValueError("Název události nesmí být prázdný.")
        if not self.event_type:
            raise ValueError("Typ události nesmí být prázdný.")

    def __repr__(self):
        """
        Vrací řetězcovou reprezentaci objektu události, vhodnou pro ladění.

        Returns:
            str: Reprezentace události.
        """
        return f"Event(id='{self.id[:8]}...', title='{self.title}', date='{self.date}', time='{self.time_str}', type='{self.event_type}')"

    def to_dict(self):
        """
        Převede objekt události na slovník, vhodný pro serializaci (např. do JSON).

        Returns:
            dict: Slovníková reprezentace události.
        """
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date.strftime("%Y-%m-%d"),
            "time": self.time_str,
            "type": self.event_type,
            "details": self.details,
            "tags": self.tags
        }

    @staticmethod
    def from_dict(data):
        """
        Vytvoří objekt Event ze slovníku.

        Tato metoda slouží k deserializaci události, například při načítání z JSON souboru.

        Args:
            data (dict): Slovník obsahující data události. Očekává klíče
                         "id", "title", "date", "time", "type".
                         Klíče "details" a "tags" jsou volitelné.

        Returns:
            Event: Nová instance třídy Event vytvořená z poskytnutých dat.

        Raises:
            ValueError: Pokud slovník neobsahuje všechny povinné klíče.
        """
        if not all(k in data for k in ["id", "title", "date", "time", "type"]):
            raise ValueError("Neplatná data události ve slovníku.")
        return Event(
            title=data["title"],
            date_str=data["date"],
            time_str=data.get("time", ""),
            event_type=data["type"],
            details=data.get("details", ""),
            tags=data.get("tags", []),
            event_id=data["id"]
        )