"""
Script para poblar la base de datos de Wayki Trek con datos realistas y estructurados en abundancia (mínimo 20 registros por modelo/app).
Pobla:
- Clientes / Contactos (res.partner)
- Leads / Oportunidades (crm.lead)
- Servicios Incluidos / Plantillas de Servicios (x_wtk_custom_service_template)
- Cotizaciones / Ventas (sale.order) con sus líneas
"""
import sys, random
from datetime import datetime, timedelta

sys.path.insert(0, '../knowledge/wayki-trek-develop/29_custom_quote_app')
from odoo_cli import OdooClient
client = OdooClient()
# Conectar como admin
client.username = 'leocusi@waykitrek.net'
client.password = 'usuario123'
client.connect()

print("================ START DATA POPULATION ================")

# ----------------- 1. CREACIÓN DE CONTACTOS (res.partner) -----------------
print("\n--- Creando Contactos ---")
contact_names = [
    ("Liam O'Connor", "liam.oconnor@example.com", "+1-202-555-0143", "USA"),
    ("Charlotte Dubois", "charlotte.dubois@example.com", "+33-1-4227-7890", "Francia"),
    ("Hiroshi Tanaka", "hiroshi.tanaka@example.com", "+81-90-5555-1234", "Japón"),
    ("Amelie Schmidt", "amelie.schmidt@example.com", "+49-89-6321-4567", "Alemania"),
    ("Mateo Fernandez", "mateo.fernandez@example.com", "+34-91-555-6789", "España"),
    ("Oliver Smith", "oliver.smith@example.com", "+44-20-7946-0958", "Reino Unido"),
    ("Sofia Rossi", "sofia.rossi@example.com", "+39-02-555-4321", "Italia"),
    ("Lucas Silva", "lucas.silva@example.com", "+55-11-98765-4321", "Brasil"),
    ("Emma Watson", "emma.watson@example.com", "+1-310-555-0192", "USA"),
    ("Alexander Petrov", "alexander.petrov@example.com", "+7-495-555-7890", Russian := "Rusia"),
    ("Ji-Yeon Kim", "jiyeon.kim@example.com", "+82-10-5555-6789", "Corea del Sur"),
    ("Santiago Gomez", "santiago.gomez@example.com", "+57-315-555-6789", "Colombia"),
    ("Mia Wong", "mia.wong@example.com", "+86-21-555-6789", "China"),
    ("Noah Johnson", "noah.johnson@example.com", "+1-718-555-0156", "USA"),
    ("Chloe Lefevre", "chloe.lefevre@example.com", "+32-2-555-1234", "Bélgica"),
    ("William Davies", "william.davies@example.com", "+61-2-9876-5432", "Australia"),
    ("Zoe Martinez", "zoe.martinez@example.com", "+52-55-5555-1234", "México"),
    ("Leo Andersen", "leo.andersen@example.com", "+45-35-55-1234", "Dinamarca"),
    ("Yuki Sato", "yuki.sato@example.com", "+81-80-5555-9876", "Japón"),
    ("Elena Vance", "elena.vance@example.com", "+1-503-555-0178", "USA"),
    ("Gabriel Dupont", "gabriel.dupont@example.com", "+33-6-5555-4321", "Francia"),
    ("Isabella Conti", "isabella.conti@example.com", "+39-333-555-7890", "Italia")
]

partner_ids = []
for name, email, phone, country in contact_names:
    # Buscar si ya existe por email
    exist = client.search_read('res.partner', [('email', '=', email)], ['id'])
    if exist:
        partner_ids.append(exist[0]['id'])
        print(f"  Contacto existente: {name}")
    else:
        pid = client.execute('res.partner', 'create', [{
            'name': name,
            'email': email,
            'phone': phone,
            'type': 'contact',
            'street': f"Main street, {country}"
        }])
        # La API de este cliente envuelve el retorno en una lista [ID]
        if isinstance(pid, list):
            pid = pid[0]
        partner_ids.append(pid)
        print(f"  Contacto creado: {name} (ID: {pid})")

# ----------------- 2. CREACIÓN DE LEADS / OPORTUNIDADES (crm.lead) -----------------
print("\n--- Creando Leads / Oportunidades ---")
lead_titles = [
    "Inca Trail 4 Days - Private Family Trek",
    "Lares Trek 4 Days - Honeymoon Luxury",
    "Salkantay Trek 5 Days - Adventure Group",
    "Choquequirao Expedition 5 Days - Couple",
    "Cusco City Tour & Sacred Valley - Shared",
    "Inca Trail 2 Days - Express Tour",
    "Ausangate Trek 6 Days - High Mountain",
    "Huchuy Qosqo Trek 3 Days - Leisure Travel",
    "Rainbow Mountain & Red Valley 1 Day",
    "Maras & Moray Quad Biking Adventure",
    "Humantay Lake Day Trip - Private Service",
    "Short Inca Trail to Machu Picchu 2D/1N",
    "Classic Sacred Valley & Machu Picchu 3D",
    "Writings of Peru Cultural Tour 7 Days",
    "Amazon Rainforest Tour & Cusco Trekking 10D",
    "Salkantay Trek Luxury Dome Experience",
    "Lares Valley Cultural Exchange & Trek 4D",
    "Ultimate Cusco Explorer Package 5D",
    "Inca Quarry Trek to Machu Picchu 4D",
    "Ancascocha Trek to Machu Picchu 5D"
]

stage_ids = [5, 11, 12, 6]  # Open stages only to avoid won/lost trigger conflicts
lead_ids = []

for i, title in enumerate(lead_titles):
    partner_id = partner_ids[i % len(partner_ids)]
    partner_data = client.search_read('res.partner', [('id', '=', partner_id)], ['name', 'email', 'phone'])[0]
    
    # Repartir usuarios de asignación
    user_id = random.choice([5, 9, 13]) # sales, coordinator, leocusi
    
    lead_id = client.execute('crm.lead', 'create', [{
        'name': f"{partner_data['name']} - {title}",
        'partner_id': partner_id,
        'contact_name': partner_data['name'],
        'email_from': partner_data['email'],
        'phone': partner_data['phone'],
        'user_id': user_id,
        'stage_id': random.choice(stage_ids),
        'probability': random.choice([10, 30, 70, 100]),
        'expected_revenue': random.randint(500, 3500)
    }])
    if isinstance(lead_id, list):
        lead_id = lead_id[0]
    lead_ids.append(lead_id)
    print(f"  Lead creado: {partner_data['name']} - {title} (ID: {lead_id})")

# ----------------- 3. PLANTILLAS DE SERVICIOS (x_wtk_custom_service_template) -----------------
print("\n--- Creando Servicios Incluidos / Plantillas ---")
# Obtener categorías (2: Transporte, 3: Guías, 4: Boletos, 5: Alimentación, 6: Hoteles)
# Tipos de servicio correspondientes
services_to_create = [
    # Transporte (x_category_id = 2)
    ("Traslado In/Out Cusco (Aeropuerto - Hotel)", 2, 8, 15.0, 4), # Auto
    ("Traslado Cusco - Ollantaytambo (Sprinter)", 2, 5, 85.0, 15), # Sprinter
    ("Ticket de Tren Voyager Ollantaytambo - Machu Picchu", 2, 8, 70.0, 1),
    ("Ticket de Tren Vistadome Machu Picchu - Cusco", 2, 8, 115.0, 1),
    ("Bus de Consettur Subida/Bajada Machu Picchu", 2, 4, 24.0, 1), # Bus grande
    ("Traslado Privado en Camioneta 4x4 (Valle Sagrado)", 2, 7, 120.0, 4), # Camioneta

    # Guías (x_category_id = 3)
    ("Guía Privado en Machu Picchu (Inglés/Español)", 3, 9, 75.0, 10), 
    ("Guía de Montaña Certificado - Salkantay Trek", 3, 9, 350.0, 12),
    ("Guía Oficial de Turismo - City Tour Cusco", 3, 9, 50.0, 15),

    # Boletos (x_category_id = 4)
    ("Boleto Turístico del Cusco (General - BTG)", 4, 10, 37.0, 1),
    ("Entrada Circuito Clásico a Machu Picchu", 4, 10, 45.0, 1),
    ("Entrada Machu Picchu + Montaña Huayna Picchu", 4, 10, 62.0, 1),
    ("Boleto Turístico del Cusco Parcial (Circuito I)", 4, 10, 20.0, 1),

    # Alimentación (x_category_id = 5)
    ("Almuerzo Buffet en Tinkuy (Belmond Sanctuary Lodge)", 5, 12, 48.0, 1),
    ("Box Lunch Ejecutivo para Trekking", 5, 12, 12.0, 1),
    ("Cena de Bienvenida en Cusco (Restaurante Local)", 5, 13, 25.0, 1),
    ("Almuerzo Buffet Turístico en Urubamba", 5, 12, 20.0, 1),

    # Hoteles (x_category_id = 6)
    ("Hotel 3 Estrellas Cusco (Hab. Doble/Matrimonial)", 6, 14, 85.0, 2),
    ("Hotel 4 Estrellas Cusco (Hab. Suite)", 6, 14, 180.0, 2),
    ("Hotel 3 Estrellas Aguas Calientes (Hab. Estándar)", 6, 14, 75.0, 2)
]

service_ids = []
for x_raw, cat, s_type, price, cap in services_to_create:
    sid = client.execute('x_wtk_custom_service_template', 'create', [{
        'x_name': f"{x_raw} (Ref: ${price})",
        'x_raw_name': x_raw,
        'x_category_id': cat,
        'x_service_type_id': s_type,
        'x_price': price,
        'x_capacity': cap
    }])
    if isinstance(sid, list):
        sid = sid[0]
    service_ids.append(sid)
    print(f"  Servicio/Plantilla creada: {x_raw} (ID: {sid})")

# ----------------- 4. COTIZACIONES Y VENTAS (sale.order) -----------------
print("\n--- Creando Cotizaciones / Ventas ---")

# Obtener tours/servicios reales de product.template
tours = client.search_read('product.template', [('type', '=', 'service')], ['id', 'name', 'list_price'], limit=10)
if not tours:
    # Fallback si type falló
    tours = client.search_read('product.template', [], ['id', 'name', 'list_price'], limit=10)

quote_ids = []

for i in range(20):
    partner_id = partner_ids[i % len(partner_ids)]
    lead_id = lead_ids[i % len(lead_ids)]
    
    # Elegir tour
    tour = tours[i % len(tours)]
    
    # Crear cotización
    so_id = client.execute('sale.order', 'create', [{
        'partner_id': partner_id,
        'opportunity_id': lead_id,
        'x_package_name': f"Paquete Especial - {tour['name']}",
        'date_order': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S'),
        'validity_date': (datetime.now() + timedelta(days=random.randint(5, 15))).strftime('%Y-%m-%d'),
        'state': random.choice(['draft', 'sent', 'sale'])
    }])
    if isinstance(so_id, list):
        so_id = so_id[0]
    quote_ids.append(so_id)
    
    # Agregar líneas a la cotización (Línea del Tour base + servicios incluidos)
    # Línea 1: Tour Base
    client.execute('sale.order.line', 'create', [{
        'order_id': so_id,
        'product_template_id': tour['id'],
        'name': tour['name'],
        'product_uom_qty': random.randint(2, 6),
        'price_unit': tour['list_price'] or 850.0 # si list_price es 0 ponemos uno realista
    }])
    
    # Líneas 2 y 3: Servicios incluidos al azar de nuestras plantillas
    for j in range(2):
        s_template = client.search_read('x_wtk_custom_service_template', [('id', '=', random.choice(service_ids))], ['x_raw_name', 'x_price'])[0]
        # Crear un producto comodín "Custom Quotation" o similar si existe,
        # o simplemente vincular un servicio. En Odoo las sale.order.line se vinculan a un product_id.
        # Buscamos el product.product id del tour o un generico:
        tour_product = client.search_read('product.product', [('product_tmpl_id', '=', tour['id'])], ['id'])[0]['id']
        
        client.execute('sale.order.line', 'create', [{
            'order_id': so_id,
            'product_id': tour_product,
            'name': f"Incluye: {s_template['x_raw_name']}",
            'product_uom_qty': random.randint(2, 6),
            'price_unit': s_template['x_price']
        }])
        
    print(f"  Cotización creada: S{str(so_id).zfill(5)} para Partner ID: {partner_id} (ID SO: {so_id})")

print("\n================ DATA POPULATION COMPLETED ================")
