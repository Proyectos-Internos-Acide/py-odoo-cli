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
# Key: (source_text, translated_text)
LANG_TRANSLATIONS = {
    'es_419': [],  # base — no replacements needed
    'es_ES': [],   # same as Spanish base
    'en_US': [
        ('Fecha de Servicio', 'Service Date'),
        ('Producto: </span>', 'Product: </span>'),
    ],
    'de_DE': [
        ('Fecha de Servicio', 'Servicedatum'),
        ('Producto: </span>', 'Produkt: </span>'),
    ],
    'pt_BR': [
        ('Fecha de Servicio', 'Data do Serviço'),
        ('Producto: </span>', 'Produto: </span>'),
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

    for lang, replacements in LANG_TRANSLATIONS.items():
        arch = base_arch
        for src, dst in replacements:
            arch = arch.replace(src, dst)

        client.execute(
            'ir.ui.view',
            'write',
            [view_id],
            {'arch_db': arch},
            context={'lang': lang}
        )
        print(f"  ✅ [{lang}] Updated ({len(replacements)} replacements applied)")

    print("\n🎉 View updated for all languages successfully.")


if __name__ == "__main__":
    main()
