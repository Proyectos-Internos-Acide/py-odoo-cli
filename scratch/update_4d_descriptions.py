import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

DESC_SHARED = """INCLUDED SERVICES
Briefing the day before the trek.
Entrance tickets to the Inca Trail and Machu Picchu (second entrance).
Staff: Professional guide, cooks, porters, and an extra porter for 8 kg of personal belongings.
Meals: 3 breakfasts, 4 snacks, 3 lunches, 3 tea times, and 3 dinners.
Camping equipment: Tents, inflatable sleeping pads, fully equipped kitchen and dining tents, toilet tents, and trekking poles.
Emergency equipment: Satellite phones, radios, and first aid kit.
Transportation:
Bus to Km 82 (starting point of the hike)
Bus down from Machu Picchu
Expedition return train
Transfer from the train station to the hotel
NOT INCLUDED
Breakfast on the first day and the last lunch, sleeping bag, Huayna Picchu entrance tickets, tips (optional), and travel insurance."""

DESC_OTHERS = """INCLUDED SERVICES
Briefing the day before the trek.
Entrance tickets to the Inca Trail and Machu Picchu (second entrance).
Staff: Professional guide, cooks, porters, and an extra porter for 8 kg of personal belongings.
Meals: 3 breakfasts, 4 snacks, 4 lunches, 3 tea times, and 3 dinners.
Camping equipment: Tents, inflatable sleeping pads, sleeping bag, fully equipped kitchen and dining tents, toilet tents, and trekking poles.
Emergency equipment: Satellite phones, radios, and first aid kit.
Transportation:
Bus to Km 82 (starting point of the hike)
Bus down from Machu Picchu
Expedition return train
Transfer from the train station to the hotel
NOT INCLUDED
Breakfast on the first day, Huayna Picchu entrance tickets, tips (optional), and travel insurance."""

UPDATES = {
    11: DESC_SHARED, # Inca Trail 4 Days - Shared Group
    14: DESC_OTHERS, # Inca Trail 4 Days – For Couples
    15: DESC_OTHERS, # Inca Trail 4 Days – For Families
    16: DESC_OTHERS  # Inca Trail 4 Days – For Friends
}

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    languages = ["es_419", "en_US"]
    for lang in languages:
        print(f"\nUpdating descriptions in context lang={lang}...")
        for product_id, desc in UPDATES.items():
            print(f"Updating product ID {product_id}...")
            client.execute(
                "product.template",
                "write",
                [product_id],
                {"description_sale": desc},
                context={"lang": lang}
            )
            
    print("\n🎉 Descriptions updated successfully in all contexts.")

if __name__ == "__main__":
    main()
