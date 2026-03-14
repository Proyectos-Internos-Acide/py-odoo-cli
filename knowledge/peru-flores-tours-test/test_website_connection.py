#!/usr/bin/env python3
"""
Script para listar los sitios web configurados en Odoo.
"""

import sys
import os

# Ajustar el path para importar odoo_cli desde la raíz del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient, OdooConfigError, OdooConnectionError, OdooFaultError

def main():
    try:
        client = OdooClient()
        uid = client.connect()
        print(f"✅ Conectado exitosamente. User ID: {uid}")
        
        print("\n--- Sitios Web Configurados ---")
        websites = client.search_read(
            'website',
            domain=[],
            fields=['name', 'domain', 'company_id'],
            limit=10
        )
        
        if not websites:
            print("No se encontraron registros en el modelo 'website'.")
        else:
            for w in websites:
                name = w.get('name', 'N/A')
                domain = w.get('domain') or 'Sin dominio'
                company = w.get('company_id')[1] if w.get('company_id') else 'N/A'
                print(f"🔹 {name} ({domain}) - Compañía: {company}")
        
        print("\n✅ Script ejecutado exitosamente")
        
    except OdooFaultError as e:
        if "Access Denied" in str(e) or "Access Error" in str(e):
            print(f"❌ Error de acceso: Es posible que el módulo 'website' no esté instalado o no tengas permisos.")
        else:
            print(f"❌ Error de Odoo: {e.fault_string}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
