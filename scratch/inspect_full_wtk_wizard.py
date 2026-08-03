import sys
import os
import json
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def main():
    client = OdooClient()
    client.connect()

    models_to_inspect = [
        'x_wtk_custom_quote_wizard',
        'x_wtk_custom_quote_wizard_line',
        'x_wtk_custom_quote_wizard_service_line',
        'x_wtk_custom_service_template',
        'x_wtk_service_category',
        'x_wtk_service_type',
        'x_tour_pax_type',
        'x_tour_pax_price',
        'x_tour_group_price',
        'x_tour_addon',
    ]

    # 1. Inspect Fields of each model
    print_section("1. MODEL FIELDS DEFINITIONS (ir.model.fields)")
    for model_name in models_to_inspect:
        fields = client.search_read(
            'ir.model.fields',
            domain=[('model', '=', model_name)],
            fields=['name', 'field_description', 'ttype', 'relation', 'required', 'readonly', 'selection', 'compute', 'depends', 'on_delete']
        )
        print(f"\nModel: {model_name} ({len(fields)} fields)")
        print("-" * 60)
        for f in fields:
            rel_str = f" -> {f['relation']}" if f['relation'] else ""
            compute_str = f" [compute: {f['compute']}]" if f.get('compute') else ""
            depends_str = f" [depends: {f['depends']}]" if f.get('depends') else ""
            print(f"  • {f['name']} ({f['ttype']}{rel_str}): '{f['field_description']}' required={f['required']} readonly={f['readonly']}{compute_str}{depends_str}")

    # 2. Check custom fields on sale.order and sale.order.line
    print_section("2. CUSTOM FIELDS ON sale.order AND sale.order.line")
    for main_model in ['sale.order', 'sale.order.line', 'product.template', 'product.product']:
        custom_fields = client.search_read(
            'ir.model.fields',
            domain=[('model', '=', main_model), ('name', '=like', 'x_%')],
            fields=['name', 'field_description', 'ttype', 'relation', 'required', 'readonly', 'compute', 'depends']
        )
        print(f"\nModel: {main_model} ({len(custom_fields)} custom x_ fields)")
        print("-" * 60)
        for f in custom_fields:
            rel_str = f" -> {f['relation']}" if f['relation'] else ""
            compute_str = f" [compute: {f['compute']}]" if f.get('compute') else ""
            depends_str = f" [depends: {f['depends']}]" if f.get('depends') else ""
            print(f"  • {f['name']} ({f['ttype']}{rel_str}): '{f['field_description']}'{compute_str}{depends_str}")

    # 3. Views (ir.ui.view)
    print_section("3. VIEWS DEFINITIONS (ir.ui.view)")
    views = client.search_read(
        'ir.ui.view',
        domain=['|', '|', ('model', 'in', models_to_inspect), ('name', 'ilike', 'wtk'), ('name', 'ilike', 'custom_quote')],
        fields=['id', 'name', 'model', 'type', 'arch_db', 'priority', 'mode', 'inherit_id']
    )
    print(f"Found {len(views)} views.")
    for v in views:
        print(f"\nView ID: {v['id']} | Name: {v['name']} | Model: {v['model']} | Type: {v['type']}")
        print("Arch DB (XML snippet):")
        print(v['arch_db'])

    # 4. Server Actions (ir.actions.server)
    print_section("4. SERVER ACTIONS (ir.actions.server)")
    server_actions = client.search_read(
        'ir.actions.server',
        domain=['|', ('model_id.model', 'in', models_to_inspect), ('name', 'ilike', 'wtk')],
        fields=['id', 'name', 'model_id', 'state', 'code', 'crud_model_id']
    )
    print(f"Found {len(server_actions)} server actions.")
    for sa in server_actions:
        model_name = sa['model_id'][1] if sa['model_id'] else 'N/A'
        print(f"\nAction ID: {sa['id']} | Name: {sa['name']} | Model: {model_name} | State: {sa['state']}")
        if sa.get('code'):
            print("Python Code:")
            print(sa['code'])

    # 5. Window Actions (ir.actions.act_window)
    print_section("5. WINDOW ACTIONS (ir.actions.act_window)")
    act_windows = client.search_read(
        'ir.actions.act_window',
        domain=['|', ('res_model', 'in', models_to_inspect), ('name', 'ilike', 'wtk')],
        fields=['id', 'name', 'res_model', 'view_mode', 'target', 'domain', 'context']
    )
    print(f"Found {len(act_windows)} window actions.")
    for aw in act_windows:
        print(f"  • ID: {aw['id']} | Name: {aw['name']} | Target model: {aw['res_model']} | View mode: {aw['view_mode']} | Target: {aw['target']} | Context: {aw['context']}")

if __name__ == '__main__':
    main()
