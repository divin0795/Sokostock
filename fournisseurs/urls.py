from django.urls import path
from . import views

urlpatterns = [
    path('fournisseurs/', views.liste_fournisseurs, name='liste_fournisseurs'),
    path('fournisseurs/ajouter/', views.ajouter_fournisseur, name='ajouter_fournisseur'),
    path('fournisseurs/<int:pk>/', views.detail_fournisseur, name='detail_fournisseur'),
    path('fournisseurs/<int:pk>/modifier/', views.modifier_fournisseur, name='modifier_fournisseur'),
    path('fournisseurs/<int:pk>/supprimer/', views.supprimer_fournisseur, name='supprimer_fournisseur'),
    path('commandes/', views.liste_commandes, name='liste_commandes'),
    path('commandes/creer/', views.creer_commande, name='creer_commande'),
    path('commandes/<int:pk>/', views.detail_commande, name='detail_commande'),
    path('commandes/<int:pk>/recevoir/', views.recevoir_commande, name='recevoir_commande'),
]
