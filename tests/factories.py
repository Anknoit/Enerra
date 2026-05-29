import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.core.models import AuditLog, Currency, Organisation, UnitOfMeasure, UserProfile
from apps.portfolio.models import Desk

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    is_active = True


class CurrencyFactory(DjangoModelFactory):
    class Meta:
        model = Currency
        django_get_or_create = ['code']

    code = factory.Sequence(lambda n: f'C{n:02d}')
    name = factory.LazyAttribute(lambda o: f'Currency {o.code}')
    decimal_places = 2
    is_active = True


class OrganisationFactory(DjangoModelFactory):
    class Meta:
        model = Organisation

    name = factory.Sequence(lambda n: f'Organisation {n}')
    currency = factory.SubFactory(CurrencyFactory)
    timezone = 'UTC'
    regulatory_regime = 'EMIR'


class DeskFactory(DjangoModelFactory):
    class Meta:
        model = Desk

    name = factory.Sequence(lambda n: f'Desk {n}')
    is_active = True
    cost_centre = factory.Sequence(lambda n: f'CC{n:03d}')


class UnitOfMeasureFactory(DjangoModelFactory):
    class Meta:
        model = UnitOfMeasure
        django_get_or_create = ['symbol']

    symbol = factory.Sequence(lambda n: f'UOM{n}')
    name = factory.LazyAttribute(lambda o: f'Unit {o.symbol}')
    commodity_type = 'POWER'
    conversion_factor_to_base = factory.LazyFunction(lambda: __import__('decimal').Decimal('1.0'))


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    organisation = factory.SubFactory(OrganisationFactory)
    desk = None
    role = 'READ_ONLY'
    timezone = 'UTC'


class AuditLogFactory(DjangoModelFactory):
    class Meta:
        model = AuditLog

    action = AuditLog.ACTION_CREATE
    model_name = 'Trade'
    object_id = factory.Sequence(lambda n: str(n))
    user = factory.SubFactory(UserFactory)
