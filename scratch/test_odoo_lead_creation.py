from odoo_cli import OdooClient
import json

def test_odoo_automation():
    client = OdooClient()
    client.connect()

    print('Conectado a Odoo. Preparando envio de prueba...')
    
    payload = {
        'action': 'wayki_reserve_tour',
        'booking_id': 'TEST-PYTHON-002',
        'bookingId': 'TEST-PYTHON-002',
        'trip_name': 'Inca Trail 4 Days - Automatizado',
        'tourName': 'Inca Trail 4 Days - Automatizado',
        'tourId': '12345',
        'startDate': '2026-10-15',
        'endDate': '2026-10-19',
        'adultPassengers': 2,
        'childrenPassengers': 0,
        'studentPassengers': 0,
        'babyPassengers': 0,
        'adultPrice': 750.00,
        'studentPrice': 0.0,
        'childrenPrice': 0.0,
        'amountStr': '$1500.00',
        'amount': 1500.00,
        'debt': 0.0,
        'passengers': [
            {
                'firstName': 'Prueba',
                'lastName': 'Python',
                'email': 'prueba_python@test.com',
                'phone': '+51999888777'
            }
        ]
    }
    
    lead_id = client.create('crm.lead', {
        'name': 'Incoming Form Payload (Python Test)',
        'x_wayki_sync_payload': json.dumps(payload)
    })
    
    print('Lead creado con exito en Odoo! ID:', lead_id)
    print('Revisa el CRM. Deberias ver un nuevo lead de Prueba Python.')

if __name__ == '__main__':
    test_odoo_automation()
