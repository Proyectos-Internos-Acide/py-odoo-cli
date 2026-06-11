import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

DESC = """Included Services
Pre-Trek Briefing Session
One day before the trek begins, you will have an informative meeting with your guide, who will answer all your questions and provide key advice to help you fully enjoy the experience.
Official Entrance Permits
Wayki Trek manages your entrance permits to Ausangate National Park once your reservation is confirmed, ensuring a regulated and environmentally respectful experience.
Specialized Trekking Team
Professional mountain guides with extensive high-altitude experience, fluent English skills, and training in first aid and rescue.
Expert chefs specialized in Andean, international, and vegetarian cuisine, trained in local culinary schools.
Muleteers and horses responsible for transporting expedition logistics and up to 8 kg of your personal belongings. An emergency horse is also included.
Premium Camping Equipment
High-mountain tents (North Face, Eureka, Mountain Hardwear) resistant to extreme conditions.
Therm-a-Rest inflatable sleeping mats.
Trekking poles.
Spacious and fully equipped dining tent.
Kitchen tent with complete cooking equipment.
Bathroom tents with water system.
Full Meal Service During the 5 Days
Nutritious Breakfasts:
Fruit, yogurt, oatmeal, pancakes, eggs, and hot beverages.
Daily Snacks:
Fresh and dried fruits, cookies, and chocolates.
Buffet-Style Lunches:
Soups, 2–4 main dishes (including Peruvian and international options), desserts, and herbal teas.
Afternoon Tea Time:
Popcorn, cookies, hot chocolate, and a variety of teas.
Comforting Dinners:
Soups, stews, and pasta dishes.
Boiled and purified water available from the first lunch and throughout the trek.
Comfortable Private Transportation
Mercedes Benz minibus transportation from Cusco to the trek starting point.
Return transportation from Pacchanta to your hotel in Cusco.
2 nights in Arequipa (3-star hotel).  ???????????
Biodegradable Products
We provide eco-friendly hygiene products for staff, guests, and the cleaning of kitchen and camping equipment. We are committed to protecting the environment.
Emergency Equipment & Remote Medical Assistance
Satellite phone available at all times.
Long-range communication radios for the trekking staff.
Complete first aid kit.
Remote medical assistance via satellite phone with professional follow-up in case of emergency.
Services Not Included
Sleeping bag (-10°C) – available for rent if you do not bring your own.
Single-use tent – thermal and waterproof, ideal if you prefer to sleep alone.
Additional pack horse – for those wishing to transport more than 8 kg (up to 15 kg).
Personal saddle horse – if you prefer not to walk during certain sections.
Voluntary tips – for guides, cooks, and muleteers. They are not mandatory but are appreciated as a gesture of gratitude for their dedication.
Travel insurance."""

UPDATES = {
    30: {
        "name": "Ausangate Trek 5 Days",
        "description_sale": DESC
    }
}

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    languages = ["es_419", "en_US"]
    for lang in languages:
        print(f"\nUpdating Ausangate product in context lang={lang}...")
        for product_id, vals in UPDATES.items():
            print(f"Updating product ID {product_id} to '{vals['name']}'...")
            client.execute(
                "product.template",
                "write",
                [product_id],
                vals,
                context={"lang": lang}
            )
            
    print("\n🎉 Ausangate product updated successfully in all contexts.")

if __name__ == "__main__":
    main()
