import sys
import os
import base64
sys.path.insert(0, os.path.abspath('.'))

from odoo_cli import OdooClient

def get_b64_image(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    return None

def main():
    client = OdooClient()
    client.connect()
    
    print("--- Connected to Odoo. Beginning data population... ---")
    
    # Paths to generated images in the artifacts directory
    img_dir = r"C:\Users\rogel\.gemini\antigravity-ide\brain\c2f25562-ad63-41ad-83d7-435c1f26c120"
    
    mp_img_path = os.path.join(img_dir, "machu_picchu_tour_1783358529560.png")
    sv_img_path = os.path.join(img_dir, "sacred_valley_tour_1783358540071.png")
    cc_img_path = os.path.join(img_dir, "cusco_city_tour_1783358550892.png")
    
    mp_b64 = get_b64_image(mp_img_path)
    sv_b64 = get_b64_image(sv_img_path)
    cc_b64 = get_b64_image(cc_img_path)
    
    # 1. Create Tours (Products)
    print("\n[Step 1] Creating Tour Products...")
    tours_data = [
        {
            'name': "Tour Privado Machu Picchu Full Day",
            'list_price': 350.00,
            'type': 'service',
            'image': mp_b64
        },
        {
            'name': "Valle Sagrado de los Incas VIP",
            'list_price': 120.00,
            'type': 'service',
            'image': sv_b64
        },
        {
            'name': "City Tour Cusco y Ruinas Aledañas",
            'list_price': 85.00,
            'type': 'service',
            'image': cc_b64
        },
        {
            'name': "Camino Inca Clásico (4 Días / 3 Noches)",
            'list_price': 780.00,
            'type': 'service',
            'image': sv_b64
        }
    ]
    
    tour_ids = {}
    for tour in tours_data:
        # Check if already exists
        exist = client.search_read('product.template', [('name', '=', tour['name'])], fields=['id', 'product_variant_id'])
        if exist:
            t_id = exist[0]['id']
            # Get the variant product.product ID
            variant_id = exist[0]['product_variant_id'][0] if exist[0]['product_variant_id'] else None
            if not variant_id:
                # Fallback search in product.product
                p_prod = client.search_read('product.product', [('product_tmpl_id', '=', t_id)], fields=['id'])
                variant_id = p_prod[0]['id'] if p_prod else None
            tour_ids[tour['name']] = (t_id, variant_id)
            print(f"Product '{tour['name']}' already exists (ID: {t_id}, Variant ID: {variant_id})")
        else:
            vals = {
                'name': tour['name'],
                'list_price': tour['list_price'],
                'type': tour['type']
            }
            if tour['image']:
                vals['image_1920'] = tour['image']
            
            t_id = client.create('product.template', vals)
            
            # Read variant ID
            tmpl_data = client.search_read('product.template', [('id', '=', t_id)], fields=['product_variant_id'])[0]
            variant_id = tmpl_data['product_variant_id'][0] if tmpl_data['product_variant_id'] else None
            if not variant_id:
                p_prod = client.search_read('product.product', [('product_tmpl_id', '=', t_id)], fields=['id'])
                variant_id = p_prod[0]['id'] if p_prod else None
                
            tour_ids[tour['name']] = (t_id, variant_id)
            print(f"Created Product '{tour['name']}' (ID: {t_id}, Variant ID: {variant_id})")

    # 2. Create Clients
    print("\n[Step 2] Creating Clients...")
    clients_data = [
        {
            'name': "Emily Watson",
            'email': "emily.watson@example.com",
            'phone': "+1 415 555 2671",
            'country_id': 233  # US
        },
        {
            'name': "Hans Müller",
            'email': "hans.mueller@example.com",
            'phone': "+49 89 2443 8990",
            'country_id': 57   # Germany
        },
        {
            'name': "Yuki Tanaka",
            'email': "yuki.tanaka@example.com",
            'phone': "+81 3 5555 0192",
            'country_id': 113  # Japan
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
    print(f"Pricelist ID: {pl_id}")

    # 3. Create CRM Opportunities and Quotations
    print("\n[Step 3] Creating CRM Opportunties and Sale Orders...")
    
    # Case 1: Emily Watson (Feb 2026)
    lead1_name = "Emily Watson - Viaje de Bodas Cusco & Machu Picchu"
    lead1_exist = client.search_read('crm.lead', [('name', '=', lead1_name)], fields=['id'])
    if not lead1_exist:
        lead1_id = client.create('crm.lead', {
            'name': lead1_name,
            'partner_id': client_ids["Emily Watson"],
            'stage_id': 6,  # Propuesta Enviada
            'date_deadline': "2026-02-25",
            'expected_revenue': 870.00
        })
        print(f"Created CRM Lead: '{lead1_name}' (ID: {lead1_id})")
        
        # Create Quote
        so1_vals = {
            'partner_id': client_ids["Emily Watson"],
            'date_order': "2026-02-15 14:30:00",
            'opportunity_id': lead1_id,
            'order_line': [
                (0, 0, {
                    'product_id': tour_ids["Tour Privado Machu Picchu Full Day"][1],
                    'product_uom_qty': 2,
                    'price_unit': 350.00
                }),
                (0, 0, {
                    'product_id': tour_ids["City Tour Cusco y Ruinas Aledañas"][1],
                    'product_uom_qty': 2,
                    'price_unit': 85.00
                })
            ]
        }
        if pl_id:
            so1_vals['pricelist_id'] = pl_id
            
        so1_id = client.create('sale.order', so1_vals)
        print(f"Created Sale Order for Emily Watson (ID: {so1_id}, Date: 2026-02-15)")
    else:
        print(f"Lead/Quote for Emily Watson already exists.")

    # Case 2: Hans Müller (Mar 2026)
    lead2_name = "Hans Müller - Aventura Camino Inca"
    lead2_exist = client.search_read('crm.lead', [('name', '=', lead2_name)], fields=['id'])
    if not lead2_exist:
        lead2_id = client.create('crm.lead', {
            'name': lead2_name,
            'partner_id': client_ids["Hans Müller"],
            'stage_id': 5,  # Nuevo Prospecto
            'date_deadline': "2026-03-20",
            'expected_revenue': 780.00
        })
        print(f"Created CRM Lead: '{lead2_name}' (ID: {lead2_id})")
        
        # Create Quote
        so2_vals = {
            'partner_id': client_ids["Hans Müller"],
            'date_order': "2026-03-10 09:15:00",
            'opportunity_id': lead2_id,
            'order_line': [
                (0, 0, {
                    'product_id': tour_ids["Camino Inca Clásico (4 Días / 3 Noches)"][1],
                    'product_uom_qty': 1,
                    'price_unit': 780.00
                })
            ]
        }
        if pl_id:
            so2_vals['pricelist_id'] = pl_id
            
        so2_id = client.create('sale.order', so2_vals)
        print(f"Created Sale Order for Hans Müller (ID: {so2_id}, Date: 2026-03-10)")
    else:
        print(f"Lead/Quote for Hans Müller already exists.")

    # Case 3: Yuki Tanaka (Apr 2026)
    lead3_name = "Yuki Tanaka - Tour Privado Cusco Completo"
    lead3_exist = client.search_read('crm.lead', [('name', '=', lead3_name)], fields=['id'])
    if not lead3_exist:
        lead3_id = client.create('crm.lead', {
            'name': lead3_name,
            'partner_id': client_ids["Yuki Tanaka"],
            'stage_id': 7,  # Confirmado (Adelanto)
            'date_deadline': "2026-04-15",
            'expected_revenue': 940.00
        })
        print(f"Created CRM Lead: '{lead3_name}' (ID: {lead3_id})")
        
        # Create Quote
        so3_vals = {
            'partner_id': client_ids["Yuki Tanaka"],
            'date_order': "2026-04-05 16:45:00",
            'opportunity_id': lead3_id,
            'order_line': [
                (0, 0, {
                    'product_id': tour_ids["Tour Privado Machu Picchu Full Day"][1],
                    'product_uom_qty': 2,
                    'price_unit': 350.00
                }),
                (0, 0, {
                    'product_id': tour_ids["Valle Sagrado de los Incas VIP"][1],
                    'product_uom_qty': 2,
                    'price_unit': 120.00
                })
            ]
        }
        if pl_id:
            so3_vals['pricelist_id'] = pl_id
            
        so3_id = client.create('sale.order', so3_vals)
        print(f"Created Sale Order for Yuki Tanaka (ID: {so3_id}, Date: 2026-04-05)")
    else:
        print(f"Lead/Quote for Yuki Tanaka already exists.")

    print("\n--- Data population successfully finished! ---")

if __name__ == '__main__':
    main()
