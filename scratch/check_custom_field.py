#!/usr/bin/env python3
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    print("Conectado a Odoo.")

    # 1. Check field
    print("\n--- Verificando el campo x_description_sale_html ---")
    fields = client.search_read(
        'ir.model.fields',
        domain=[['model', '=', 'product.template'], ['name', '=', 'x_description_sale_html']],
        fields=['id', 'name', 'field_description', 'ttype', 'state']
    )
    if fields:
        print(f"Campo encontrado: {fields[0]}")
    else:
        print("El campo x_description_sale_html NO existe en product.template.")

    # 2. Check view
    print("\n--- Verificando la vista heredada ---")
    views = client.search_read(
        'ir.ui.view',
        domain=[['model', '=', 'product.template'], ['name', '=', 'product_template_form_inherit_sale_html']],
        fields=['id', 'name', 'inherit_id', 'arch_db']
    )
    if views:
        print(f"Vista heredada encontrada (ID: {views[0]['id']}, Name: {views[0]['name']})")
        # Print a portion of arch_db
        print("Arch DB snippet:")
        print(views[0]['arch_db'][:400] + "...")
    else:
        print("La vista heredada 'product_template_form_inherit_sale_html' NO existe.")

    # 3. Check records
    print("\n--- Verificando cuántos productos tienen el campo completado ---")
    templates_with_html = client.search_read(
        'product.template',
        domain=[['x_description_sale_html', '!=', False], ['x_description_sale_html', '!=', '']],
        fields=['id', 'name'],
        limit=5
    )
    total_count = len(client.search_read(
        'product.template',
        domain=[['x_description_sale_html', '!=', False], ['x_description_sale_html', '!=', '']],
        fields=['id']
    ))
    print(f"Total de productos con x_description_sale_html completado: {total_count}")
    if templates_with_html:
        print("Ejemplos (primeros 5):")
        for t in templates_with_html:
            print(f"- [{t['id']}] {t['name']}")

if __name__ == "__main__":
    main()
