from django.contrib import admin
from .models import AuditLog, Currency, Organisation, UnitOfMeasure, UserProfile


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'decimal_places', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ['name', 'currency', 'timezone', 'regulatory_regime']
    search_fields = ['name']


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'commodity_type', 'conversion_factor_to_base']
    list_filter = ['commodity_type']
    search_fields = ['symbol', 'name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'organisation', 'role', 'desk', 'timezone']
    list_filter = ['role', 'organisation']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user', 'organisation', 'desk']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'model_name', 'object_id', 'user', 'timestamp']
    list_filter = ['action', 'model_name']
    search_fields = ['model_name', 'object_id', 'user__username']
    readonly_fields = ['action', 'model_name', 'object_id', 'user', 'timestamp', 'before_json', 'after_json']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
