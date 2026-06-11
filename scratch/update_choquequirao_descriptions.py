import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

DESC = """Briefing one day before the trek.
Entrance permits to the Choquequirao Trek.
Trekking Team:
Professional guides, chefs, muleteers, horses, and emergency horse.
Camping Equipment:
Tents: 4-season high-mountain tents from North Face, Eureka, and Mountain Hardwear.
Therm-a-Rest sleeping mats
Sleeping bags
Dining tent
Kitchen tent
Bathroom tents
Meals:
3 breakfasts, 4 morning snacks, 4 lunches, 3 afternoon snacks, and 3 dinners.
Transportation:
From Cusco to the trailhead in Cachora by Mercedes Benz minibus.
Return bus from Cachora to your hotel in Cusco.
Biodegradable products.
Emergency Equipment:
Satellite phones, first aid kit, and medical assistance through satellite communication.
NOT INCLUDED SERVICES
Trekking poles
Tips: These are VOLUNTARY. Each traveler may decide whether or not to give them.
Travel insurance: This is not mandatory, but we always recommend that our clients purchase it in case of flight issues or unexpected health problems.
A horse to carry 8 kg (17.6 lb) of your personal gear is included. If you need to bring additional weight, you must request an extra horse at the time of booking."""

UPDATES = {
    33: {
        "name": "Choquequirao Trek 4 Days",
        "description_sale": DESC
    }
}

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    languages = ["es_419", "en_US"]
    for lang in languages:
        print(f"\nUpdating Choquequirao product in context lang={lang}...")
        for product_id, vals in UPDATES.items():
            print(f"Updating product ID {product_id} to '{vals['name']}'...")
            client.execute(
                "product.template",
                "write",
                [product_id],
                vals,
                context={"lang": lang}
            )
            
    print("\n🎉 Choquequirao product updated successfully in all contexts.")

if __name__ == "__main__":
    main()
