import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    print("--- Connected to Odoo. Beginning additional data population... ---")
    
    # 1. Search existing tour products to get their variant IDs
    tour_names = [
        "Tour Privado Machu Picchu Full Day",
        "Valle Sagrado de los Incas VIP",
        "City Tour Cusco y Ruinas Aledañas",
        "Camino Inca Clásico (4 Días / 3 Noches)"
    ]
    
    tour_ids = {}
    for name in tour_names:
        exist = client.search_read('product.template', [('name', '=', name)], fields=['id', 'product_variant_id'])
        if exist:
            t_id = exist[0]['id']
            variant_id = exist[0]['product_variant_id'][0] if exist[0]['product_variant_id'] else None
            tour_ids[name] = (t_id, variant_id)
        else:
            print(f"⚠️ Error: Tour '{name}' not found. Run populate_real_data.py first.")
            return

    # 2. Create New Clients
    print("\n[Step 2] Creating Additional Clients...")
    clients_data = [
        {
            'name': "Sarah Jenkins",
            'email': "sarah.jenkins@example.co.uk",
            'phone': "+44 20 7946 0958",
            'country_id': 231  # UK
        },
        {
            'name': "Jean Dupont",
            'email': "jean.dupont@example.fr",
            'phone': "+33 1 42 27 78 90",
            'country_id': 75   # France
        },
        {
            'name': "Lucas Silva",
            'email': "lucas.silva@example.com.br",
            'phone': "+55 11 98765-4321",
            'country_id': 31   # Brazil
        }
    ]
    
    client_ids = {}
    for c in clients_data:
        exist = client.search_read('res.partner', [('name', '=', c['name'])], fields=['id'])
        if exist:
            c_id = exist[0]['id']
            client_ids[c['name']] = c_id
            print(f"Client '{c['name']}' already exists (ID: {c_id})")
        else:
            vals = {
                'name': c['name'],
                'email': c['email'],
                'phone': c['phone'],
                'country_id': c['country_id'],
                'is_company': False
            }
            c_id = client.create('res.partner', vals)
            client_ids[c['name']] = c_id
            print(f"Created Client '{c['name']}' (ID: {c_id})")

    # Get pricelist (Tarifa Receptivo USD)
    pl = client.search_read('product.pricelist', [('name', '=', 'Tarifa Receptivo USD')], fields=['id'])
    pl_id = pl[0]['id'] if pl else None

    # 3. Create Additional CRM Opportunities and Quotations
    print("\n[Step 3] Creating Additional CRM Opportunities and Sale Orders...")
    
    # Case 4: Lucas Silva (Feb 2026)
    lead4_name = "Lucas Silva - Tour Privado Cusco Familiar"
    lead4_exist = client.search_read('crm.lead', [('name', '=', lead4_name)], fields=['id'])
    if not lead4_exist:
        lead4_id = client.create('crm.lead', {
            'name': lead4_name,
            'partner_id': client_ids["Lucas Silva"],
            'stage_id': 7,  # Confirmado (Adelanto)
            'date_deadline': "2026-02-28",
            'expected_revenue': 1880.00
        })
        print(f"Created CRM Lead: '{lead4_name}' (ID: {lead4_id})")
        
        # Create Quote
        so4_vals = {
            'partner_id': client_ids["Lucas Silva"],
            'date_order': "2026-02-28 10:00:00",
            'opportunity_id': lead4_id,
            'order_line': [
                (0, 0, {
                    'product_id': tour_ids["Tour Privado Machu Picchu Full Day"][1],
                    'product_uom_qty': 4,
                    'price_unit': 350.00
                }),
                (0, 0, {
                    'product_id': tour_ids["Valle Sagrado de los Incas VIP"][1],
                    'product_uom_qty': 4,
                    'price_unit': 120.00
                })
            ]
        }
        if pl_id:
            so4_vals['pricelist_id'] = pl_id
            
        so4_id = client.create('sale.order', so4_vals)
        print(f"Created Sale Order for Lucas Silva (ID: {so4_id}, Date: 2026-02-28)")
    else:
        print(f"Lead/Quote for Lucas Silva already exists.")

    # Case 5: Jean Dupont (Mar 2026)
    lead5_name = "Jean Dupont - Escapada Express Cusco"
    lead5_exist = client.search_read('crm.lead', [('name', '=', lead5_name)], fields=['id'])
    if not lead5_exist:
        lead5_id = client.create('crm.lead', {
            'name': lead5_name,
            'partner_id': client_ids["Jean Dupont"],
            'stage_id': 5,  # Nuevo Prospecto
            'date_deadline': "2026-03-28",
            'expected_revenue': 435.00
        })
        print(f"Created CRM Lead: '{lead5_name}' (ID: {lead5_id})")
        
        # Create Quote
        so5_vals = {
            'partner_id': client_ids["Jean Dupont"],
            'date_order': "2026-03-25 11:30:00",
            'opportunity_id': lead5_id,
            'order_line': [
                (0, 0, {
                    'product_id': tour_ids["Tour Privado Machu Picchu Full Day"][1],
                    'product_uom_qty': 1,
                    'price_unit': 350.00
                }),
                (0, 0, {
                    'product_id': tour_ids["City Tour Cusco y Ruinas Aledañas"][1],
                    'product_uom_qty': 1,
                    'price_unit': 85.00
                })
            ]
        }
        if pl_id:
            so5_vals['pricelist_id'] = pl_id
            
        so5_id = client.create('sale.order', so5_vals)
        print(f"Created Sale Order for Jean Dupont (ID: {so5_id}, Date: 2026-03-25)")
    else:
        print(f"Lead/Quote for Jean Dupont already exists.")

    # Case 6: Sarah Jenkins (May 2026)
    lead6_name = "Sarah Jenkins - Camino Inca de Lujo"
    lead6_exist = client.search_read('crm.lead', [('name', '=', lead6_name)], fields=['id'])
    if not lead6_exist:
        lead6_id = client.create('crm.lead', {
            'name': lead6_name,
            'partner_id': client_ids["Sarah Jenkins"],
            'stage_id': 6,  # Propuesta Enviada
            'date_deadline': "2026-05-20",
            'expected_revenue': 1560.00
        })
        print(f"Created CRM Lead: '{lead6_name}' (ID: {lead6_id})")
        
        # Create Quote
        so6_vals = {
            'partner_id': client_ids["Sarah Jenkins"],
            'date_order': "2026-05-12 15:45:00",
            'opportunity_id': lead6_id,
            'order_line': [
                (0, 0, {
                    'product_id': tour_ids["Camino Inca Clásico (4 Días / 3 Noches)"][1],
                    'product_uom_qty': 2,
                    'price_unit': 780.00
                })
            ]
        }
        if pl_id:
            so6_vals['pricelist_id'] = pl_id
            
        so6_id = client.create('sale.order', so6_vals)
        print(f"Created Sale Order for Sarah Jenkins (ID: {so6_id}, Date: 2026-05-12)")
    else:
        print(f"Lead/Quote for Sarah Jenkins already exists.")

    print("\n--- Additional data population successfully finished! ---")

if __name__ == '__main__':
    main()
