"""
Script de Reversión para la personalización del modal de correo en el CRM.
Ejecutar este script desactiva o elimina la vista heredada y el campo personalizado,
devolviendo el asistente mail.compose.message a su estado 100% estándar de fábrica.

Uso:
    python scratch/revert_crm_mail_composer.py --disable  # Solo desactiva la vista (recomendado para prueba rápida)
    python scratch/revert_crm_mail_composer.py --delete   # Elimina la vista y el campo por completo
"""
import sys
import argparse
from odoo_cli import OdooClient

def main():
    parser = argparse.ArgumentParser(description="Revertir personalización de correo CRM")
    parser.add_argument("--delete", action="store_true", help="Eliminar por completo la vista y el campo")
    parser.add_argument("--disable", action="store_true", help="Solo desactivar la vista heredada")
    args = parser.parse_args()

    client = OdooClient()

    # 1. Buscar la vista heredada
    views = client.search_read('ir.ui.view', [('name', '=', 'wtk.mail.compose.message.lead.details')], ['id', 'active'])
    if views:
        v_id = views[0]['id']
        if args.delete:
            print(f"Eliminando vista heredada ID {v_id}...")
            client.execute('ir.ui.view', 'unlink', [v_id])
            print("Vista eliminada.")
        else:
            print(f"Desactivando vista heredada ID {v_id}...")
            client.execute('ir.ui.view', 'write', [v_id], {'active': False})
            print("Vista desactivada. El modal vuelve al estado nativo de Odoo.")
    else:
        print("No se encontró la vista heredada.")

    # 2. Si se pidió eliminar, borrar también el campo personalizado
    if args.delete:
        fields = client.search_read('ir.model.fields', [
            ('name', '=', 'x_crm_contact_details'),
            ('model', '=', 'mail.compose.message')
        ], ['id'])
        if fields:
            f_id = fields[0]['id']
            print(f"Eliminando campo personalizado ID {f_id}...")
            client.execute('ir.model.fields', 'unlink', [f_id])
            print("Campo eliminado.")

    print("\nProceso de reversión finalizado con éxito.")

if __name__ == "__main__":
    main()
