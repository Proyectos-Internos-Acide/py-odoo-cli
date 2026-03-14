import sys
import os
import time

# Add root directory to sys.path to import odoo_cli
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient
from odoo_cli.exceptions import OdooClientError

def full_flow():
    client = OdooClient()
    try:
        print("🚀 Iniciando flujo completo de Compra + Lotes...")
        client.connect()

        # 1. Habilitar Lotes (si es necesario)
        # En Odoo, esto suele ser un grupo. Intentaremos activarlo vía res.config.settings
        print("\n1. Verificando configuración de Lotes...")
        config_id = client.create('res.config.settings', {
            'group_stock_production_lot': True,
        })
        client.execute('res.config.settings', 'execute', [config_id])
        print("✅ Funcionalidad de Lotes asegurada.")

        # 2. Crear Producto "Cemento Sol (Prueba)"
        print("\n2. Creando Producto...")
        product_name = "Cemento Sol (Prueba)"
        existing_product = client.search_read('product.template', domain=[['name', '=', product_name]], fields=['id'])
        
        if existing_product:
            product_tmpl_id = existing_product[0]['id']
            client.write('product.template', [product_tmpl_id], {'tracking': 'lot'})
            print(f"⚠️ Producto ya existe (ID: {product_tmpl_id}). Seguimiento por lotes activado.")
        else:
            product_tmpl_id = client.create('product.template', {
                'name': product_name,
                'type': 'consu', # Goods (Storable/Consumable in Odoo 17+)
                'tracking': 'lot',
            })
            print(f"✅ Producto creado: {product_name} (ID: {product_tmpl_id})")

        # Get product variant ID
        product_product = client.search_read('product.product', domain=[['product_tmpl_id', '=', product_tmpl_id]], fields=['id'])
        product_id = product_product[0]['id']

        # 3. Crear Proveedor
        print("\n3. Creando Proveedor...")
        vendor_name = "Distribuidora Ferretera AQP"
        existing_vendor = client.search_read('res.partner', domain=[['name', '=', vendor_name]], fields=['id'])
        
        if existing_vendor:
            vendor_id = existing_vendor[0]['id']
            print(f"⚠️ Proveedor ya existe (ID: {vendor_id})")
        else:
            vendor_id = client.create('res.partner', {
                'name': vendor_name,
                'is_company': True,
            })
            print(f"✅ Proveedor creado: {vendor_name} (ID: {vendor_id})")

        # 4. Crear Orden de Compra (PO)
        print("\n4. Creando Orden de Compra...")
        po_id = client.create('purchase.order', {
            'partner_id': vendor_id,
        })
        
        # Add line to PO
        client.create('purchase.order.line', {
            'order_id': po_id,
            'product_id': product_id,
            'name': product_name,
            'product_qty': 50.0,
            'price_unit': 25.5,
            'date_planned': time.strftime('%Y-%m-%d %H:%M:%S'),
        })
        print(f"✅ PO creada (ID: {po_id}) con 50 unidades de Cemento.")

        # 5. Confirmar PO
        print("\n5. Confirmando Orden de Compra...")
        client.execute('purchase.order', 'button_confirm', [po_id])
        print("✅ PO Confirmada. Se ha generado una Recepción de Inventario.")

        # 6. Referencia de Recepción (Picking)
        # Buscamos el picking generado
        picking = client.search_read('stock.picking', domain=[['purchase_id', '=', po_id]], fields=['id', 'name'])
        if picking:
            print(f"\n📦 Recepción generada: {picking[0]['name']} (ID: {picking[0]['id']})")
            print("\n💡 NOTA: Para completar la recepción con lotes desde el script,")
            print("se requiere asignar el lote en las 'move_line_ids'.")
            print("En la guía manual encontrarás cómo hacerlo paso a paso en la interfaz.")

        print("\n🎉 Flujo de automatización completado.")

    except OdooClientError as e:
        print(f"❌ Error de Odoo: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    full_flow()
