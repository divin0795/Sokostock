"""
Modèles Client, Dette et PaiementDette — extraits de stock/models.py
et re-exportés depuis ce module pour centraliser la gestion clients.
"""
# On importe depuis stock pour éviter de dupliquer les modèles.
# Cela permet de garder une seule source de vérité (stock.models)
# tout en rendant les imports dans l'app clients plus expressifs.
from stock.models import Client, Dette, PaiementDette

__all__ = ['Client', 'Dette', 'PaiementDette']
