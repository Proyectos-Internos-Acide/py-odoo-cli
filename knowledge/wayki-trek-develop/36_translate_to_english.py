#!/usr/bin/env python3
"""
Translates Odoo product categories, attributes, attribute values, and product templates to English.
Supports both multilingual translation (updating en_US context) and global override (updating es_419 base context).
By default, it will update BOTH es_419 (main/base) and en_US (English) contexts to ensure everything is in English.
"""

from pathlib import Path
import sys
import argparse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

# Translation mappings
CATEGORIES_MAP = {
    "Caminatas alternas": "Alternative Treks",
    "Camino Inca": "Inca Trail",
    "Paquetes": "Packages",
    "Servicios adicionales": "Additional Services",
    "Tours diarios": "Daily Tours"
}

ATTRIBUTES_MAP = {
    "Tipo de pasajero": "Passenger Type",
    "Modalidad / Group": "Group Option",  # Handle possible typos
    "Modalidad / Grupo": "Group Option",
    "Tipo de grupo": "Group Size",
    "Tipo de tren": "Train Class",
    "Número de personas": "Number of People",
    "Alojamiento": "Accommodation",
    "Tipo de alojamiento": "Accommodation Type",
    "Tipo de habitación": "Room Type"
}

VALUES_MAP = {
    "Adulto": "Adult",
    "Estudiante": "Student",
    "Niño": "Child",
    "Compartido (Base por persona)": "Shared (Base per person)",
    "Privado 2 personas (por persona)": "Private 2 people (per person)",
    "Privado 3-4 personas (por persona)": "Private 3-4 people (per person)",
    "Privado 5+ personas (por persona)": "Private 5+ people (per person)",
    "Grupo grande (15 a 30 personas)": "Large group (15 to 30 people)",
    "Grupo mediano (10 a 16 personas)": "Medium group (10 to 16 people)",
    "Grupo pequeño (4 a 10 personas)": "Small group (4 to 10 people)",
    "Tren Expedition / Voyager": "Expedition / Voyager Train",
    "Tren Vistadome": "Vistadome Train",
    "Tren Hiram Bingham": "Hiram Bingham Train",
    "1 persona": "1 person",
    "2 personas": "2 people",
    "3 personas": "3 people",
    "Hotel 3★ – DWB": "Hotel 3★ – DWB",
    "Hotel 3★ – SWD": "Hotel 3★ – SWD",
    "BED & BREAKFAST": "Bed & Breakfast",
    "HOTEL 3 ESTRELLAS": "3-Star Hotel",
    "DWB": "DWB",
    "SWD": "SWD"
}

PRODUCTS_MAP = {
    "Alquiler de bolsa de dormir": "Sleeping bag rental",
    "Ausangate 5 días": "Ausangate 5 Days",
    "Caballo de silla": "Riding horse",
    "Caminatas Cortas - Laguna Humantay": "Short Hikes - Humantay Lake",
    "Caminatas Cortas - Montaña de 7 Colores": "Short Hikes - Rainbow Mountain",
    "Camino Inca 2 días – Grupo Compartido": "Inca Trail 2 Days – Shared Group",
    "Camino Inca 2 días – Para Amigos": "Inca Trail 2 Days – For Friends",
    "Camino Inca 2 días – Para Familias": "Inca Trail 2 Days – For Families",
    "Camino Inca 2 días – Para Parejas": "Inca Trail 2 Days – For Couples",
    "Camino Inca 4 días – Para Amigos": "Inca Trail 4 Days – For Friends",
    "Camino Inca 4 días – Para Familias": "Inca Trail 4 Days – For Families",
    "Camino Inca 4 días – Para Parejas": "Inca Trail 4 Days – For Couples",
    "Camino Inca 4 días-Grupo compartid": "Inca Trail 4 Days - Shared Group",
    "Camino Inca 5 días – Para Amigos": "Inca Trail 5 Days – For Friends",
    "Camino Inca 5 días – Para Familias": "Inca Trail 5 Days – For Families",
    "Camino Inca 5 días – Para Parejas": "Inca Trail 5 Days – For Couples",
    "Camino Inca 5 días – Solitarios": "Inca Trail 5 Days – Solo Travelers",
    "Carpa Privada en TT4D": "Private Tent in TT4D",
    "Choquequirao 4 días": "Choquequirao 4 Days",
    "City tour": "City tour",
    "Cusco - Cusco City Tour": "Cusco - Cusco City Tour",
    "Cusco - Moray & Maras": "Cusco - Moray & Maras",
    "Cusco - Valle Sagrado": "Cusco - Sacred Valley",
    "Habitación Simple": "Single Room",
    "Laguna de Humantay": "Humantay Lake",
    "Lares & Inca 4 días – Para Amigos": "Lares & Inca 4 Days – For Friends",
    "Lares & Inca 4 días – Para Familias": "Lares & Inca 4 Days – For Families",
    "Lares & Inca 4 días – Para Parejas": "Lares & Inca 4 Days – For Couples",
    "Lares & Inca 4 días – Solo": "Lares & Inca 4 Days – Solo",
    "Lares & Machu Picchu 4 días": "Lares & Machu Picchu 4 Days",
    "Machu Picchu - Machu Picchu 1 día": "Machu Picchu - Machu Picchu 1 Day",
    "Machu Picchu - Machu Picchu 2 días": "Machu Picchu - Machu Picchu 2 Days",
    "Machu Picchu - Machu Picchu 3 días": "Machu Picchu - Machu Picchu 3 Days",
    "Montaña de 7 colores": "Rainbow Mountain",
    "Paquetes - Perú 6 días": "Packages - Peru 6 Days",
    "Perú - Perú 10 días": "Peru - Peru 10 Days",
    "Perú - Perú 12 días": "Peru - Peru 12 Days",
    "Perú - Perú 15 días": "Peru - Peru 15 Days",
    "Porter extra 15kg": "Extra porter 15kg",
    "Porter extra 8kg": "Extra porter 8kg",
    "Salkantay & Inca 6 días – Para Amigos": "Salkantay & Inca 6 Days – For Friends",
    "Salkantay & Inca 6 días – Para Familias": "Salkantay & Inca 6 Days – For Families",
    "Salkantay & Inca 6 días – Para Parejas": "Salkantay & Inca 6 Days – For Couples",
    "Salkantay & Inca 6 días – Solo": "Salkantay & Inca 6 Days – Solo",
    "Salkantay 5 días": "Salkantay 5 Days",
    "Ticket Huayna Picchu o Machu Picchu": "Huayna Picchu or Machu Picchu Ticket",
    "Upgrade Vistadome observatory": "Vistadome Observatory Upgrade",
    "Upgrade Vistadome regular": "Vistadome Regular Upgrade",
    "Valle Sagrado": "Sacred Valley",
    "Alquiler bastones": "Walking poles rental",
    "city tour": "City tour",
    "descuento": "Discount"
}

DESCRIPTIONS_MAP = {
    "Ausangate 5 días": (
        "Explore one of Peru's most awe-inspiring routes, surrounded by sacred mountains, "
        "turquoise lagoons, and Quechua communities. The Ausangate Trek is ideal for those seeking "
        "a physical challenge, cultural connection, and genuine camaraderie. In small groups of 4 to 6 people, "
        "you will cross passes over 5,000 meters, camp under starry skies, and end your days in hot springs. "
        "With an expert guide, reliable logistics, and constant warmth, you will live a safe, "
        "profound, and truly transformative experience."
    ),
    "Caminatas Cortas - Laguna Humantay": (
        "Located at the foot of the imposing Mount Salkantay, Humantay Lake is a natural gem of "
        "turquoise waters surrounded by sacred mountains. This one-day hike combines nature, "
        "spirituality, and physical challenge in an unforgettable setting. Ideal for travelers who "
        "are already acclimated and seek an intense and rewarding experience in the Andes. "
        "A route that connects the body with the mountain and the soul with nature!\n\n"
        "We offer different rates based on group size, special discounts, and the option to "
        "customize your experience without compromising quality."
    ),
    "Caminatas Cortas - Montaña de 7 Colores": (
        "Located at over 5,000 m a.s.l., Rainbow Mountain (Vinicunca) is one of Peru's most stunning "
        "natural wonders. This adventure tour takes you through high-altitude landscapes, Andean "
        "communities, and glacier views. Ideal for active travelers seeking a challenging and "
        "rewarding single-day experience.\n\n"
        "Conquer Rainbow Mountain with a complete, safe, and accessible service. We offer different "
        "rates based on group size, special discounts, and the option to customize your experience "
        "without compromising quality."
    ),
    "Camino Inca 2 días – Grupo Compartido": (
        "Live the essence of the legendary Inca Trail in a short but deeply meaningful version. "
        "This shared adventure takes you along ancient pathways through the Andean cloud forest, "
        "surrounded by orchids, birds, and spectacular landscapes. Along the way, you will discover "
        "archaeological sites like Chachabamba and Wiñay Wayna, where the past comes to life. "
        "The highlight comes as you cross Inti Punku, the Sun Gate, and see Machu Picchu for the "
        "first time just as the ancient pilgrims did. An ideal route for those seeking history, "
        "nature, and connection, in the company of other adventurers."
    ),
    "Camino Inca 2 días – Para Parejas": (
        "Perfect for couples seeking an intimate and transformative adventure, this experience "
        "condenses the best of the Inca legacy into a short but deeply meaningful journey. Traverse "
        "the high Andean jungle, surrounded by living nature, wild orchids, and hidden archaeological "
        "remains. Ancient paths will lead you to sacred sites like Chachabamba and Wiñay Wayna, "
        "culminating in an unforgettable arrival at Machu Picchu through the Sun Gate. An experience "
        "that joins not only landscapes, but also hearts. Walking together, discovering together, "
        "growing together."
    ),
    "Camino Inca 4 días – Para Amigos": (
        "Embark with your best friends on a journey that has it all: history, otherworldly landscapes, "
        "living culture, and the personal challenge of conquering the legendary Inca Trail. For four "
        "days, you will hike among ancient ruins, sacred mountains, and cloud forests, sharing laughter, "
        "incredible photos, and moments that will define your friendship forever. With passionate "
        "guides, gourmet meals, comfortable campsites, and authentic cultural experiences, this is more "
        "than a hike: it is a celebration of friendship, adventure, and free spirit. You bring the "
        "energy, we bring the Andean magic."
    ),
    "Camino Inca 4 días – Para Familias": (
        "Live an unforgettable adventure where every step unites generations. The Inca Trail becomes "
        "a natural classroom to learn, share, and grow as a family. Specially designed for those "
        "traveling with children, this journey adapts the pace, services, and experience so that "
        "everyone, from the youngest to the adults, enjoys and connects with Inca history, nature, "
        "and each other. More than a hike, it is an opportunity to build memories and strengthen "
        "bonds with every footprint you leave together in the heart of the Andes."
    ),
    "Camino Inca 4 días – Para Parejas": (
        "Embark on a magical journey designed for two. The Inca Trail 4D - Two Souls Journey is an "
        "intimate and transformative experience that intertwines nature, history, and love. Specially "
        "designed for adventurous couples, this trip combines physical challenge with emotional "
        "depth, passing through sacred landscapes, ancient temples, and nights under millions of "
        "stars. From the first step, Wayki Trek takes care of every detail: dedicated guides, "
        "moments of introspection, Andean gastronomy, and romantic spaces high in the mountains. "
        "This is not just a hike: it is a rite of connection, a reunion with each other and with the "
        "ancestral soul of the Andes."
    ),
    "Camino Inca 4 días-Grupo compartid": (
        "Live the essence of the legendary Inca Trail in a short but deeply meaningful version. "
        "This shared adventure takes you along ancient pathways through the Andean cloud forest, "
        "surrounded by orchids, birds, and spectacular landscapes. Along the way, you will discover "
        "archaeological sites like Chachabamba and Wiñay Wayna, where the past comes to life. "
        "The highlight comes as you cross Inti Punku, the Sun Gate, and see Machu Picchu for the "
        "first time just as the ancient pilgrims did. An ideal route for those seeking history, "
        "nature, and connection, in the company of other adventurers."
    ),
    "Camino Inca 5 días – Para Amigos": (
        "Embark on a legendary journey, where every step among sacred mountains, cloud forests, and "
        "ancestral ruins will strengthen your bond like never before. At a flexible and lively pace, "
        "you will share challenges, laughter, and dreams under infinite skies. Enjoy logistics designed "
        "for your comfort and spaces to celebrate every achievement. Together you will culminate this "
        "odyssey in Machu Picchu, with memories that will be tattooed on your souls."
    ),
    "Camino Inca 5 días – Para Familias": (
        "Discover together the magic of the Andes, step by step, on a journey designed to strengthen "
        "your bonds, awaken your spirit of adventure, and create unforgettable memories. This trip "
        "combines flexible hiking, authentic cultural exploration, and moments of shared reflection. "
        "Accompanied by expert guides, you will travel sacred paths, discover Machu Picchu, and "
        "build memories that will last a lifetime.\n\nA safe, enriching, and transformative "
        "experience, where every step is an opportunity to grow together."
    ),
    "Camino Inca 5 días – Para Parejas": (
        "Discover every corner of the Inca Trail with calm and complicity, exploring even rarely "
        "traveled paths. Walk hand in hand along sacred routes, cross imposing mountains, and share "
        "together the thrill of reaching Machu Picchu. This intimate and flexible journey is filled "
        "with unique moments that will strengthen your connection and reveal new dimensions of your "
        "love, enveloped in the immensity and eternal magic of the Andes."
    ),
    "Camino Inca 5 días – Solitarios": (
        "Embark on a journey designed for solo adventurers seeking more than just a hike: this is "
        "a path to personal transformation. For five days, explore ancient paths, high mountain "
        "passes, and hidden archaeological sites at a gentler pace, allowing a deep connection with "
        "nature, history, and yourself. With individual tents, mindful meals, flexible hiking "
        "schedules, and quiet reflection times, this sacred adventure helps you rediscover your "
        "essence while conquering not just mountains, but new parts of who you are."
    ),
    "Choquequirao 4 días": (
        "Experience a unique journey to Choquequirao, the mystical sister of Machu Picchu. On this "
        "4-day trek, you will share paths with free-spirited travelers, crossing deep canyons, "
        "cloud forests, and Inca staircases, guided by experts and supported by an efficient "
        "logistics team. Everything is included: nutritious food, premium equipment, and space to "
        "enjoy both natural silence and group energy. More than a destination, Choquequirao is an "
        "experience that connects, challenges, and inspires."
    ),
    "Cusco - Cusco City Tour": (
        "Rates by group size:\n- Medium group (10 to 16 people): USD $55 per person. Perfect balance "
        "between price, interaction, and service quality.\n- Large group (15 to 30 people): USD $45 "
        "per person. Most economical and social option, maintaining the Wayki Trek standard."
    ),
    "Cusco - Moray & Maras": (
        "Rates by group size:\n- Small group (4 to 10 people): USD $60 per person. Ideal for those "
        "seeking a more personalized experience with more guide interaction.\n- Medium group (10 to 16 people): "
        "USD $50 per person. Perfect balance between quality service and affordable price.\n- Large group "
        "(15 to 30 people): USD $40 per person. Most economical shared option for social travelers and family groups."
    ),
    "Cusco - Valle Sagrado": (
        "Rates by group size:\n- Medium group (10 to 16 people): USD $55 per person. Perfect balance "
        "between price, interaction, and service quality.\n- Large group (15 to 30 people): USD $45 "
        "per person. Most economical and social option, maintaining the Wayki Trek standard."
    ),
    "Lares & Inca 4 días – Para Amigos": (
        "Embark on a unique journey with your friends through the Peruvian Andes. Experience the magic "
        "of Lares by living with Quechua families, learning from their ancestral wisdom. Then, "
        "connect with the ancient history of the 2-Day Inca Trail, culminating at Machu Picchu at "
        "sunrise, passing through the mystical Sun Gate. These will be days of laughter, challenge, "
        "and connection with the earth, guided by experts and wrapped in sacred landscapes. Comfort, "
        "safety, and soul in every step. A profound, authentic, and powerful experience, made for "
        "those who choose to live the best stories together."
    ),
    "Lares & Inca 4 días – Para Familias": (
        "An experience that transforms with every step, where the family immerses itself in the ancestral "
        "wisdom of the Andes. The Lares + 2-Day Inca Trail route invites you to explore the cultural "
        "heart of Peru through authentic contact with living communities, ancestral ceremonies, and the "
        "magic of sharing learning across generations. Children, youth, and adults will discover new "
        "ways of seeing the world while traveling sacred paths and engaging with the living history "
        "of the area. A journey that inspires, educates, and deeply connects, awakening values, "
        "empathy, and wonder in every family member."
    ),
    "Lares & Inca 4 días – Para Parejas": (
        "Live a transformative journey where love and connection deepen amidst Andean landscapes, "
        "living communities, and ancient trails to Machu Picchu. In Lares, you will be warmly "
        "welcomed by local families, sharing homemade breakfasts, rituals to Pachamama, and simple "
        "moments full of meaning. Then, you will hike the 2-Day Inca Trail together to the Sun Gate, "
        "where Machu Picchu is revealed as a symbol of your shared journey. You will enjoy "
        "personalized attention, comfortable logistics, and intimate spaces. More than a destination, "
        "it is an experience that strengthens your bond at every step."
    ),
    "Lares & Inca 4 días – Solo": (
        "This trip is for those seeking more than just adventure, who desire connection, reflection, "
        "and transformation. The Lares + Inca Trail 4D route combines the cultural wealth of living "
        "Andean communities with the sacred power of hiking to Machu Picchu along ancient Inca trails.\n\n"
        "In Lares, you will share with local families and their ancestral wisdom. Then you will "
        "cross high-altitude landscapes, lagoons, and challenging mountains that strengthen body "
        "and spirit. The Inca Trail guides you through archaeological sites, cloud forests, and "
        "unforgettable views. Always accompanied by a team that cares for every detail, you will "
        "live an intimate, authentic, and deeply revealing experience."
    ),
    "Lares & Machu Picchu 4 días": (
        "This trip is not just a route to Machu Picchu, but a profound experience that connects you "
        "with the living essence of the Andes. You will hike among sacred mountains and high Andean "
        "communities who share their table, stories, and ancestral way of living in harmony with "
        "nature with you. From the looms of Wakawasi to the farms of Patakancha, you will live "
        "an authentic cultural immersion. A safe and well-organized journey combining moderate "
        "hiking, unforgettable landscapes, and real human connection."
    ),
    "Machu Picchu - Machu Picchu 1 día": (
        "Travel from Cusco to the sacred citadel of the Incas in a full day organized in detail. "
        "Enjoy a guided tour in a shared group, with transport, train, tickets, and logistics "
        "included. Ideal for those who have little time but do not want to leave Peru without "
        "discovering Machu Picchu. An intense, efficient, and deeply memorable experience!\n\n"
        "With Wayki Trek you can visit Machu Picchu in a single day with the peace of mind of "
        "an organized, safe service, with options that fit your travel style. Whether by tourist, "
        "panoramic, or luxury train, the experience will be unforgettable."
    ),
    "Machu Picchu - Machu Picchu 2 días": (
        "This 2-day trip combines living culture, sacred landscapes, and the majesty of Machu Picchu "
        "in a private and deeply personalized tour. From Moray and the Salt Mines to the heart of the "
        "Inca citadel, you will walk to the rhythm of your story, with an exclusive guide, attention "
        "to every detail, and real time to absorb the energy of the Apus. Ideal for travelers "
        "seeking depth, quality, and connection."
    ),
    "Machu Picchu - Machu Picchu 3 días": (
        "This 3-day itinerary takes you through the heart of the Inca legacy: from the ancient temples "
        "of Cusco, past the agricultural laboratories of Moray and the living salt mines of Maras, "
        "to reaching Machu Picchu without haste. Designed as a private service, it combines a "
        "flexible pace, a specialist and human guide, comfortable transfers, selected food, "
        "accommodation with Wayki standards, and constant accompaniment. Ideal for those seeking "
        "cultural depth, natural connection, and flawless logistics. Because the path matters too, "
        "as much as the destination."
    ),
    "Paquetes - Perú 6 días": (
        "Explore the essence of the ancient Inca Empire on a 6-day journey combining living culture, "
        "legendary hikes, and transformative moments. From the streets of Cusco to Machu Picchu, "
        "connect with history, nature, and yourself. Includes guided tours, private transfers, "
        "accommodation in selected hotels, and the iconic 2-day Inca Trail. In small groups of "
        "4 to 8 people or as a private service, experience an authentic, flexible, and close journey "
        "with Wayki Trek. Every step is a memory; every look, an emotion.\n\n"
        "SWD: Single room accommodation.\n"
        "DWB: Double or twin room accommodation."
    ),
    "Perú - Perú 10 días": (
        "Experience a 10-day journey through the coast, desert, Andes, and Andean Amazon. Discover "
        "wonders like the Ballestas Islands, the enigmatic Nazca Lines, vibrant Cusco, the Sacred Valley, "
        "and local communities. This itinerary is designed for an authentic connection with Peru's "
        "history, nature, and living culture. The journey culminates with the legendary 4-day Inca Trail, "
        "in a transformative and deeply meaningful experience. Enjoy reliable services, expert guides, "
        "and top-tier logistics. Peru awaits you with a thousand emotions in a single trip."
    ),
    "Perú - Perú 12 días": (
        "Discover the most authentic Peru on a 12-day journey linking culture, adventure, and nature. "
        "From the temples of Cusco and the Sacred Valley to the shared experience with the Inca Trail "
        "porters, every moment is designed to transform. Hike 4 days along ancestral pathways towards "
        "Machu Picchu, exploring hidden ruins and soul-lifting landscapes. Then, immerse yourself "
        "in the jungle of Puerto Maldonado, among oxbow lakes, monkeys, and macaws. With premium "
        "logistics, expert guides, and small groups, this trip is not just a tour: it is a deep "
        "connection with history, life, and the essential."
    ),
    "Perú - Perú 15 días": (
        "Explore Peru on a 15-day journey of culture, nature, and deep connection. From Lima to "
        "Machu Picchu, this itinerary travels the coast, Andes, and high plains with authentic "
        "experiences: Ballestas Islands, Nazca Lines, Arequipa, Colca Canyon, Lake Titicaca, and "
        "local communities. Live the essence of Cusco, the Sacred Valley, and the Wayki Experience "
        "before hiking the 4-day Inca Trail and entering Machu Picchu through the Sun Gate. Small "
        "groups, a permanent guide, private transfers, and premium logistics guarantee a "
        "transformative and humane journey."
    ),
    "Salkantay & Inca 6 días – Para Amigos": (
        "Prepare for an unforgettable crossing between glaciers, high passes, cloud forests, and "
        "ancient structures. In six days, you and your friends will trek the powerful combination "
        "of challenging Salkantay and the legendary Inca Trail. Laughter, challenges, and "
        "companionship will mark each day, as you share hikes, discoveries, and starry skies. "
        "With premium logistics, an exclusive guide, and an itinerary designed for freedom and "
        "group connection, you will live an adventure that will strengthen your friendship and "
        "leave lifetime memories."
    ),
    "Salkantay & Inca 6 días – Para Familias": (
        "Six days to experience a great family adventure, exploring majestic glaciers, cloud forests, "
        "and ancestral trails leading to Machu Picchu. This route combines the excitement of Salkantay "
        "with the mystique of the Inca Trail, at a safe and adaptable pace for adults and children "
        "alike. With specialized guides, nutritious food, comfortable camps, and moments designed to "
        "share, learn, and enjoy, every step will strengthen your bonds. An unforgettable experience "
        "where history, nature, and family love walk together."
    ),
    "Salkantay & Inca 6 días – Para Parejas": (
        "Embark on a journey that is more than a hike—an intimate and transformative experience. "
        "For six days, you will walk among glaciers, cloud forests, and ancient ruins along sacred "
        "Inca trails to Machu Picchu. Every step strengthens your bond, merging adventure and emotion. "
        "With a flexible pace, top-tier logistics, and breathtaking landscapes, this is a rite of "
        "love and discovery. Hand in hand, you will discover the secrets of the Andes... and new "
        "dimensions of your connection."
    ),
    "Salkantay & Inca 6 días – Solo": (
        "Dare to cross snowy peaks, hidden valleys, and cloud forests heading to Machu Picchu. "
        "Six days where physical challenge transforms into an awakening of the spirit. Every step on "
        "Salkantay and the Inca Trail will be an intimate conversation with yourself, guiding you "
        "towards strength, introspection, and deep connection with the Andes. More than a destination, "
        "you will live a personal rebirth."
    ),
    "Salkantay 5 días": (
        "Embark on a sacred journey to Machu Picchu via the imposing Salkantay route. For five days "
        "you will hike among majestic glaciers, crystalline lagoons, cloud forests, and moving landscapes. "
        "But this experience goes beyond the physical challenge; you will camp at the foot of Apu "
        "Salkantay and share nights with families from the inter-Andean valleys, getting to know "
        "their traditions, hospitality, and daily life first-hand. With expert guides, premium "
        "logistics, and authentic care, you will experience a transformative, profound, and "
        "meaningful journey. Machu Picchu will be the destination, but the true gift is in the path."
    )
}


def translate_categories(client: OdooClient, dry_run: bool, lang: str):
    print("\n--- Translating Categories ---")
    categories = client.search_read("product.category", [], ["id", "name"])
    for cat in categories:
        name = cat["name"]
        if name in CATEGORIES_MAP:
            translated_name = CATEGORIES_MAP[name]
            print(f"[Category] {name} -> {translated_name}")
            if not dry_run:
                client.execute(
                    "product.category",
                    "write",
                    [cat["id"]],
                    {"name": translated_name},
                    context={"lang": lang}
                )


def translate_attributes(client: OdooClient, dry_run: bool, lang: str):
    print("\n--- Translating Attributes ---")
    attributes = client.search_read("product.attribute", [], ["id", "name"])
    for attr in attributes:
        name = attr["name"]
        if name in ATTRIBUTES_MAP:
            translated_name = ATTRIBUTES_MAP[name]
            print(f"[Attribute] {name} -> {translated_name}")
            if not dry_run:
                client.execute(
                    "product.attribute",
                    "write",
                    [attr["id"]],
                    {"name": translated_name},
                    context={"lang": lang}
                )


def translate_attribute_values(client: OdooClient, dry_run: bool, lang: str):
    print("\n--- Translating Attribute Values ---")
    values = client.search_read("product.attribute.value", [], ["id", "name"])
    for val in values:
        name = val["name"]
        if name in VALUES_MAP:
            translated_name = VALUES_MAP[name]
            print(f"[Attribute Value] {name} -> {translated_name}")
            if not dry_run:
                client.execute(
                    "product.attribute.value",
                    "write",
                    [val["id"]],
                    {"name": translated_name},
                    context={"lang": lang}
                )


def translate_product_templates(client: OdooClient, dry_run: bool, lang: str):
    print("\n--- Translating Product Templates ---")
    templates = client.search_read("product.template", [], ["id", "name", "description_sale"])
    for tmpl in templates:
        name = tmpl["name"]
        id_ = tmpl["id"]
        
        # Check if name needs translation
        new_name = PRODUCTS_MAP.get(name)
        new_desc = DESCRIPTIONS_MAP.get(name)
        
        vals = {}
        if new_name:
            vals["name"] = new_name
        if new_desc:
            vals["description_sale"] = new_desc
            
        if vals:
            action_desc = []
            if "name" in vals:
                action_desc.append(f"name: '{name}' -> '{new_name}'")
            if "description_sale" in vals:
                action_desc.append("description translated")
            print(f"[Product Template ID {id_}] " + ", ".join(action_desc))
            if not dry_run:
                client.execute(
                    "product.template",
                    "write",
                    [id_],
                    vals,
                    context={"lang": lang}
                )


def main():
    parser = argparse.ArgumentParser(description="Translate Odoo catalog to English.")
    parser.add_argument("--dry-run", action="store_true", help="Print updates without writing them.")
    parser.add_argument("--lang", default="es_419", help="Odoo language context to write to (default: es_419).")
    args = parser.parse_args()

    print("Connecting to Odoo...")
    client = OdooClient()
    client.connect()
    print("Successfully connected.")

    if args.dry_run:
        print("!!! DRY RUN MODE - No database changes will be written !!!")

    # The user wants "pasar todo a ingles" (global overwrite mode).
    # We will write directly to args.lang (default es_419) AND also write to en_US.
    # Writing to both ensures that English translation is saved in Odoo translations table, 
    # and default/base language is also English!
    
    languages_to_update = [args.lang]
    if args.lang != "en_US":
        languages_to_update.append("en_US")

    for target_lang in languages_to_update:
        print(f"\n=============================================")
        print(f"Applying translations for context: {target_lang}")
        print(f"=============================================")
        
        translate_categories(client, args.dry_run, target_lang)
        translate_attributes(client, args.dry_run, target_lang)
        translate_attribute_values(client, args.dry_run, target_lang)
        translate_product_templates(client, args.dry_run, target_lang)

    print("\n🎉 Translation task completed.")


if __name__ == "__main__":
    main()
