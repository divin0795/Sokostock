"""
App rapports — dashboard analytics et historique des ventes.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from stock.models import Produit, Vente, LigneVente, MouvementStock
from clients.models import Dette


@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()
    debut_mois = today.replace(day=1)

    # ── PRODUITS ─────────────────────────────────────────────
    produits_qs = Produit.objects.filter(user=user, actif=True)

    produits_stats = produits_qs.aggregate(
        total=Count('id'),
        ruptures=Count('id', filter=Q(stock_actuel=0)),
    )

    total_produits = produits_stats['total']
    ruptures = produits_stats['ruptures']

    alertes_qs = produits_qs.filter(
        stock_actuel__lte=F('stock_minimum')
    ).only('id', 'nom', 'stock_actuel', 'stock_minimum').order_by('stock_actuel')

    nb_alertes = alertes_qs.count()
    alertes = alertes_qs[:3]

    valeur_stock = produits_qs.aggregate(
        total=Coalesce(
            Sum(
                ExpressionWrapper(
                    F('stock_actuel') * F('prix_achat'),
                    output_field=DecimalField(max_digits=16, decimal_places=2)
                )
            ),
            Decimal('0')
        )
    )['total']

    # ── VENTES (CA ENCAISSÉ) ─────────────────────────────────
    ventes_jour_agg = Vente.objects.filter(
        user=user,
        statut='completee',
        created_at__date=today
    ).exclude(
        mode_paiement='credit'
    ).aggregate(
        total=Coalesce(Sum('montant_recu'), Decimal('0')),
        nb=Count('id'),
    )

    ventes_jour = ventes_jour_agg['total']
    nb_ventes_jour = ventes_jour_agg['nb']

    ventes_mois_agg = Vente.objects.filter(
        user=user,
        statut='completee',
        created_at__date__gte=debut_mois
    ).exclude(
        mode_paiement='credit'
    ).aggregate(
        total=Coalesce(Sum('montant_recu'), Decimal('0')),
        nb=Count('id'),
    )

    ventes_mois = ventes_mois_agg['total']
    nb_ventes_mois = ventes_mois_agg['nb']

    panier_moyen = ventes_mois / nb_ventes_mois if nb_ventes_mois > 0 else Decimal('0')

    # ── CRÉDIT ───────────────────────────────────────────────
    credit_jour_agg = Vente.objects.filter(
        user=user,
        statut='completee',
        mode_paiement='credit',
        created_at__date=today
    ).aggregate(
        total=Coalesce(Sum('total_ttc'), Decimal('0')),
        nb=Count('id'),
    )

    credit_jour = credit_jour_agg['total']
    nb_credit_jour = credit_jour_agg['nb']

    credit_mois_agg = Vente.objects.filter(
        user=user,
        statut='completee',
        mode_paiement='credit',
        created_at__date__gte=debut_mois
    ).aggregate(
        total=Coalesce(Sum('total_ttc'), Decimal('0')),
        nb=Count('id'),
    )

    credit_mois = credit_mois_agg['total']
    nb_credit_mois = credit_mois_agg['nb']

    dettes_en_cours = Dette.objects.filter(
        client__user=user,
        remboursee=False
    ).aggregate(
        total=Coalesce(Sum('montant_restant'), Decimal('0'))
    )['total']

    # ── BÉNÉFICE (ENCAISSÉ UNIQUEMENT) ───────────────────────
    benefice_jour = LigneVente.objects.filter(
        vente__user=user,
        vente__statut='completee',
        vente__created_at__date=today,
    ).exclude(
        vente__mode_paiement='credit'
    ).aggregate(
        total=Coalesce(
            Sum(
                ExpressionWrapper(
                    (F('prix_unitaire') - F('produit__prix_achat')) * F('quantite'),
                    output_field=DecimalField(max_digits=16, decimal_places=2)
                )
            ),
            Decimal('0')
        )
    )['total']

    # ── GRAPHIQUE 7 JOURS (ENCAISSÉ) ─────────────────────────
    debut_7j = today - timedelta(days=6)

    ventes_7j_qs = (
        Vente.objects
        .filter(
            user=user,
            statut='completee',
            created_at__date__gte=debut_7j
        )
        .exclude(mode_paiement='credit')
        .values('created_at__date')
        .annotate(total=Sum('montant_recu'))
    )

    totaux_par_jour = {
        v['created_at__date']: float(v['total'] or 0)
        for v in ventes_7j_qs
    }

    labels = []
    data_ventes = []

    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime('%d/%m'))
        data_ventes.append(totaux_par_jour.get(d, 0))

    # ── TOP PRODUITS ─────────────────────────────────────────
    top_produits = list(
        LigneVente.objects
        .filter(
            vente__user=user,
            vente__statut='completee',
            vente__created_at__date__gte=debut_mois,
        )
        .values('produit__nom')
        .annotate(qty=Sum('quantite'), ca=Sum('sous_total'))
        .order_by('-ca')[:5]
    )

    if top_produits:
        max_ca = float(max(p['ca'] or 0 for p in top_produits) or 1)
        for p in top_produits:
            p['ratio'] = round(float(p['ca'] or 0) / max_ca * 100, 1)

    # ── DERNIÈRES VENTES ─────────────────────────────────────
    dernieres_ventes = (
        Vente.objects
        .filter(user=user, statut='completee')
        .only('numero', 'client_nom', 'total_ttc', 'mode_paiement', 'statut', 'created_at')
        .order_by('-created_at')[:10]
    )

    # ── MOUVEMENTS STOCK ─────────────────────────────────────
    derniers_mouvements = (
        MouvementStock.objects
        .filter(produit__user=user)
        .select_related('produit')
        .only('produit__nom', 'type_mouvement', 'quantite', 'created_at')
        .order_by('-created_at')[:8]
    )

    context = {
        'total_produits': total_produits,
        'nb_alertes': nb_alertes,
        'alertes': alertes,
        'ventes_jour': ventes_jour,
        'ventes_mois': ventes_mois,
        'nb_ventes_jour': nb_ventes_jour,
        'nb_ventes_mois': nb_ventes_mois,
        'panier_moyen': panier_moyen,
        'valeur_stock': valeur_stock,
        'ruptures': ruptures,
        'benefice_jour': benefice_jour,
        'labels': json.dumps(labels),
        'data_ventes': json.dumps(data_ventes),
        'top_produits': top_produits,
        'dernieres_ventes': dernieres_ventes,
        'derniers_mouvements': derniers_mouvements,
        'credit_jour': credit_jour,
        'credit_mois': credit_mois,
        'nb_credit_jour': nb_credit_jour,
        'nb_credit_mois': nb_credit_mois,
        'dettes_en_cours': dettes_en_cours,
    }

    return render(request, 'stock/dashboard.html', context)


@login_required
def rapports(request):
    user = request.user
    today = timezone.now().date()

    try:
        nb_jours = int(request.GET.get('periode', 30))
        if nb_jours not in (7, 30, 90, 365):
            nb_jours = 30
    except ValueError:
        nb_jours = 30

    debut = today - timedelta(days=nb_jours - 1)

    ventes = Vente.objects.filter(
        user=user,
        statut='completee',
        created_at__date__gte=debut
    )

    agg = ventes.exclude(
        mode_paiement='credit'
    ).aggregate(
        ca=Coalesce(Sum('montant_recu'), Decimal('0')),
        nb=Count('id'),
    )

    ca_total = agg['ca']
    nb_ventes = agg['nb']

    panier_moyen = ca_total / nb_ventes if nb_ventes > 0 else Decimal('0')

    ventes_par_jour = {
        v['created_at__date']: float(v['s'] or 0)
        for v in ventes.exclude(mode_paiement='credit')
        .values('created_at__date')
        .annotate(s=Sum('montant_recu'))
    }

    labels = []
    ca_jour = []

    for i in range(nb_jours - 1, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime('%d/%m'))
        ca_jour.append(ventes_par_jour.get(d, 0))

    top = list(
        LigneVente.objects
        .filter(vente__in=ventes)
        .values('produit__nom')
        .annotate(qty=Sum('quantite'), ca=Sum('sous_total'))
        .order_by('-ca')[:10]
    )

    if top:
        max_qty = max((p['qty'] or 0) for p in top) or 1
        for p in top:
            p['ratio'] = round((p['qty'] or 0) / max_qty * 100, 1)

    repartition = ventes.values('mode_paiement').annotate(
        total=Sum('total_ttc'),
        nb=Count('id')
    ).order_by('-total')

    historique = ventes.order_by('-created_at')[:20]

    context = {
        'periode': str(nb_jours),
        'ca_total': ca_total,
        'nb_ventes': nb_ventes,
        'panier_moyen': panier_moyen,
        'labels': json.dumps(labels),
        'ca_jour': json.dumps(ca_jour),
        'top': top,
        'repartition': repartition,
        'historique': historique,
        'periods': [('7', '7 jours'), ('30', '30 jours'), ('90', '90 jours'), ('365', '1 an')],
    }

    return render(request, 'stock/rapports.html', context)
