import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    class Meta:
        abstract = True


class Currency(BaseModel):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    decimal_places = models.PositiveSmallIntegerField(default=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'currencies'
        ordering = ['code']

    def __str__(self):
        return self.code


class Organisation(BaseModel):
    REGULATORY_REGIME_CHOICES = [
        ('EMIR', 'EMIR'),
        ('REMIT', 'REMIT'),
        ('CFTC', 'CFTC'),
        ('MIFID', 'MiFID II'),
        ('MULTIPLE', 'Multiple Regimes'),
    ]

    name = models.CharField(max_length=255)
    currency = models.ForeignKey(
        'Currency',
        on_delete=models.PROTECT,
        related_name='organisations',
    )
    timezone = models.CharField(max_length=50, default='UTC')
    regulatory_regime = models.CharField(
        max_length=20,
        choices=REGULATORY_REGIME_CHOICES,
        default='EMIR',
    )

    def __str__(self):
        return self.name


class UnitOfMeasure(BaseModel):
    COMMODITY_TYPE_CHOICES = [
        ('POWER', 'Power'),
        ('GAS', 'Gas'),
        ('OIL', 'Oil'),
        ('LNG', 'LNG'),
        ('EMISSIONS', 'Emissions'),
    ]

    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    commodity_type = models.CharField(max_length=20, choices=COMMODITY_TYPE_CHOICES)
    conversion_factor_to_base = models.DecimalField(max_digits=20, decimal_places=10)

    class Meta:
        verbose_name = 'unit of measure'
        verbose_name_plural = 'units of measure'

    def __str__(self):
        return self.symbol


class UserProfile(BaseModel):
    ROLE_CHOICES = [
        ('TRADER', 'Trader'),
        ('RISK_MANAGER', 'Risk Manager'),
        ('SCHEDULER', 'Scheduler'),
        ('BACK_OFFICE', 'Back Office'),
        ('ANALYST', 'Analyst'),
        ('ADMIN', 'Admin'),
        ('READ_ONLY', 'Read Only'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    organisation = models.ForeignKey(
        'Organisation',
        on_delete=models.PROTECT,
        related_name='user_profiles',
    )
    desk = models.ForeignKey(
        'portfolio.Desk',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='members',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='READ_ONLY')
    timezone = models.CharField(max_length=50, default='UTC')
    api_key_hash = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class AuditLog(models.Model):
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    ACTION_CHOICES = [
        (ACTION_CREATE, 'Create'),
        (ACTION_UPDATE, 'Update'),
        (ACTION_DELETE, 'Delete'),
    ]

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=36)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    before_json = models.JSONField(null=True, blank=True)
    after_json = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.action} {self.model_name}({self.object_id}) at {self.timestamp}"
