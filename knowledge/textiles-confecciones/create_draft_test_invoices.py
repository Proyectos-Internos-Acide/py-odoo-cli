#!/usr/bin/env python3
"""
Script para crear borradores de prueba para Factura (F101-00000005)
y Boleta (B101-00000005) en Odoo.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from odoo_cli import OdooClient

def main():
    print("Conectando a Odoo (Textiles y Confecciones Atlas)...")
    client = OdooClient()
    uid = client.connect()
    print(f"Conexión exitosa con UID: {uid}")

    # Verificar si ya existen
    existing = client.execute('account.move', 'search_read', [('name', 'in', ['F101-00000005', 'B101-00000005'])], ['id', 'name', 'state', 'amount_total'])
    for e in existing:
        print(f"Comprobante existente: ID {e['id']} - {e['name']} (Estado: {e['state']})")

if __name__ == '__main__':
    main()
