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

emails = [
    'contactorogeris@gmail.com',
    'rogeliosanchez405@gmail.com',
    'rinfasanchez@gmail.com'
]

print("==================================================")
print("1. BUSCANDO EN CONTACTOS (res.partner)")
print("==================================================")
partners = models.execute_kw(DB, uid, PASS, 'res.partner', 'search_read',
    [[('email', 'in', emails)]],
    {'fields': ['id', 'name', 'email', 'phone', 'create_date']})

partner_ids = [p['id'] for p in partners]
for p in partners:
    print(f"ID: {p['id']} | Nombre: {p['name']} | Email: {p['email']} | Tel: {p['phone']} | Creado: {p['create_date']}")

if not partners:
    print("No se encontraron contactos directos con estos correos.")

print("\n==================================================")
print("2. BUSCANDO EN LEADS / OPORTUNIDADES (crm.lead)")
print("==================================================")
domain_leads = ['|', ('email_from', 'in', emails), ('partner_id', 'in', partner_ids)] if partner_ids else [('email_from', 'in', emails)]
leads = models.execute_kw(DB, uid, PASS, 'crm.lead', 'search_read',
    [domain_leads],
    {'fields': ['id', 'name', 'stage_id', 'user_id', 'email_from', 'partner_id', 'expected_revenue', 'create_date']})

lead_ids = [l['id'] for l in leads]
for l in leads:
    print(f"Lead ID: {l['id']} | Nombre: {l['name']} | Etapa: {l['stage_id'][1] if l['stage_id'] else 'N/A'} | Vendedor: {l['user_id'][1] if l['user_id'] else 'N/A'} | Email: {l['email_from']} | Partner: {l['partner_id']} | Creado: {l['create_date']}")

if not leads:
    print("No se encontraron Oportunidades/Leads.")

print("\n==================================================")
print("3. BUSCANDO EN ORDENES DE VENTA (sale.order)")
print("==================================================")
if partner_ids:
    sales = models.execute_kw(DB, uid, PASS, 'sale.order', 'search_read',
        [[('partner_id', 'in', partner_ids)]],
        {'fields': ['id', 'name', 'state', 'amount_total', 'date_order', 'partner_id']})
    for s in sales:
        print(f"SO ID: {s['id']} | Número: {s['name']} | Estado: {s['state']} | Total: ${s['amount_total']} | Partner: {s['partner_id']} | Fecha: {s['date_order']}")
    if not sales:
        print("No se encontraron Órdenes de Venta para estos contactos.")
else:
    print("No hay contactos encontrados para buscar Órdenes de Venta.")

print("\n==================================================")
print("4. BUSCANDO CORREOS Y MENSAJES (mail.message)")
print("==================================================")
domain_messages = ['|', ('email_from', 'in', emails), ('partner_ids', 'in', partner_ids)] if partner_ids else [('email_from', 'in', emails)]
messages = models.execute_kw(DB, uid, PASS, 'mail.message', 'search_read',
    [domain_messages],
    {'fields': ['id', 'date', 'email_from', 'subject', 'model', 'res_id'], 'limit': 15, 'order': 'id desc'})

for m in messages:
    print(f"Msg ID: {m['id']} | Fecha: {m['date']} | De: {m['email_from']} | Asunto: {m['subject']} | Modelo: {m['model']} (#{m['res_id']})")

if not messages:
    print("No se encontraron mensajes registrados para estos correos.")

