import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

DESC = """Briefing
Entrance permits to Lares and Machu Picchu, including entrance tickets to the Lares hot springs.
TRANSPORTATION
Bus from Cusco to Lares (start of the hike)
Expedition Train from Ollantaytambo to Aguas Calientes
Bus from Aguas Calientes → Machu Picchu → Aguas Calientes (second day)
Expedition Train from Aguas Calientes to Ollantaytambo
Bus from Ollantaytambo station to your hotel in Cusco
TREKKING STAFF
Professional guide, cooks, muleteers, pack horses, llamas for personal belongings, and an emergency horse.
MEALS
3 breakfasts, 3 snacks, 3 lunches, 3 tea times, and 3 dinners (last lunch in Aguas Calientes).
CAMPING EQUIPMENT
Tents, inflatable sleeping pads, sleeping bags, pillows, dining tent, kitchen tent, and bathroom tents.
SAFETY EQUIPMENT
Satellite phones, radios, and first aid kit.
NOT INCLUDED
First breakfast and last lunch, hiking poles, entrance to Huayna Picchu Mountain or Machu Picchu Mountain (we can help you purchase them separately), tips, and travel insurance."""

UPDATES = {
    31: {
        "name": "Lares Trek 4 Days",
        "description_sale": DESC
    }
}

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    languages = ["es_419", "en_US"]
    for lang in languages:
        print(f"\nUpdating Lares & Machu Picchu product in context lang={lang}...")
        for product_id, vals in UPDATES.items():
            print(f"Updating product ID {product_id} to '{vals['name']}'...")
            client.execute(
                "product.template",
                "write",
                [product_id],
                vals,
                context={"lang": lang}
            )
            
    print("\n🎉 Lares & Machu Picchu product updated successfully in all contexts.")

if __name__ == "__main__":
    main()
