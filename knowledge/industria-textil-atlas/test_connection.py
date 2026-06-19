#!/usr/bin/env python3
"""
Test de conexión para Industria Textil Atlas E.I.R.L.
"""

import sys
import os
# Ajustar el path para importar odoo_cli desde la raíz del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient, OdooConfigError, OdooConnectionError, OdooFaultError

def main():
    try:
        print("🔌 Inicializando cliente de Odoo...")
        client = OdooClient()
        uid = client.connect()
        print(f"✅ Conexión establecida con éxito.")
        print(f"   User ID en Odoo: {uid}")
        print(f"   Base de Datos: {client.db}")
        print(f"   URL: {client._base_url}")
        
        print("\n📊 Consultando información básica del sistema...")
        # Obtener información de la moneda de la compañía
        currencies = client.search_read(
            'res.currency',
            domain=[],
            fields=['name', 'symbol', 'active']
        )
        active_currencies = [c for c in currencies if c.get('active')]
        print(f"✅ Monedas activas encontradas ({len(active_currencies)}):")
        for curr in active_currencies:
            print(f"   - {curr['name']} ({curr['symbol']})")

    except OdooConfigError as e:
        print(f"❌ Error de configuración: {e}")
        sys.exit(1)
    except OdooConnectionError as e:
        print(f"❌ Error de conexión: {e}")
        sys.exit(1)
    except OdooFaultError as e:
        print(f"❌ Error de Odoo: {e.fault_string}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
