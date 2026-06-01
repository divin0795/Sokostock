from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_user_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='commerce',
            name='type_commerce',
            field=models.CharField(
                choices=[
                    ('boutique', 'Boutique générale'),
                    ('alimentation', 'Alimentation / Épicerie'),
                    ('pharmacie', 'Pharmacie / Parapharmacie'),
                    ('quincaillerie', 'Quincaillerie / BTP'),
                    ('electronique', 'Électronique / Téléphonie'),
                    ('cosmetique', 'Cosmétique / Beauté'),
                    ('restaurant', 'Restaurant / Snack'),
                    ('textile', 'Textile / Vêtements'),
                    ('autre', 'Autre'),
                ],
                default='boutique', max_length=50, verbose_name="Type d'activité"
            ),
        ),
        migrations.AddField(
            model_name='commerce',
            name='devise',
            field=models.CharField(
                choices=[
                    ('FCFA', 'FCFA (Franc CFA)'),
                    ('USD', 'Dollar US'),
                    ('EUR', 'Euro'),
                    ('CDF', 'Franc Congolais'),
                    ('XOF', 'Franc CFA Ouest'),
                ],
                default='FCFA', max_length=10, verbose_name='Devise'
            ),
        ),
        migrations.AddField(
            model_name='commerce',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='logos/', verbose_name='Logo'),
        ),
        migrations.AddField(
            model_name='commerce',
            name='slogan',
            field=models.CharField(blank=True, max_length=255, verbose_name='Slogan / Message ticket'),
        ),
        migrations.AddField(
            model_name='commerce',
            name='tva_taux',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Taux TVA (%)'),
        ),
        migrations.AddField(
            model_name='commerce',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='commerce',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
