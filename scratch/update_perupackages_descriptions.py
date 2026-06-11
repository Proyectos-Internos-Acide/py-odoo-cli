import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

DESC_6D = """Included Services
1. Transportation & Transfers
Airport – hotel – airport transfers in Lima and Cusco 
Tourist transportation for the Cusco City Tour and Sacred Valley Tour 
Round-trip Expedition tourist train: Ollantaytambo – Km 104 – Aguas Calientes – Ollantaytambo 
Transfer from Cusco – Ollantaytambo train station – Cusco (start and end of the Inca Trail) 
Machu Picchu – Aguas Calientes – Machu Picchu bus service (3 tickets included) 
2. Excursions & Experiences
Cusco City Tour: Cathedral, Qoricancha, Sacsayhuamán, Q’enqo, Tambomachay, and Puca Pucara 
Sacred Valley Tour: Pisac market and Inca town, Ollantaytambo, Chinchero Inca town and market 
2-Day Inca Trail: Chachabamba, Wiñay Wayna, Intipunku, and Machu Picchu 
Full guided tour of Machu Picchu on the second day of the trek 
3. Entrance Tickets & Permits
Entrance tickets to all sites included in the City Tour and Sacred Valley Tour 
Official permit for the 2-Day Inca Trail 
Entrance ticket to Machu Picchu 
4. Professional Guides
Experts in history, archaeology, nature, and Andean culture 
Extensive experience in trekking and international group assistance 
Friendly, bilingual, and trained in first aid and rescue 
Personalized assistance throughout all tours and the Inca Trail 
5. Accommodation – 5 Nights
1 night in Lima (3-star hotel) 
3 nights in Cusco (3-star hotel) 
1 night in Aguas Calientes (3-star hotel) 
Standard double or matrimonial rooms with breakfast included 
6. Meals During the Inca Trail
1 breakfast, 1 box lunch, and 1 dinner 
Vegetarian, vegan, or special dietary options available upon request 
7. Safety & Permanent Assistance
Trekking poles 
Complete first aid kit along the route 
Communication radios for constant contact with the main office 
Logistical supervision before, during, and after the Inca Trail 
Not Included Services
Meals: City Tour and Sacred Valley tours do not include meals. The Inca Trail does not include the first breakfast or the final lunch. 
Airfare: Domestic and international flights are not included. 
Huayna Picchu Mountain or Machu Picchu Mountain entrance tickets: Optional and subject to availability (advance reservation required). 
Travel insurance: Not mandatory, but highly recommended to cover medical or logistical emergencies. 
Tips: Voluntary and intended to recognize the effort of the staff accompanying you."""

DESC_10D = """Included Services
Transportation & Transfers
Airport – hotel – airport transfers in Lima (2 transfers) 
Airport – hotel – airport transfers in Cusco (2 transfers) 
Tourist transportation from Lima to Paracas, Paracas to Nazca, and return to Lima 
Transportation for the Cusco City Tour and Sacred Valley excursion 
Private transfer Cusco – Km 82 (start of the Inca Trail) 
Bus down from Machu Picchu to Aguas Calientes 
Expedition tourist train return ticket: Aguas Calientes – Ollantaytambo 
Private transfer from the train station to your hotel in Cusco 
Excursions & Experiences
Ballestas Islands: boat excursion to observe marine wildlife (sea lions, penguins, birds) 
Nazca Lines: 40-minute flight over the ancient geoglyphs 
Cusco City Tour: Cathedral, Qoricancha, Sacsayhuamán, Q’enqo, Tambomachay, and Puca Pucara 
Sacred Valley Tour: Pisac, Ollantaytambo, Chinchero, and traditional markets 
Wayki Experience: authentic immersion in a porter community 
Classic 4-Day Inca Trail: archaeological sites, Intipunku, and Machu Picchu 
Complete guided tour of Machu Picchu with free time to explore 
Official Entrance Tickets & Permits
Entrance to Ballestas Islands, Nazca flight, and port taxes 
Tourist tickets for all sites included in the City Tour and Sacred Valley 
Inca Trail and Machu Picchu permits (managed by Wayki Trek) 
Official entrance to the Wayki community cultural experience 
Specialized Staff & Logistics
Professional bilingual guides trained in history, Andean culture, and first aid 
Specialized trekking chef and assistant 
Porters carrying all expedition equipment plus 8 kg of personal belongings per traveler 
Premium Camping Equipment (Inca Trail)
High-mountain 4-season tents (North Face, Eureka, or Mountain Hardwear) 
Therm-a-Rest inflatable sleeping mats 
Personal pillows and extra blankets 
Trekking poles 
Fully equipped dining tent (chairs, tables, complete tableware) 
Professional kitchen tent 
Eco-friendly portable toilets with water pump system 
Accommodation – 9 Nights
2 nights in Lima (3-star hotel) 
3 nights in Cusco (3-star hotel) 
1 night in an Andean community (Wayki Experience) 
3 nights camping on the Inca Trail 
Double or matrimonial rooms with breakfast included 
Full Meal Plan
Breakfasts included at hotels 
In the Wayki community: 1 lunch, 1 dinner, and 1 breakfast 
During the Inca Trail: 3 breakfasts, 3 lunches, 3 tea times, 3 dinners, and 3 daily energy snacks 
Vegetarian, vegan, and special dietary options available upon request 
Safety & Permanent Assistance
Complete first aid kit along the route 
Communication radios and satellite phones in remote areas 
Remote medical assistance and emergency protocols 
Daily logistical coordination and supervision by the Wayki Trek team 
Not Included Services
Flights & Air Transportation
International flights to and from Peru 
Domestic flights between Lima and Cusco 
Equipment
Sleeping bag 
Meals & Drinks
Lunches and dinners in Lima, Paracas, Nazca, and Cusco (except those specified in the itinerary) 
Alcoholic beverages and additional snacks not mentioned 
Optional Entrance Tickets & Activities
Additional entrance tickets not specified in the itinerary 
Optional activities such as climbing Huayna Picchu or Machu Picchu Mountain (subject to availability and advance reservation) 
Additional Accommodation & Services
Extra hotel nights before or after the tour 
Hotel upgrades or accommodation category changes (subject to availability and additional cost) 
Travel Insurance
Personal travel insurance (highly recommended to cover cancellations, medical emergencies, lost luggage, among others) 
Tips & Personal Expenses
Tips for guides, chefs, porters, and service staff (optional but recommended) 
Personal expenses such as souvenirs, laundry, phone calls, restaurant tips, or anything not mentioned in the itinerary"""

DESC_12D = """Included Services
1. Transportation & Transfers
Airport – hotel – airport transfers in Lima (2 transfers) 
Airport – hotel – airport transfers in Cusco (2 transfers) 
Tourist transportation for the Cusco City Tour and Sacred Valley Tour 
Local transportation to and from the porter community 
Transportation from the community or Cusco to Km 82 (start of the Inca Trail) 
Bus down from Machu Picchu to Aguas Calientes 
Expedition tourist train return ticket: Aguas Calientes – Ollantaytambo 
Transfer from the train station to your hotel in Cusco 
2. Excursions & Experiences
Cusco City Tour: Cathedral, Qoricancha, Sacsayhuamán, Q’enqo, Tambomachay, and Puca Pucara 
Sacred Valley Tour: Pisac, Ollantaytambo, Chinchero, and traditional markets 
Wayki Experience: authentic immersion in the porter community 
4-Day Inca Trail: archaeological sites, Intipunku, and Machu Picchu 
Amazon Jungle Adventure (Puerto Maldonado): hikes, lakes, Monkey Island, wildlife observation, and oxbow lakes 
3. Official Entrance Tickets & Permits
Tourist tickets for all attractions included in the City Tour and Sacred Valley 
Official Ministry of Culture permits for the Inca Trail and Machu Picchu 
Entrance to the Andean porter community for the cultural experience 
Entrance tickets and permits for all activities in the Puerto Maldonado Amazon reserve 
4. Specialized Staff & Logistics
Professional bilingual guides trained in history, Andean culture, biodiversity, and first aid 
Specialized chef and assistant during the Inca Trail and at the Amazon lodge 
Porters carrying expedition logistics and up to 8 kg of personal belongings per traveler 
Professional drivers and logistical staff throughout every stage of the trip 
5. Premium Camping Equipment (Inca Trail)
High-mountain 4-season tents (North Face, Eureka, or Mountain Hardwear) 
Therm-a-Rest inflatable sleeping mats 
Trekking poles 
Fully equipped dining tent (chairs, tables, utensils) 
Kitchen tent with all necessary equipment 
Eco-friendly portable toilets with water pump system for greater hygiene 
6. Accommodation & Campsites – 10 Nights
1 night in Lima (3-star hotel) 
5 nights in Cusco (3-star hotel) 
1 night in an Andean community (family homestay) 
3 nights camping during the Inca Trail 
3 nights at the Ecoamazonia Amazon lodge 
Note: Double or matrimonial rooms with breakfast included.
7. Meals
Breakfasts included at hotels 
In the porter community: 1 lunch, 1 dinner, and 1 traditional breakfast 
During the Inca Trail: 3 breakfasts, 3 lunches, 3 tea times, 3 dinners, and 3 daily energy snacks 
In the Amazon jungle: 3 breakfasts, 3 lunches, and 3 dinners 
Vegetarian, vegan, and special diet options available upon request 
8. Safety & Permanent Assistance
Complete first aid kit throughout the journey 
Communication radios and satellite phones in remote areas 
Remote medical assistance and emergency protocols 
Daily logistical supervision by the Wayki Trek team 
Not Included Services
1. Air Transportation
International flights to and from Peru 
Domestic flights between Lima – Cusco – Puerto Maldonado – Lima
2. Personal Equipment
Sleeping bag for the Inca Trail (available for rent if you do not bring your own) 
3. Meals & Drinks
Lunches and dinners in Lima, during the City Tour, Sacred Valley Tour, and the final lunch in Aguas Calientes after visiting Machu Picchu 
Alcoholic beverages and additional snacks not specified in the itinerary 
4. Optional Entrance Tickets & Activities
Additional entrance tickets not detailed in the program 
Optional climb to Huayna Picchu or Machu Picchu Mountain (subject to availability and advance reservation) 
5. Additional Accommodation & Services
Extra nights in Lima, Cusco, or other cities before or after the tour
(We can help organize this if you decide to extend your stay.) 
6. Travel Insurance
Personal travel insurance (highly recommended and should cover medical emergencies, cancellations, lost luggage, etc.) 
7. Tips & Personal Expenses
Tips for guides, chefs, porters, and service staff (optional but recommended) 
Personal expenses such as souvenirs, laundry, phone calls, restaurant tips, or anything not mentioned in the itinerary"""

DESC_15D = """Included Services
Transportation & Transfers
Travel throughout Peru in comfort and efficiency, combining private transportation and reclining sleeper buses for long-distance routes:
Airport – hotel – airport transfers in Lima
Interprovincial sleeper buses on the Lima–Paracas, Paracas–Nazca, and Nazca–Arequipa routes
Speedboat tour to the Ballestas Islands
Tourist transportation in Arequipa, Colca Canyon, Puno, the Sacred Valley, and Cusco
Transfers to the Andean community and to Km 82 (start of the Inca Trail)
Bus down from Machu Picchu to Aguas Calientes
Expedition tourist train from Aguas Calientes to Ollantaytambo
Transfer from the train station to your hotel and airport in Cusco
Excursions & Experiences
Ballestas Islands: vibrant marine wildlife in a unique ecosystem
Nazca Lines: scenic flight over ancient desert geoglyphs
Arequipa countryside tour: viewpoints, Andean terraces, and colonial-mestizo architecture
Colca Canyon: condor watching and breathtaking landscapes
Lake Titicaca (2 days): visits to the communities of Uros, Amantaní, and Taquile
Route of the Sun: visits to Pukará, Raqchi, and Andahuaylillas
Sacred Valley: Pisac, Ollantaytambo, Chinchero, and traditional markets
Wayki Experience: cultural immersion with porters in an Andean community
Classic 4-Day Inca Trail: an unforgettable trek featuring archaeological sites, biodiversity, and spiritual connection
Official Entrance Tickets & Permits
Entrance tickets to the Ballestas Islands, Nazca Lines, and attractions in Arequipa
Permits and entrance tickets to Chivay and Colca Canyon
Entrance tickets to Uros, Amantaní, and Taquile
Tourist tickets for the Route of the Sun and the Sacred Valley
Official Inca Trail and Machu Picchu permits regulated by the Ministry of Culture
Authorized access to the porter community
Specialized Staff & Logistics
Professional bilingual guides, empathetic and highly knowledgeable in culture, history, nature, and first aid
Specialized chef and assistant during the Inca Trail trek
Trained porters who carry up to 8 kg (17.6 lb) of your personal belongings
Responsible drivers and logistics staff throughout every stage of the trip
Premium Camping Equipment (Inca Trail)
High-mountain 4-season tents from recognized brands
Therm-a-Rest inflatable mattresses, pillows, and extra blankets
Trekking poles included
Dining tent with tables, chairs, and complete tableware
Professional kitchen tent and eco-friendly portable toilets
Accommodation & Campsites – 15 Nights
1 night in Lima (3★ hotel)
1 night in Nazca (3★ hotel)
2 nights in Arequipa (3★ hotel)
1 night in Chivay (3★ hotel)
2 nights in Puno (3★ hotel)
1 night in Amantaní (local homestay)
3 nights in Cusco (3★ hotel)
1 night in an Andean community (family homestay)
3 nights camping during the Inca Trail
Hotel rooms are double or matrimonial and include breakfast.
Meals
Breakfasts included at hotels
1 breakfast, 1 lunch, and 1 dinner on the Amantaní and Taquile Islands
Lunch during the Route of the Sun tour (Puno – Cusco)
In the porter community: 1 lunch, 1 dinner, and 1 breakfast
During the Inca Trail: 3 breakfasts, 3 lunches, 3 afternoon snacks, 3 dinners, and 3 daily energy snacks
Vegetarian, vegan, and special diet options available upon request
Safety & Permanent Assistance
First aid kits available throughout the route
Communication radios and satellite phones in remote areas
Remote medical assistance and active emergency protocols
Daily logistical supervision by the Wayki Trek team
Services Not Included
Air Transportation
International flights to and from Peru
Domestic flight from Cusco to Lima
(We can help you find the best schedules and fares upon request.)
Personal Equipment
Sleeping bag for the Inca Trail
(You may rent a high-mountain sleeping bag through us if you prefer not to bring your own.)
Meals & Beverages
Lunches and dinners in cities such as Lima, Nazca, Arequipa, Chivay, Puno, Cusco, and Aguas Calientes
(except for those specifically listed as included in the itinerary; the last lunch in Aguas Calientes after the Inca Trail is not included)
Alcoholic beverages, soft drinks, and additional snacks not specified
Optional Activities & Entrance Fees
Optional hike to Huayna Picchu Mountain or Machu Picchu Mountain
(subject to availability and advance reservation)
We can help arrange these additional experiences if you wish to include them in your Machu Picchu visit.
Additional Accommodation & Services
Extra nights in Lima, Cusco, or other cities before or after the tour
(We can arrange additional accommodation or upgrades if you decide to extend your trip.)
Hotel upgrades to 4★ or 5★ categories available upon request
Travel Insurance
Personal travel insurance is highly recommended
(It should include coverage for cancellations, emergency medical care, lost luggage, and other unforeseen situations.)
Tips & Personal Expenses
Voluntary tips for guides, chefs, porters, and logistics staff
Personal expenses such as souvenirs, laundry, phone calls, restaurant tips, or anything not mentioned in the itinerary"""

UPDATES = {
    42: {
        "name": "Peru 6 Days",
        "description_sale": DESC_6D
    },
    44: {
        "name": "Peru 10 Days",
        "description_sale": DESC_10D
    },
    45: {
        "name": "Peru 12 Days",
        "description_sale": DESC_12D
    },
    43: {
        "name": "Peru 15 Days",
        "description_sale": DESC_15D
    }
}

def main():
    client = OdooClient()
    client.connect()
    print("Connected to Odoo.")

    languages = ["es_419", "en_US"]
    for lang in languages:
        print(f"\nUpdating Peru Packages in context lang={lang}...")
        for product_id, vals in UPDATES.items():
            print(f"Updating product ID {product_id} to '{vals['name']}'...")
            client.execute(
                "product.template",
                "write",
                [product_id],
                vals,
                context={"lang": lang}
            )
            
    print("\n🎉 Peru Packages updated successfully in all contexts.")

if __name__ == "__main__":
    main()
