import os
import django
import requests


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pokevault.settings')
django.setup()

from api.models import Card, ExpansionSet


FALLBACK_DATA = [
    {
        "name": "Charizard", "rarity": "Rare Holocarbon",
        "set": {"name": "Base Set", "releaseDate": "1999-01-09", "total": 102},
        "pricing": {"tcgplayer": {"holo": {"midPrice": 350.00}}},
        "images": {"small": "https://images.pokemontcg.io/base1/4.png"}
    },
    {
        "name": "Pikachu", "rarity": "Common",
        "set": {"name": "Base Set", "releaseDate": "1999-01-09", "total": 102},
        "pricing": {"tcgplayer": {"normal": {"midPrice": 5.00}}},
        "images": {"small": "https://images.pokemontcg.io/base1/58.png"}
    },
    {
        "name": "Umbreon VMAX", "rarity": "Rare Secret",
        "set": {"name": "Evolving Skies", "releaseDate": "2021-08-27", "total": 237},
        "pricing": {"tcgplayer": {"holo": {"midPrice": 450.00}}},
        "images": {"small": "https://images.pokemontcg.io/swsh7/215.png"}
    }
]

def clean_rarity(api_rarity):
    if not api_rarity:
        return 'Common'
    if 'Secret' in api_rarity:
        return 'Rare Secret'
    if 'Ultra' in api_rarity or 'VMAX' in api_rarity or 'GX' in api_rarity:
        return 'Rare Ultra'
    if 'Holo' in api_rarity:
        return 'Rare Holocarbon'
    if 'Rare' in api_rarity:
        return 'Rare'
    if 'Uncommon' in api_rarity:
        return 'Uncommon'
    return 'Common'

def fetch_pokemon_cards():
    print(" Starting to fetch Pokémon data from TCGdex...")
    
    url = 'https://api.tcgdex.net/v2/en/cards'
    headers = {'User-Agent': 'Mozilla/5.0'}

    summary_list = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() 
        data = response.json()
        
        # TCGdex returns the first 50 summaries.
        summary_list = data[:50] 
        print(f"Successfully connected to TCGdex API. Retrieved {len(summary_list)} card summaries.")
    except Exception as e:
        print(f"API Connection Failed: {e}")
        print("Switching to the built-in Fallback Dataset... ")

        summary_list = FALLBACK_DATA

    print("\nWriting to database...")

    for summary in summary_list:
        try:
            card_data = summary 
            card_id = summary.get('id')
            

            if card_id:
                detail_url = f'https://api.tcgdex.net/v2/en/cards/{card_id}'
                detail_response = requests.get(detail_url, headers=headers, timeout=5)
                detail_response.raise_for_status()
                card_data = detail_response.json() # This contains pricing, rarity, etc.

            #Process Expansion Set 
            set_data = card_data.get('set', {})
            set_name = set_data.get('name', 'Unknown Set') if isinstance(set_data, dict) else 'Unknown Set'
            release_date = set_data.get('releaseDate', '2000-01-01').replace('/', '-') if isinstance(set_data, dict) else '2000-01-01'
            
            if isinstance(set_data, dict) and 'cardCount' in set_data:
                total_cards = set_data.get('cardCount', {}).get('total', 0)
            else:
                total_cards = set_data.get('total', 0) if isinstance(set_data, dict) else 0

            expansion_set, created = ExpansionSet.objects.get_or_create(
                name=set_name,
                defaults={
                    'release_date': release_date,
                    'total_cards': total_cards
                }
            )

            #Process Prices
            market_price = 0.0
            pricing = card_data.get('pricing', {})
            
            tcgplayer = pricing.get('tcgplayer')
            
            # Ensure tcgplayer is a valid dictionary before checking for 'holo'
            if tcgplayer:
                if 'holo' in tcgplayer:
                    market_price = tcgplayer['holo'].get('midPrice', 0.0)
                elif 'reverse' in tcgplayer:
                    market_price = tcgplayer['reverse'].get('midPrice', 0.0)
                elif 'normal' in tcgplayer:
                    market_price = tcgplayer['normal'].get('midPrice', 0.0)
            
            #Clean Rarity
            valid_rarity = clean_rarity(card_data.get('rarity'))

            #Process Image 
            image_base = card_data.get('image')
            if image_base and 'assets.tcgdex.net' in image_base:
                image_url = f"{image_base}/high.webp"
            else:
                image_url = card_data.get('images', {}).get('small', '')

            #Write to Database 
            Card.objects.get_or_create(
                name=card_data.get('name', 'Unknown Name'),
                set=expansion_set,
                defaults={
                    'rarity': valid_rarity,
                    'image_url': image_url,
                    'average_price': market_price,
                }
            )
            print(f"  [+] Imported: {card_data.get('name')} | Rarity: {valid_rarity} | Price: ${market_price}")

        except Exception as e:
            print(f"  [!] Skipped a card ({summary.get('name', 'Unknown')}): {e}")

    print("\n All done! Database updated successfully.")

if __name__ == '__main__':
    fetch_pokemon_cards()