from django.urls import path
from . import views

urlpatterns = [
    path('parametres/', views.parametres, name='parametres'),
    path('parametres/save/', views.save_parametres, name='save_parametres'),
]
