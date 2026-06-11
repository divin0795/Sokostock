"""
App stock — gestion des produits, catégories et profil commerce.
Les ventes → app ventes/
Les clients & dettes → app clients/
Le dashboard & rapports → app rapports/
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, F

from .models import Produit, Categorie, MouvementStock
from .forms import ProduitForm, CategorieForm, MouvementForm


# ── PRODUITS ──────────────────────────────────────────────────────────────────

@login_required
def liste_produits(request):
    q            = request.GET.get('q', '').strip()
    categorie_id = request.GET.get('categorie', '')
    alerte       = request.GET.get('alerte', '')

    produits = (
        Produit.objects
        .filter(user=request.user, actif=True)
        .select_related('categorie')
        .order_by('nom')
    )
    if q:
        produits = produits.filter(Q(nom__icontains=q) | Q(reference__icontains=q))
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)
    if alerte == '1':
        produits = produits.filter(stock_actuel__lte=F('stock_minimum'))

    categories = Categorie.objects.filter(user=request.user)
    return render(request, 'stock/produits.html', {
        'produits': produits,
        'categories': categories,
        'q': q,
        'categorie_id': categorie_id,
    })


@login_required
def ajouter_produit(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST, user=request.user)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.user = request.user
            produit.save()
            if produit.stock_actuel > 0:
                MouvementStock.objects.create(
                    produit=produit,
                    type_mouvement='entree',
                    quantite=produit.stock_actuel,
                    stock_avant=0,
                    stock_apres=produit.stock_actuel,
                    note='Stock initial',
                    created_by=request.user,
                )
            messages.success(request, f'Produit « {produit.nom} » ajouté.')
            return redirect('liste_produits')
    else:
        form = ProduitForm(user=request.user)
    return render(request, 'stock/produit_form.html', {'form': form, 'titre': 'Ajouter un produit'})


@login_required
def modifier_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit mis à jour.')
            return redirect('liste_produits')
    else:
        form = ProduitForm(instance=produit, user=request.user)
    return render(request, 'stock/produit_form.html', {
        'form': form, 'titre': 'Modifier le produit', 'produit': produit
    })


@login_required
def supprimer_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk, user=request.user)
    if request.method == 'POST':
        produit.actif = False
        produit.save()
        messages.success(request, f'Produit « {produit.nom} » supprimé.')
        return redirect('liste_produits')
    return render(request, 'stock/confirmer_suppression.html', {'produit': produit})


@login_required
def ajuster_stock(request, pk):
    produit = get_object_or_404(Produit, pk=pk, user=request.user)
    if request.method == 'POST':
        form = MouvementForm(request.POST)
        if form.is_valid():
            type_mv  = form.cleaned_data['type_mouvement']
            quantite = form.cleaned_data['quantite']
            note     = form.cleaned_data.get('note', '')

            stock_avant = produit.stock_actuel
            if type_mv == 'entree':
                produit.stock_actuel += quantite
            elif type_mv in ('sortie', 'vente'):
                produit.stock_actuel = max(0, produit.stock_actuel - quantite)
            elif type_mv == 'ajustement':
                produit.stock_actuel = quantite
            else:
                messages.error(request, 'Type de mouvement invalide.')
                return redirect('liste_produits')

            produit.save()
            MouvementStock.objects.create(
                produit=produit,
                type_mouvement=type_mv,
                quantite=quantite,
                stock_avant=stock_avant,
                stock_apres=produit.stock_actuel,
                note=note,
                created_by=request.user,
            )
            messages.success(request, 'Stock mis à jour.')
            return redirect('liste_produits')
    else:
        form = MouvementForm()
    return render(request, 'stock/ajuster_stock.html', {'form': form, 'produit': produit})


# ── CATÉGORIES ────────────────────────────────────────────────────────────────

@login_required
def categories(request):
    cats = Categorie.objects.filter(user=request.user).annotate(nb=Count('produits'))
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = request.user
            cat.save()
            messages.success(request, 'Catégorie créée.')
            return redirect('categories')
    else:
        form = CategorieForm()
    return render(request, 'stock/categories.html', {'categories': cats, 'form': form})


# ── PROFIL COMMERCE ───────────────────────────────────────────────────────────

from accounts.models import Commerce
from accounts.forms import CommerceForm


@login_required
def profil_commerce(request):
    commerce = getattr(request.user, 'commerce', None)
    if request.method == 'POST':
        form = CommerceForm(request.POST, request.FILES, instance=commerce)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour.')
            return redirect('profil_commerce')
    else:
        form = CommerceForm(instance=commerce)
    return render(request, 'stock/profil_commerce.html', {'form': form, 'commerce': commerce})


# ── MOUVEMENTS DE STOCK ───────────────────────────────────────────────────────

from django.core.paginator import Paginator


@login_required
def mouvements_stock(request):
    type_filtre = request.GET.get('type', '')
    produit_filtre = request.GET.get('produit', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')

    mvts = (
        MouvementStock.objects
        .filter(produit__user=request.user)
        .select_related('produit')
        .order_by('-created_at')
    )

    if type_filtre:
        mvts = mvts.filter(type_mouvement=type_filtre)
    if produit_filtre:
        mvts = mvts.filter(produit_id=produit_filtre)
    if date_debut:
        mvts = mvts.filter(created_at__date__gte=date_debut)
    if date_fin:
        mvts = mvts.filter(created_at__date__lte=date_fin)

    nb_total = mvts.count()
    paginator = Paginator(mvts, 50)
    page = request.GET.get('page', 1)
    mouvements = paginator.get_page(page)

    produits = Produit.objects.filter(user=request.user, actif=True).order_by('nom')

    return render(request, 'stock/mouvements.html', {
        'mouvements': mouvements,
        'produits': produits,
        'nb_total': nb_total,
        'type_filtre': type_filtre,
        'produit_filtre': produit_filtre,
        'date_debut': date_debut,
        'date_fin': date_fin,
    })
