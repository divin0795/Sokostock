from django.urls import path
from .views import SignUpView, post_login_redirect

urlpatterns = [
    # On ne garde que ce qui est spécifique à ton application accounts
    path('signup/', SignUpView.as_view(), name='signup'),
    path('redirect/', post_login_redirect, name='post_login_redirect'),
    
    # On peut ajouter ici la future route du dashboard
    # path('dashboard/', views.dashboard, name='dashboard'),
]