#!/usr/bin/env python3
import sys
import os
import base64
import time

# Ajustar el path para importar odoo_cli desde la raíz del proyecto
sys.path.insert(0, os.path.abspath('.'))

from odoo_cli import OdooClient, OdooConfigError, OdooConnectionError, OdooFaultError

def main():
    try:
        client = OdooClient()
        uid = client.connect()
        print(f"✅ Conectado como User ID: {uid}")

        # 1. Instalar Módulos
        for module_name in ['crm', 'mrp']:
            module = client.search_read('ir.module.module', [['name', '=', module_name]], ['state'])
            if module and module[0]['state'] != 'installed':
                print(f"📦 Instalando módulo: {module_name}...")
                client.execute('ir.module.module', 'button_immediate_install', [module[0]['id']])
                # Odoo suele reiniciar o requiere tiempo tras instalación inmediata
                time.sleep(5) 
            else:
                print(f"✅ Módulo {module_name} ya está instalado.")

        # 2. Configurar Divisas
        usd = client.search_read('res.currency', [['name', '=', 'USD']], ['active'])
        if not usd:
            # Buscar si está inactivo (usando execute para pasar el contexto)
            print("🔍 Buscando moneda USD inactiva...")
            usd_inactive = client.execute('res.currency', 'search_read', [['name', '=', 'USD']], fields=['active'], context={'active_test': False})
            if usd_inactive:
                print("💵 Activando moneda USD...")
                client.write('res.currency', [usd_inactive[0]['id']], {'active': True})
                usd_id = usd_inactive[0]['id']
            else:
                print("❌ No se encontró la moneda USD.")
                return
        else:
            usd_id = usd[0]['id']
            print("✅ Moneda USD ya está activa.")

        # 3. Listas de Precios
        pen_id = client.search_read('res.currency', [['name', '=', 'PEN']], ['id'])[0]['id']
        
        pricelists = [
            {'name': 'Tarifa Receptivo USD', 'currency_id': usd_id},
            {'name': 'Tarifa Nacional PEN', 'currency_id': pen_id}
        ]
        
        plist_ids = {}
        for pl in pricelists:
            existing = client.search_read('product.pricelist', [['name', '=', pl['name']]], ['id'])
            if not existing:
                print(f"🏷️ Creando lista de precios: {pl['name']}...")
                id_ = client.create('product.pricelist', pl)
                plist_ids[pl['name']] = id_
            else:
                plist_ids[pl['name']] = existing[0]['id']
                print(f"✅ Lista de precios {pl['name']} ya existe.")

        # 4. Maestro de Productos
        base_services = ["Ticket Machupicchu", "Traslado", "Guía"]
        service_ids = {}
        for s in base_services:
            existing = client.search_read('product.product', [['name', '=', s]], ['id'])
            if not existing:
                print(f"🛠️ Creando servicio base: {s}...")
                id_ = client.create('product.product', {
                    'name': s,
                    'type': 'service',
                    'list_price': 50.0 # Precio base referencial
                })
                service_ids[s] = id_
            else:
                service_ids[s] = existing[0]['id']

        # Pack Imperial
        pack_existing = client.search_read('product.product', [['name', '=', 'Pack Imperial']], ['id'])
        if not pack_existing:
            print("📦 Creando Pack Imperial...")
            pack_id = client.create('product.product', {
                'name': 'Pack Imperial',
                'type': 'service',
                'list_price': 150.0
            })
            # Crear BoM tipo Kit si MRP está disponible
            try:
                client.create('mrp.bom', {
                    'product_tmpl_id': client.search_read('product.product', [['id', '=', pack_id]], ['product_tmpl_id'])[0]['product_tmpl_id'][0],
                    'type': 'phantom', # Kit
                    'bom_line_ids': [
                        (0, 0, {'product_id': service_ids[s], 'product_qty': 1}) for s in base_services
                    ]
                })
                print("✅ BoM tipo Kit creada para Pack Imperial.")
            except Exception as e:
                print(f"⚠️ No se pudo crear la BoM: {e}")
        else:
            pack_id = pack_existing[0]['id']

        # 5. CRM Stages
        stages = ["Prospecto", "Cotización Enviada", "Confirmado (Adelanto)", "Ejecución", "Finalizado"]
        for idx, stage_name in enumerate(stages):
            existing = client.search_read('crm.stage', [['name', '=', stage_name]], ['id'])
            if not existing:
                print(f"📊 Creando etapa CRM: {stage_name}...")
                client.create('crm.stage', {'name': stage_name, 'sequence': idx + 1})

        # Tags
        tags = ["Turista Extranjero", "Turista Nacional"]
        tag_ids = {}
        for t in tags:
            existing = client.search_read('crm.tag', [['name', '=', t]], ['id'])
            if not existing:
                id_ = client.create('crm.tag', {'name': t})
                tag_ids[t] = id_
            else:
                tag_ids[t] = existing[0]['id']

        # 6. Datos de Prueba (Seed Data)
        customers = [
            {'name': 'Juan Perez', 'email': 'juan@example.com', 'country_id': client.search_read('res.country', [['code', '=', 'PE']], ['id'])[0]['id'], 'lang': 'es_PE'},
            {'name': 'John Doe', 'email': 'john@example.com', 'country_id': client.search_read('res.country', [['code', '=', 'US']], ['id'])[0]['id'], 'lang': 'en_US'}
        ]
        
        cust_ids = []
        for c in customers:
            existing = client.search_read('res.partner', [['email', '=', c['email']]], ['id'])
            if not existing:
                print(f"👤 Creando cliente: {c['name']}...")
                id_ = client.create('res.partner', c)
                cust_ids.append(id_)
            else:
                cust_ids.append(existing[0]['id'])

        # Adjuntar Pasaporte a John Doe
        passport_path = 'knowledge/machupicchu-exclusive-tours/Pasaporte_Ejemplo.pdf'
        if os.path.exists(passport_path):
            with open(passport_path, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode()
                client.create('ir.attachment', {
                    'name': 'Pasaporte_Ejemplo.pdf',
                    'datas': encoded,
                    'res_model': 'res.partner',
                    'res_id': cust_ids[1]
                })
                print(f"📎 Pasaporte adjuntado a {customers[1]['name']}.")

        # Leads (Opportunities)
        for i, cid in enumerate(cust_ids):
            existing = client.search_read('crm.lead', [['partner_id', '=', cid]], ['id'])
            if not existing:
                print(f"💡 Creando oportunidad para {customers[i]['name']}...")
                client.create('crm.lead', {
                    'name': f'Tour {customers[i]["name"]}',
                    'partner_id': cid,
                    'type': 'opportunity',
                    'tag_ids': [(6, 0, [tag_ids["Turista Receptivo" if i==1 else "Turista Nacional"]])] if "Turista Receptivo" in tag_ids else []
                })

        # 7. Flujo de Ventas
        # Crear Sales Order en USD para John Doe
        so_id = client.create('sale.order', {
            'partner_id': cust_ids[1],
            'pricelist_id': plist_ids['Tarifa Receptivo USD'],
            'order_line': [
                (0, 0, {'product_id': pack_id, 'product_uom_qty': 1}),
                (0, 0, {'product_id': service_ids["Guía"], 'product_uom_qty': 1})
            ]
        })
        print(f"📝 Sales Order creada (ID: {so_id}). Confirmando...")
        client.execute('sale.order', 'action_confirm', [so_id])

        # Obtener o Crear Factura
        sale_order = client.search_read('sale.order', [['id', '=', so_id]], ['invoice_ids'])[0]
        if not sale_order['invoice_ids']:
            print("🧾 Creando Factura...")
            wizard_inv_id = client.execute('sale.advance.payment.inv', 'create', {
                'sale_order_ids': [(6, 0, [so_id])],
                'advance_payment_method': 'delivered',
            })
            client.execute('sale.advance.payment.inv', 'create_invoices', [wizard_inv_id])
            sale_order = client.search_read('sale.order', [['id', '=', so_id]], ['invoice_ids'])[0]
        
        inv_id = sale_order['invoice_ids'][0]
        invoice = client.search_read('account.move', [['id', '=', inv_id]], ['state', 'amount_total', 'payment_state'])[0]
        
        if invoice['state'] == 'draft':
            print(f"🧾 Factura creada (ID: {inv_id}). Publicando...")
            client.execute('account.move', 'action_post', [inv_id])
            invoice = client.search_read('account.move', [['id', '=', inv_id]], ['state', 'amount_total', 'payment_state'])[0]

        # Registrar Pago Parcial (Adelanto)
        if invoice['payment_state'] == 'not_paid':
            print("💰 Registrando pago parcial...")
            half_payment = invoice['amount_total'] / 2
            
            # Usar el wizard de pago
            wizard_id = client.execute('account.payment.register', 'create', {
                'payment_date': time.strftime('%Y-%m-%d'),
                'amount': half_payment,
                'communication': f'Adelanto SO {so_id}',
                'journal_id': client.search_read('account.journal', [['type', 'in', ['bank', 'cash']]], ['id'])[0]['id']
            }, context={'active_model': 'account.move', 'active_ids': [inv_id]})
            client.execute('account.payment.register', 'action_create_payments', [wizard_id])
        else:
            print(f"✅ La factura ya tiene pagos registrados (Estado: {invoice['payment_state']}).")
        
        print("✅ Implementación completada con éxito.")

    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
