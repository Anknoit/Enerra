import logging
import threading
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import Optional, Any

from rest_framework.pagination import CursorPagination

logger = logging.getLogger(__name__)

_thread_locals = threading.local()


# ---------------------------------------------------------------------------
# Thread-local current user (set by AuditMiddleware)
# ---------------------------------------------------------------------------

def get_current_user():
    return getattr(_thread_locals, 'user', None)


def set_current_user(user) -> None:
    _thread_locals.user = user


# ---------------------------------------------------------------------------
# Trade reference generation
# ---------------------------------------------------------------------------

def generate_trade_ref(book, trade_date: date) -> str:
    """Generates unique trade reference: {book_code}-{YYYYMMDD}-{seq:04d}."""
    from apps.trade_capture.models import Trade  # lazy — avoids circular import

    book_code = ''.join(c for c in book.name.upper() if c.isalnum())[:8]
    date_str = trade_date.strftime('%Y%m%d')
    prefix = f"{book_code}-{date_str}-"
    existing_count = Trade.objects.filter(trade_ref__startswith=prefix).count()
    return f"{prefix}{existing_count + 1:04d}"


# ---------------------------------------------------------------------------
# Quantity & currency helpers
# ---------------------------------------------------------------------------

def round_to_lot(qty: Decimal, lot_size: Decimal) -> Decimal:
    if lot_size <= 0:
        return qty
    lots = (qty / lot_size).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return lots * lot_size


def convert_currency(amount: Decimal, from_ccy, to_ccy, as_of: date) -> Decimal:
    """FX conversion using stored fixing rates; triangulates via USD if needed."""
    from apps.market_data.models import FXRate  # lazy

    if from_ccy.code == to_ccy.code:
        return amount

    def _latest_rate(src, dst):
        return FXRate.objects.filter(
            from_ccy=src, to_ccy=dst, rate_date__lte=as_of
        ).latest('rate_date').rate

    try:
        return (amount * _latest_rate(from_ccy, to_ccy)).quantize(Decimal('0.000001'))
    except Exception:
        pass

    # Triangulate via USD
    try:
        from apps.core.models import Currency
        usd = Currency.objects.get(code='USD')
        to_usd = _latest_rate(from_ccy, usd)
        from_usd = _latest_rate(usd, to_ccy)
        return (amount * to_usd * from_usd).quantize(Decimal('0.000001'))
    except Exception:
        raise ValueError(
            f"No FX rate found for {from_ccy.code}/{to_ccy.code} on {as_of}"
        )


def convert_unit(qty: Decimal, from_uom, to_uom) -> Decimal:
    if from_uom.symbol == to_uom.symbol:
        return qty
    base_qty = qty * from_uom.conversion_factor_to_base
    return (base_qty / to_uom.conversion_factor_to_base).quantize(Decimal('0.000001'))


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

class StandardCursorPagination(CursorPagination):
    page_size = 50
    ordering = '-created_at'


def paginate_queryset(qs, request):
    paginator = StandardCursorPagination()
    return paginator.paginate_queryset(qs, request)


# ---------------------------------------------------------------------------
# Audit helpers
# ---------------------------------------------------------------------------

def _snapshot(instance) -> Optional[dict[str, Any]]:
    if instance is None:
        return None
    data: dict[str, Any] = {}
    for field in instance._meta.fields:
        value = getattr(instance, field.attname)
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        elif hasattr(value, 'hex'):  # UUID
            value = str(value)
        data[field.name] = value
    return data


def write_audit(action: str, instance, user=None):
    from apps.core.models import AuditLog

    if user is None:
        user = get_current_user()
    authenticated_user = user if (user and getattr(user, 'is_authenticated', False)) else None

    return AuditLog.objects.create(
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk),
        user=authenticated_user,
        before_json=None,
        after_json=_snapshot(instance),
    )


class AuditLogMixin:
    """Mixin for models that should be automatically tracked in AuditLog."""

    def save(self, *args, **kwargs):
        from apps.core.models import AuditLog

        is_new = self._state.adding
        before = None
        if not is_new:
            try:
                old = self.__class__.objects.get(pk=self.pk)
                before = _snapshot(old)
            except self.__class__.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        user = get_current_user()
        authenticated_user = user if (user and getattr(user, 'is_authenticated', False)) else None
        AuditLog.objects.create(
            action=AuditLog.ACTION_CREATE if is_new else AuditLog.ACTION_UPDATE,
            model_name=self.__class__.__name__,
            object_id=str(self.pk),
            user=authenticated_user,
            before_json=before,
            after_json=_snapshot(self),
        )

    def delete(self, *args, **kwargs):
        from apps.core.models import AuditLog

        before = _snapshot(self)
        user = get_current_user()
        authenticated_user = user if (user and getattr(user, 'is_authenticated', False)) else None
        pk_str = str(self.pk)
        result = super().delete(*args, **kwargs)
        AuditLog.objects.create(
            action=AuditLog.ACTION_DELETE,
            model_name=self.__class__.__name__,
            object_id=pk_str,
            user=authenticated_user,
            before_json=before,
            after_json=None,
        )
        return result


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def format_decimal(value: Optional[Decimal], places: int = 2) -> str:
    if value is None:
        return ''
    quantized = value.quantize(Decimal(10) ** -places)
    return f"{quantized:,.{places}f}"
