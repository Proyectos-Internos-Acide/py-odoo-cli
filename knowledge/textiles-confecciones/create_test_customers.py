#!/usr/bin/env python3
"""
Script para crear clientes de prueba en Odoo para Factura (RUC) y Boleta (DNI)
con la localización peruana para SUNAT.
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

    # 1. Cliente para Factura (RUC)
    ruc_vals = {
        'name': 'COLEGIO MÉDICO DEL PERÚ',
        'vat': '20139589638',
        'l10n_latam_identification_type_id': 4, # RUC (código 6)
        'is_company': True,
        'country_id': 173,                      # Perú
        'street': 'Malecón de la Reserva N° 791',
        'city': 'Lima',
        'customer_rank': 1
    }

    # Verificar si ya existe por RUC
    existing_ruc = client.execute('res.partner', 'search_read', [('vat', '=', '20139589638')], ['id', 'name'])
    if existing_ruc:
        ruc_id = existing_ruc[0]['id']
        print(f"Cliente con RUC 20139589638 ya existe: ID {ruc_id} - {existing_ruc[0]['name']}")
    else:
        ruc_id = client.execute('res.partner', 'create', [ruc_vals])
        if isinstance(ruc_id, list):
            ruc_id = ruc_id[0]
        print(f"Cliente con RUC creado exitosamente: ID {ruc_id} - {ruc_vals['name']}")

    # 2. Cliente para Boleta (DNI)
    dni_vals = {
        'name': 'CLIENTE BOLETA PRUEBA',
        'vat': '72190044',
        'l10n_latam_identification_type_id': 5, # DNI (código 1)
        'is_company': False,
        'country_id': 173,                      # Perú
        'customer_rank': 1
    }

    # Verificar si ya existe por DNI
    existing_dni = client.execute('res.partner', 'search_read', [('vat', '=', '72190044')], ['id', 'name'])
    if existing_dni:
        dni_id = existing_dni[0]['id']
        print(f"Cliente con DNI 72190044 ya existe: ID {dni_id} - {existing_dni[0]['name']}")
    else:
        dni_id = client.execute('res.partner', 'create', [dni_vals])
        if isinstance(dni_id, list):
            dni_id = dni_id[0]
        print(f"Cliente con DNI creado exitosamente: ID {dni_id} - {dni_vals['name']}")

    print("\n--- Clientes Creados para Pruebas SUNAT ---")
    ruc_partner = client.execute('res.partner', 'read', [ruc_id], ['name', 'vat', 'l10n_latam_identification_type_id', 'is_company', 'street'])[0]
    dni_partner = client.execute('res.partner', 'read', [dni_id], ['name', 'vat', 'l10n_latam_identification_type_id', 'is_company'])[0]

    print("Cliente Factura (RUC):", ruc_partner)
    print("Cliente Boleta (DNI):", dni_partner)

if __name__ == '__main__':
    main()
