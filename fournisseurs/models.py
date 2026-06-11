"""
App fournisseurs — Fournisseurs et commandes d'approvisionnement.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from uuid import uuid4


class Fournisseur(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fournisseurs'
    )
    nom = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    @property
    def nb_commandes(self):
        return self.commandes.count()

    @property
    def total_commandes(self):
        from django.db.models import Sum
        from django.db.models.functions import Coalesce
        from decimal import Decimal
        return self.commandes.aggregate(
            total=Coalesce(Sum('montant_total'), Decimal('0'))
        )['total']

    class Meta:
        verbose_name = "Fournisseur"
        ordering = ['nom']


class CommandeFournisseur(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('recue', 'Reçue'),
        ('partielle', 'Partiellement reçue'),
        ('annulee', 'Annulée'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='commandes_fournisseur'
    )
    fournisseur = models.ForeignKey(
        Fournisseur,
        on_delete=models.CASCADE,
        related_name='commandes'
    )
    numero = models.CharField(max_length=20, unique=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    montant_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    note = models.TextField(blank=True)
    date_commande = models.DateField(default=timezone.now)
    date_livraison_prevue = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.numero:
            today = timezone.now()
            count = CommandeFournisseur.objects.filter(
                user=self.user,
                created_at__date=today.date()
            ).count() + 1
            self.numero = f"CF{today.strftime('%Y%m%d')}-{count:04d}-{uuid4().hex[:4].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commande {self.numero} — {self.fournisseur.nom}"

    class Meta:
        verbose_name = "Commande fournisseur"
        ordering = ['-created_at']


class LigneCommande(models.Model):
    commande = models.ForeignKey(
        CommandeFournisseur,
        on_delete=models.CASCADE,
        related_name='lignes'
    )
    produit = models.ForeignKey(
        'stock.Produit',
        on_delete=models.PROTECT
    )
    quantite_commandee = models.IntegerField()
    quantite_recue = models.IntegerField(default=0)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    sous_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.sous_total = self.quantite_commandee * self.prix_unitaire
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produit.nom} x{self.quantite_commandee}"

    class Meta:
        verbose_name = "Ligne de commande"
