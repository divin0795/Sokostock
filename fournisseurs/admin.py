from django.contrib import admin
from .models import Fournisseur, CommandeFournisseur, LigneCommande

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'telephone', 'actif']
    list_filter = ['actif']

@admin.register(CommandeFournisseur)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['numero', 'fournisseur', 'statut', 'montant_total', 'date_commande']
    list_filter = ['statut']
