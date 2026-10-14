from django.db import models
from django.utils import timezone


class LoginAttempt(models.Model):
    """Controla los intentos fallidos de login por email para el bloqueo temporal."""

    email = models.EmailField(unique=True)
    failed_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_attempt_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email

    def is_locked(self):
        return self.locked_until is not None and self.locked_until > timezone.now()
