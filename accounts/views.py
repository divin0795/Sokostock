from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import InscriptionForm
from django.shortcuts import redirect
from licenses.models import UserLicense
from django.utils import timezone

class SignUpView(CreateView):
    form_class = InscriptionForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('login') # On redirige vers la connexion après
    
def csrf_failure(request, reason=""):
    return render(request, "accounts/csrf_error.html", status=403)

def post_login_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        user_license = UserLicense.objects.get(user=request.user)

        if user_license.is_active and user_license.expiry_date > timezone.now():
            return redirect('/dashboard/')

    except UserLicense.DoesNotExist:
        pass

    return redirect('/activate-license/')