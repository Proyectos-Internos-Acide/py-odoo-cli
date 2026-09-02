from odoo_cli import OdooClient

def revert_standard_quote():
    client = OdooClient()
    client.connect()
    
    xml_content = """<?xml version="1.0"?>
<t t-name="sale.report_saleorder">
    <t t-call="sale.report_saleorder_raw"/>
</t>"""
    
    views = client.search_read('ir.ui.view', domain=[('key', '=', 'sale.report_saleorder')], fields=['id'])
    if views:
        view_id = views[0]['id']
        client.write('ir.ui.view', [view_id], {'arch': xml_content})
        print(f"Vista sale.report_saleorder REVERTIDA exitosamente (ID: {view_id})!")
    else:
        print("No se encontro la vista sale.report_saleorder")

if __name__ == '__main__':
    revert_standard_quote()
