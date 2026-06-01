from django.urls import path
from . import views

urlpatterns = [
    path('clients/', views.liste_clients, name='liste_clients'),
    path('clients/ajouter/', views.ajouter_client, name='ajouter_client'),
    path('clients/<int:pk>/', views.detail_client, name='detail_client'),
    path('clients/<int:pk>/supprimer/', views.supprimer_client, name='supprimer_client'),
    path('api/clients/', views.api_clients, name='api_clients'),
    path('dettes/', views.liste_dettes, name='liste_dettes'),
    path('dettes/creer/', views.creer_dette_manuelle, name='creer_dette'),
    path('dettes/<int:pk>/payer/', views.enregistrer_paiement, name='enregistrer_paiement'),
]
