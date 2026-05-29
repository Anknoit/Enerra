from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CurrencyViewSet, UnitOfMeasureViewSet, UserProfileViewSet

router = DefaultRouter()
router.register('currencies', CurrencyViewSet, basename='currency')
router.register('units', UnitOfMeasureViewSet, basename='unit')
router.register('users', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('', include(router.urls)),
]
