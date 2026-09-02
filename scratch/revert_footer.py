from odoo_cli import OdooClient
import sys

def revert_footer():
    client = OdooClient()
    client.connect()
    
    with open('scratch/footer_original.xml', 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    views = client.search_read('ir.ui.view', domain=[('key', '=', 'web.external_layout_footer_content')], fields=['id'])
    if views:
        view_id = views[0]['id']
        client.write('ir.ui.view', [view_id], {'arch': xml_content})
        print(f"Footer REVERTIDO a la version original en la vista {view_id}!")
    else:
        print("No se encontro la vista web.external_layout_footer_content")

if __name__ == '__main__':
    revert_footer()
