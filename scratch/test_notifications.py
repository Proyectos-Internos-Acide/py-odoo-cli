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

# 1. Info del Lead 1857
lead = models.execute_kw(DB, uid, PASS, 'crm.lead', 'read', [[1857]], {'fields': ['name', 'user_id', 'team_id', 'message_follower_ids']})
print("Lead 1857:", lead)

# 2. Grupos de los usuarios
users = models.execute_kw(DB, uid, PASS, 'res.users', 'read', [[2, 5, 9, 13]], {'fields': ['login', 'groups_id']})
for u in users:
    groups = models.execute_kw(DB, uid, PASS, 'res.groups', 'read', [u['groups_id']], {'fields': ['name', 'full_name']})
    # Filter only sales related groups to see their CRM access level
    sales_groups = [g['full_name'] for g in groups if 'Sales' in g.get('full_name', '') or 'Ventas' in g.get('full_name', '')]
    print(f"User {u['login']} CRM Access: {sales_groups}")
