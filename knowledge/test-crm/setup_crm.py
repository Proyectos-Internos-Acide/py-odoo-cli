#!/usr/bin/env python3
import sys
import time
from odoo_cli import OdooClient

def setup_crm():
    client = OdooClient()
    try:
        print("🔗 Conectando a Odoo...")
        client.connect()
        print("✅ Conexión exitosa.")

        # Módulos necesarios
        modules_to_install = [
            'crm', 
            'sale_management', 
            'purchase', 
            'stock', 
            'mrp'
        ]

        # Buscar módulos y sus IDs
        print(f"📦 Verificando módulos: {', '.join(modules_to_install)}...")
        domain = [('name', 'in', modules_to_install), ('state', '!=', 'installed')]
        modules = client.search_read('ir.module.module', domain=domain, fields=['name', 'state'])

        if not modules:
            print("🚀 Todos los módulos ya están instalados.")
        else:
            module_ids = [m['id'] for m in modules]
            module_names = [m['name'] for m in modules]
            print(f"🛠️ Instalando módulos pendientes: {', '.join(module_names)}...")
            
            # Instalar módulos
            client.execute('ir.module.module', 'button_immediate_install', module_ids)
            print("✨ Instalación completada (o iniciada en segundo plano).")

        # Activar configuraciones específicas (opcional, vía parámetros del sistema o res.config.settings)
        # Por ahora, nos aseguramos de que los módulos estén arriba.

    except Exception as e:
        print(f"❌ Error durante la configuración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_crm()
