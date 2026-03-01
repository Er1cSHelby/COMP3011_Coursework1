from rest_framework import serializers
from .models import ExpansionSet, Card, CollectionItem


class ExpansionSetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ExpansionSet
        fields = ['url', 'id', 'name', 'release_date', 'total_cards']
        extra_kwargs = {
            'url': {'view_name': 'expansionset-detail', 'lookup_field': 'pk'}
        }


class CardSerializer(serializers.HyperlinkedModelSerializer):
    set_name = serializers.CharField(source='set.name', read_only=True)
    set_url = serializers.HyperlinkedRelatedField(
        source='set', view_name='expansionset-detail', read_only=True
    )

    class Meta:
        model = Card
        fields = ['url', 'id', 'name', 'rarity', 'image_url', 'average_price', 'set', 'set_name', 'set_url']
        extra_kwargs = {
            'url': {'view_name': 'card-detail', 'lookup_field': 'pk'},
            'set': {'view_name': 'expansionset-detail', 'lookup_field': 'pk'}
        }


class CardListSerializer(serializers.ModelSerializer):
    set_name = serializers.CharField(source='set.name', read_only=True)

    class Meta:
        model = Card
        fields = ['id', 'name', 'rarity', 'set_name', 'average_price']


class CollectionItemSerializer(serializers.HyperlinkedModelSerializer):
    card_name = serializers.CharField(source='card.name', read_only=True)
    card_image = serializers.CharField(source='card.image_url', read_only=True)
    card_price = serializers.DecimalField(source='card.average_price', max_digits=10, decimal_places=2, read_only=True)
    total_value = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()

    class Meta:
        model = CollectionItem
        fields = ['url', 'id', 'card', 'card_name', 'card_image', 'card_price', 
                  'condition', 'quantity', 'acquired_date', 'grade',
                  'purchase_price', 'market_price', 'total_value', 'profit']
        extra_kwargs = {
            'url': {'view_name': 'collectionitem-detail', 'lookup_field': 'pk'},
            'card': {'view_name': 'card-detail', 'lookup_field': 'pk'}
        }

    def get_total_value(self, obj):
        return float(obj.market_price or obj.card.average_price) * obj.quantity

    def get_profit(self, obj):
        if obj.purchase_price:
            return float(obj.market_price or obj.card.average_price) * obj.quantity - float(obj.purchase_price) * obj.quantity
        return 0


class CollectionItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionItem
        fields = ['id', 'card', 'condition', 'quantity', 'grade', 'purchase_price', 'market_price']
