from rest_framework import serializers
from .models import Card, ExpansionSet, CollectionItem

class ExpansionSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpansionSet
        fields = ['id', 'name', 'release_date', 'total_cards']

class CardSerializer(serializers.ModelSerializer):
    # Read-only nested relationship to display full set details instead of just the ID
    set = ExpansionSetSerializer(read_only=True)

    class Meta:
        model = Card
        fields = ['id', 'name', 'rarity', 'set', 'average_price', 'image_url']

class CollectionItemSerializer(serializers.ModelSerializer):
    # Display detailed card information when retrieving data
    card_detail = CardSerializer(source='card', read_only=True)
    
    class Meta:
        model = CollectionItem
        fields = ['id', 'card', 'card_detail', 'quantity', 'purchase_price', 'date_added']
        # Make date_added read-only so it cannot be modified via the API
        read_only_fields = ['date_added']