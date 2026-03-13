import sys
import os

# Add root directory to sys.path to import odoo_cli
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient
from odoo_cli.exceptions import OdooClientError

def setup_warehouses():
    client = OdooClient()
    try:
        print("🚀 Iniciando configuración de almacenes...")
        client.connect()

        warehouses_to_create = [
            {"name": "Almacén Principal: Arequipa", "code": "AQP"},
            {"name": "Almacén 1: Moquegua", "code": "MOC"},
            {"name": "Almacén 2: Puno", "code": "PUN"},
        ]

        internal_locations = [
            "Materiales de Construcción",
            "Hogar y Limpieza",
            "EPS (Equipos de Protección Personal)"
        ]

        for wh_data in warehouses_to_create:
            print(f"\n--- Creando Almacén: {wh_data['name']} ({wh_data['code']}) ---")
            
            # Check if warehouse already exists
            existing_wh = client.search_read(
                'stock.warehouse',
                domain=[['code', '=', wh_data['code']]],
                fields=['id', 'lot_stock_id']
            )

            if existing_wh:
                wh_id = existing_wh[0]['id']
                lot_stock_id = existing_wh[0]['lot_stock_id'][0]
                print(f"⚠️ El almacén ya existe (ID: {wh_id}).")
            else:
                wh_id = client.create('stock.warehouse', {
                    'name': wh_data['name'],
                    'code': wh_data['code'],
                })
                # Re-read to get the default lot_stock_id created by Odoo
                created_wh = client.search_read(
                    'stock.warehouse',
                    domain=[['id', '=', wh_id]],
                    fields=['lot_stock_id']
                )
                lot_stock_id = created_wh[0]['lot_stock_id'][0]
                print(f"✅ Almacén creado exitosamente (ID: {wh_id}).")

            # Create internal locations under the warehouse's main stock location
            for loc_name in internal_locations:
                full_loc_name = f"{wh_data['code']}/Stock/{loc_name}"
                
                # Check if location already exists
                existing_loc = client.search_read(
                    'stock.location',
                    domain=[['location_id', '=', lot_stock_id], ['name', '=', loc_name]],
                    fields=['id']
                )

                if existing_loc:
                    print(f"  - ⚠️ Ubicación '{loc_name}' ya existe (ID: {existing_loc[0]['id']}).")
                else:
                    loc_id = client.create('stock.location', {
                        'name': loc_name,
                        'location_id': lot_stock_id,
                        'usage': 'internal',
                    })
                    print(f"  - ✅ Ubicación '{loc_name}' creada (ID: {loc_id}).")

        print("\n🎉 Configuración completada con éxito.")

    except OdooClientError as e:
        print(f"❌ Error de Odoo: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    setup_warehouses()
