import sys
import os

# Add root directory to sys.path to import odoo_cli
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient
from odoo_cli.exceptions import OdooClientError

def cleanup_locations():
    client = OdooClient()
    try:
        print("🧹 Iniciando limpieza de ubicaciones...")
        client.connect()

        # IDs identified previously
        location_ids = [21, 20, 19, 30, 29, 28, 39, 38, 37]
        
        # Verify they exist before deleting
        locations = client.search_read(
            'stock.location',
            domain=[['id', 'in', location_ids]],
            fields=['complete_name']
        )

        if not locations:
            print("ℹ️ No se encontraron las ubicaciones para eliminar (tal vez ya fueron eliminadas).")
            return

        print(f"Se eliminarán {len(locations)} ubicaciones:")
        for loc in locations:
            print(f"  - {loc['complete_name']}")

        # Unlink the locations
        success = client.unlink('stock.location', location_ids)
        
        if success:
            print("\n✅ Ubicaciones eliminadas satisfactoriamente.")
        else:
            print("\n❌ Hubo un problema al intentar eliminar las ubicaciones.")

    except OdooClientError as e:
        print(f"❌ Error de Odoo: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    cleanup_locations()
