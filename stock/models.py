from django.db import models
from django.conf import settings
from django.utils import timezone
from uuid import uuid4


class Categorie(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    couleur = models.CharField(max_length=7, default='#2563eb')  # hex color
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Catégorie"
        ordering = ['nom']


class Produit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='produits')
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='produits')
    
    nom = models.CharField(max_length=255)
    reference = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    
    prix_achat = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    prix_vente = models.DecimalField(max_digits=12, decimal_places=2)
    
    stock_actuel = models.IntegerField(default=0)
    stock_minimum = models.IntegerField(default=5, help_text="Seuil d'alerte stock bas")
    unite = models.CharField(max_length=20, default='pièce')
    
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom} ({self.reference})" if self.reference else self.nom

    @property
    def marge(self):
        if self.prix_achat > 0:
            return round(((self.prix_vente - self.prix_achat) / self.prix_achat) * 100, 1)
        return 0

    @property
    def valeur_stock(self):
        return self.stock_actuel * self.prix_achat

    @property
    def en_alerte(self):
        return self.stock_actuel <= self.stock_minimum

    class Meta:
        verbose_name = "Produit"
        ordering = ['nom']


class MouvementStock(models.Model):
    TYPES = [
        ('entree', 'Entrée de stock'),
        ('sortie', 'Sortie de stock'),
        ('ajustement', 'Ajustement'),
        ('vente', 'Vente'),
        ('retour', 'Retour client'),
    ]

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='mouvements')
    type_mouvement = models.CharField(max_length=20, choices=TYPES)
    quantite = models.IntegerField()
    stock_avant = models.IntegerField()
    stock_apres = models.IntegerField()
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_mouvement_display()} - {self.produit.nom} ({self.quantite})"

    class Meta:
        verbose_name = "Mouvement de stock"
        ordering = ['-created_at']


class Vente(models.Model):
    MODES_PAIEMENT = [
        ('especes', 'Espèces'),
        ('mobile_money', 'Mobile Money'),
        ('carte', 'Carte bancaire'),
        ('credit', 'À crédit'),
    ]

    STATUTS = [
        ('completee', 'Complétée'),
        ('annulee', 'Annulée'),
        ('credit', 'À crédit'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ventes')
    numero = models.CharField(max_length=20, unique=True)
    # FK optionnelle vers Client — rétrocompatible (null=True)
    client = models.ForeignKey(
        'Client', on_delete=models.SET_NULL, null=True, blank=True, related_name='ventes_liees'
    )
    client_nom = models.CharField(max_length=255, blank=True, default='Client comptant')
    client_telephone = models.CharField(max_length=20, blank=True)
    
    mode_paiement = models.CharField(max_length=20, choices=MODES_PAIEMENT, default='especes')
    statut = models.CharField(max_length=20, choices=STATUTS, default='completee')
    
    total_ht = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # pourcentage
    total_ttc = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    montant_recu = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    monnaie_rendue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.numero:
            today = timezone.now()
            count = Vente.objects.filter(
                user=self.user,
                created_at__date=today.date()
            ).count() + 1
            self.numero = f"V{today.strftime('%Y%m%d')}-{count:04d}-{uuid4().hex[:4].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Vente {self.numero} - {self.total_ttc} FCFA"

    class Meta:
        verbose_name = "Vente"
        ordering = ['-created_at']


class LigneVente(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    sous_total = models.DecimalField(max_digits=14, decimal_places=2)

    def save(self, *args, **kwargs):
        self.sous_total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produit.nom} x{self.quantite}"

    class Meta:
        verbose_name = "Ligne de vente"


# ── CLIENT ────────────────────────────────────────────────────────────────────

class Client(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='clients')
    nom = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    @property
    def solde_dette(self):
        from django.db.models import Sum
        from django.db.models.functions import Coalesce
        from decimal import Decimal
        total = self.dettes.filter(remboursee=False).aggregate(
            s=Coalesce(Sum('montant_restant'), Decimal('0'))
        )['s']
        return total
    @property
    def nb_achats(self):
        return self.ventes_liees.filter(statut='completee').count()

    class Meta:
        verbose_name = "Client"
        ordering = ['nom']


# ── DETTE ─────────────────────────────────────────────────────────────────────

class Dette(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='dettes')
    vente = models.OneToOneField(Vente, on_delete=models.CASCADE, related_name='dette', null=True, blank=True)
    montant_initial = models.DecimalField(max_digits=14, decimal_places=2)
    montant_restant = models.DecimalField(max_digits=14, decimal_places=2)
    remboursee = models.BooleanField(default=False)
    echeance = models.DateField(null=True, blank=True, help_text="Date limite de remboursement")
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dette {self.client.nom} — {self.montant_restant} FCFA"

    @property
    def montant_paye(self):
        return self.montant_initial - self.montant_restant

    @property
    def est_en_retard(self):
        if self.echeance and not self.remboursee:
            return timezone.now().date() > self.echeance
        return False

    class Meta:
        verbose_name = "Dette"
        ordering = ['-created_at']


class PaiementDette(models.Model):
    dette = models.ForeignKey(Dette, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=14, decimal_places=2)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement {self.montant} FCFA → {self.dette.client.nom}"

    class Meta:
        verbose_name = "Paiement de dette"
        ordering = ['-created_at']
