import sys
import os

# Add root directory to sys.path to import odoo_cli
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient
from odoo_cli.exceptions import OdooClientError

def main():
    print("--- Probar conexión: production-inventory ---")
    try:
        client = OdooClient()
        uid = client.connect()
        print(f"✅ Conexión exitosa. User ID: {uid}")
        
        # Opcional: listar algunos productos para verificar acceso
        print("Consultando últimos 3 productos...")
        products = client.search_read(
            'product.template',
            domain=[['active', '=', True]],
            fields=['name', 'default_code'],
            limit=3
        )
        for p in products:
            print(f"- [{p.get('default_code') or 'N/A'}] {p.get('name')}")
            
    except OdooClientError as e:
        print(f"❌ Error de Odoo: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
