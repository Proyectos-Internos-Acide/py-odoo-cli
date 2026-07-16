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

# Restaurar el correo original de Américo (User ID 5, Partner 36)
try:
    # Escribir en res.users
    models.execute_kw(DB, uid, PASS, 'res.users', 'write', [[5], {'email': 'sales@waykitrek.net'}])
    print("Correo restaurado a sales@waykitrek.net en res.users")
    
    # También asegurar en res.partner por si acaso (el partner asociado al user 5 suele ser 36)
    partner_id = models.execute_kw(DB, uid, PASS, 'res.users', 'read', [[5]], {'fields': ['partner_id']})[0]['partner_id'][0]
    models.execute_kw(DB, uid, PASS, 'res.partner', 'write', [[partner_id], {'email': 'sales@waykitrek.net'}])
    print(f"Correo restaurado a sales@waykitrek.net en res.partner ({partner_id})")
except Exception as e:
    print(f"Error restaurando correo: {e}")
