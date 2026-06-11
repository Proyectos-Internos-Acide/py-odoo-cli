import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

DESC = """Included Services
Authorized and modern tourist transportation:
Spacious, clean, comfortable vehicles with air conditioning, adapted to the group size.
Pick-up from your hotel located in Cusco’s historic center.
If you stay outside this area, a nearby meeting point will be arranged.
Professional bilingual guide (Spanish – English):
Highly trained in Andean history and culture, with first aid training.
Personalized assistance:
Coordinator or transfer assistant for medium and large groups.
Prior coordination via WhatsApp or email:
Clear confirmation and continuous support before and during the tour.
Entrance tickets to all tourist sites included in the itinerary:
Partial Tourist Ticket – Circuit III:
Entrance to Moray.
Entrance to the Maras Salt Mines.
Personalized assistance before and during the tour:
Support via email and WhatsApp to answer questions and provide assistance.
Services Not Included
Meals and beverages:
The tour does not include breakfast, snacks, or lunch.
Tips:
Voluntary for the guide and driver.
Personal expenses:
Shopping at local stores, souvenirs, use of public restrooms, etc.
Travel insurance:
Not included. We recommend purchasing one that covers medical assistance and cancellations due to external causes."""

UPDATES = {
    36: {
        "name": "Moray & Maras Salt Mines",
        "description_sale": DESC
    }
}

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    languages = ["es_419", "en_US"]
    for lang in languages:
        print(f"\nUpdating Moray product in context lang={lang}...")
        for product_id, vals in UPDATES.items():
            print(f"Updating product ID {product_id} to '{vals['name']}'...")
            client.execute(
                "product.template",
                "write",
                [product_id],
                vals,
                context={"lang": lang}
            )
            
    print("\n🎉 Moray product updated successfully in all contexts.")

if __name__ == "__main__":
    main()
