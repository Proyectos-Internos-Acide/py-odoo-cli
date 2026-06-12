#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

def text_to_html(text):
    if not text:
        return ""
    
    lines = [l.strip() for l in text.split('\n')]
    html_parts = []
    in_list = False
    
    inclusion_headers = [
        "INCLUDED SERVICES", "SERVICES INCLUDED", "INCLUDES", "INCLUYE", "SERVICIOS INCLUIDOS",
        "SERVIÇOS INCLUSOS", "SERVIÇOS INCLUÍDOS", "INCLUI", "INBEGRIFFENE LEISTUNGEN", "LEISTUNGEN INBEGRIFFEN", "INKLUSIVE"
    ]

    exclusion_headers = [
        "NOT INCLUDED", "NO INCLUYE", "SERVICES NOT INCLUDED", "SERVICIOS NO INCLUIDOS", "NO INCLUIDO",
        "NÃO INCLUSO", "SERVIÇOS NÃO INCLUSOS", "NICHT INBEGRIFFEN", "EXKLUSIVE"
    ]
    
    rates_headers = [
        "TARIFAS POR TIPO DE GRUPO", "TARIFAS", "RATES", "GROUP RATES", "TARIFAS POR GRUPO"
    ]
    
    for line in lines:
        if not line:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            continue
            
        upper_line = line.upper().replace(":", "").strip()
        
        is_inclusion = any(h in upper_line for h in inclusion_headers)
        is_exclusion = any(h in upper_line for h in exclusion_headers)
        is_rates = any(h in upper_line for h in rates_headers)
        
        if is_inclusion:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f'<div style="font-weight: bold; color: #20603D; margin-top: 12px; margin-bottom: 6px; font-size: 11px;">{line.upper()}</div>')
        elif is_exclusion:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f'<div style="font-weight: bold; color: #c0392b; margin-top: 12px; margin-bottom: 6px; font-size: 11px;">{line.upper()}</div>')
        elif is_rates:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f'<div style="font-weight: bold; color: #E5B745; margin-top: 12px; margin-bottom: 6px; font-size: 11px;">{line.upper()}</div>')
        else:
            clean_item_text = line
            is_bullet = False
            for marker in ["-", "*", "•"]:
                if line.startswith(marker):
                    is_bullet = True
                    clean_item_text = line[len(marker):].strip()
                    break
            
            last_was_header = len(html_parts) > 0 and 'font-weight: bold;' in html_parts[-1]
            
            if is_bullet or last_was_header or in_list:
                if not in_list:
                    html_parts.append('<ul style="margin: 0; padding-left: 16px; list-style-type: disc; color: #4b5563; line-height: 1.45;">')
                    in_list = True
                html_parts.append(f'<li style="margin-bottom: 2px;">{clean_item_text}</li>')
            else:
                html_parts.append(f'<p style="margin: 0 0 8px 0; line-height: 1.45; color: #4b5563;">{line}</p>')
                
    if in_list:
        html_parts.append("</ul>")
        
    return "\n".join(html_parts)

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    # Get active languages in Odoo
    print("Fetching active languages...")
    langs = client.search_read('res.lang', [['active', '=', True]], ['code'])
    lang_codes = [l['code'] for l in langs]
    print(f"Active languages to process: {lang_codes}")

    for lang in lang_codes:
        print(f"\n--- Processing Language: {lang} ---")
        
        # Read all product templates with a description
        templates = client.search_read(
            'product.template',
            domain=[['description_sale', '!=', False], ['description_sale', '!=', '']],
            fields=['id', 'name', 'description_sale'],
            context={'lang': lang}
        )
        
        print(f"Found {len(templates)} product templates with descriptions in context '{lang}'")
        
        for tmpl in templates:
            tid = tmpl['id']
            name = tmpl['name']
            plain_desc = tmpl['description_sale']
            
            # Convert plain text description to HTML
            html_desc = text_to_html(plain_desc)
            
            print(f"Updating product [{tid}] '{name}' with formatted HTML description...")
            
            client.execute(
                'product.template',
                'write',
                [tid],
                {'x_description_sale_html': html_desc},
                context={'lang': lang}
            )
            
    print("\n🎉 Proceso de migración y formateo HTML completado exitosamente.")

if __name__ == "__main__":
    main()
