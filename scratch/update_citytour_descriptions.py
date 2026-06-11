import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

DESC = """Included Services
Everything Essential, No Surprises
Enjoy a worry-free experience. We take care of everything needed to make your tour comfortable, safe, and fully organized from the beginning.
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
Cusco Partial Tourist Ticket (Circuit I):
Includes Sacsayhuamán, Q’enqo, Puka Pukara, and Tambomachay.
Entrance to Cusco Cathedral.
Entrance to Qorikancha (Temple of the Sun).
Services Not Included
Meals and beverages:
The tour does not include snacks, drinks, or lunch.
Tips:
Optional and at your discretion for the guide and driver.
Personal expenses:
Shopping, souvenirs, travel insurance, among others."""

UPDATES = {
    34: {
        "name": "Cusco City Tour",
        "description_sale": DESC
    }
}

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    languages = ["es_419", "en_US"]
    for lang in languages:
        print(f"\nUpdating City Tour product in context lang={lang}...")
        for product_id, vals in UPDATES.items():
            print(f"Updating product ID {product_id} to '{vals['name']}'...")
            client.execute(
                "product.template",
                "write",
                [product_id],
                vals,
                context={"lang": lang}
            )
            
    print("\n🎉 Cusco City Tour product updated successfully in all contexts.")

if __name__ == "__main__":
    main()
