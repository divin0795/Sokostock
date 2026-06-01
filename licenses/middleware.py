from django.shortcuts import redirect
from licenses.models import UserLicense


class LicenseRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # 1. anonymes
        if not request.user.is_authenticated:
            return self.get_response(request)

        # 2. admin / propriétaire (bypass total)
        if request.user.is_superuser or request.user.is_staff:
            return self.get_response(request)

        # 3. routes autorisées (FIABLE)
        allowed_paths = [
            '/accounts/login/',
            '/accounts/signup/',
            '/accounts/logout/',
            '/licenses/activate/',
        ]

        if any(request.path.startswith(path) for path in allowed_paths):
            return self.get_response(request)

        # 4. vérification licence
        try:
            user_license = UserLicense.objects.get(user=request.user)

            if user_license.is_valid:
                return self.get_response(request)
            else:
                return redirect('activate_license')

        except UserLicense.DoesNotExist:
            return redirect('activate_license')