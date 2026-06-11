"""
App fournisseurs — gestion des fournisseurs et commandes.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from decimal import Decimal, InvalidOperation

from .models import Fournisseur, CommandeFournisseur, LigneCommande
from stock.models import Produit, MouvementStock


# ── FOURNISSEURS ──────────────────────────────────────────────────────────────

@login_required
def liste_fournisseurs(request):
    q = request.GET.get('q', '').strip()
    fournisseurs = Fournisseur.objects.filter(user=request.user, actif=True).order_by('nom')
    if q:
        fournisseurs = fournisseurs.filter(
            Q(nom__icontains=q) | Q(telephone__icontains=q)
        )
    return render(request, 'fournisseurs/liste.html', {
        'fournisseurs': fournisseurs,
        'q': q,
    })


@login_required
def ajouter_fournisseur(request):
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        if not nom:
            messages.error(request, 'Le nom est requis.')
            return redirect('liste_fournisseurs')
        Fournisseur.objects.create(
            user=request.user,
            nom=nom,
            telephone=request.POST.get('telephone', '').strip(),
            email=request.POST.get('email', '').strip(),
            adresse=request.POST.get('adresse', '').strip(),
            note=request.POST.get('note', '').strip(),
        )
        messages.success(request, f'Fournisseur « {nom} » ajouté.')
    return redirect('liste_fournisseurs')


@login_required
def detail_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk, user=request.user)
    commandes = fournisseur.commandes.order_by('-created_at')[:20]
    return render(request, 'fournisseurs/detail.html', {
        'fournisseur': fournisseur,
        'commandes': commandes,
    })


@login_required
def modifier_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk, user=request.user)
    if request.method == 'POST':
        fournisseur.nom = request.POST.get('nom', fournisseur.nom).strip()
        fournisseur.telephone = request.POST.get('telephone', '').strip()
        fournisseur.email = request.POST.get('email', '').strip()
        fournisseur.adresse = request.POST.get('adresse', '').strip()
        fournisseur.note = request.POST.get('note', '').strip()
        fournisseur.save()
        messages.success(request, 'Fournisseur mis à jour.')
        return redirect('detail_fournisseur', pk=pk)
    return render(request, 'fournisseurs/form.html', {'fournisseur': fournisseur})


@login_required
@require_POST
def supprimer_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk, user=request.user)
    fournisseur.actif = False
    fournisseur.save()
    messages.success(request, f'Fournisseur « {fournisseur.nom} » supprimé.')
    return redirect('liste_fournisseurs')


# ── COMMANDES ─────────────────────────────────────────────────────────────────

@login_required
def liste_commandes(request):
    statut = request.GET.get('statut', '')
    commandes = CommandeFournisseur.objects.filter(
        user=request.user
    ).select_related('fournisseur').order_by('-created_at')
    if statut:
        commandes = commandes.filter(statut=statut)
    return render(request, 'fournisseurs/commandes.html', {
        'commandes': commandes,
        'statut': statut,
        'statuts': CommandeFournisseur.STATUTS,
    })


@login_required
def creer_commande(request):
    fournisseurs = Fournisseur.objects.filter(user=request.user, actif=True)
    produits = Produit.objects.filter(user=request.user, actif=True)

    if request.method == 'POST':
        fournisseur_id = request.POST.get('fournisseur_id')
        try:
            fournisseur = Fournisseur.objects.get(pk=fournisseur_id, user=request.user)
        except Fournisseur.DoesNotExist:
            messages.error(request, 'Fournisseur invalide.')
            return redirect('creer_commande')

        with transaction.atomic():
            commande = CommandeFournisseur.objects.create(
                user=request.user,
                fournisseur=fournisseur,
                note=request.POST.get('note', '').strip(),
                date_livraison_prevue=request.POST.get('date_livraison') or None,
            )

            produit_ids = request.POST.getlist('produit_id')
            quantites = request.POST.getlist('quantite')
            prix = request.POST.getlist('prix_unitaire')

            montant_total = Decimal('0')
            for pid, qty, pu in zip(produit_ids, quantites, prix):
                try:
                    produit = Produit.objects.get(pk=pid, user=request.user)
                    q = int(qty)
                    p = Decimal(str(pu))
                    if q > 0 and p >= 0:
                        ligne = LigneCommande.objects.create(
                            commande=commande,
                            produit=produit,
                            quantite_commandee=q,
                            prix_unitaire=p,
                        )
                        montant_total += ligne.sous_total
                except (Produit.DoesNotExist, ValueError, InvalidOperation):
                    continue

            commande.montant_total = montant_total
            commande.save()

        messages.success(request, f'Commande {commande.numero} créée.')
        return redirect('detail_commande', pk=commande.pk)

    return render(request, 'fournisseurs/creer_commande.html', {
        'fournisseurs': fournisseurs,
        'produits': produits,
    })


@login_required
def detail_commande(request, pk):
    commande = get_object_or_404(CommandeFournisseur, pk=pk, user=request.user)
    lignes = commande.lignes.select_related('produit').all()
    return render(request, 'fournisseurs/detail_commande.html', {
        'commande': commande,
        'lignes': lignes,
    })


@login_required
@require_POST
def recevoir_commande(request, pk):
    """Marquer une commande comme reçue et mettre à jour le stock."""
    commande = get_object_or_404(CommandeFournisseur, pk=pk, user=request.user)

    if commande.statut in ('recue', 'annulee'):
        messages.error(request, 'Cette commande ne peut plus être modifiée.')
        return redirect('detail_commande', pk=pk)

    with transaction.atomic():
        for ligne in commande.lignes.select_related('produit').all():
            produit = ligne.produit
            stock_avant = produit.stock_actuel
            produit.stock_actuel += ligne.quantite_commandee
            # Mettre à jour le prix d'achat si fourni
            if ligne.prix_unitaire > 0:
                produit.prix_achat = ligne.prix_unitaire
            produit.save(update_fields=['stock_actuel', 'prix_achat', 'updated_at'])

            MouvementStock.objects.create(
                produit=produit,
                type_mouvement='entree',
                quantite=ligne.quantite_commandee,
                stock_avant=stock_avant,
                stock_apres=produit.stock_actuel,
                note=f'Réception commande {commande.numero}',
                created_by=request.user,
            )
            ligne.quantite_recue = ligne.quantite_commandee
            ligne.save()

        commande.statut = 'recue'
        commande.save()

    messages.success(request, f'Commande {commande.numero} reçue. Stock mis à jour.')
    return redirect('detail_commande', pk=pk)
