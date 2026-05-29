from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import BasePermission


class Role:
    TRADER = 'TRADER'
    RISK_MANAGER = 'RISK_MANAGER'
    SCHEDULER = 'SCHEDULER'
    BACK_OFFICE = 'BACK_OFFICE'
    ANALYST = 'ANALYST'
    ADMIN = 'ADMIN'
    READ_ONLY = 'READ_ONLY'

    ALL = [TRADER, RISK_MANAGER, SCHEDULER, BACK_OFFICE, ANALYST, ADMIN, READ_ONLY]


_ROLE_PERMISSIONS: dict[str, dict[str, bool]] = {
    Role.ADMIN: {
        'can_create_trade': True,
        'can_amend_trade': True,
        'can_cancel_trade': True,
        'can_confirm_trade': True,
        'can_view_risk': True,
        'can_approve_limits': True,
        'can_manage_limits': True,
        'can_view_settlements': True,
        'can_approve_invoices': True,
        'can_view_credit': True,
        'can_approve_margin': True,
        'can_manage_users': True,
        'can_view_audit': True,
        'can_submit_nominations': True,
        'can_view_reports': True,
        'can_submit_reports': True,
    },
    Role.TRADER: {
        'can_create_trade': True,
        'can_amend_trade': True,
        'can_cancel_trade': True,
        'can_confirm_trade': False,
        'can_view_risk': True,
        'can_approve_limits': False,
        'can_manage_limits': False,
        'can_view_settlements': True,
        'can_approve_invoices': False,
        'can_view_credit': True,
        'can_approve_margin': False,
        'can_manage_users': False,
        'can_view_audit': False,
        'can_submit_nominations': False,
        'can_view_reports': True,
        'can_submit_reports': False,
    },
    Role.RISK_MANAGER: {
        'can_create_trade': False,
        'can_amend_trade': False,
        'can_cancel_trade': False,
        'can_confirm_trade': False,
        'can_view_risk': True,
        'can_approve_limits': True,
        'can_manage_limits': True,
        'can_view_settlements': True,
        'can_approve_invoices': False,
        'can_view_credit': True,
        'can_approve_margin': True,
        'can_manage_users': False,
        'can_view_audit': True,
        'can_submit_nominations': False,
        'can_view_reports': True,
        'can_submit_reports': False,
    },
    Role.BACK_OFFICE: {
        'can_create_trade': False,
        'can_amend_trade': False,
        'can_cancel_trade': False,
        'can_confirm_trade': True,
        'can_view_risk': True,
        'can_approve_limits': False,
        'can_manage_limits': False,
        'can_view_settlements': True,
        'can_approve_invoices': True,
        'can_view_credit': True,
        'can_approve_margin': False,
        'can_manage_users': False,
        'can_view_audit': True,
        'can_submit_nominations': False,
        'can_view_reports': True,
        'can_submit_reports': True,
    },
    Role.SCHEDULER: {
        'can_create_trade': False,
        'can_amend_trade': False,
        'can_cancel_trade': False,
        'can_confirm_trade': False,
        'can_view_risk': True,
        'can_approve_limits': False,
        'can_manage_limits': False,
        'can_view_settlements': True,
        'can_approve_invoices': False,
        'can_view_credit': False,
        'can_approve_margin': False,
        'can_manage_users': False,
        'can_view_audit': False,
        'can_submit_nominations': True,
        'can_view_reports': True,
        'can_submit_reports': False,
    },
    Role.ANALYST: {
        'can_create_trade': False,
        'can_amend_trade': False,
        'can_cancel_trade': False,
        'can_confirm_trade': False,
        'can_view_risk': True,
        'can_approve_limits': False,
        'can_manage_limits': False,
        'can_view_settlements': True,
        'can_approve_invoices': False,
        'can_view_credit': True,
        'can_approve_margin': False,
        'can_manage_users': False,
        'can_view_audit': True,
        'can_submit_nominations': False,
        'can_view_reports': True,
        'can_submit_reports': False,
    },
    Role.READ_ONLY: {
        'can_create_trade': False,
        'can_amend_trade': False,
        'can_cancel_trade': False,
        'can_confirm_trade': False,
        'can_view_risk': True,
        'can_approve_limits': False,
        'can_manage_limits': False,
        'can_view_settlements': True,
        'can_approve_invoices': False,
        'can_view_credit': False,
        'can_approve_margin': False,
        'can_manage_users': False,
        'can_view_audit': False,
        'can_submit_nominations': False,
        'can_view_reports': True,
        'can_submit_reports': False,
    },
}


def _get_role(user) -> str:
    try:
        return user.profile.role
    except AttributeError:
        return Role.READ_ONLY


def get_user_permissions(user) -> dict:
    role = _get_role(user)
    return _ROLE_PERMISSIONS.get(role, _ROLE_PERMISSIONS[Role.READ_ONLY])


def has_book_access(user, book) -> bool:
    try:
        profile = user.profile
    except AttributeError:
        return False
    if profile.role == Role.ADMIN:
        return True
    return profile.desk_id is not None and profile.desk_id == book.desk_id


def has_instrument_access(user, instrument) -> bool:
    try:
        profile = user.profile
    except AttributeError:
        return False
    if profile.role == Role.ADMIN:
        return True
    if profile.desk is None:
        return False
    desk_commodity_types = list(
        profile.desk.commodities.values_list('type', flat=True)
    )
    return instrument.commodity.type in desk_commodity_types


class RoleRequiredMixin(LoginRequiredMixin):
    required_roles: list[str] = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        role = _get_role(request.user)
        if role != Role.ADMIN and role not in self.required_roles:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


def role_required(roles: list[str]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            role = _get_role(request.user)
            if role != Role.ADMIN and role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class _RolePermission(BasePermission):
    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request, view):
        try:
            return request.user.profile.role in self.allowed_roles
        except AttributeError:
            return False


class IsTrader(_RolePermission):
    allowed_roles = (Role.TRADER, Role.ADMIN)


class IsRiskManager(_RolePermission):
    allowed_roles = (Role.RISK_MANAGER, Role.ADMIN)


class IsBackOffice(_RolePermission):
    allowed_roles = (Role.BACK_OFFICE, Role.ADMIN)
