from odoo_cli import OdooClient

client = OdooClient()
client.connect()

# Buscar plantillas de sale.order que estén en draft
templates = client.search_read("whatsapp.template", [["model", "=", "sale.order"], ["status", "=", "draft"]], ["id", "name"])

if not templates:
    print("No se encontraron plantillas en estado draft para sale.order.")
else:
    template_ids = [t["id"] for t in templates]
    # Intentar actualizarlas a approved
    try:
        client.write("whatsapp.template", template_ids, {"status": "approved"})
        print(f"✅ Se actualizaron {len(template_ids)} plantillas al estado 'approved'.")
    except Exception as e:
        print(f"❌ Error al actualizar: {e}")
