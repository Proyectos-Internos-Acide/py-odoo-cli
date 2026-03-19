import os
import base64
from odoo_cli import OdooClient, OdooFaultError, OdooExecutionError

def main():
    print("Iniciando script de configuración para Machu Picchu Exclusive Tours...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado exitosamente con ID de usuario: {uid}")

    # ===== PASO 1: LIMPIEZA CRM Y CONTACTOS =====
    print("\n[Paso 1] Limpieza de Leads y Contactos de Prueba")
    
    # 1.1 Limpiar Leads (Archivarlos o Eliminarlos)
    # Buscamos todos los leads para borrarlos, asumiendo que es una bd nueva
    leads = client.search_read('crm.lead', [], fields=['id'])
    if leads:
        lead_ids = [l['id'] for l in leads]
        print(f"Se encontraron {len(lead_ids)} Leads/Oportunidades. Intentando eliminar...")
        try:
            client.unlink('crm.lead', lead_ids)
            print("✅ Leads y Oportunidades eliminados.")
        except OdooFaultError:
            # Fallback a archivar si hay dependencias
            print("⚠️ No se pudieron eliminar (posibles dependencias). Archivando...")
            client.write('crm.lead', lead_ids, {'active': False})
            print("✅ Leads y Oportunidades archivados.")
    else:
        print("✅ No hay Leads por limpiar.")

    # 1.2 Archivar contactos demo (Azure, Deco, etc.)
    demo_names = ['Azure Interior', 'Deco Addict', 'Wood Corner', 'Ready Mat', 'Gemini Furniture']
    domain = ['|'] * (len(demo_names) - 1)
    for name in demo_names:
        domain.extend([('name', 'ilike', name)])
    
    contacts_to_archive = client.search_read('res.partner', domain, fields=['id', 'name'])
    if contacts_to_archive:
        contact_ids = [c['id'] for c in contacts_to_archive]
        print(f"Archivando contactos de demo: {[c['name'] for c in contacts_to_archive]}")
        client.write('res.partner', contact_ids, {'active': False})
        print("✅ Contactos demo archivados.")

    # ===== PASO 2: DIVISAS Y LISTAS DE PRECIOS =====
    print("\n[Paso 2] Configuración de Divisas y Monedas")
    
    # 2.1 Buscar monedas
    pen_curr = client.search_read('res.currency', [('name', '=', 'PEN')], fields=['id'], limit=1)
    usd_curr = client.search_read('res.currency', [('name', '=', 'USD')], fields=['id'], limit=1)
    
    if pen_curr:
        print("✅ Activando PEN y USD")
        client.write('res.currency', [pen_curr[0]['id']], {'active': True})
    if usd_curr:
        client.write('res.currency', [usd_curr[0]['id']], {'active': True})

    # 2.2 Configurar compañía conPEN
    companies = client.search_read('res.company', [], fields=['id'], limit=1)
    if companies and pen_curr:
        # Nota: Cambiar la moneda base puede arrojar error si ya hay movimientos,
        # pero intentamos configurarlo.
        try:
            client.write('res.company', [companies[0]['id']], {'currency_id': pen_curr[0]['id']})
            print("✅ Moneda base de la compañía configurada a PEN.")
        except OdooFaultError as e:
            print(f"⚠️ No se pudo cambiar la moneda base a PEN (es normal si ya hay facturas): {e.fault_string}")

    # 2.3 Listas de precios
    print("Creando listas de precios...")
    pricelists = []
    if usd_curr:
        dl_usd = client.search_read('product.pricelist', [('name','=','Tarifa Receptivo USD')], fields=['id'])
        if not dl_usd:
            pl_usd_id = client.create('product.pricelist', {'name': 'Tarifa Receptivo USD', 'currency_id': usd_curr[0]['id']})
            pricelists.append(pl_usd_id)
        else:
            pricelists.append(dl_usd[0]['id'])

    if pen_curr:
        dl_pen = client.search_read('product.pricelist', [('name','=','Tarifa Nacional PEN')], fields=['id'])
        if not dl_pen:
            pl_pen_id = client.create('product.pricelist', {'name': 'Tarifa Nacional PEN', 'currency_id': pen_curr[0]['id']})
            pricelists.append(pl_pen_id)
        else:
            pricelists.append(dl_pen[0]['id'])
    print(f"✅ Listas de precios listas: {pricelists}")


    # ===== PASO 3: GESTIÓN DE CLIENTES Y TAGS =====
    print("\n[Paso 3] Etiquetas y Clientes de Prueba")
    
    tags = ["Pasajero VIP", "Turista Nacional", "Turista Extranjero"]
    tag_ids = []
    for tag in tags:
        exist_tag = client.search_read('res.partner.category', [('name', '=', tag)], fields=['id'])
        if exist_tag:
            tag_ids.append(exist_tag[0]['id'])
        else:
            new_tag = client.create('res.partner.category', {'name': tag})
            tag_ids.append(new_tag)
    print("✅ Etiquetas creadas/verificadas.")

    # Crear 2 clientes
    cli1 = client.search_read('res.partner', [('name', '=', 'Cliente Prueba Nacional')], fields=['id'])
    if not cli1:
        cli1_id = client.create('res.partner', {'name': 'Cliente Prueba Nacional', 'category_id': [(6, 0, [tag_ids[1]])]})
    else:
        cli1_id = cli1[0]['id']

    cli2 = client.search_read('res.partner', [('name', '=', 'Cliente Prueba VIP USD')], fields=['id'])
    if not cli2:
        cli2_id = client.create('res.partner', {'name': 'Cliente Prueba VIP USD', 'category_id': [(6, 0, [tag_ids[0], tag_ids[2]])]})
    else:
        cli2_id = cli2[0]['id']
    
    print(f"✅ Clientes creados con IDs: {cli1_id}, {cli2_id}")

    # Subir pasaporte
    pasaporte_path = os.path.join(os.path.dirname(__file__), "Pasaporte_Ejemplo.pdf")
    if os.path.exists(pasaporte_path):
        with open(pasaporte_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Verificar si ya tiene archivo
        attach = client.search_read('ir.attachment', [('res_model', '=', 'res.partner'), ('res_id', '=', cli2_id), ('name', '=', 'Pasaporte_Ejemplo.pdf')], fields=['id'])
        if not attach:
            client.create('ir.attachment', {
                'name': 'Pasaporte_Ejemplo.pdf',
                'res_model': 'res.partner',
                'res_id': cli2_id,
                'type': 'binary',
                'datas': b64_data
            })
            print("✅ Pasaporte adjuntado al Cliente Prueba VIP USD.")
        else:
            print("✅ Pasaporte ya estaba adjunto al cliente.")
    else:
        print("⚠️ No se encontró Pasaporte_Ejemplo.pdf")


    # ===== PASO 4: PACK CAMINO INCA Y ADJUNTO =====
    print("\n[Paso 4] Configuración del Pack y Automatización (PDF)")
    
    prod = client.search_read('product.template', [('name', '=', 'Pack Camino Inca Clásico')], fields=['id'])
    if not prod:
        prod_id = client.create('product.template', {
            'name': 'Pack Camino Inca Clásico',
            'type': 'service',  # Usamos 'service' para servicios puros
            'list_price': 1500.0,
        })
    else:
        prod_id = prod[0]['id']
        client.write('product.template', [prod_id], {'type': 'service'})
    
    print(f"✅ Producto 'Pack Camino Inca Clásico' verificado (ID {prod_id}).")

    # Adjuntar el programa
    programa_path = os.path.join(os.path.dirname(__file__), "Programa Camino inca clasico y otras actividades Marzo 2026 Final.pdf")
    if os.path.exists(programa_path):
        with open(programa_path, "rb") as f:
            b64_prog = base64.b64encode(f.read()).decode('utf-8')
        
        attach_id = client.search_read('ir.attachment', [('res_model', '=', 'product.template'), ('res_id', '=', prod_id), ('name', '=', 'Programa Camino Inca.pdf')], fields=['id'])
        if not attach_id:
            client.create('ir.attachment', {
                'name': 'Programa Camino Inca.pdf',
                'res_model': 'product.template',
                'res_id': prod_id,
                'type': 'binary',
                'datas': b64_prog
            })
            print("✅ Programa adjuntado al producto.")
        else:
            print("✅ Programa ya estaba adjunto al producto.")
    else:
        print("⚠️ No se encontró el archivo del Programa PDF")

    # ===== PASO 5: FLUJO COMERCIAL CRM =====
    print("\n[Paso 5] Configuración de Embudo CRM")
    
    etapas_requeridas = [
        "Nuevo Prospecto",
        "Propuesta Enviada",
        "Confirmado (Adelanto)",
        "Pagado Total / Ejecución"
    ]
    
    # Vamos a crear/asegurar que existan estas etapas en orden, y las que ya están por defecto archivarlas o adaptarlas.
    # Primero buscamos todas para no duplicar.
    current_stages = client.search_read('crm.stage', [], fields=['id', 'name'], order="sequence")
    
    # Archivamos las actuales (para evitar New, Qualified, Proposition, Won originales)
    if current_stages:
        client.write('crm.stage', [s['id'] for s in current_stages], {'is_won': False})
        
    for idx, stage_name in enumerate(etapas_requeridas):
        exist = client.search_read('crm.stage', [('name', '=', stage_name)], fields=['id'])
        if not exist:
            is_won = (stage_name == "Pagado Total / Ejecución")
            client.create('crm.stage', {
                'name': stage_name,
                'sequence': idx * 10,
                'is_won': is_won,
                'fold': False
            })
        else:
            client.write('crm.stage', [exist[0]['id']], {'sequence': idx * 10})
            
    print("✅ Etapas del CRM configuradas correctamente.")
    print("\n🎉 Todos los setups ejecutados exitosamente!")

if __name__ == "__main__":
    main()
