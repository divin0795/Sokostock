"""
App paramètres — configuration de l'interface et du commerce.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from accounts.models import Commerce
from accounts.forms import CommerceForm

COLORS = [
    ('#2563eb', 'Bleu'),
    ('#10b981', 'Vert'),
    ('#f59e0b', 'Ambre'),
    ('#ef4444', 'Rouge'),
    ('#8b5cf6', 'Violet'),
    ('#06b6d4', 'Cyan'),
    ('#f97316', 'Orange'),
    ('#ec4899', 'Rose'),
]

@login_required
def parametres(request):
    commerce = getattr(request.user, 'commerce', None)
    form = CommerceForm(instance=commerce)
    return render(request, 'parametres/parametres.html', {
        'form': form,
        'commerce': commerce,
        'colors': COLORS,
        'selected_color': '#2563eb',
    })


@login_required
@require_POST
def save_parametres(request):
    commerce = getattr(request.user, 'commerce', None)
    form = CommerceForm(request.POST, request.FILES, instance=commerce)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        messages.success(request, 'Paramètres sauvegardés avec succès.')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')
    return redirect('parametres')
