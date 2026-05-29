import pytest
from unittest.mock import MagicMock

from apps.core.permissions import (
    Role,
    get_user_permissions,
    has_book_access,
    IsTrader,
    IsRiskManager,
    IsBackOffice,
)
from tests.factories import DeskFactory, OrganisationFactory, UserFactory, UserProfileFactory


def _make_user(role, with_desk=False):
    user = UserFactory.build()
    profile = MagicMock()
    profile.role = role
    profile.desk = DeskFactory.build() if with_desk else None
    profile.desk_id = profile.desk.id if profile.desk else None
    user.profile = profile
    return user


@pytest.mark.django_db
class TestGetUserPermissions:
    def test_admin_can_do_everything(self):
        user = UserProfileFactory(role=Role.ADMIN).user
        perms = get_user_permissions(user)
        assert all(perms.values())

    def test_trader_can_create_trade(self):
        user = UserProfileFactory(role=Role.TRADER).user
        perms = get_user_permissions(user)
        assert perms['can_create_trade'] is True
        assert perms['can_manage_users'] is False

    def test_risk_manager_cannot_create_trade(self):
        user = UserProfileFactory(role=Role.RISK_MANAGER).user
        perms = get_user_permissions(user)
        assert perms['can_create_trade'] is False
        assert perms['can_manage_limits'] is True

    def test_read_only_minimal_permissions(self):
        user = UserProfileFactory(role=Role.READ_ONLY).user
        perms = get_user_permissions(user)
        assert perms['can_create_trade'] is False
        assert perms['can_view_reports'] is True

    def test_no_profile_returns_read_only(self):
        user = UserFactory()
        perms = get_user_permissions(user)
        assert perms['can_create_trade'] is False


@pytest.mark.django_db
class TestHasBookAccess:
    def test_admin_always_has_access(self):
        desk = DeskFactory()
        profile = UserProfileFactory(role=Role.ADMIN, desk=desk)
        book = MagicMock()
        book.desk_id = DeskFactory().id
        assert has_book_access(profile.user, book) is True

    def test_trader_on_same_desk_has_access(self):
        desk = DeskFactory()
        profile = UserProfileFactory(role=Role.TRADER, desk=desk)
        book = MagicMock()
        book.desk_id = desk.id
        assert has_book_access(profile.user, book) is True

    def test_trader_on_different_desk_no_access(self):
        desk1 = DeskFactory()
        desk2 = DeskFactory()
        profile = UserProfileFactory(role=Role.TRADER, desk=desk1)
        book = MagicMock()
        book.desk_id = desk2.id
        assert has_book_access(profile.user, book) is False


class TestDRFPermissions:
    def _make_request(self, role):
        request = MagicMock()
        profile = MagicMock()
        profile.role = role
        request.user.profile = profile
        return request

    def test_is_trader_allows_trader(self):
        perm = IsTrader()
        assert perm.has_permission(self._make_request(Role.TRADER), None) is True

    def test_is_trader_allows_admin(self):
        perm = IsTrader()
        assert perm.has_permission(self._make_request(Role.ADMIN), None) is True

    def test_is_trader_rejects_analyst(self):
        perm = IsTrader()
        assert perm.has_permission(self._make_request(Role.ANALYST), None) is False

    def test_is_risk_manager_allows_risk_manager(self):
        perm = IsRiskManager()
        assert perm.has_permission(self._make_request(Role.RISK_MANAGER), None) is True

    def test_is_back_office_allows_back_office(self):
        perm = IsBackOffice()
        assert perm.has_permission(self._make_request(Role.BACK_OFFICE), None) is True

    def test_no_profile_returns_false(self):
        perm = IsTrader()
        request = MagicMock()
        del request.user.profile
        type(request.user).profile = property(lambda self: (_ for _ in ()).throw(AttributeError()))
        assert perm.has_permission(request, None) is False
