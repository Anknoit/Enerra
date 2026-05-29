import logging
import time

from .utils import set_current_user

logger = logging.getLogger(__name__)


class AuditMiddleware:
    """Stores request.user in thread-local so AuditLogMixin can access it."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        set_current_user(user)
        try:
            return self.get_response(request)
        finally:
            set_current_user(None)


class OrganisationMiddleware:
    """Attaches request.org from user.profile.organisation."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.org = None
        user = getattr(request, 'user', None)
        if user and getattr(user, 'is_authenticated', False):
            try:
                request.org = user.profile.organisation
            except AttributeError:
                pass
        return self.get_response(request)


class RequestLoggingMiddleware:
    """Logs method, path, status code, and duration for every request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = (time.monotonic() - start) * 1000
        logger.info(
            '%s %s %d %.1fms',
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response
