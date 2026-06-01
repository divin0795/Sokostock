from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os

from .models import LicenseKey, UserLicense


@login_required
def activate_license(request):
    user_license = None
    try:
        user_license = UserLicense.objects.get(user=request.user)
    except UserLicense.DoesNotExist:
        pass

    if request.method == 'POST':
        code_saisi = request.POST.get('license_code', '').strip()

        if not code_saisi:
            messages.error(request, "Veuillez entrer un code.")
            return redirect('activate_license')

        try:
            with transaction.atomic():
                key_obj = LicenseKey.objects.select_for_update().get(
                    code=code_saisi,
                    is_used=False
                )
                UserLicense.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'license_key': key_obj,
                        'expiry_date': timezone.now() + timedelta(days=key_obj.duration_days),
                        'is_active': True
                    }
                )
                key_obj.is_used = True
                key_obj.save()

            messages.success(request, "Licence activée avec succès !")
            return redirect('/dashboard/')

        except LicenseKey.DoesNotExist:
            messages.error(request, "Code invalide ou déjà utilisé.")

    return render(request, 'licenses/activate.html', {'user_license': user_license})


@csrf_exempt
def api_get_license(request):
    token = request.headers.get('X-Bot-Token', '')
    if token != os.environ.get('BOT_SECRET_TOKEN'):
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)

    with transaction.atomic():
        key = LicenseKey.objects.select_for_update().filter(is_used=False).first()
        if not key:
            return JsonResponse({'success': False, 'error': 'Aucune clé disponible'})

        key.is_used = True
        key.save()

    return JsonResponse({'success': True, 'code': key.code, 'duration_days': key.duration_days})