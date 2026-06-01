from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage

urlpatterns = [
    path('admin/', admin.site.urls),

    # Racine → signup (non connecté) ou dashboard (@login_required redirige vers login)
    path('', RedirectView.as_view(url='/accounts/signup/', permanent=False), name='home'),

    # Auth
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html'
    ), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),

    # Licences
    path('licenses/', include('licenses.urls')),

    # Apps métier
    path('', include('rapports.urls')),   # dashboard + rapports
    path('', include('ventes.urls')),     # pos + ventes + api produits
    path('', include('clients.urls')),    # clients + dettes + api clients
    path('', include('stock.urls')),      # produits + catégories + profil

    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=getattr(settings, 'MEDIA_ROOT', ''))
