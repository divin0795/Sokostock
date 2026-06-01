from django.contrib import admin
from .models import Categorie, Produit, MouvementStock, Vente, LigneVente


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'user', 'created_at']
    list_filter = ['user']


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'reference', 'categorie', 'prix_vente', 'stock_actuel', 'user', 'actif']
    list_filter = ['actif', 'categorie', 'user']
    search_fields = ['nom', 'reference']


@admin.register(MouvementStock)
class MouvementAdmin(admin.ModelAdmin):
    list_display = ['produit', 'type_mouvement', 'quantite', 'stock_avant', 'stock_apres', 'created_at']
    list_filter = ['type_mouvement']


class LigneVenteInline(admin.TabularInline):
    model = LigneVente
    extra = 0
    readonly_fields = ['sous_total']


@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ['numero', 'client_nom', 'total_ttc', 'mode_paiement', 'statut', 'created_at']
    list_filter = ['statut', 'mode_paiement', 'user']
    inlines = [LigneVenteInline]
