import requests
import json
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pokevault.settings')
django.setup()

from api.models import ExpansionSet, Card


def fetch_pokemon_cards():
    base_url = "https://api.pokemontcg.io/v2/cards"
    headers = {"X-Api-Key": "YOUR_API_KEY_HERE"}
    
    sets_to_fetch = ["sv3", "sv2", "sv1", "swsh7", "swsh6", "swsh5"]
    
    for set_code in sets_to_fetch:
        print(f"Fetching cards from set: {set_code}")
        
        response = requests.get(
            f"{base_url}?q=set.id:{set_code}&pageSize=100",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            cards_data = data.get('data', [])
            
            set_obj, _ = ExpansionSet.objects.get_or_create(
                name=cards_data[0]['set']['name'] if cards_data else set_code,
                defaults={'total_cards': len(cards_data)}
            )
            
            for card_data in cards_data:
                rarity = card_data.get('rarity', 'Common')
                if rarity not in dict(Card.RARITY_CHOICES):
                    rarity = 'Rare'
                
                Card.objects.get_or_create(
                    name=card_data['name'],
                    set=set_obj,
                    defaults={
                        'rarity': rarity,
                        'image_url': card_data.get('images', {}).get('small', ''),
                        'average_price': float(card_data.get('cardmarket', {}).get('prices', {}).get('averageSellPrice', 0) or 0)
                    }
                )
            
            print(f"Imported {len(cards_data)} cards from {set_code}")
        else:
            print(f"Failed to fetch {set_code}: {response.status_code}")


def create_sample_data():
    if ExpansionSet.objects.exists():
        print("Data already exists. Skipping...")
        return
    
    sets_data = [
        {"name": "Scarlet & Violet", "total_cards": 250},
        {"name": "Sword & Shield", "total_cards": 200},
        {"name": "Sun & Moon", "total_cards": 300},
    ]
    
    for set_data in sets_data:
        expansion_set = ExpansionSet.objects.create(**set_data)
        
        cards_data = [
            {"name": "Pikachu", "rarity": "Rare", "average_price": 15.00},
            {"name": "Charizard", "rarity": "Rare Ultra", "average_price": 150.00},
            {"name": "Bulbasaur", "rarity": "Common", "average_price": 2.00},
            {"name": "Squirtle", "rarity": "Common", "average_price": 2.00},
            {"name": "Charmander", "rarity": "Common", "average_price": 2.50},
            {"name": "Eevee", "rarity": "Rare", "average_price": 12.00},
            {"name": "Gengar", "rarity": "Rare Holocarbon", "average_price": 80.00},
            {"name": "Mewtwo", "rarity": "Rare Ultra", "average_price": 200.00},
            {"name": "Rayquaza", "rarity": "Rare Secret", "average_price": 300.00},
            {"name": "Lucario", "rarity": "Rare", "average_price": 25.00},
        ]
        
        for card_data in cards_data:
            Card.objects.create(
                name=card_data["name"],
                rarity=card_data["rarity"],
                average_price=card_data["average_price"],
                set=expansion_set,
                image_url=f"https://example.com/images/{card_data['name'].lower()}.png"
            )
    
    print("Sample data created successfully!")


if __name__ == "__main__":
    create_sample_data()
