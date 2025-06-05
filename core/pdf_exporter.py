import os
import sys
from datetime import datetime

# Přidání cesty k vendor složce, aby Python našel reportlab
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vendor_path = os.path.join(project_root, "vendor")
if vendor_path not in sys.path:
    sys.path.insert(0, vendor_path)
    # print(f"Přidána cesta do sys.path: {vendor_path}")

# Tyto proměnné budou na úrovni modulu
_SimpleDocTemplate = None
_Paragraph = None
_Spacer = None
_Table = None
_TableStyle = None
_getSampleStyleSheet = None
_ParagraphStyle = None
_inch = None
_cm = None
_colors = None
_TA_CENTER = None
_TA_LEFT = None
_TA_RIGHT = None

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

    # Přiřazení importovaných modulů/tříd k našim modulovým proměnným
    _SimpleDocTemplate = SimpleDocTemplate
    _Paragraph = Paragraph
    _Spacer = Spacer
    _Table = Table
    _TableStyle = TableStyle
    _getSampleStyleSheet = getSampleStyleSheet
    _ParagraphStyle = ParagraphStyle
    _inch = inch
    _cm = cm
    _colors = colors
    _TA_CENTER = TA_CENTER
    _TA_LEFT = TA_LEFT
    _TA_RIGHT = TA_RIGHT

except ImportError as e:
    print(f"Chyba při importu reportlab: {e}")
    print("Ujistěte se, že knihovna reportlab je ve složce 'vendor' vašeho projektu.")


class PDFExporter:
    """
    Třída pro export dat událostí do PDF souboru pomocí knihovny ReportLab.

    Zajišťuje formátování událostí do přehledného dokumentu,
    včetně titulku, zápatí s datem generování a vlastních stylů pro text.
    """
    def __init__(self, events_data):
        """
        Inicializuje PDFExporter se seznamem událostí k exportu.

        Události jsou interně seřazeny podle data a času.
        Pokud je knihovna ReportLab dostupná, inicializují se také styly.

        Args:
            events_data (list[Event]): Seznam objektů Event, které mají být exportovány.
                                       Očekává se, že každý objekt má atributy `date`,
                                       `time_str`, `title`, `event_type`, `details`, `tags`.
        """
        self.events_data = sorted(events_data, key=lambda e: (e.date, e.time_str if e.time_str else "24:00"))
        if _getSampleStyleSheet:
            self.styles = _getSampleStyleSheet()
            self._setup_custom_styles()
        else:
            self.styles = None # Nebo nějaká výchozí prázdná struktura

    def _setup_custom_styles(self):
        """
        Nastaví vlastní styly pro formátování textu v PDF dokumentu.

        Definuje styly pro nadpisy událostí, detaily událostí a zápatí.
        Tato metoda je volána interně při inicializaci, pokud je ReportLab dostupný.
        """
        if not self.styles or not _ParagraphStyle or not _inch or not _TA_CENTER: # Kontrola dostupnosti
            return
        self.styles.add(_ParagraphStyle(name='EventTitle',
                                        parent=self.styles['h2'],
                                        fontSize=12,
                                        leading=14))
        self.styles.add(_ParagraphStyle(name='EventDetail',
                                        parent=self.styles['Normal'],
                                        leftIndent=0.2 * _inch,
                                        fontSize=9,
                                        leading=11))
        self.styles.add(_ParagraphStyle(name='Footer',
                                        parent=self.styles['Normal'],
                                        fontSize=8,
                                        alignment=_TA_CENTER))

    @staticmethod
    def is_reportlab_available():
        """
        Kontroluje, zda je knihovna ReportLab (alespoň její základní části) dostupná.

        Returns:
            bool: True, pokud je ReportLab k dispozici, jinak False.
        """
        return _SimpleDocTemplate is not None

    def export(self, filepath):
        """
        Vygeneruje a uloží PDF soubor s přehledem událostí.

        Pokud ReportLab není k dispozici nebo styly nebyly inicializovány,
        export se neprovede a vrátí False.

        Args:
            filepath (str): Cesta k souboru, kam má být PDF uloženo.

        Returns:
            bool: True, pokud byl PDF soubor úspěšně vygenerován a uložen, jinak False.
        """
        if not PDFExporter.is_reportlab_available():
            print("Reportlab není k dispozici. Export do PDF nelze provést.")
            return False

        if not self.styles: # Další kontrola pro případ, že styly nebyly inicializovány
            print("Chyba: Styly pro PDF nebyly inicializovány (pravděpodobně chybí reportlab).")
            return False

        doc = _SimpleDocTemplate(filepath,
                                 pagesize=(21.0 * _cm, 29.7 * _cm),  # A4
                                 rightMargin=2 * _cm, leftMargin=2 * _cm,
                                 topMargin=2 * _cm, bottomMargin=2 * _cm)
        story = []

        # Titulek dokumentu
        title_text = "Přehled fotbalových událostí"
        story.append(_Paragraph(title_text, self.styles['h1']))
        story.append(_Spacer(1, 0.5 * _cm))

        if not self.events_data:
            story.append(_Paragraph("Žádné události k exportu.", self.styles['Normal']))
        else:
            for event in self.events_data:
                story.append(_Paragraph(f"{event.date.strftime('%d.%m.%Y')} - {event.title} ({event.event_type})",
                                        self.styles['EventTitle']))

                details_text = []
                if event.time_str:
                    details_text.append(f"Čas: {event.time_str}")
                if event.details:
                    # Nahradíme nové řádky HTML tagem <br/> pro správné zobrazení v ReportLab Paragraph
                    details_cleaned = event.details.replace('\n', '<br/>')
                    details_text.append(f"Detaily: {details_cleaned}")
                if event.tags:
                    details_text.append(f"Štítky: {', '.join(event.tags)}")

                if details_text:
                    for detail_line in details_text:
                        story.append(_Paragraph(detail_line, self.styles['EventDetail']))
                story.append(_Spacer(1, 0.3 * _cm))

        def my_page_layout(canvas, doc_template):
            """Vnitřní funkce pro vykreslení zápatí na každé stránce."""
            canvas.saveState()
            footer_text = f"Vygenerováno: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            p = _Paragraph(footer_text, self.styles['Footer'])
            p.wrapOn(canvas, doc_template.width, doc_template.bottomMargin)
            p.drawOn(canvas, doc_template.leftMargin, 0.5 * _cm) # Umístění zápatí
            canvas.restoreState()

        try:
            doc.build(story, onFirstPage=my_page_layout, onLaterPages=my_page_layout)
            return True
        except Exception as e:
            print(f"Chyba při generování PDF: {e}")
            return False