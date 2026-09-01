import re
from odoo_cli.client import OdooClient

client = OdooClient()
a582 = client.search_read('ir.actions.server', [('id', '=', 582)], ['id', 'name', 'code'])[0]
curr_code = a582['code']

# Build the exact code replacement
replacement_code = """try:
    # --- AGREGADO ESPECIAL PARA EL FORMULARIO DE CONTACTO WEB ---
    # Interceptamos si el PHP de WordPress mando el texto directo en la descripcion
    if record.description and 'DETALLES DEL TOUR (FORMULARIO CUSTOM)' in record.description:
        raw_desc = str(record.description or '')
        record.write({'description': ''})

        # Extraer nombre del lead
        rec_name = str(record.name or '').strip()
        client_name = rec_name
        if client_name.lower().startswith('cliente:'):
            client_name = client_name[8:].strip()
        elif client_name.lower().startswith('cliente :'):
            client_name = client_name[9:].strip()

        # Limpiar cualquier tag HTML y convertir a texto plano limpio
        clean_text = raw_desc.replace('<br/>', '\\n').replace('<br />', '\\n').replace('<br>', '\\n')
        clean_text = re.sub(r'<[^>]+>', '', clean_text)
        lines = [l.strip() for l in clean_text.split('\\n') if l.strip()]

        result_lines = ['=== DETALLES DEL FORMULARIO DE CONTACTO ===', '']
        if client_name:
            result_lines.append('Cliente: ' + client_name)
        if record.email_from:
            result_lines.append('Email: ' + str(record.email_from))
        if record.phone:
            result_lines.append('Telefono: ' + str(record.phone))
        result_lines.append('')

        msg_block = []
        is_msg = False

        for line in lines:
            if 'DETALLES DEL TOUR' in line:
                continue
            if line.startswith('Mensaje:'):
                is_msg = True
                msg_val = line[8:].strip()
                if msg_val:
                    msg_block.append(msg_val)
            elif is_msg:
                msg_block.append(line)
            else:
                result_lines.append(line)

        if msg_block:
            result_lines.append('')
            result_lines.append('Mensaje:')
            result_lines.extend(msg_block)

        final_note = '\\n'.join(result_lines)

        def post_contact_msg():
            env['crm.lead'].browse(record.id).message_post(
                body=final_note, 
                message_type='comment', 
                subtype_xmlid='mail.mt_note'
            )
        env.cr.postcommit.add(post_contact_msg)
        
        payload_raw = ''
    else:
        # Leemos el payload del campo dedicado o de description
        payload_raw = record.x_wayki_sync_payload"""

# Find where 'else:\n        # Leemos el payload' is in curr_code
idx_else = curr_code.find("    else:\n        # Leemos el payload")
assert idx_else != -1, "Could not find 'else:' anchor in current code"

final_code = replacement_code + curr_code[idx_else + len("    else:\n        # Leemos el payload") - len("        # Leemos el payload"):]

# Test compilation
compile(final_code, '<string>', 'exec')
print("Compiled successfully!")

# Write to Odoo
res = client.write('ir.actions.server', [582], {'code': final_code})
print("Odoo update result:", res)
