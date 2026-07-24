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

print("Revisando campos del modelo whatsapp.message...")
try:
    fields = models.execute_kw(DB, uid, PASS, 'whatsapp.message', 'fields_get', [], {'attributes': ['type', 'string']})
    for f in ['body', 'author_id', 'mail_message_id', 'mobile_number', 'wa_account_id', 'state', 'message_type']:
        if f in fields:
            print(f"- {f}: {fields[f]['type']} ({fields[f]['string']})")
except Exception as e:
    print(f"Error al leer whatsapp.message: {e}")

print("\nRevisando campos del modelo discuss.channel (filtrando type=whatsapp)...")
try:
    fields_chan = models.execute_kw(DB, uid, PASS, 'discuss.channel', 'fields_get', [], {'attributes': ['type']})
    print(f"Campos clave en discuss.channel: channel_type: {fields_chan.get('channel_type', {}).get('type')}")
    
    # Buscar un canal reciente de WSP
    channels = models.execute_kw(DB, uid, PASS, 'discuss.channel', 'search_read', 
        [[('channel_type', '=', 'whatsapp')]], 
        {'fields': ['name', 'whatsapp_number', 'whatsapp_mail_message_id'], 'limit': 1})
    if channels:
        print(f"Ejemplo canal WSP: {channels[0]}")
    else:
        print("No se encontraron canales de WSP recientes.")
except Exception as e:
    print(f"Error al leer discuss.channel: {e}")
