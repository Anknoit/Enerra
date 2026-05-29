import uuid
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('portfolio', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Currency first — Organisation FKs to it
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(max_length=3, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('decimal_places', models.PositiveSmallIntegerField(default=2)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name_plural': 'currencies',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('timezone', models.CharField(default='UTC', max_length=50)),
                ('regulatory_regime', models.CharField(
                    choices=[
                        ('EMIR', 'EMIR'),
                        ('REMIT', 'REMIT'),
                        ('CFTC', 'CFTC'),
                        ('MIFID', 'MiFID II'),
                        ('MULTIPLE', 'Multiple Regimes'),
                    ],
                    default='EMIR',
                    max_length=20,
                )),
                ('created_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('currency', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='organisations',
                    to='core.currency',
                )),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UnitOfMeasure',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('symbol', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('commodity_type', models.CharField(
                    choices=[
                        ('POWER', 'Power'),
                        ('GAS', 'Gas'),
                        ('OIL', 'Oil'),
                        ('LNG', 'LNG'),
                        ('EMISSIONS', 'Emissions'),
                    ],
                    max_length=20,
                )),
                ('conversion_factor_to_base', models.DecimalField(decimal_places=10, max_digits=20)),
                ('created_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'unit of measure',
                'verbose_name_plural': 'units of measure',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('role', models.CharField(
                    choices=[
                        ('TRADER', 'Trader'),
                        ('RISK_MANAGER', 'Risk Manager'),
                        ('SCHEDULER', 'Scheduler'),
                        ('BACK_OFFICE', 'Back Office'),
                        ('ANALYST', 'Analyst'),
                        ('ADMIN', 'Admin'),
                        ('READ_ONLY', 'Read Only'),
                    ],
                    default='READ_ONLY',
                    max_length=20,
                )),
                ('timezone', models.CharField(default='UTC', max_length=50)),
                ('api_key_hash', models.CharField(blank=True, max_length=128)),
                ('created_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('desk', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='members',
                    to='portfolio.desk',
                )),
                ('organisation', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='user_profiles',
                    to='core.organisation',
                )),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='profile',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(
                    choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete')],
                    max_length=10,
                )),
                ('model_name', models.CharField(max_length=100)),
                ('object_id', models.CharField(max_length=36)),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('before_json', models.JSONField(blank=True, null=True)),
                ('after_json', models.JSONField(blank=True, null=True)),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='audit_logs',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['model_name', 'object_id'], name='core_audit_model_obj_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['user', 'timestamp'], name='core_audit_user_ts_idx'),
        ),
    ]
