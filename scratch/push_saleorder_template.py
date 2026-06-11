"""
Pushes the sale.report_saleorder_document view to Odoo for each active language,
replacing translatable strings (like 'Fecha de Servicio', 'Producto:') with the
correct translation per language.

In Odoo 17, ir.translation is gone. View translations are stored directly in
arch_db as a per-language JSON internally. Writing arch_db with a specific lang
context updates only that language's version.
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

# Base XML file (written in Spanish — es_419 is the system's base language)
XML_PATH = os.path.join(os.path.dirname(__file__), 'standard_saleorder_document.xml')

# Translations: what to replace per language.
# Key: list of (source_text, translated_text) tuples applied to the base Spanish XML.
LANG_TRANSLATIONS = {
    'es_419': [],  # base — no replacements needed (already in Spanish)
    'es_ES': [],   # same as Spanish base
    'en_US': [
        ('Fecha de Servicio', 'Service Date'),
        ('>Cliente<', '>Client<'),
    ],
    'de_DE': [
        ('Fecha de Servicio', 'Servicedatum'),
        ('>Cliente<', '>Kunde<'),
    ],
    'pt_BR': [
        ('Fecha de Servicio', 'Data do Serviço'),
        # 'Cliente' is the same in Portuguese
    ],
}


def main():
    with open(XML_PATH, 'r') as f:
        base_arch = f.read()

    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    views = client.search_read(
        'ir.ui.view',
        [('key', '=', 'sale.report_saleorder_document')],
        ['id', 'name']
    )
    if not views:
        print("ERROR: View 'sale.report_saleorder_document' not found!")
        return
    view_id = views[0]['id']
    print(f"Found view ID {view_id}: {views[0]['name']}")

    # i18n is now handled directly in QWeb via Python dicts at render time.
    # We only need to push one version — no per-language arch_db writes needed.
    client.execute('ir.ui.view', 'write', [view_id], {'arch_db': base_arch})
    print("✅ View updated successfully (i18n handled inline by QWeb).")


if __name__ == "__main__":
    main()

