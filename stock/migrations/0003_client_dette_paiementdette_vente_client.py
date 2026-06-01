from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0002_alter_produit_stock_minimum'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Modèle Client
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255)),
                ('telephone', models.CharField(blank=True, max_length=20)),
                ('adresse', models.CharField(blank=True, max_length=255)),
                ('note', models.TextField(blank=True)),
                ('actif', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='clients', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Client', 'ordering': ['nom']},
        ),
        # 2. FK client sur Vente (nullable, rétrocompat)
        migrations.AddField(
            model_name='vente',
            name='client',
            field=models.ForeignKey(blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='ventes_liees', to='stock.client'),
        ),
        # 3. Modèle Dette
        migrations.CreateModel(
            name='Dette',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant_initial', models.DecimalField(decimal_places=2, max_digits=14)),
                ('montant_restant', models.DecimalField(decimal_places=2, max_digits=14)),
                ('remboursee', models.BooleanField(default=False)),
                ('echeance', models.DateField(blank=True, null=True)),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='dettes', to='stock.client')),
                ('vente', models.OneToOneField(blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='dette', to='stock.vente')),
            ],
            options={'verbose_name': 'Dette', 'ordering': ['-created_at']},
        ),
        # 4. Modèle PaiementDette
        migrations.CreateModel(
            name='PaiementDette',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant', models.DecimalField(decimal_places=2, max_digits=14)),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL)),
                ('dette', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='paiements', to='stock.dette')),
            ],
            options={'verbose_name': 'Paiement de dette', 'ordering': ['-created_at']},
        ),
    ]
