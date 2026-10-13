from datetime import timedelta
from math import ceil

from django.db import transaction
from django.utils import timezone

from .models import LoginAttempt

# Política de bloqueo temporal: 5 intentos fallidos -> 15 minutos de bloqueo.
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)
# Si pasan más de 30 minutos entre intentos fallidos, el contador arranca de cero.
ATTEMPT_RESET_WINDOW = timedelta(minutes=30)


def _normalize(email):
    return (email or '').strip().lower()


def check_lockout(email):
    """Devuelve los segundos restantes de bloqueo (0 si no está bloqueado)."""
    key = _normalize(email)
    if not key:
        return 0
    try:
        attempt = LoginAttempt.objects.get(email=key)
    except LoginAttempt.DoesNotExist:
        return 0
    now = timezone.now()
    if attempt.locked_until and attempt.locked_until > now:
        return max(1, ceil((attempt.locked_until - now).total_seconds()))
    return 0


def register_failure(email):
    """Registra un intento fallido. Devuelve los segundos de bloqueo si se superó el límite."""
    key = _normalize(email)
    if not key:
        return 0
    now = timezone.now()
    with transaction.atomic():
        LoginAttempt.objects.get_or_create(email=key)
        attempt = LoginAttempt.objects.select_for_update().get(email=key)

        if attempt.locked_until and attempt.locked_until <= now:
            # El bloqueo anterior expiró: arranca una ventana nueva.
            attempt.failed_attempts = 0
            attempt.locked_until = None
        elif attempt.last_attempt_at and now - attempt.last_attempt_at > ATTEMPT_RESET_WINDOW:
            # Demasiado tiempo sin fallos: el contador vuelve a cero.
            attempt.failed_attempts = 0

        attempt.failed_attempts += 1
        attempt.last_attempt_at = now

        locked_for = 0
        if attempt.failed_attempts >= MAX_FAILED_ATTEMPTS:
            attempt.failed_attempts = 0
            attempt.locked_until = now + LOCKOUT_DURATION
            locked_for = int(LOCKOUT_DURATION.total_seconds())

        attempt.save()
    return locked_for


def reset_failures(email):
    """Limpia el contador de intentos tras un login exitoso."""
    key = _normalize(email)
    if not key:
        return
    LoginAttempt.objects.filter(email=key).delete()
