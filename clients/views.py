"""
App clients — gestion des clients et des dettes.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import Q, Sum, F, DecimalField
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation

from stock.models import Client, Dette, PaiementDette


# ── CLIENTS ───────────────────────────────────────────────────────────────────

@login_required
def liste_clients(request):
    q = request.GET.get('q', '').strip()
    clients = (
        Client.objects
        .filter(user=request.user, actif=True)
        .order_by('nom')
    )
    if q:
        clients = clients.filter(
            Q(nom__icontains=q) | Q(telephone__icontains=q)
        )
    return render(request, 'stock/clients.html', {'clients': clients, 'q': q})


@login_required
@require_POST
def ajouter_client(request):
    nom = request.POST.get('nom', '').strip()
    if not nom:
        messages.error(request, 'Le nom est requis.')
        return redirect('liste_clients')

    Client.objects.create(
        user=request.user,
        nom=nom,
        telephone=request.POST.get('telephone', '').strip(),
        adresse=request.POST.get('adresse', '').strip(),
        note=request.POST.get('note', '').strip(),
    )
    messages.success(request, f'Client « {nom} » ajouté.')
    return redirect('liste_clients')


@login_required
def detail_client(request, pk):
    client = get_object_or_404(Client, pk=pk, user=request.user)

    # Toutes les ventes non-annulées (le crédit est géré par Dette, pas par statut)
    ventes = (
        client.ventes_liees
        .exclude(statut='annulee')
        .order_by('-created_at')[:20]
    )

    dettes = client.dettes.filter(remboursee=False).order_by('-created_at')

    return render(request, 'stock/detail_client.html', {
        'client': client,
        'ventes': ventes,
        'dettes': dettes,
    })


@login_required
@require_POST
def supprimer_client(request, pk):
    client = get_object_or_404(Client, pk=pk, user=request.user)
    client.actif = False
    client.save()
    messages.success(request, f'Client « {client.nom} » supprimé.')
    return redirect('liste_clients')


@login_required
def api_clients(request):
    """API JSON pour l'autocomplete POS."""
    q = request.GET.get('q', '').strip()
    clients = Client.objects.filter(user=request.user, actif=True)

    if q:
        clients = clients.filter(
            Q(nom__icontains=q) | Q(telephone__icontains=q)
        )

    try:
        limit = min(int(request.GET.get('limit', 20)), 100)
    except ValueError:
        limit = 20

    data = [
        {'id': c.id, 'nom': c.nom, 'telephone': c.telephone}
        for c in clients[:limit]
    ]

    return JsonResponse({'clients': data})


# ── DETTES ────────────────────────────────────────────────────────────────────

@login_required
def liste_dettes(request):

    dettes = (
        Dette.objects
        .filter(
            client__user=request.user,
            remboursee=False
        )
        .values(
            'client__id',
            'client__nom',
            'client__telephone',
        )
        .annotate(
            total_initial=Coalesce(
                Sum('montant_initial'),
                Decimal('0')
            ),
            total_restant=Coalesce(
                Sum('montant_restant'),
                Decimal('0')
            ),
            total_paye=Coalesce(
                Sum(
                    F('montant_initial') - F('montant_restant'),
                    output_field=DecimalField()
                ),
                Decimal('0')
            ),
        )
        .order_by('-total_restant')
    )

    total_du = dettes.aggregate(
        total=Coalesce(
            Sum('total_restant'),
            Decimal('0')
        )
    )['total']

    clients = Client.objects.filter(
        user=request.user,
        actif=True
    ).order_by('nom')

    return render(request, 'stock/dettes.html', {
        'dettes': dettes,
        'clients': clients,
        'total_du': total_du,
    })


@login_required
@require_POST
def enregistrer_paiement(request, pk):
    dette = get_object_or_404(Dette, pk=pk, client__user=request.user)

    try:
        montant = Decimal(str(request.POST.get('montant', 0)))
        if montant <= 0:
            raise ValueError()
    except (InvalidOperation, ValueError):
        messages.error(request, 'Montant invalide.')
        return redirect('liste_dettes')

    with transaction.atomic():
        montant = min(montant, dette.montant_restant)

        dette.montant_restant -= montant
        if dette.montant_restant <= 0:
            dette.montant_restant = Decimal('0')
            dette.remboursee = True

        dette.save()

        PaiementDette.objects.create(
            dette=dette,
            montant=montant,
            note=request.POST.get('note', '').strip(),
            created_by=request.user,
        )

        # Intégration au CA : on met à jour montant_recu sur la vente liée
        # afin que les calculs de CA incluent les encaissements de dettes.
        if dette.vente_id:
            from stock.models import Vente
            Vente.objects.filter(pk=dette.vente_id).update(
                montant_recu=F('montant_recu') + montant
            )

    messages.success(request, f'Paiement de {montant:,.0f} FCFA enregistré.')
    return redirect('liste_dettes')


@login_required
@require_POST
def creer_dette_manuelle(request):
    """Créer une dette sans vente liée (prêt direct)."""
    client_id = request.POST.get('client_id')

    try:
        client = Client.objects.get(pk=client_id, user=request.user)
        montant = Decimal(str(request.POST.get('montant', 0)))
        if montant <= 0:
            raise ValueError()
    except (Client.DoesNotExist, InvalidOperation, ValueError):
        messages.error(request, 'Données invalides.')
        return redirect('liste_dettes')

    echeance = request.POST.get('echeance') or None

    Dette.objects.create(
        client=client,
        montant_initial=montant,
        montant_restant=montant,
        echeance=echeance,
        note=request.POST.get('note', '').strip(),
    )

    messages.success(request, f'Dette de {montant:,.0f} FCFA créée pour {client.nom}.')
    return redirect('liste_dettes')
