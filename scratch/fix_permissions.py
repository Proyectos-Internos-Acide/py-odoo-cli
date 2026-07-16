import os
from dotenv import load_dotenv
import xmlrpc.client

load_dotenv()

URL = os.getenv("ODOO_URL")
DB = os.getenv("ODOO_DB")
USER = os.getenv("ODOO_USER")
PASS = os.getenv("ODOO_PASSWORD")

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

# Buscar IDs de los grupos de ventas
all_documents_group_ext = models.execute_kw(DB, uid, PASS, 'ir.model.data', 'search_read', 
    [[('module', '=', 'sales_team'), ('name', '=', 'group_sale_salesman_all_leads')]], 
    {'fields': ['res_id']})

own_documents_group_ext = models.execute_kw(DB, uid, PASS, 'ir.model.data', 'search_read', 
    [[('module', '=', 'sales_team'), ('name', '=', 'group_sale_salesman')]], 
    {'fields': ['res_id']})

if all_documents_group_ext and own_documents_group_ext:
    all_docs_id = all_documents_group_ext[0]['res_id']
    own_docs_id = own_documents_group_ext[0]['res_id']
    print(f"All Docs Group ID: {all_docs_id}")
    print(f"Own Docs Group ID: {own_docs_id}")
    
    # Descubrir el nombre del campo exacto para los grupos de ventas en res.users
    user_fields = models.execute_kw(DB, uid, PASS, 'res.users', 'fields_get', [], {'attributes': ['string', 'type', 'help']})
    print("Campos relacionados con permisos (in_group / sel_groups):")
    for f_name, f_info in user_fields.items():
        if f_name.startswith('in_group_') or f_name.startswith('sel_groups_'):
            if 'sale' in f_info.get('string', '').lower() or 'ventas' in f_info.get('string', '').lower() or str(all_docs_id) in f_name or str(own_docs_id) in f_name:
                print(f"{f_name}: {f_info.get('string')} ({f_info.get('type')})")
