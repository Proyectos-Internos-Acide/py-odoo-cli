import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

DESC_ALL = """INCLUDED SERVICES
Pre-Trek Briefing
Entrance permits to the Inca Trail and Machu Picchu (second entrance)
Professional Mountain Guide
Specialized Mountain Chef
Horsemen and Horses (Salkantay Trek)
Local porters for equipment and an additional 8 kg porter allowance for your personal belongings
Meals: 5 breakfasts, 5 snacks, 6 lunches, 5 tea times, and 5 dinners
Premium Camping Equipment: The North Face tents, Therm-a-Rest inflatable mattresses, sleeping bags, trekking poles, dining and kitchen tents, and eco-friendly portable toilet tent
Safety & Emergency Equipment: Satellite phone for emergencies, radios, and a complete first aid kit
Private Transportation & Train Tickets:
Mercedes Benz minibus: Cusco → Km 82 (start of the trek)
Bus down from Machu Picchu to Aguas Calientes
Expedition Train: Aguas Calientes → Ollantaytambo
Private transfer: Ollantaytambo → your hotel in Cusco
NOT INCLUDED SERVICES
First breakfast, Huayna Picchu entrance, travel insurance, gratuities, or tips."""

# Note: Couples description had "gratuities or tips" instead of "gratuities, or tips."
DESC_COUPLES = """INCLUDED SERVICES
Pre-Trek Briefing
Entrance permits to the Inca Trail and Machu Picchu (second entrance)
Professional Mountain Guide
Specialized Mountain Chef
Horsemen and Horses (Salkantay Trek)
Local porters for equipment and an additional 8 kg porter allowance for your personal belongings
Meals: 5 breakfasts, 5 snacks, 6 lunches, 5 tea times, and 5 dinners
Premium Camping Equipment: The North Face tents, Therm-a-Rest inflatable mattresses, sleeping bags, trekking poles, dining and kitchen tents, and eco-friendly portable toilet tent
Safety & Emergency Equipment: Satellite phone for emergencies, radios, and a complete first aid kit
Private Transportation & Train Tickets:
Mercedes Benz minibus: Cusco → Km 82 (start of the trek)
Bus down from Machu Picchu to Aguas Calientes
Expedition Train: Aguas Calientes → Ollantaytambo
Private transfer: Ollantaytambo → your hotel in Cusco
NOT INCLUDED SERVICES
First breakfast, Huayna Picchu entrance, travel insurance, gratuities or tips."""

UPDATES = {
    26: {
        "name": "Salkantay & Inca Trail 6 Days – Solo",
        "description_sale": DESC_ALL
    },
    27: {
        "name": "Salkantay & Inca Trail 6 Days – Couples",
        "description_sale": DESC_COUPLES
    },
    28: {
        "name": "Salkantay & Inca Trail 6 Days – Families",
        "description_sale": DESC_ALL
    },
    29: {
        "name": "Salkantay & Inca Trail 6 Days – Friends",
        "description_sale": DESC_ALL
    }
}

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    languages = ["es_419", "en_US"]
    for lang in languages:
        print(f"\nUpdating Salkantay & Inca products in context lang={lang}...")
        for product_id, vals in UPDATES.items():
            print(f"Updating product ID {product_id} to '{vals['name']}'...")
            client.execute(
                "product.template",
                "write",
                [product_id],
                vals,
                context={"lang": lang}
            )
            
    print("\n🎉 Salkantay & Inca products and descriptions updated successfully in all contexts.")

if __name__ == "__main__":
    main()
