from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, F
from .models import ExpansionSet, Card, CollectionItem
from .serializers import (
    ExpansionSetSerializer,
    CardSerializer,
    CardListSerializer,
    CollectionItemSerializer,
    CollectionItemCreateSerializer,
)


class ExpansionSetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExpansionSet.objects.all()
    serializer_class = ExpansionSetSerializer


class CardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return CardListSerializer
        return CardSerializer

    def get_queryset(self):
        queryset = Card.objects.all()
        name = self.request.query_params.get('name')
        rarity = self.request.query_params.get('rarity')
        set_id = self.request.query_params.get('set')

        if name:
            queryset = queryset.filter(name__icontains=name)
        if rarity:
            queryset = queryset.filter(rarity=rarity)
        if set_id:
            queryset = queryset.filter(set_id=set_id)

        return queryset


class CollectionItemViewSet(viewsets.ModelViewSet):
    queryset = CollectionItem.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CollectionItemCreateSerializer
        return CollectionItemSerializer


@api_view(['GET'])
def collection_value(request):
    items = CollectionItem.objects.annotate(
        item_value=(F('market_price') or F('card__average_price')) * F('quantity'),
        cost=F('purchase_price') * F('quantity')
    )
    total_value = sum(float(i.item_value or 0) for i in items)
    total_cost = sum(float(i.cost or 0) for i in items)
    profit = total_value - total_cost
    
    return Response({
        'total_value': total_value,
        'total_cost': total_cost,
        'profit': profit
    })


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'PokeVault API'})
