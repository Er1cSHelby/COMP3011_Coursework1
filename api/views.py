from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ExpansionSet, Card, CollectionItem
from .serializers import ExpansionSetSerializer, CardSerializer, CollectionItemSerializer

#listing and retrieving expansion sets.
#Users only read, not be allow to modify
class ExpansionSetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExpansionSet.objects.all()
    serializer_class = ExpansionSetSerializer

#Viewset for cards,
class CardViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Card.objects.all()
    serializer_class = CardSerializer

    def get_queryset(self):
        #QuerySet filtering by name or rarity
        queryset = Card.objects.all()
        name = self.request.query_params.get('name')
        rarity = self.request.query_params.get('rarity')

        #Perform a case-insensitive partial match
        if name:
            queryset = queryset.filter(name__icontains=name)
            
        #Perform an exact match
        if rarity:
            queryset = queryset.filter(rarity=rarity)

        return queryset
    
#managing personal collection items
class CollectionItemViewSet(viewsets.ModelViewSet):
    #support CURD   
    queryset = CollectionItem.objects.all()
    serializer_class = CollectionItemSerializer

@api_view(['GET'])
def collection_value(request):
    """
    Calculate total value and profit
    """
    items = CollectionItem.objects.all()
    total_value = 0.0
    total_cost = 0.0

    for item in items:
        quantity = item.quantity
        
        # Calculate total cost 
        cost_per_item = item.purchase_price if item.purchase_price else 0
        total_cost += cost_per_item * quantity
        
        # Calculate market value by accessing the related Card model's average_price via the foreign key
        if item.card and item.card.average_price:
            total_value += item.card.average_price * quantity

    profit = total_value - total_cost
    
    return Response({
        'total_value': round(total_value, 2),
        'total_cost': round(total_cost, 2),
        'profit': round(profit, 2)
    })

@api_view(['GET'])
def health_check(request):
    """
    Basic health check endpoint to verify API status.
    """
    return Response({'status': 'healthy', 'service': 'PokeVault API'})