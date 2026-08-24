import requests
import json

def test_contact_form():
    # La URL real oculta a la que el Javascript manda los datos del formulario:
    url = 'https://www.waykitrek.net/wp-content/themes/wayki/ajax/ajax-contacto2026.php'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.waykitrek.net',
        'Referer': 'https://www.waykitrek.net/contact-us/'
    }
    
    data = {
        'contactID': '1',
        'name': 'Test Formulario',
        'lastname': 'Automatizado',
        'email': 'test@test.net',
        'phone': '+51999888777',
        'blID': '1',
        'blPaquete': 'Inca Trail 4 Days - For Families',
        'registerCode': 'web',
        'datetravel': '25/08/2026',
        'countryID': 'US',
        'comment': 'Este es un mensaje de prueba desde Python simulando el formulario web real.',
    }
    
    print('Enviando POST a', url)
    
    try:
        response = requests.post(url, headers=headers, data=data)
        print('Status Code:', response.status_code)
        print('Respuesta del servidor:', response.text)
        
        if response.status_code == 200:
            if response.text.strip().isdigit() and int(response.text.strip()) > 0:
                print('Solicitud enviada con exito! El servidor PHP devolvio OK. Deberia llegar a Odoo en breve.')
            else:
                print('El servidor respondio 200 pero devolvio un valor inesperado.')
        else:
            print('Error en la solicitud HTTP.')
            
    except Exception as e:
        print('Ocurrio un error:', e)

if __name__ == '__main__':
    test_contact_form()
