from django.test import TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from auth_app.models import User, Organisation
from datetime import timedelta

class TokenGenerationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            firstName='Test',
            lastName='User'
        )

    def test_token_generation(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token

        # Test for token expiration
        self.assertAlmostEqual(
            access_token['exp'] - access_token['iat'],
            timedelta(minutes=60).total_seconds(),
            delta=1  # Allowing 1 second difference because of any potential execution time
        )

        # Test for user detail in token
        self.assertEqual(access_token['user_id'], str(self.user.userId))


class OrganisationAccessTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='password1',
            firstName='User',
            lastName='One'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='password2',
            firstName='User',
            lastName='Two'
        )
        self.org1 = Organisation.objects.create(name="User One's Organisation")
        self.org1.users.add(self.user1)
        self.org2 = Organisation.objects.create(name="User Two's Organisation")
        self.org2.users.add(self.user2)

    def test_user_can_access_own_organisation(self):
        self.assertIn(self.org1, self.user1.organisations.all())
        self.assertNotIn(self.org2, self.user1.organisations.all())

    def test_user_cannot_access_other_organisation(self):
        self.assertNotIn(self.org1, self.user2.organisations.all())
        self.assertIn(self.org2, self.user2.organisations.all())