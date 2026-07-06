import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from odoo_cli import OdooClient

def main():
    print("--- Operaciones Esenciales para Textiles y Confecciones ---")
    try:
        client = OdooClient()
        client.connect()
        
        # 1. Contactos (Clientes)
        print("\n[Contactos] Creando cliente de prueba (Facturación RUC)...")
        partner_vals = {
            'name': 'CONFECCIONES ATLAS DE PRUEBA S.A.C.',
            'is_company': True,
            'l10n_latam_identification_type_id': 4, # RUC en Peru
            'vat': '20123456789',
            'street': 'Av. Huánuco 1234 - Gamarra',
            'city': 'Lima',
            'email': 'contacto@confeccionesatlasprueba.com',
            'phone': '987654321'
        }
        # Intentamos buscar si ya existe
        existing = client.search_read('res.partner', domain=[['vat', '=', '20123456789']], fields=['id', 'name'])
        if existing:
            partner_id = existing[0]['id']
            print(f"Cliente ya existía: ID {partner_id} ({existing[0]['name']})")
        else:
            partner_id = client.create('res.partner', partner_vals)
            print(f"Cliente creado con éxito: ID {partner_id}")

        # 2. Productos y Stock
        print("\n[Inventario] Consultando productos y su stock disponible...")
        products = client.search_read(
            'product.product',
            domain=[['type', '=', 'product']], # Productos almacenables
            fields=['name', 'default_code', 'qty_available', 'lst_price'],
            limit=5
        )
        for prod in products:
            print(f"Producto: {prod.get('name')} | Código: {prod.get('default_code')} | Stock: {prod.get('qty_available')} | Precio: S/. {prod.get('lst_price')}")

        # 3. Ventas (Presupuestos B2B)
        print("\n[Ventas] Creando presupuesto B2B...")
        # Obtenemos un producto elegible para la venta
        sale_products = client.search_read(
            'product.product',
            domain=[['sale_ok', '=', True]],
            fields=['id', 'name', 'lst_price'],
            limit=1
        )
        if sale_products and partner_id:
            prod_id = sale_products[0]['id']
            prod_price = sale_products[0]['lst_price']
            
            order_vals = {
                'partner_id': partner_id,
                'order_line': [
                    (0, 0, {
                        'product_id': prod_id,
                        'product_uom_qty': 10, # 10 unidades
                        'price_unit': prod_price,
                    })
                ]
            }
            order_id = client.create('sale.order', order_vals)
            print(f"Presupuesto de Venta creado: ID {order_id}")
            
            # Consultar estado del presupuesto creado
            order = client.search_read('sale.order', domain=[['id', '=', order_id]], fields=['name', 'state', 'amount_total'])
            if order:
                print(f"Presupuesto: {order[0]['name']} | Estado: {order[0]['state']} | Total: S/. {order[0]['amount_total']}")
        else:
            print("No se encontraron productos aptos para la venta B2B.")

    except Exception as e:
        print(f"Error durante las operaciones: {e}")

if __name__ == "__main__":
    main()
