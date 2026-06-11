from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stock', '0003_client_dette_paiementdette_vente_client'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Fournisseur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255)),
                ('telephone', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('adresse', models.CharField(blank=True, max_length=255)),
                ('note', models.TextField(blank=True)),
                ('actif', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fournisseurs', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Fournisseur', 'ordering': ['nom']},
        ),
        migrations.CreateModel(
            name='CommandeFournisseur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(blank=True, max_length=20, unique=True)),
                ('statut', models.CharField(choices=[('en_attente', 'En attente'), ('recue', 'Reçue'), ('partielle', 'Partiellement reçue'), ('annulee', 'Annulée')], default='en_attente', max_length=20)),
                ('montant_total', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('note', models.TextField(blank=True)),
                ('date_commande', models.DateField(default=django.utils.timezone.now)),
                ('date_livraison_prevue', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('fournisseur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commandes', to='fournisseurs.fournisseur')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commandes_fournisseur', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Commande fournisseur', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='LigneCommande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantite_commandee', models.IntegerField()),
                ('quantite_recue', models.IntegerField(default=0)),
                ('prix_unitaire', models.DecimalField(decimal_places=2, max_digits=12)),
                ('sous_total', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('commande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes', to='fournisseurs.commandefournisseur')),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stock.produit')),
            ],
            options={'verbose_name': 'Ligne de commande'},
        ),
    ]
