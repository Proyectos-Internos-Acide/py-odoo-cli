import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

DESC_GROUP = """2-DAY INCA TRAIL – GROUP
Briefing
Entrance permits to the Inca Trail and Machu Picchu with Circuit No. 3
Transportation
Hotel to train station transfer (round trip)
Expedition train round trip
Machu Picchu bus down/up/down (3 rides)
3-star hotel in a double room (two beds)
MEALS: 1 box lunch, 1 dinner, and 1 breakfast at the hotel
PROFESSIONAL GUIDE
SAFETY EQUIPMENT: First aid kit, oxygen tank, and satellite phone
NOT INCLUDED:
First breakfast and last lunch, hiking poles, entrance to Huayna Picchu Mountain or Machu Picchu Mountain, optional tips, and travel insurance."""

DESC_COUPLES = """2-DAY INCA TRAIL – COUPLES
Briefing
Entrance permits to the Inca Trail and Machu Picchu with Circuit No. 3
Transportation
Hotel to train station transfer (round trip)
Expedition train round trip
Machu Picchu bus down/up/down (3 rides)
Picnic tent, trekking poles, and cook
3-star hotel in a double room (two beds)
MEALS: 1 box lunch, 1 dinner, 1 lunch, and 1 breakfast at the hotel
PROFESSIONAL GUIDE
SAFETY EQUIPMENT: First aid kit, oxygen tank, and satellite phone
NOT INCLUDED:
First breakfast, entrance to Huayna Picchu Mountain or Machu Picchu Mountain, optional tips, and travel insurance."""

DESC_FAMILIES = """2-DAY INCA TRAIL – FAMILIES
Briefing
Entrance permits to the Inca Trail and Machu Picchu with Circuit No. 3
Transportation
Hotel to train station transfer (round trip)
Expedition train round trip
Machu Picchu bus down/up/down (3 rides)
Picnic tent, trekking poles, and cook
3-star hotel in a double room (two beds)
MEALS: 1 box lunch, 1 dinner, 1 lunch, and 1 breakfast at the hotel
PROFESSIONAL GUIDE
SAFETY EQUIPMENT: First aid kit, oxygen tank, and satellite phone
NOT INCLUDED:
First breakfast, entrance to Huayna Picchu Mountain or Machu Picchu Mountain, optional tips, and travel insurance."""

DESC_FRIENDS = """2-DAY INCA TRAIL – FRIENDS
Briefing
Entrance permits to the Inca Trail and Machu Picchu with Circuit No. 3
Transportation
Hotel to train station transfer (round trip)
Expedition train round trip
Machu Picchu bus down/up/down (3 rides)
Picnic tent, trekking poles, and cook
3-star hotel in a double room (two beds)
MEALS: 1 box lunch, 1 dinner, 1 lunch, and 1 breakfast at the hotel
PROFESSIONAL GUIDE
SAFETY EQUIPMENT: First aid kit, oxygen tank, and satellite phone
NOT INCLUDED:
First breakfast, entrance to Huayna Picchu Mountain or Machu Picchu Mountain, optional tips, and travel insurance."""

UPDATES = {
    5: DESC_GROUP,
    6: DESC_COUPLES,
    8: DESC_FAMILIES,
    13: DESC_FRIENDS
}

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    languages = ["es_419", "en_US"]
    for lang in languages:
        print(f"\nUpdating 2-Day descriptions in context lang={lang}...")
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
