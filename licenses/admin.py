# Register your models here.
from django.contrib import admin
from .models import LicenseKey, UserLicense

admin.site.register(LicenseKey)
admin.site.register(UserLicense)