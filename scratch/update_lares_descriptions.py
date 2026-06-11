import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

DESC_GROUP = """Briefing
Entrance permits to Lares, the 2-day Inca Trail, and Machu Picchu (second entrance)
Transportation:
Bus from Cusco to Huacawasi-Lares (starting point of the hike)
Expedition train from Ollantaytambo to Km 104 (starting point of the hike)
Machu Picchu bus down/up/down (3 rides)
Expedition train from Aguas Calientes to Ollantaytambo
Bus from Ollantaytambo station to hotel in Cusco
Meals: 3 breakfasts, 3 snacks, 3 lunches, 3 tea times, and 3 dinners
Trek staff: Professional guide, cooks, muleteers, pack horses, llamas for personal belongings, and an emergency horse
Accommodation: 2 nights homestay in Lares and 1 night in a 3-star hotel in Machu Picchu
Safety equipment: Satellite phones, radios, and first aid kit
NOT INCLUDED:
First breakfast and last lunch, hiking poles, entrance to Huayna Picchu Mountain or Machu Picchu Mountain (we can help you purchase them separately), tips, and travel insurance."""

DESC_COUPLES = """Briefing
Entrance permits to Lares, the 2-day Inca Trail, and Machu Picchu (second entrance)
Transportation:
Bus from Cusco to Huacawasi-Lares (starting point of the hike)
Expedition train from Ollantaytambo to Km 104 (starting point of the hike)
Machu Picchu bus down/up/down (3 rides)
Expedition train from Aguas Calientes to Ollantaytambo
Bus from Ollantaytambo station to hotel in Cusco
Picnic tent (third day) and hiking poles
Meals: 3 breakfasts, 3 snacks, 4 lunches (1 box lunch), 3 tea times, and 3 dinners
Trek staff: Professional guide, cooks, muleteers, pack horses, llamas for personal belongings, and an emergency horse
Accommodation: 2 nights homestay in Lares and 1 night in a 3-star hotel in Machu Picchu
Safety equipment: Satellite phones, radios, and first aid kit
NOT INCLUDED:
First breakfast, entrance to Huayna Picchu Mountain or Machu Picchu Mountain (we can help you purchase them separately), optional tips, and travel insurance."""

DESC_FAMILIES = """Briefing
Entrance permits to Lares, the 2-day Inca Trail, and Machu Picchu (second entrance)
Transportation:
Bus from Cusco to Huacawasi-Lares (starting point of the hike)
Expedition train from Ollantaytambo to Km 104 (starting point of the hike)
Machu Picchu bus down/up/down (3 rides)
Expedition train from Aguas Calientes to Ollantaytambo
Bus from Ollantaytambo station to hotel in Cusco
Picnic tent (third day) and hiking poles
Meals: 3 breakfasts, 3 snacks, 4 lunches (1 box lunch), 3 tea times, and 3 dinners
Trek staff: Professional guide, cooks, muleteers, pack horses, llamas for personal belongings, and an emergency horse
Accommodation: 2 nights homestay in Lares and 1 night in a 3-star hotel in Machu Picchu
Safety equipment: Satellite phones, radios, and first aid kit
NOT INCLUDED:
First breakfast, entrance to Huayna Picchu Mountain or Machu Picchu Mountain (we can help you purchase them separately), optional tips, and travel insurance."""

DESC_FRIENDS = """Briefing
Entrance permits to Lares, the 2-day Inca Trail, and Machu Picchu (second entrance)
Transportation:
Bus from Cusco to Huacawasi-Lares (starting point of the hike)
Expedition train from Ollantaytambo to Km 104 (starting point of the hike)
Machu Picchu bus down/up/down (3 rides)
Expedition train from Aguas Calientes to Ollantaytambo
Bus from Ollantaytambo station to hotel in Cusco
Picnic tent (third day) and hiking poles
Meals: 3 breakfasts, 3 snacks, 4 lunches (1 box lunch), 3 tea times, and 3 dinners
Trek staff: Professional guide, cooks, muleteers, pack horses, llamas for personal belongings, and an emergency horse
Accommodation: 2 nights homestay in Lares and 1 night in a 3-star hotel in Machu Picchu
Safety equipment: Satellite phones, radios, and first aid kit
NOT INCLUDED:
First breakfast, entrance to Huayna Picchu Mountain or Machu Picchu Mountain (we can help you purchase them separately), optional tips, and travel insurance."""

UPDATES = {
    22: {
        "name": "4-Day Lares & Short Inca Trail – Group",
        "description_sale": DESC_GROUP
    },
    23: {
        "name": "4-Day Lares & Short Inca Trail – Couples",
        "description_sale": DESC_COUPLES
    },
    24: {
        "name": "4-Day Lares & Short Inca Trail – Families",
        "description_sale": DESC_FAMILIES
    },
    25: {
        "name": "4-Day Lares & Short Inca Trail – Friends",
        "description_sale": DESC_FRIENDS
    }
}

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    languages = ["es_419", "en_US"]
    for lang in languages:
        print(f"\nUpdating Lares products in context lang={lang}...")
        for product_id, vals in UPDATES.items():
            print(f"Updating product ID {product_id} to '{vals['name']}'...")
            client.execute(
                "product.template",
                "write",
                [product_id],
                vals,
                context={"lang": lang}
            )
            
    print("\n🎉 Lares products and descriptions updated successfully in all contexts.")

if __name__ == "__main__":
    main()
