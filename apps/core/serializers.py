from rest_framework import serializers
from .models import Currency, Organisation, UnitOfMeasure, UserProfile


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'decimal_places', 'is_active']


class OrganisationSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Organisation
        fields = ['id', 'name', 'currency', 'currency_id', 'timezone', 'regulatory_regime']


class UnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = ['id', 'symbol', 'name', 'commodity_type', 'conversion_factor_to_base']


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'organisation', 'desk', 'role', 'timezone']
        read_only_fields = ['id']
