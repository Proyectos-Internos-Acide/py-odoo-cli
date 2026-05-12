
WIZ_MODEL = "x_wtk_custom_quote_wizard"
WIZ_MODEL_NAME = "WTK Custom Quote Wizard"
WIZ_LINE_MODEL = "x_wtk_custom_quote_wizard_line"
WIZ_LINE_MODEL_NAME = "WTK Custom Quote Wizard Line"
WIZ_SERVICE_LINE_MODEL = "x_wtk_custom_quote_wizard_service_line"
WIZ_SERVICE_LINE_MODEL_NAME = "WTK Custom Quote Wizard Service Line"
WIZ_VIEW_NAME = "wtk.custom.quote.wizard.form"
WIZ_REPORT_TEMPLATE_NAME = "wtk.report_custom_quote_document"
WIZ_REPORT_ACTION_NAME = "WTK - PDF Cotización personalizada"
WIZ_PRINT_ACTION_NAME = "WTK - Generar PDF desde wizard"
BTN_ACTION_NAME = "WTK - Abrir modal cotización personalizada"
BTN_VIEW_NAME = "wtk.sale.order.form.custom.quote.button"

def _get_model(client, model_name: str) -> dict:
    rec = client.search_read("ir.model", domain=[["model", "=", model_name]], fields=["id", "model", "name"], limit=1)
    return rec[0] if rec else {}
