import os
from dotenv import load_dotenv
import xmlrpc.client
from datetime import datetime, timedelta

load_dotenv()

URL = os.getenv("ODOO_URL")
DB = os.getenv("ODOO_DB")
USER = os.getenv("ODOO_USER")
PASS = os.getenv("ODOO_PASSWORD")

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

print("Buscando los últimos mensajes de WhatsApp que han entrado a la base de datos de Odoo...")
try:
    messages = models.execute_kw(DB, uid, PASS, 'whatsapp.message', 'search_read', 
        [[]], 
        {'fields': ['id', 'create_date', 'mobile_number', 'body', 'message_type', 'state'], 'limit': 10, 'order': 'id desc'})
    
    if not messages:
        print("No se encontró NINGÚN mensaje de WhatsApp en la base de datos.")
    else:
        for m in messages:
            print(f"ID: {m['id']} | Fecha: {m['create_date']} | Tipo: {m['message_type']} | Estado: {m['state']} | Número: {m['mobile_number']} | Texto: {m.get('body')}")
except Exception as e:
    print(f"Error al leer whatsapp.message: {e}")


print("\nBuscando Oportunidades (Leads) creados hoy con 'WhatsApp' en el nombre...")
try:
    today_str = (datetime.utcnow() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
    leads = models.execute_kw(DB, uid, PASS, 'crm.lead', 'search_read',
        [[('create_date', '>=', today_str), ('name', 'ilike', 'WhatsApp')]],
        {'fields': ['id', 'name', 'phone', 'create_date'], 'order': 'id desc', 'limit': 5})
    
    if leads:
        for l in leads:
            print(f"Lead ID: {l['id']} | Nombre: {l['name']} | Teléfono: {l['phone']} | Creado: {l['create_date']}")
    else:
        print("No se encontraron leads creados por WhatsApp recientemente.")
except Exception as e:
    print(f"Error al leer crm.lead: {e}")

