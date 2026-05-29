from django.contrib import admin
from .models import Desk


@admin.register(Desk)
class DeskAdmin(admin.ModelAdmin):
    list_display = ['name', 'head_trader', 'cost_centre', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'cost_centre']
