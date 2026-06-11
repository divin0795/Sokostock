from django.urls import path
from .views import activate_license
from . import views
urlpatterns = [
    path('activate/', activate_license, name='activate_license'),
    path('api/get-license/', views.api_get_license, name='api_get_license'),
]