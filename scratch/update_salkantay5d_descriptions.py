import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

DESC = """Briefing before the hike on the agreed date and time.
Entrance permits to Salkantay and Machu Picchu with Circuit No. 1.
TRANSPORTATION
From your hotel in Cusco to the trailhead in Soraypampa by Mercedes Benz minibus.
Train from Hydroelectric Station to the town of Aguas Calientes.
Bus from Aguas Calientes → Machu Picchu → Aguas Calientes.
Return Expedition train ticket from Aguas Calientes to Ollantaytambo after your visit to Machu Picchu.
Bus from Ollantaytambo to your hotel in Cusco.
TREKKING STAFF
Professional Guide:
With more than 12 years of trekking experience, fluent foreign language skills, constant first aid and group management training, and extensive cultural and natural knowledge.
Chefs:
Trained in various culinary schools with more than 10 years of experience, specializing in local, national, and international cuisine.
Friendly muleteers and pack horses from different communities who will transport all expedition logistics.
Additional 8 kg porter allowance to carry the client’s personal belongings.
MEALS
3 breakfasts, 4 snacks, 4 lunches, 3 tea times, and 3 dinners.
Breakfasts:
Fruit salad, yogurt, oatmeal, hot chocolate, milk, coffee, tea, pancakes, scrambled eggs, jam, butter, and bread.
Snacks:
Fruits, cookies, nuts, and sweets (chocolates and candies).
Lunches:
Buffet-style meals including soups, 2 to 4 main course options, desserts, and hot beverages. Main dishes include Peruvian classics such as lomo saltado (stir-fried beef with rice and fries) and ají de gallina (creamy mildly spicy chicken), among other options. Vegetarian meals are also available.
Tea Time:
Popcorn, cookies, coffee, hot chocolate, milk, and a variety of teas.
Dinners:
Soups, chicken dishes, pasta, and more.
Water:
Boiled water is provided every day during the trek starting at lunchtime.
CAMPING EQUIPMENT
Tents:
High-mountain 4-season tents from North Face, Eureka, and Mountain Hardwear.
Sleeping Mats:
Our Therm-a-Rest inflatable mattresses guarantee a warm and comfortable night’s sleep on the trail.
Sleeping Bags:
Down sleeping bags rated to -10°C (14°F).
Pillows:
Comfortable pillows for a complete night’s rest.
Blankets:
Each participant will have one available if needed.
Dining Tent:
A spacious dining tent equipped with tables, tablecloths, chairs, and complementary dining items.
Kitchen Tent:
Equipped with everything our chef needs to prepare meals, including gas tanks, gas stove, cookware, and utensils.
Bathroom Tents:
Portable toilet tent with water pump system.
EMERGENCY EQUIPMENT
Satellite Phones:
For communication with the office and anywhere in the world in case of emergency.
Radios:
With a 10 km range and 8 frequencies so guides, chefs, and porters can communicate with each other.
First Aid Kit:
We carry a full selection of over-the-counter medications and supplies, including alcohol, hydrogen peroxide, iodine tincture, germicidal soap, cotton, gauze, bandages, medical adhesive tape, surgical gloves, pain relievers for muscle and stomach aches, fever reducers, antihistamines, anti-inflammatory medication, oral rehydration salts, laxatives, burn creams, splints, blood pressure monitors, and thermometers. If you take prescription medication, you may bring your own medicine.
Note:
Guides are not authorized to medicate or prescribe medicine. The use of any medication is under the client’s authorization.
NOT INCLUDED
Lunch on the fifth day
Trekking poles
Tips: These are VOLUNTARY. Each traveler may decide whether or not to give them.
Travel insurance: This is not mandatory, but we always recommend that our clients purchase it in case of flight issues or unexpected health problems. Please check if your travel insurance policy has altitude restrictions. Some policies are void above 4,000 m (13,123 ft), and the Salkantay Trek reaches 4,600 m (15,091 ft). Other treks in the Cusco region may reach up to 5,000 m (16,404 ft).
One horse to carry up to 10 kg of your personal gear is included. If you need to bring additional weight, you must request an extra horse at the time of booking.
Horse service is only available during the first 2 days of the trek, as these are the most difficult sections. From the third day onward, vehicles are available for luggage transportation."""

UPDATES = {
    32: {
        "name": "Salkantay Trek 5 Days",
        "description_sale": DESC
    }
}

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    languages = ["es_419", "en_US"]
    for lang in languages:
        print(f"\nUpdating Salkantay 5-Day product in context lang={lang}...")
        for product_id, vals in UPDATES.items():
            print(f"Updating product ID {product_id} to '{vals['name']}'...")
            client.execute(
                "product.template",
                "write",
                [product_id],
                vals,
                context={"lang": lang}
            )
            
    print("\n🎉 Salkantay 5-Day product updated successfully in all contexts.")

if __name__ == "__main__":
    main()
