from django.urls import path
from . import views

urlpatterns = [
    path('pos/', views.pos, name='pos'),
    path('pos/vente/', views.creer_vente, name='creer_vente'),
    path('ventes/<int:pk>/', views.detail_vente, name='detail_vente'),
    path('api/produits/', views.api_produits, name='api_produits'),
]
