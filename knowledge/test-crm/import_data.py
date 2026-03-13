#!/usr/bin/env python3
import sys
from odoo_cli import OdooClient

def import_data():
    client = OdooClient()
    try:
        print("🔗 Conectando a Odoo...")
        client.connect()
        print("✅ Conexión exitosa.")

        # 1. Crear Proveedores
        print("👥 Creando proveedores...")
        suppliers = [
            {'name': 'Hotel Casa Andina Standard', 'is_company': True, 'comment': 'Hotel Cusco - Crédito 30 días'},
            {'name': 'Transportes El Chasqui', 'is_company': True, 'comment': 'Transporte - Minivan H-1'},
            {'name': 'Inca Rail', 'is_company': True, 'comment': 'Tren Tickets'},
            {'name': 'Carlos Mamani', 'is_company': False, 'comment': 'Guía Oficial - Inglés/Francés'},
            {'name': 'Restaurante Tunupa', 'is_company': True, 'comment': 'Restaurante Buffet - Valle Sagrado'},
        ]
        supplier_ids = {}
        for s in suppliers:
            sid = client.create('res.partner', s)
            supplier_ids[s['name']] = sid
            print(f"  - {s['name']} (ID: {sid})")

        # 2. Crear Productos Base (Servicios)
        print("📦 Creando productos base...")
        # Nota: En Odoo SaaS, 'type' para servicios suele ser 'service'.
        # Las rutas MTO y Buy se asignan después de buscar los IDs de las rutas.
        
        # Intentar buscar rutas Buy y MTO
        routes = client.search_read('stock.route', domain=[('name', 'ilike', 'Buy')], fields=['id'])
        buy_route_id = routes[0]['id'] if routes else None
        
        routes_mto = client.search_read('stock.route', domain=[('name', 'ilike', 'MTO')], fields=['id'])
        mto_route_id = routes_mto[0]['id'] if routes_mto else None

        route_ids = []
        if buy_route_id: route_ids.append(buy_route_id)
        if mto_route_id: route_ids.append(mto_route_id)

        products_base = [
            {'name': 'Noche Hab. Doble - Hotel 3* (Cusco)', 'type': 'service', 'list_price': 80.0, 'standard_price': 60.0, 'seller_ids': [[0, 0, {'partner_id': supplier_ids['Hotel Casa Andina Standard'], 'price': 60.0}]]},
            {'name': 'Traslado Aep - Hotel (Privado)', 'type': 'service', 'list_price': 20.0, 'standard_price': 10.0, 'seller_ids': [[0, 0, {'partner_id': supplier_ids['Transportes El Chasqui'], 'price': 10.0}]]},
            {'name': 'Ticket Tren Expedition (Ollanta - Mapi)', 'type': 'service', 'list_price': 75.0, 'standard_price': 65.0, 'seller_ids': [[0, 0, {'partner_id': supplier_ids['Inca Rail'], 'price': 65.0}]]},
            {'name': 'Gastos Administrativos / Fee', 'type': 'service', 'list_price': 30.0, 'standard_price': 0.0},
        ]
        
        prod_ids = {}
        for p in products_base:
            if route_ids and 'seller_ids' in p:
                p['route_ids'] = [[6, 0, route_ids]]
            
            pid = client.create('product.template', p)
            # Para la BoM necesitaremos el product.product ID
            variant = client.search_read('product.product', domain=[('product_tmpl_id', '=', pid)], fields=['id'], limit=1)
            prod_ids[p['name']] = variant[0]['id'] if variant else pid
            print(f"  - {p['name']} (ID Template: {pid})")

        # 3. Crear Paquete (Kit)
        print("🏗️ Creando Paquete Kit...")
        kit_vals = {
            'name': 'Paquete: Cusco Mágico & Machupicchu 4D/3N',
            'type': 'service',
            'list_price': 590.0,
            'description_sale': 'Programa detallado de 4 días que incluye alojamiento premium, boletos de tren y guiado especializado.'
        }
        kit_tmpl_id = client.create('product.template', kit_vals)
        kit_product = client.search_read('product.product', domain=[('product_tmpl_id', '=', kit_tmpl_id)], fields=['id'], limit=1)
        kit_id = kit_product[0]['id']

        # Crear BoM tipo Kit
        bom_vals = {
            'product_tmpl_id': kit_tmpl_id,
            'type': 'phantom', # 'phantom' es el nombre técnico del Kit en Odoo
            'bom_line_ids': [
                [0, 0, {'product_id': prod_ids['Noche Hab. Doble - Hotel 3* (Cusco)'], 'product_qty': 3}],
                [0, 0, {'product_id': prod_ids['Traslado Aep - Hotel (Privado)'], 'product_qty': 2}],
                [0, 0, {'product_id': prod_ids['Ticket Tren Expedition (Ollanta - Mapi)'], 'product_qty': 1}],
                [0, 0, {'product_id': prod_ids['Gastos Administrativos / Fee'], 'product_qty': 1}],
            ]
        }
        bom_id = client.create('mrp.bom', bom_vals)
        print(f"  - Kit Paquete creado con BoM ID: {bom_id}")

        # 4. Crear CRM Oportunidades
        print("📈 Creando oportunidades en CRM...")
        client_tanaka = client.create('res.partner', {'name': 'Familia Tanaka', 'email': 'tanaka@demo.com'})
        
        opp_vals = {
            'name': 'Familia Tanaka - Cusco Clásico',
            'partner_id': client_tanaka,
            'expected_revenue': 1180.0,
            'description': 'Requieren guía en japonés obligatoriamente.'
        }
        opp_id = client.create('crm.lead', opp_vals)
        print(f"  - Oportunidad creada: Familia Tanaka (ID: {opp_id})")

        print("🎉 ¡Importación completada exitosamente!")

    except Exception as e:
        print(f"❌ Error durante la importación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import_data()
