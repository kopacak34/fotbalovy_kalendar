import json
import os

class DataHandler:
    """
    Zpracovává ukládání a načítání dat událostí do/ze souboru JSON.

    Tato třída se stará o perzistenci dat aplikace, konkrétně o seznam
    událostí. Zajišťuje, že adresář pro ukládání dat existuje,
    a ošetřuje možné chyby při čtení nebo zápisu souboru.
    """
    def __init__(self, filepath):
        """
        Inicializuje DataHandler s cestou k datovému souboru.

        Pokud adresář specifikovaný v cestě neexistuje, pokusí se ho vytvořit.

        Args:
            filepath (str): Cesta k souboru JSON, kde budou data uložena/načtena.
        """
        self.filepath = filepath
        data_dir = os.path.dirname(self.filepath)
        if data_dir and not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir)
                print(f"Vytvořen adresář pro data: {data_dir}")
            except OSError as e:
                print(f"Chyba při vytváření adresáře {data_dir}: {e}")

    def load_data(self):
        """
        Načte data ze souboru JSON.

        Pokud soubor neexistuje, je prázdný, poškozený, nebo data nejsou
        ve formátu seznamu, vypíše varování/chybu a vrátí prázdný seznam.

        Returns:
            list: Seznam načtených dat (typicky slovníků reprezentujících události),
                  nebo prázdný seznam v případě chyby či neexistence souboru.
        """
        if not os.path.exists(self.filepath):
            print(f"Soubor s daty nenalezen: {self.filepath}. Vracím prázdný seznam.")
            return []

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content:
                    print(f"Soubor s daty je prázdný: {self.filepath}. Vracím prázdný seznam.")
                    return []
                data = json.loads(content)
                if not isinstance(data, list):
                     print(f"Varování: Data v souboru {self.filepath} nejsou ve formátu seznamu. Vracím prázdný seznam.")
                     return []
                return data
        except json.JSONDecodeError:
            print(f"Chyba při dekódování JSON ze souboru {self.filepath}. Soubor může být poškozen. Vracím prázdný seznam.")
            return []
        except Exception as e:
            print(f"Došlo k neočekávané chybě při načítání dat ze souboru {self.filepath}: {e}. Vracím prázdný seznam.")
            return []

    def save_data(self, data):
        """
        Uloží data (seznam slovníků) do souboru JSON.

        Data jsou uložena s odsazením pro lepší čitelnost.
        Pokud data nejsou ve formátu seznamu, vypíše chybu a neuloží je.

        Args:
            data (list): Seznam dat (typicky slovníků) k uložení.

        Returns:
            bool: True, pokud byla data úspěšně uložena, jinak False.
        """
        if not isinstance(data, list):
             print("Chyba při ukládání: Data nejsou ve formátu seznamu.")
             return False

        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Chyba při zápisu do souboru {self.filepath}: {e}")
            return False
        except Exception as e:
            print(f"Došlo k neočekávané chybě při ukládání dat do souboru {self.filepath}: {e}")
            return False