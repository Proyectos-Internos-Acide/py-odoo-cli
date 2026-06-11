import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

DESC_1D = """Included Services According to Train Type
Expedition / Voyager Train (Standard Tourist Service)
Pick-up from your hotel in Cusco (historic center).
Tourist transportation Cusco – Ollantaytambo – Cusco.
Round-trip Expedition or Voyager train tickets (Peru Rail / Inca Rail).
Reception in Aguas Calientes by local staff.
Tourist bus tickets Aguas Calientes – Machu Picchu – Aguas Calientes.
Entrance ticket to Machu Picchu (Circuit 1, 2, 3, or 4, subject to availability).
Group guided tour (2 to 2.5 hours) with an official guide (the guide will meet you in Aguas Calientes).
Personalized assistance before and during the tour.
In-person or virtual briefing before the trip.
Vistadome Train (Superior Panoramic Service)
Includes everything above, plus:
Train with panoramic windows and more comfortable seats.
Snacks and beverages onboard.
Cultural show or Andean fashion show (only with Peru Rail on the return train).
Greater comfort to enjoy the Sacred Valley scenery.
Hiram Bingham Train (Luxury All-Inclusive Service)
Includes all previous services, plus:
Private transfers from Cusco (optional depending on departure time).
VIP waiting lounge at the station.
Dining car with gourmet lunch onboard.
Open bar with selected wines and cocktails.
Private professional guide throughout the entire journey.
Priority entrance to Machu Picchu and luxury bus service.
Gourmet dinner on the return train.
Live music, exclusive atmosphere, and personalized service at all times.
Services Not Included
Breakfast and lunch (except on the Hiram Bingham train, where they are included).
Tips: Voluntary for the guide or staff (optional).
Personal expenses: Shopping at local stores, souvenirs, use of public restrooms, etc.
Travel insurance: Not included. We recommend purchasing one that covers medical assistance and cancellations due to external causes.
Transfers outside the established schedule (can be arranged for an additional fee).
Entrance to Huayna Picchu Mountain or Machu Picchu Mountain (not included in this program, but can be added in advance subject to limited availability)."""

DESC_2D = """Included Services
General Services (for both train types)
Pick-up from your hotel in Cusco (historic center).
Private tourist transportation Cusco – Moray – Maras Salt Mines – Ollantaytambo.
Private professional bilingual guide (Spanish or English): Specialist in Andean culture, nature, and human experience.
Entrance tickets to all archaeological sites: Moray, Maras Salt Mines, and Partial Tourist Ticket (BTC).
Entrance ticket to Machu Picchu (official circuit subject to availability).
Tourist bus Aguas Calientes – Machu Picchu – Aguas Calientes.
Private guided tour in Machu Picchu (2 to 3 hours).
Personalized assistance and continuous support at all times.
Meals Included
Lunch at a local restaurant in Ollantaytambo (Day 1).
Dinner at a tourist restaurant in Aguas Calientes (Day 1).
Breakfast at the hotel (Day 2).
Vegetarian, vegan, or special meal options available upon request.
Accommodation
1 night in a 3-star hotel in Aguas Calientes (double or matrimonial room).
Upgrade to a 4- or 5-star hotel available upon request.
Included Train – Choose Your Experience
Option 1: Expedition / Voyager Train
Comfortable tourist train with panoramic windows.
Standard and efficient service.
Ideal for travelers who prioritize cultural experience over luxury.
Option 2: Vistadome Train
Panoramic side and ceiling windows.
Snacks and beverages included onboard.
Cultural show onboard (on the return trip).
More space, comfort, and extended landscape views.
Services Not Included
Lunch on the second day in Aguas Calientes (can be added upon request).
Entrance to Huayna Picchu Mountain or Machu Picchu Mountain: not included (can be added in advance, subject to limited availability).
Tips for guides, drivers, or local staff (optional, according to your satisfaction).
Personal expenses: snacks, souvenirs, extra beverages, use of public restrooms.
Travel insurance: highly recommended, not included.
Upgrade to the Hiram Bingham train or luxury accommodation: available upon request."""

DESC_3D = """Included Services
General Services
Private transfers throughout the entire journey:
Hotel – archaeological sites – train station – hotel in Cusco.
Private professional bilingual guide (Spanish or English):
Accompaniment throughout the 3 days with a cultural and human-centered approach.
Official entrance tickets to all sites:
Tourist Tickets (City Tour + Moray + Ollantaytambo), Maras Salt Mines, and official entrance ticket to Machu Picchu (circuit assigned according to availability).
Tourist bus Aguas Calientes – Machu Picchu – Aguas Calientes.
Private guided tour in Machu Picchu (2 to 3 hours).
Meals Included
Lunch at a local restaurant in Ollantaytambo (Day 2).
Breakfast at the hotel in Aguas Calientes (Day 3).
Vegetarian, vegan, or special meal options available upon request.
Accommodation
1 night in a 3-star hotel in Aguas Calientes (double or matrimonial room).
Hotels such as Tierra Viva, Casa Andina, or similar.
Includes buffet breakfast, Wi-Fi, and permanent service.
Upgrade to a 4- or 5-star hotel available upon request.
Included Train – Choose Your Experience
Option 1: Expedition / Voyager Train
Comfortable tourist train with panoramic windows.
Standard and efficient service.
Ideal for travelers who prioritize cultural experiences over luxury.
Option 2: Vistadome Train
Panoramic side and ceiling windows.
Snacks and beverages included onboard.
Cultural show onboard (return trip).
More space, comfort, and extended views of the landscape.
Services Not Included
Lunch and dinner on Day 1 (City Tour).
Dinner on Day 2 in Aguas Calientes (can be added as an extra).
Lunch on Day 3 in Aguas Calientes (free time before the return train).
Tips for the guide, driver, or local staff (optional, based on your experience).
Personal expenses: beverages, snacks, souvenirs, use of public restrooms.
Entrance to Huayna Picchu Mountain or Machu Picchu Mountain (available with advance reservation and limited availability).
Travel insurance: not included, but highly recommended."""

UPDATES = {
    37: {
        "name": "Machu Picchu 1 Day",
        "description_sale": DESC_1D
    },
    38: {
        "name": "Machu Picchu 2 Days",
        "description_sale": DESC_2D
    },
    39: {
        "name": "Machu Picchu 3 Days",
        "description_sale": DESC_3D
    }
}

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    languages = ["es_419", "en_US"]
    for lang in languages:
        print(f"\nUpdating Machu Picchu products in context lang={lang}...")
        for product_id, vals in UPDATES.items():
            print(f"Updating product ID {product_id} to '{vals['name']}'...")
            client.execute(
                "product.template",
                "write",
                [product_id],
                vals,
                context={"lang": lang}
            )
            
    print("\n🎉 Machu Picchu products updated successfully in all contexts.")

if __name__ == "__main__":
    main()
