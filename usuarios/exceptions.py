from rest_framework.exceptions import APIException


class AccountLocked(APIException):
    """Cuenta bloqueada temporalmente por intentos fallidos de login (HTTP 423)."""

    status_code = 423
    default_detail = 'Cuenta bloqueada temporalmente por intentos fallidos.'
    default_code = 'account_locked'

    def __init__(self, detail=None, wait=None, code=None):
        super().__init__(detail, code)
        self.wait = wait

    def get_headers(self):
        headers = super().get_headers()
        if self.wait is not None:
            headers['Retry-After'] = '%d' % self.wait
        return headers
