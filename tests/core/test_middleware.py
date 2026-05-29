import pytest
from unittest.mock import MagicMock, patch

from apps.core.middleware import AuditMiddleware, OrganisationMiddleware, RequestLoggingMiddleware
from apps.core.utils import get_current_user
from tests.factories import OrganisationFactory, UserProfileFactory


def _make_request(user=None, authenticated=True):
    request = MagicMock()
    if user is None:
        user = MagicMock()
        user.is_authenticated = authenticated
    request.user = user
    request.method = 'GET'
    request.path = '/api/test/'
    return request


def _make_response(status=200):
    response = MagicMock()
    response.status_code = status
    return response


class TestAuditMiddleware:
    def test_sets_thread_local_user(self):
        user = MagicMock()
        user.is_authenticated = True
        request = _make_request(user=user)
        response = _make_response()
        captured = []

        def get_response(req):
            captured.append(get_current_user())
            return response

        middleware = AuditMiddleware(get_response)
        middleware(request)
        assert captured[0] is user

    def test_clears_thread_local_after_response(self):
        request = _make_request()
        response = _make_response()
        middleware = AuditMiddleware(lambda req: response)
        middleware(request)
        assert get_current_user() is None

    def test_clears_thread_local_on_exception(self):
        def get_response(req):
            raise ValueError('boom')

        middleware = AuditMiddleware(get_response)
        with pytest.raises(ValueError):
            middleware(_make_request())
        assert get_current_user() is None


@pytest.mark.django_db
class TestOrganisationMiddleware:
    def test_attaches_org_for_authenticated_user(self):
        profile = UserProfileFactory()
        user = profile.user
        user.is_authenticated = True
        request = _make_request(user=user)
        response = _make_response()
        middleware = OrganisationMiddleware(lambda req: response)
        middleware(request)
        assert request.org == profile.organisation

    def test_org_is_none_for_anonymous(self):
        user = MagicMock()
        user.is_authenticated = False
        request = _make_request(user=user)
        middleware = OrganisationMiddleware(lambda req: _make_response())
        middleware(request)
        assert request.org is None

    def test_org_is_none_when_no_profile(self):
        user = MagicMock()
        user.is_authenticated = True
        del user.profile
        type(user).profile = property(lambda self: (_ for _ in ()).throw(AttributeError()))
        request = _make_request(user=user)
        middleware = OrganisationMiddleware(lambda req: _make_response())
        middleware(request)
        assert request.org is None


class TestRequestLoggingMiddleware:
    def test_logs_request(self):
        request = _make_request()
        response = _make_response(status=200)

        with patch('apps.core.middleware.logger') as mock_logger:
            middleware = RequestLoggingMiddleware(lambda req: response)
            middleware(request)
            assert mock_logger.info.called
            call_args = mock_logger.info.call_args[0]
            assert 'GET' in call_args
            assert '/api/test/' in call_args
            assert 200 in call_args

    def test_logs_non_200_status(self):
        request = _make_request()
        response = _make_response(status=404)

        with patch('apps.core.middleware.logger') as mock_logger:
            middleware = RequestLoggingMiddleware(lambda req: response)
            middleware(request)
            call_args = mock_logger.info.call_args[0]
            assert 404 in call_args
