import pytest
from django.contrib.auth import get_user_model

from apps.core.models import AuditLog, Currency, Organisation, UnitOfMeasure, UserProfile
from tests.factories import (
    AuditLogFactory,
    CurrencyFactory,
    DeskFactory,
    OrganisationFactory,
    UnitOfMeasureFactory,
    UserFactory,
    UserProfileFactory,
)

User = get_user_model()


@pytest.mark.django_db
class TestCurrency:
    def test_str(self):
        c = CurrencyFactory(code='EUR')
        assert str(c) == 'EUR'

    def test_uuid_pk(self):
        c = CurrencyFactory()
        assert c.pk is not None
        assert len(str(c.pk)) == 36  # UUID format

    def test_defaults(self):
        c = CurrencyFactory()
        assert c.decimal_places == 2
        assert c.is_active is True


@pytest.mark.django_db
class TestOrganisation:
    def test_str(self):
        org = OrganisationFactory(name='Acme Energy')
        assert str(org) == 'Acme Energy'

    def test_currency_fk(self):
        ccy = CurrencyFactory(code='GBP')
        org = OrganisationFactory(currency=ccy)
        assert org.currency.code == 'GBP'

    def test_default_timezone(self):
        org = OrganisationFactory()
        assert org.timezone == 'UTC'


@pytest.mark.django_db
class TestUnitOfMeasure:
    def test_str(self):
        uom = UnitOfMeasureFactory(symbol='MWh')
        assert str(uom) == 'MWh'

    def test_commodity_type_choices(self):
        for ctype in ['POWER', 'GAS', 'OIL', 'LNG', 'EMISSIONS']:
            uom = UnitOfMeasureFactory(commodity_type=ctype)
            assert uom.commodity_type == ctype


@pytest.mark.django_db
class TestUserProfile:
    def test_str(self):
        profile = UserProfileFactory(role='TRADER')
        assert 'TRADER' in str(profile)

    def test_one_to_one_user(self):
        profile = UserProfileFactory()
        assert profile.user.profile == profile

    def test_desk_nullable(self):
        profile = UserProfileFactory(desk=None)
        assert profile.desk is None

    def test_desk_can_be_set(self):
        desk = DeskFactory()
        profile = UserProfileFactory(desk=desk)
        assert profile.desk == desk

    def test_default_role(self):
        profile = UserProfileFactory()
        assert profile.role == 'READ_ONLY'


@pytest.mark.django_db
class TestAuditLog:
    def test_str(self):
        log = AuditLogFactory(action=AuditLog.ACTION_CREATE, model_name='Trade')
        assert 'CREATE' in str(log)
        assert 'Trade' in str(log)

    def test_never_deleted_by_cascade(self):
        """AuditLog user FK is SET_NULL so deleting user preserves the log."""
        user = UserFactory()
        log = AuditLogFactory(user=user)
        log_id = log.id
        user.delete()
        surviving = AuditLog.objects.get(id=log_id)
        assert surviving.user is None

    def test_json_fields(self):
        log = AuditLogFactory(
            before_json={'price': '100.00'},
            after_json={'price': '105.00'},
        )
        assert log.before_json['price'] == '100.00'
        assert log.after_json['price'] == '105.00'
