import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from odoo_cli.client import OdooClient
from odoo_cli.exceptions import OdooClientError

def main():
    try:
        client = OdooClient()
        client.connect()
        
        # 1. Update Company Ubigeo (assuming we will update the zip statically once known)
        ubigeo = "040101" # Arequipa - Arequipa - Arequipa. (El usuario uso el CP 04002)
        companies = client.search_read('res.company', limit=1)
        if companies and ubigeo != "REPLACE_ME":
            c_id = companies[0]['id']
            client.write('res.company', [c_id], {'zip': ubigeo})
            print(f"✅ Ubigeo actualizado a {ubigeo} en la compañía principal.")
            
        # 2. Setup F001 and B001 Journals
        print("\n🔍 Buscando diarios existentes para evitar duplicados...")
        existing = client.search_read('account.journal', domain=[('code', 'in', ['F001', 'B001'])], fields=['code'])
        existing_codes = [j['code'] for j in existing]
        
        if 'F001' not in existing_codes:
            # Factura type might require l10n_latam_use_documents in newer versions, 
            # let's write basic sale journal configuration
            vals_f001 = {
                'name': 'Facturas Electrónicas',
                'code': 'F001',
                'type': 'sale',
                'refund_sequence': True,
                # For peruvian localization, usually checking l10n_latam_use_documents is needed, 
                # but depending on saas~19.2 it's handled by EDI modules implicitly.
            }
            try:
                # Intenta crear con facturas LATAM habilitado
                vals_f001['l10n_latam_use_documents'] = True
                f001_id = client.create('account.journal', vals_f001)
            except Exception as e:
                # Si falla, crea sin el campo específico
                vals_f001.pop('l10n_latam_use_documents', None)
                f001_id = client.create('account.journal', vals_f001)
            print(f"✅ Diario 'Facturas Electrónicas' creado (código F001, ID: {f001_id})")
        else:
            print("⚠️ El diario F001 ya existe.")
            
        if 'B001' not in existing_codes:
            vals_b001 = {
                'name': 'Boletas Electrónicas',
                'code': 'B001',
                'type': 'sale',
                'refund_sequence': True,
            }
            try:
                vals_b001['l10n_latam_use_documents'] = True
                b001_id = client.create('account.journal', vals_b001)
            except Exception as e:
                vals_b001.pop('l10n_latam_use_documents', None)
                b001_id = client.create('account.journal', vals_b001)
            print(f"✅ Diario 'Boletas Electrónicas' creado (código B001, ID: {b001_id})")
        else:
            print("⚠️ El diario B001 ya existe.")

    except OdooClientError as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
