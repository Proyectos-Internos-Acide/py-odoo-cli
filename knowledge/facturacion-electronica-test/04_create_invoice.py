import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from odoo_cli.client import OdooClient
from odoo_cli.exceptions import OdooClientError

def main():
    client = OdooClient()
    client.connect()
    
    try:
        # Buscar el diario F001
        journals = client.search_read('account.journal', domain=[('code', '=', 'F001')], limit=1)
        if not journals:
            print("❌ No se encontró el diario F001. Ejecuta primero 03_create_journals.py")
            return
        journal_id = journals[0]['id']
        
        # Buscar o crear un cliente de prueba
        partners = client.search_read('res.partner', domain=[('vat', '=', '20100047218')], limit=1) # RUC de Sunat o cliente de prueba
        if not partners:
            print("Creando cliente de prueba (SUNAT - 20100047218)...")
            partner_id = client.create('res.partner', {
                'name': 'SUPERINTENDENCIA NACIONAL DE ADUANAS Y DE ADMINISTRACION TRIBUTARIA',
                'vat': '20100047218',
                'l10n_latam_identification_type_id': 4, # Asumiendo RUC
                'country_id': 173, # PE
                'street': 'Av. Garcilaso de la Vega 1472',
                'city': 'Lima',
                'zip': '150101',
            })
        else:
            partner_id = partners[0]['id']
            
        print("Creando factura en borrador...")
        # Buscar producto
        products = client.search_read('product.product', domain=[('type', '=', 'service')], limit=1)
        if not products:
            p_id = client.create('product.product', {'name': 'Servicio Web de Pruebas', 'type': 'service', 'list_price': 100.0})
        else:
            p_id = products[0]['id']
            
        # Crear la factura
        invoice_vals = {
            'move_type': 'out_invoice',
            'journal_id': journal_id,
            'partner_id': partner_id,
            'invoice_line_ids': [(0, 0, {
                'product_id': p_id,
                'name': 'Servicios profesionales de integración EDI',
                'quantity': 1,
                'price_unit': 10.00,
            })]
        }
        
        invoice_id = client.create('account.move', invoice_vals)
        print(f"✅ Factura creada exitosamente en Odoo con ID: {invoice_id}")
        
        # Intentar validarla
        print("Procesando la factura para enviarla a SUNAT...")
        client.execute('account.move', 'action_post', [invoice_id])
        print("🚀 ¡Factura firmada/publicada! Revisa en tu Odoo si generó el XML exitosamente y lo envió.")

    except OdooClientError as e:
        print(f"❌ Error durante el proceso: {e}")

if __name__ == '__main__':
    main()
