#!/usr/bin/env python3
"""
Template para scripts de knowledge/

Este template muestra cómo crear un script que interactúa con Odoo usando py-odoo-cli.
La IA puede usar este template como base para crear nuevos scripts en knowledge/<proyecto>/

Uso con Docker:
    docker-compose run --rm odoo-cli python knowledge/<proyecto>/mi_script.py
"""

import sys
import os
# Ajustar el path para importar odoo_cli desde la raíz del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient, OdooConfigError, OdooConnectionError, OdooFaultError

def main():
    """Función principal del script"""
    try:
        # Crear cliente y conectar
        client = OdooClient()
        uid = client.connect()
        print(f"✅ Conectado exitosamente. User ID: {uid}")
        
        # Aquí va tu lógica específica
        # Ejemplo: buscar registros
        # partners = client.search_read(
        #     'res.partner',
        #     domain=[['customer_rank', '>', 0]],
        #     fields=['name', 'email'],
        #     limit=10
        # )
        # 
        # for partner in partners:
        #     print(f"  - {partner['name']}: {partner.get('email', 'N/A')}")
        
        print("✅ Script ejecutado exitosamente")
        
    except OdooConfigError as e:
        print(f"❌ Error de configuración: {e}")
        print("   Verifica que tu archivo .env esté configurado correctamente")
        sys.exit(1)
    except OdooConnectionError as e:
        print(f"❌ Error de conexión: {e}")
        print("   Verifica tus credenciales y que Odoo esté accesible")
        sys.exit(1)
    except OdooFaultError as e:
        print(f"❌ Error de Odoo: {e.fault_string}")
        if e.fault_code:
            print(f"   Código de error: {e.fault_code}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
