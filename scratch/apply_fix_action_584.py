import sys
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

print(f"Conectado a {URL} DB {DB}")

# 1. Código mejorado para la Server Action 584 sin comillas en conflicto
new_sa_code = """if record.email_from:
    raw_from = str(record.email_from or '').strip()
    display_name = ''
    clean_email = raw_from.lower()

    if '<' in raw_from and '>' in raw_from:
        parts = raw_from.split('<')
        name_part = parts[0].replace('"', '').replace("'", "").strip()
        email_part = parts[1].split('>')[0].replace('"', '').replace("'", "").strip().lower()
        if name_part and '@' not in name_part:
            display_name = name_part
        if email_part:
            clean_email = email_part
    else:
        clean_email = raw_from.replace('"', '').replace("'", "").strip().lower()

    if '@' in clean_email and len(clean_email) > 4:
        # 2. Buscar si ya existe un Contacto con este correo limpio
        partner = env['res.partner'].search([('email', '=ilike', clean_email)], limit=1)
        if not partner:
            partner = env['res.partner'].search([('email', 'ilike', clean_email)], limit=1)

        if partner:
            # Si el contacto existe, lo enlazamos al Lead
            record.write({'partner_id': partner.id})
            
            # Si el contacto tenía de nombre el asunto o el correo, y ahora tenemos el nombre real del remitente, lo actualizamos
            if display_name and (partner.name == record.name or '@' in partner.name):
                partner.write({'name': display_name})
            if partner.email != clean_email and clean_email:
                partner.write({'email': clean_email})
        else:
            # 3. Determinar el nombre real del contacto (Prioridad: Display Name -> contact_name -> Nombre formateado del email)
            contact_name = display_name or (record.contact_name and record.contact_name.strip())
            
            if not contact_name:
                user_part = clean_email.split('@')[0]
                contact_name = user_part.replace('.', ' ').replace('_', ' ').replace('-', ' ').title()

            # Limpiar prefijos de etiquetas como [INTERNO] o "Cliente:"
            if contact_name.startswith('['):
                p_parts = contact_name.split(']', 1)
                if len(p_parts) > 1:
                    contact_name = p_parts[1].strip()

            if contact_name.lower().startswith('cliente:'):
                contact_name = contact_name[8:].strip()
            elif contact_name.lower().startswith('cliente :'):
                contact_name = contact_name[9:].strip()

            partner_vals = {
                'name': contact_name,
                'email': clean_email,
            }
            if record.phone:
                partner_vals['phone'] = record.phone

            new_partner = env['res.partner'].create(partner_vals)
            record.write({
                'partner_id': new_partner.id,
                'contact_name': contact_name
            })
"""

# 2. Actualizar la Server Action 584 en Odoo
action = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'read', [[584]], {'fields': ['id', 'name']})
if action:
    models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'write', [[584], {'code': new_sa_code}])
    print("✅ Acción de Servidor ID 584 ('Auto-Ligar Lead por Email') actualizada con éxito en Odoo.")

# 3. Analizar y corregir contactos existentes en res.partner
print("\n--- Analizando y corrigiendo contactos existentes en la base de datos ---")

leads = models.execute_kw(DB, uid, PASS, 'crm.lead', 'search_read',
    [[('email_from', '!=', False), ('partner_id', '!=', False)]],
    {'fields': ['id', 'name', 'email_from', 'contact_name', 'partner_id'], 'limit': 500})

fixed_count = 0
for lead in leads:
    raw_from = str(lead['email_from'] or '').strip()
    partner_id = lead['partner_id'][0]
    
    display_name = ''
    clean_email = raw_from.lower()
    if '<' in raw_from and '>' in raw_from:
        parts = raw_from.split('<')
        name_part = parts[0].replace('"', '').replace("'", "").strip()
        email_part = parts[1].split('>')[0].replace('"', '').replace("'", "").strip().lower()
        if name_part and '@' not in name_part:
            display_name = name_part
        if email_part:
            clean_email = email_part
    else:
        clean_email = raw_from.replace('"', '').replace("'", "").strip().lower()

    partner = models.execute_kw(DB, uid, PASS, 'res.partner', 'read', [[partner_id]], {'fields': ['id', 'name', 'email']})[0]
    p_name = partner['name']
    p_email = partner['email'] or ''

    needs_update = False
    new_vals = {}

    # Si el nombre del partner es igual al asunto del lead (lead['name']) y tenemos display_name o contact_name real
    target_name = display_name or lead.get('contact_name')
    if (p_name == lead['name'] or p_name == raw_from or '@' in p_name) and target_name:
        if target_name != p_name:
            new_vals['name'] = target_name
            needs_update = True

    # Si el email guardado en res.partner contiene corchetes o "Nombre <email>" en lugar de solo email
    if '<' in p_email or '>' in p_email or (clean_email and p_email != clean_email):
        if clean_email and clean_email != p_email:
            new_vals['email'] = clean_email
            needs_update = True

    if needs_update:
        print(f"Corrigiendo Contacto ID {partner_id}: Nombre actual='{p_name}' ({p_email}) -> Nuevos datos: {new_vals}")
        models.execute_kw(DB, uid, PASS, 'res.partner', 'write', [[partner_id], new_vals])
        fixed_count += 1

print(f"\n✅ Proceso completado con éxito. Contactos corregidos: {fixed_count}")
