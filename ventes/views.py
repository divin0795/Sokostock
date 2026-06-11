"""
App ventes — POS, création de vente, détail vente.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
import json
from decimal import Decimal, InvalidOperation

from stock.models import Produit, Categorie, Vente, LigneVente, MouvementStock
from clients.models import Client, Dette


@login_required
def pos(request):
    produits = (
        Produit.objects
        .filter(user=request.user, actif=True, stock_actuel__gt=0)
        .select_related('categorie')
        .order_by('nom')
    )
    categories = Categorie.objects.filter(user=request.user)
    commerce = getattr(request.user, 'commerce', None)
    user = request.user

    return render(request, 'stock/pos.html', {
        'produits': produits,
        'categories': categories,
        'commerce_nom': getattr(commerce, 'name', 'Commerce'),
        'commerce_tel': getattr(commerce, 'phone', ''),
        'commerce_adresse': getattr(commerce, 'address', ''),
        'vendeur_nom': f"{user.first_name} {user.last_name}".strip() or user.username,
        'vendeur_tel': str(getattr(user, 'phone_number', '')),
        'vendeur_username': user.username,
    })


@login_required
@require_POST
def creer_vente(request):
    """
    Crée une vente depuis le POS (JSON).
    Transaction atomique, stock vérifié AVANT sauvegarde, Decimal partout.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Données JSON invalides'})

    lignes = data.get('lignes', [])
    if not lignes:
        return JsonResponse({'success': False, 'error': 'Panier vide'})

    try:
        with transaction.atomic():
            total_ht = Decimal('0')
            lignes_validees = []

            for ld in lignes:
                try:
                    produit = Produit.objects.select_for_update().get(
                        pk=int(ld['produit_id']),
                        user=request.user,
                        actif=True
                    )
                except (Produit.DoesNotExist, KeyError, ValueError):
                    return JsonResponse({
                        'success': False,
                        'error': f"Produit introuvable (id={ld.get('produit_id', '?')})"
                    })

                try:
                    qty = int(ld['quantite'])
                except (KeyError, ValueError):
                    return JsonResponse({
                        'success': False,
                        'error': f"Quantité invalide pour {produit.nom}"
                    })

                if qty <= 0:
                    return JsonResponse({
                        'success': False,
                        'error': f"Quantité invalide pour {produit.nom}"
                    })

                if produit.stock_actuel < qty:
                    return JsonResponse({
                        'success': False,
                        'error': f"Stock insuffisant pour {produit.nom} (dispo: {produit.stock_actuel})"
                    })

                prix = produit.prix_vente
                total_ht += qty * prix

                lignes_validees.append({
                    'produit': produit,
                    'qty': qty,
                    'prix': prix
                })

            # Remise
            try:
                remise_pct = Decimal(str(data.get('remise', 0)))

                if not (0 <= remise_pct <= 100):
                    remise_pct = Decimal('0')

            except InvalidOperation:
                remise_pct = Decimal('0')

            remise_montant = (
                total_ht * remise_pct / 100
            ).quantize(Decimal('0.01'))

            total_ttc = total_ht - remise_montant

            # Montant reçu
            try:
                montant_recu = Decimal(str(data.get('montant_recu', 0)))

                if montant_recu < 0:
                    montant_recu = Decimal('0')

            except InvalidOperation:
                montant_recu = Decimal('0')

            # Mode paiement
            mode_paiement = data.get('mode_paiement', 'especes')

            modes_valides = [m[0] for m in Vente.MODES_PAIEMENT]

            if mode_paiement not in modes_valides:
                return JsonResponse({
                    'success': False,
                    'error': 'Mode de paiement invalide'
                })

            monnaie_rendue = max(
                Decimal('0'),
                montant_recu - total_ttc
            )

            # Vérifications crédit
            if mode_paiement == 'credit' and not data.get('client_nom', '').strip():
                return JsonResponse({
                    'success': False,
                    'error': 'Un nom client est requis pour une vente à crédit'
                })

            if mode_paiement == 'credit' and not data.get('client_telephone', '').strip():
                return JsonResponse({
                    'success': False,
                    'error': 'Un numéro de téléphone est requis pour une vente à crédit'
                })

            # Création/récupération client
            client = None

            client_nom = data.get('client_nom', '').strip()
            client_tel = data.get('client_telephone', '').strip()

            if client_nom and client_tel:
                client, _ = Client.objects.get_or_create(
                    user=request.user,
                    telephone=client_tel,
                    defaults={
                        'nom': client_nom
                    }
                )

            # Création vente
            vente = Vente.objects.create(
                user=request.user,
                client=client,
                client_nom=client_nom or 'Client comptant',
                client_telephone=client_tel,
                mode_paiement=mode_paiement,
                statut='completee',  # Toujours complétée — le crédit est géré par Dette, pas par statut
                remise=remise_pct,
                total_ht=total_ht,
                total_ttc=total_ttc,
                montant_recu=montant_recu,
                monnaie_rendue=monnaie_rendue,
            )

            # Lignes vente + stock
            for lv in lignes_validees:

                produit = lv['produit']
                qty = lv['qty']
                prix = lv['prix']

                LigneVente.objects.create(
                    vente=vente,
                    produit=produit,
                    quantite=qty,
                    prix_unitaire=prix,
                    sous_total=qty * prix,
                )

                stock_avant = produit.stock_actuel

                produit.stock_actuel -= qty

                produit.save(update_fields=[
                    'stock_actuel',
                    'updated_at'
                ])

                MouvementStock.objects.create(
                    produit=produit,
                    type_mouvement='vente',
                    quantite=qty,
                    stock_avant=stock_avant,
                    stock_apres=produit.stock_actuel,
                    note=f'Vente {vente.numero}',
                    created_by=request.user,
                )

            # Gestion dette
            if mode_paiement == 'credit':

                montant_dette = total_ttc - montant_recu

                Dette.objects.create(
                    client=client,
                    vente=vente,
                    montant_initial=montant_dette,
                    montant_restant=montant_dette,
                )

        return JsonResponse({
            'success': True,
            'numero': vente.numero,
            'total': float(vente.total_ttc),
            'monnaie': float(vente.monnaie_rendue),
            'vendeur': request.user.username,
            'date_vente': vente.created_at.strftime('%d/%m/%Y %H:%M'),
            'mode_paiement': vente.get_mode_paiement_display(),
            'montant_recu': float(vente.montant_recu),
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def detail_vente(request, pk):

    vente = get_object_or_404(
        Vente,
        pk=pk,
        user=request.user
    )

    montant_remise = (
        (vente.total_ht * vente.remise / 100).quantize(Decimal('0.01'))
        if vente.remise else Decimal('0')
    )

    return render(request, 'stock/detail_vente.html', {
        'vente': vente,
        'montant_remise': montant_remise,
    })


@login_required
def api_produits(request):
    """API JSON pour l'autocomplete POS."""

    q = request.GET.get('q', '').strip()
    cat = request.GET.get('cat', '')

    from django.db.models import Q

    produits = (
        Produit.objects
        .filter(
            user=request.user,
            actif=True,
            stock_actuel__gt=0
        )
        .select_related('categorie')
    )

    if q:
        produits = produits.filter(
            Q(nom__icontains=q) |
            Q(reference__icontains=q)
        )

    if cat:
        produits = produits.filter(categorie_id=cat)

    try:
        limit = min(int(request.GET.get('limit', 50)), 100)

    except ValueError:
        limit = 50

    data = [{
        'id': p.id,
        'nom': p.nom,
        'reference': p.reference,
        'prix_vente': float(p.prix_vente),
        'stock_actuel': p.stock_actuel,
        'categorie': p.categorie.nom if p.categorie else '',
        'couleur': p.categorie.couleur if p.categorie else '#6b7280',
    } for p in produits[:limit]]

    return JsonResponse({'produits': data})
