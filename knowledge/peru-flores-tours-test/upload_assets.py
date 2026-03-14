#!/usr/bin/env python3
import sys
import os
import base64

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from odoo_cli import OdooClient

def upload_image(client, file_path, name):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    attachment_id = client.create('ir.attachment', {
        'name': name,
        'type': 'binary',
        'datas': encoded_string,
        'public': True,
        'res_model': 'website',
    })
    return attachment_id

def main():
    try:
        client = OdooClient()
        client.connect()
        
        base_dir = os.path.dirname(__file__)
        # Define images to upload
        images_to_upload = {
            'LOGO': 'logo.png',
            'HERO': 'machu_picchu_hero.png',
            'MONTANA_7_COLORES': 'montana_7_colores_tour_1772486458032.png',
            'LAGUNA_HUMANTAY': 'laguna_humantay_tour_1772486471975.png',
            'SACRED_VALLEY': 'sacred_valley_tour_1772486485667.png',
            'CUSCO_CITY': 'cusco_city_tour_1772486497977.png',
            'INCA_TRAIL': 'inca_trail_tour_1772486512376.png'
        }

        ids_path = os.path.join(base_dir, 'asset_ids.txt')
        with open(ids_path, 'w') as f:
            f.write("# Odoo Asset IDs for Peru Flores Tours\n")

        for key, filename in images_to_upload.items():
            file_path = os.path.join(base_dir, filename)
            if not os.path.exists(file_path):
                print(f"⚠️ Warning: {file_path} not found, skipping.")
                continue
            
            print(f"Uploading {key}: {file_path}")
            img_id = upload_image(client, file_path, filename)
            print(f"{key} uploaded with ID: {img_id}")
            
            with open(ids_path, 'a') as f:
                f.write(f"{key}_ID={img_id}\n")
            
            if key == 'LOGO':
                # Update website logo
                with open(file_path, "rb") as logo_f:
                    logo_data = base64.b64encode(logo_f.read()).decode('utf-8')
                client.write('website', [1], {'logo': logo_data})
                print("Website logo updated.")

        print(f"All Asset IDs saved to {ids_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
