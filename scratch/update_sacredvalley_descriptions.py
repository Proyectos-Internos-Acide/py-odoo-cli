import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

DESC = """Included Services
Authorized and modern tourist transportation:
Spacious, clean, comfortable vehicles with air conditioning, adapted to the size of the group.
Pick-up from your hotel located in Cusco’s historic center.
If you stay outside this area, a nearby meeting point will be arranged.
Professional bilingual guide (Spanish – English):
Highly trained in Andean history and culture, with first aid training.
Personalized assistance:
Coordinator or transfer assistant for medium and large groups.
Prior coordination via WhatsApp or email:
Clear confirmation and continuous support before and during the tour.
Entrance tickets to all tourist sites included in the itinerary:
Partial Tourist Ticket (BTC – Circuit II):
Includes Pisac, Ollantaytambo, and Chinchero.
Textile center in Chinchero and Hawana Cancha (entrance included).
Services Not Included
Lunch in Urubamba:
Not included in the base price. We can help you reserve a buffet tourist restaurant or à la carte restaurant. (See additional services section.)
Personal drinks and snacks:
We recommend bringing water, fruit, or energy bars.
Tips:
Optional and at your discretion for the guide and driver.
Personal expenses:
Shopping, souvenirs, travel insurance, among others.
Travel insurance:
Not included. We recommend traveling with insurance that covers medical assistance, accidents, or cancellations due to external causes."""

UPDATES = {
    35: {
        "name": "Sacred Valley Full Day",
        "description_sale": DESC
    }
}

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    languages = ["es_419", "en_US"]
    for lang in languages:
        print(f"\nUpdating Sacred Valley product in context lang={lang}...")
        for product_id, vals in UPDATES.items():
            print(f"Updating product ID {product_id} to '{vals['name']}'...")
            client.execute(
                "product.template",
                "write",
                [product_id],
                vals,
                context={"lang": lang}
            )
            
    print("\n🎉 Sacred Valley product updated successfully in all contexts.")

if __name__ == "__main__":
    main()
