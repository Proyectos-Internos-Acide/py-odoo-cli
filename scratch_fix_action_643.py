import sys
sys.path.insert(0, 'knowledge/wayki-trek-develop/29_custom_quote_app')
from odoo_cli import OdooClient
client = OdooClient()
client.connect()

action_code = r"""if record.email_from:
    partner = record.partner_id
    if not partner:
        partner = env['res.partner'].search([('email', '=ilike', record.email_from.strip())], limit=1)
        if not partner:
            partner = env['res.partner'].create({
                'name': record.contact_name or record.name or 'Cliente',
                'email': record.email_from,
            })
        record.write({'partner_id': partner.id})

    # Extraer texto plano sin usar re (no disponible en safe_eval)
    desc_raw = str(record.description or '')
    chars = []
    in_tag = False
    for ch in desc_raw:
        if ch == '<':
            in_tag = True
        elif ch == '>':
            in_tag = False
        elif not in_tag:
            chars.append(ch)
    desc_text = ''.join(chars).strip()
    desc_text = desc_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp;', ' ').replace('&#39;', "'")

    if record.user_id and record.user_id.email:
        email_from = record.user_id.name + ' <' + record.user_id.email + '>'
    else:
        email_from = 'Wayki Trek <coordinator@waykitrek.net>'

    nombre = partner.name

    lineas = [
        'Estimado/a ' + nombre + ',',
        '',
        'Agradecemos su interes en realizar un tour con nosotros.',
        'Hemos recibido los detalles de su solicitud:',
        '',
        desc_text,
        '',
        'Un miembro de nuestro equipo se pondra en contacto con usted a la brevedad.',
        '',
        'Atentamente,',
        'El equipo de Wayki Trek',
    ]
    cuerpo_texto = '\n'.join(lineas)
    cuerpo_html = '<pre style="font-family: Arial, sans-serif; font-size:14px; white-space: pre-wrap;">' + cuerpo_texto + '</pre>'

    # body_html -> para el email SMTP (lo que llega al cliente)
    # body      -> para el Chatter de Odoo (lo que se muestra en el historial)
    mail = env['mail.mail'].create({
        'subject': record.name,
        'email_from': email_from,
        'body_html': cuerpo_html,
        'body': cuerpo_html,
        'model': 'crm.lead',
        'res_id': record.id,
        'recipient_ids': [(4, partner.id)],
    })
    mail.send()
"""

client.write('ir.actions.server', [643], {'code': action_code.strip()})
print('Accion 643 actualizada: body Y body_html correctamente configurados.')
