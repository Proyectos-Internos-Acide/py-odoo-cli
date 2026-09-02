import base64
from odoo_cli import OdooClient

def apply_image_footer():
    client = OdooClient()
    client.connect()
    
    # Leer la imagen subida
    image_path = '/home/roger/.gemini/antigravity-ide/brain/6538d3ff-e492-4205-b694-c52b7c1c484a/.user_uploaded/media_1788363518780.png'
    with open(image_path, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')
    
    xml_content = f"""<?xml version="1.0"?>
<t t-name="web.external_layout_footer_content">
    <div t-attf-class="o_footer_content {{{{footer_content_classes}}}}" style="border-top: none !important; text-align: center; width: 100%; position: relative; top: -20px; padding-bottom: 10px;">
        <img src="data:image/png;base64,{img_b64}" style="width: 100%; max-height: 100px; display: block; margin: 0 auto; object-fit: contain;"/>
    </div>
</t>"""

    # Actualizar la vista
    views = client.search_read('ir.ui.view', domain=[('key', '=', 'web.external_layout_footer_content')], fields=['id'])
    if views:
        view_id = views[0]['id']
        client.write('ir.ui.view', [view_id], {'arch': xml_content})
        print(f"Footer de IMAGEN actualizado exitosamente en la vista {view_id}!")
    else:
        print("No se encontro la vista.")

if __name__ == '__main__':
    apply_image_footer()
