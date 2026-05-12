from odoo_cli import OdooClient
import json

def main():
    client = OdooClient()
    client.connect()
    
    # Get the templates we created
    templates = client.search_read(
        "whatsapp.template", 
        [["model", "=", "sale.order"], ["status", "in", ["draft", "approved"]]], 
        ["id", "name", "status", "wa_account_id", "lang_code", "template_type", "template_name"]
    )
    
    print(json.dumps(templates, indent=2))
    
    # Reset status to draft first so we can properly submit them
    t_ids = [t["id"] for t in templates]
    client.write("whatsapp.template", t_ids, {"status": "draft"})
    
    # Try calling common submission methods
    for t_id in t_ids:
        print(f"Intentando enviar plantilla {t_id} a Meta...")
        try:
            # Common method names in Odoo whatsapp integration
            res = client.execute("whatsapp.template", "button_submit_for_approval", [t_id])
            print(f"Éxito con button_submit_for_approval: {res}")
        except Exception as e:
            print(f"Fallo button_submit_for_approval: {e}")
            try:
                res = client.execute("whatsapp.template", "button_sync_template", [t_id])
                print(f"Éxito con button_sync_template: {res}")
            except Exception as e2:
                print(f"Fallo button_sync_template: {e2}")

if __name__ == "__main__":
    main()
