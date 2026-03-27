import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from odoo_cli.client import OdooClient
from odoo_cli.exceptions import OdooClientError

def main():
    try:
        client = OdooClient()
        client.connect()
        
        print("\n🔍 Revisando configuración de la compañía principal...")
        companies = client.search_read('res.company', limit=1)
        
        if not companies:
            print("❌ No se encontró compañía.")
            return
            
        company = companies[0]
        
        pe_fields = {k: v for k, v in company.items() if 'l10n_pe' in k}
        
        # Diccionario con los campos clave y sus valores
        critical_data = {
            "Nombre": company.get("name"),
            "RUC (vat)": company.get("vat"),
            "Dirección configurada": bool(company.get("street") and company.get("city")),
            "Código de ubigeo (zip)": company.get("zip"),
            "Moneda base": company.get("currency_id"),
        }
        
        print("\n--- DATOS BÁSICOS ---")
        for k, v in critical_data.items():
            print(f"{k}: {v}")
            
        print("\n--- CONFIGURACIÓN EDI (Facturación SUNAT/OSE) ---")
        if not pe_fields:
            print("⚠️ No hay campos 'l10n_pe' en la compañía. Verifica si la localización está asignada a esta compañía.")
        else:
            for k, v in pe_fields.items():
                print(f"{k}: {v}")
                
        # Revisamos también si hay diarios contables de ventas con configuración de facturas
        journals = client.search_read('account.journal', domain=[('type', '=', 'sale')], fields=['name', 'code'])
        
        print("\n--- DIARIOS DE VENTA (Series de Facturación) ---")
        for j in journals:
            print(f"Diario: {j.get('name')} (Código: {j.get('code')})")
            for k, v in j.items():
                if 'l10n' in k:
                    print(f"  > {k}: {v}")

    except OdooClientError as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
