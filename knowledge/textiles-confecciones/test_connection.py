import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from odoo_cli import OdooClient

def main():
    print("--- Probando Conexión para Textiles y Confecciones ---")
    try:
        client = OdooClient()
        uid = client.connect()
        print(f"¡Conexión Exitosa! User ID: {uid}")
        
        # Consultar información de la compañía
        print("\n--- Información de la Compañía ---")
        companies = client.search_read('res.company', domain=[], fields=['name', 'email', 'phone', 'currency_id'])
        for comp in companies:
            print(f"Nombre: {comp.get('name')}")
            print(f"Email: {comp.get('email')}")
            print(f"Moneda: {comp.get('currency_id')}")
            
    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    main()
