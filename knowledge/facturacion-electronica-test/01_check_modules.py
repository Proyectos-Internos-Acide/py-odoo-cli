import sys
import os

# Agregamos la raíz del proyecto al path para importar odoo_cli
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from odoo_cli.client import OdooClient
from odoo_cli.exceptions import OdooClientError

def main():
    try:
        client = OdooClient()
        print(f"✅ Conectado como usuario ID: {client.connect()}")
        
        print("\n🔍 Buscando módulos de localización instalados (Perú/Facturación)...")
        modules = client.search_read(
            'ir.module.module',
            domain=[
                ('state', '=', 'installed'),
                '|', ('name', 'ilike', 'l10n_pe'),
                ('name', 'ilike', 'einvoice')
            ],
            fields=['name', 'shortdesc', 'installed_version']
        )
        
        if not modules:
            print("⚠️ No se encontraron módulos que contengan 'l10n_pe' o 'einvoice' de momento.")
        else:
            print(f"📦 Módulos encontrados ({len(modules)}):")
            for m in modules:
                print(f" - {m.get('name')}: {m.get('shortdesc')} (Versión: {m.get('installed_version') or 'N/A'})")

    except OdooClientError as e:
        print(f"❌ Error al conectar o consultar Odoo: {e}")

if __name__ == '__main__':
    main()
