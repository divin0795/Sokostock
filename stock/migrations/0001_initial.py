from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('couleur', models.CharField(default='#2563eb', max_length=7)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Catégorie', 'ordering': ['nom']},
        ),
        migrations.CreateModel(
            name='Produit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255)),
                ('reference', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('prix_achat', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('prix_vente', models.DecimalField(decimal_places=2, max_digits=12)),
                ('stock_actuel', models.IntegerField(default=0)),
                ('stock_minimum', models.IntegerField(default=5)),
                ('unite', models.CharField(default='pièce', max_length=20)),
                ('actif', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('categorie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='produits', to='stock.categorie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='produits', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Produit', 'ordering': ['nom']},
        ),
        migrations.CreateModel(
            name='MouvementStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_mouvement', models.CharField(choices=[('entree', 'Entrée de stock'), ('sortie', 'Sortie de stock'), ('ajustement', 'Ajustement'), ('vente', 'Vente'), ('retour', 'Retour client')], max_length=20)),
                ('quantite', models.IntegerField()),
                ('stock_avant', models.IntegerField()),
                ('stock_apres', models.IntegerField()),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mouvements', to='stock.produit')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Mouvement de stock', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Vente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=20, unique=True)),
                ('client_nom', models.CharField(blank=True, default='Client comptant', max_length=255)),
                ('client_telephone', models.CharField(blank=True, max_length=20)),
                ('mode_paiement', models.CharField(choices=[('especes', 'Espèces'), ('mobile_money', 'Mobile Money'), ('carte', 'Carte bancaire'), ('credit', 'À crédit')], default='especes', max_length=20)),
                ('statut', models.CharField(choices=[('completee', 'Complétée'), ('annulee', 'Annulée'), ('credit', 'À crédit')], default='completee', max_length=20)),
                ('total_ht', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('remise', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('total_ttc', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('montant_recu', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('monnaie_rendue', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ventes', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Vente', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='LigneVente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantite', models.IntegerField()),
                ('prix_unitaire', models.DecimalField(decimal_places=2, max_digits=12)),
                ('sous_total', models.DecimalField(decimal_places=2, max_digits=14)),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stock.produit')),
                ('vente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes', to='stock.vente')),
            ],
            options={'verbose_name': 'Ligne de vente'},
        ),
    ]
