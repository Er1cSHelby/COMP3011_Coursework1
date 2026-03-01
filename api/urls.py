from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sets', views.ExpansionSetViewSet)
router.register(r'cards', views.CardViewSet)
router.register(r'collection', views.CollectionItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/value/', views.collection_value),
    path('health/', views.health_check),
]
