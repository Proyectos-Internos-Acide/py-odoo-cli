#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    # 1. Get model 'product.template'
    print("Searching for model 'product.template'...")
    model_ids = client.search_read('ir.model', domain=[['model', '=', 'product.template']], fields=['id'])
    if not model_ids:
        raise RuntimeError("No se encontró el modelo 'product.template'.")
    model_id = model_ids[0]['id']
    print(f"Found product.template model ID: {model_id}")

    # 2. Ensure field 'x_description_sale_html' exists
    field_name = 'x_description_sale_html'
    existing_fields = client.search_read('ir.model.fields', domain=[['model', '=', 'product.template'], ['name', '=', field_name]], fields=['id'])

    if not existing_fields:
        print(f"Creating custom HTML field '{field_name}'...")
        field_vals = {
            'model_id': model_id,
            'name': field_name,
            'field_description': 'Descripción de Venta (Diseño)',
            'ttype': 'html',          # HTML type field
            'state': 'manual',        # Custom field
            'translate': True,        # Enable translations
        }
        field_id = client.create('ir.model.fields', field_vals)
        print(f"Field created successfully with ID: {field_id}")
    else:
        print(f"Field '{field_name}' already exists.")

    # 3. Find parent view
    print("Searching for parent form view of 'product.template'...")
    # Try to find the specific sales inherited form view first
    parent_views = client.search_read(
        'ir.ui.view',
        domain=[['model', '=', 'product.template'], ['name', '=', 'product.template.form.inherit.sale'], ['type', '=', 'form']],
        fields=['id', 'name']
    )
    
    if parent_views:
        parent_view_id = parent_views[0]['id']
        print(f"Using inherited form view: {parent_views[0]['name']} (ID: {parent_view_id})")
        arch_xml = f"""
    <data>
        <!-- Remove description_sale from its narrow half-width group -->
        <xpath expr="//group[@name='sale_description']" position="replace"/>
        <!-- Add both descriptions at page level for full width -->
        <xpath expr="//page[@name='sales']/group[@name='sale']" position="after">
            <group col="2" colspan="2" class="o_label_nowrap">
                <group string="Descripción Corta" col="1">
                    <field name="description_sale" nolabel="1" colspan="2" placeholder="This note will show up on sales orders."/>
                </group>
                <group string="Descripción para Web/Catálogo (Con Diseño)" col="1">
                    <field name="{field_name}" widget="html" class="oe_sandbox" nolabel="1" colspan="2"/>
                </group>
            </group>
        </xpath>
    </data>
    """
    else:
        # Fallback to the base common form
        parent_views = client.search_read(
            'ir.ui.view', 
            domain=[['model', '=', 'product.template'], ['inherit_id', '=', False], ['type', '=', 'form']], 
            fields=['id', 'name']
        )
        if not parent_views:
            parent_views = client.search_read(
                'ir.ui.view', 
                domain=[['model', '=', 'product.template'], ['type', '=', 'form']], 
                fields=['id', 'name']
            )
        if not parent_views:
            raise RuntimeError("No se encontró ninguna vista de formulario para 'product.template'.")
            
        parent_view_id = parent_views[0]['id']
        print(f"Using base form view: {parent_views[0]['name']} (ID: {parent_view_id})")
        
        arch_xml = f"""
    <data>
        <!-- Remove description_sale from its narrow half-width group -->
        <xpath expr="//group[@name='description']" position="replace"/>
        <!-- Add both descriptions at page level for full width -->
        <xpath expr="//page[@name='sales']/group[@name='sale']" position="after">
            <group col="2" colspan="2" class="o_label_nowrap">
                <group string="Descripción Corta" col="1">
                    <field name="description_sale" nolabel="1" colspan="2" placeholder="This note will show up on sales orders."/>
                </group>
                <group string="Descripción para Web/Catálogo (Con Diseño)" col="1">
                    <field name="{field_name}" widget="html" class="oe_sandbox" nolabel="1" colspan="2"/>
                </group>
            </group>
        </xpath>
    </data>
    """

    # 4. Ensure inherited view to place the HTML field
    view_xml_id = 'product_template_form_inherit_sale_html'

    existing_views = client.search_read('ir.ui.view', domain=[['name', '=', view_xml_id]], fields=['id'])
    view_vals = {
        'name': view_xml_id,
        'model': 'product.template',
        'inherit_id': parent_view_id,
        'type': 'form',
        'arch': arch_xml,
        'priority': 99,
    }

    if not existing_views:
        print(f"Creating inherited view '{view_xml_id}'...")
        view_id = client.create('ir.ui.view', view_vals)
        print(f"Inherited view created with ID: {view_id}")
    else:
        print(f"Inherited view '{view_xml_id}' already exists. Updating...")
        client.write('ir.ui.view', [existing_views[0]['id']], {'arch': arch_xml})
        print("Inherited view updated.")

    print("\n🎉 Proceso completado exitosamente.")

if __name__ == "__main__":
    main()
