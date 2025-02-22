from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile
from .forms import UserProfileForm

class ProfilesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.profile = UserProfile.objects.get(user=self.user)

    def test_profile_creation(self):
        """Test profile is created automatically"""
        self.assertTrue(isinstance(self.profile, UserProfile))
        self.assertEqual(self.profile.user.username, 'testuser')

    def test_profile_str(self):
        """Test profile string representation"""
        self.assertEqual(str(self.profile), 'testuser')

    def test_profile_form_valid_data(self):
        """Test profile form with valid data"""
        form = UserProfileForm({
            'default_phone_number': '1234567890',
            'default_postcode': '12345',
            'default_town_or_city': 'Test City',
            'default_street_address1': 'Test Street',
            'default_street_address2': '',
            'default_county': 'Test County',
        })
        self.assertTrue(form.is_valid())

    def test_profile_view_get(self):
        """Test profile view GET request"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile.html')

    def test_profile_view_post(self):
        """Test profile view POST request"""
        response = self.client.post(reverse('profile'), {
            'default_phone_number': '1234567890',
            'default_postcode': '12345',
            'default_town_or_city': 'Test City',
            'default_street_address1': 'Test Street',
            'default_street_address2': '',
            'default_county': 'Test County',
        })
        self.assertEqual(response.status_code, 200)
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.default_phone_number, '1234567890')
