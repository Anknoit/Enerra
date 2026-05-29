import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
    )


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user, db):
    from tests.factories import OrganisationFactory, UserProfileFactory
    org = OrganisationFactory()
    UserProfileFactory(user=user, organisation=org, role='TRADER')
    api_client.force_authenticate(user=user)
    return api_client
