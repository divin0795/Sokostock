from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Commerce

# Configuration pour afficher tes nouveaux champs dans l'admin
class CustomUserAdmin(UserAdmin):
    # Champs affichés lors de la modification d'un utilisateur
    fieldsets = UserAdmin.fieldsets + (
        ("Informations complémentaires", {'fields': ('phone_number',)}),
    )
    # Champs affichés lors de la création d'un utilisateur dans l'admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Informations obligatoires", {'fields': ('phone_number', 'first_name', 'last_name', 'email')}),
    )
    # Colonnes affichées dans la liste des utilisateurs
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']

admin.site.register(User, CustomUserAdmin)
admin.site.register(Commerce)