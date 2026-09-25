#!/usr/bin/env python3
"""
Script para crear un producto textil de prueba en Odoo
con todos los parámetros fiscales y de inventario para SUNAT.
"""
import sys
import os

# Asegurar path para importar odoo_cli
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from odoo_cli import OdooClient

def main():
    print("Conectando a Odoo (Textiles y Confecciones Atlas)...")
    client = OdooClient()
    uid = client.connect()
    print(f"Conexión exitosa con UID: {uid}")

    # Verificar si el producto ya existe por referencia interna
    existing = client.execute('product.template', 'search_read', [('default_code', '=', 'POL-ALG-001')], ['id', 'name'])
    if existing:
        print(f"El producto de prueba ya existe: ID {existing[0]['id']} - {existing[0]['name']}")
        return existing[0]['id']

    # Datos del producto textil de prueba
    product_vals = {
        'name': 'Polo Jersey 100% Algodón - Muestra Prueba',
        'default_code': 'POL-ALG-001',
        'list_price': 1.00,       # Precio de venta en PEN
        'standard_price': 0.50,   # Costo
        'type': 'consu',           # Bienes
        'is_storable': True,       # Producto almacenable (control de inventario)
        'sale_ok': True,
        'purchase_ok': True,
        'uom_id': 1,               # Units (Código SUNAT: NIU)
        'taxes_id': [(6, 0, [5])], # Impuesto de venta: VAT 18% (Código tributo 1000, Afectación 10)
        'unspsc_code_id': 49197,   # Código SUNAT/UNSPSC: 53101602 (Prendas de vestir / Polos / Camisas)
        'available_in_pos': True,  # Habilitado en Punto de Venta (POS)
        'description_sale': 'Polo de algodón jersey 20/1, cuello redondo, teñido reactivo. Producto de prueba para emisión SUNAT.'
    }

    print("Creando producto de prueba...")
    prod_id = client.execute('product.template', 'create', [product_vals])
    
    # Manejar si devuelve id entero o lista
    if isinstance(prod_id, list):
        prod_id = prod_id[0]

    print(f"\n¡Producto creado exitosamente! ID: {prod_id}")
    
    # Leer datos del producto creado
    prod_data = client.execute('product.template', 'read', [prod_id], [
        'name', 'default_code', 'list_price', 'is_storable', 'taxes_id', 'uom_id', 'unspsc_code_id', 'available_in_pos'
    ])[0]
    
    print("\n--- Ficha del Producto Creado ---")
    print(f"Nombre: {prod_data['name']}")
    print(f"SKU / Ref: {prod_data['default_code']}")
    print(f"Precio Venta: S/ {prod_data['list_price']:.2f}")
    print(f"Almacenable: {prod_data['is_storable']}")
    print(f"Unidad de Medida: {prod_data['uom_id'][1]} (SUNAT: NIU)")
    print(f"Impuestos: {prod_data['taxes_id']}")
    print(f"Código SUNAT (UNSPSC): {prod_data['unspsc_code_id']}")
    print(f"Disponible en POS: {prod_data['available_in_pos']}")

    return prod_id

if __name__ == '__main__':
    main()
