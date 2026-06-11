from django.urls import path
from . import views

urlpatterns = [
    # Produits
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produits/ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('produits/<int:pk>/modifier/', views.modifier_produit, name='modifier_produit'),
    path('produits/<int:pk>/supprimer/', views.supprimer_produit, name='supprimer_produit'),
    path('produits/<int:pk>/stock/', views.ajuster_stock, name='ajuster_stock'),

    # Catégories
    path('categories/', views.categories, name='categories'),

    # Mouvements stock
    path('mouvements/', views.mouvements_stock, name='mouvements_stock'),

    # Profil commerce
    path('profil/', views.profil_commerce, name='profil_commerce'),
]
