from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(blank=True, null=True, verbose_name="numéro de téléphone", region=None)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


TYPE_COMMERCE_CHOICES = [
    ('boutique', 'Boutique générale'),
    ('alimentation', 'Alimentation / Épicerie'),
    ('pharmacie', 'Pharmacie / Parapharmacie'),
    ('quincaillerie', 'Quincaillerie / BTP'),
    ('electronique', 'Électronique / Téléphonie'),
    ('cosmetique', 'Cosmétique / Beauté'),
    ('restaurant', 'Restaurant / Snack'),
    ('textile', 'Textile / Vêtements'),
    ('autre', 'Autre'),
]

DEVISE_CHOICES = [
    ('FCFA', 'FCFA (Franc CFA)'),
    ('USD', 'Dollar US'),
    ('EUR', 'Euro'),
    ('CDF', 'Franc Congolais'),
    ('XOF', 'Franc CFA Ouest'),
]


class Commerce(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='commerce')
    name = models.CharField(max_length=255, verbose_name="Nom du commerce")
    type_commerce = models.CharField(
        max_length=50, choices=TYPE_COMMERCE_CHOICES,
        default='boutique', verbose_name="Type d'activité"
    )
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adresse")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    devise = models.CharField(
        max_length=10, choices=DEVISE_CHOICES,
        default='FCFA', verbose_name="Devise"
    )
    # Logo optionnel pour le ticket de caisse
    logo = models.ImageField(
        upload_to='logos/', blank=True, null=True, verbose_name="Logo"
    )
    slogan = models.CharField(max_length=255, blank=True, verbose_name="Slogan / Message ticket")
    tva_taux = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="Taux TVA (%)", help_text="0 si vous ne facturez pas la TVA"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name