import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

DESC_RAINBOW = """Included Services
Authorized tourist transportation (round trip):
Modern, comfortable, and safe vehicles from Cusco to Pampachiri or Chillihuani (starting point of the hike).
Pick-up from your hotel located in Cusco’s historic center.
If you stay outside the designated area, a nearby meeting point will be arranged.
Professional bilingual guide (Spanish – English):
Specialized in high-altitude hiking, Andean culture, and first aid.
Additional logistical assistance:
Coordinator or assistant guide for medium and large groups.
Breakfast at a local restaurant in Cusipata:
Nutritious, traditional, and light meal suitable for the hike.
Buffet lunch in Cusipata:
Traditional Andean dishes with vegetarian and vegan options.
Entrance ticket to Rainbow Mountain – Vinicunca.
First aid kit and oxygen:
Available in the vehicle and along the route.
Trekking poles (upon request):
Useful for both ascent and descent.
Personalized assistance:
Support via WhatsApp and email before, during, and after the experience.
Services Not Included
Support horse (optional).
Warm clothing, gloves, rain gear, or trekking shoes.
Personal snacks or additional beverages not included with lunch.
Tips: Optional for the guide and driver.
Personal expenses: Souvenirs, use of local restrooms, etc.
Travel insurance: Not included. We recommend having insurance that covers high-altitude medical assistance."""

DESC_HUMANTAY = """Included Services
Authorized tourist transportation (round trip):
Modern and comfortable vehicle from Cusco to Soraypampa.
Pick-up from your hotel located in Cusco’s historic center.
If you stay outside the designated area, a nearby meeting point will be arranged.
Professional bilingual guide (Spanish – English):
Specialized in high-altitude hiking, Andean culture, and first aid.
Breakfast in Mollepata:
Nutritious and adapted to the physical activity you will perform.
Buffet lunch in Mollepata:
Traditional dishes and vegetarian options.
Entrance ticket to Humantay Lake:
Tourist entrance fee included in our rates.
First aid kit and oxygen:
Available in the vehicle and during the hike.
Personalized assistance:
Support before, during, and after the tour via WhatsApp or email.
Trekking poles (optional, upon request):
Included at no additional cost.
Services Not Included
Support horse during the hike:
Optional and available at an additional cost (paid directly to local communities).
Mountain clothing:
Windbreaker jackets, gloves, hats, or rain ponchos are not included.
Personal snacks or additional beverages not included with breakfast or lunch.
Tips:
Optional for the guide and driver.
Personal expenses:
Souvenirs, use of local restrooms, etc.
Travel insurance:
Not included. We recommend having insurance that covers high-altitude medical assistance."""

UPDATES = {
    40: {
        "name": "Rainbow Mountain",
        "description_sale": DESC_RAINBOW
    },
    41: {
        "name": "Humantay Lake",
        "description_sale": DESC_HUMANTAY
    }
}

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    languages = ["es_419", "en_US"]
    for lang in languages:
        print(f"\nUpdating Rainbow and Humantay products in context lang={lang}...")
        for product_id, vals in UPDATES.items():
            print(f"Updating product ID {product_id} to '{vals['name']}'...")
            client.execute(
                "product.template",
                "write",
                [product_id],
                vals,
                context={"lang": lang}
            )
            
    print("\n🎉 Rainbow and Humantay products updated successfully in all contexts.")

if __name__ == "__main__":
    main()
