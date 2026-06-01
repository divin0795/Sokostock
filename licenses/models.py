from django.db import models
from django.conf import settings
from django.utils import timezone
import secrets
from datetime import timedelta


class LicenseKey(models.Model):
    """Clés générées à l'avance pour vente"""
    code = models.CharField(max_length=25, unique=True, editable=False)
    is_used = models.BooleanField(default=False)
    duration_days = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"SOKO-{secrets.token_hex(4).upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} ({'Used' if self.is_used else 'Free'})"


class UserLicense(models.Model):
    """Licence utilisateur"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    license_key = models.ForeignKey(LicenseKey, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}"

    @property
    def is_valid(self):
        return self.is_active and self.expiry_date > timezone.now()

    @property
    def days_left(self):
        delta = self.expiry_date - timezone.now()
        return max(0, delta.days)