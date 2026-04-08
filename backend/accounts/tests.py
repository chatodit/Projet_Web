from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationTests(APITestCase):
    """Test JWT login and token refresh."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_user",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.viewer = User.objects.create_user(
            username="viewer_user",
            password="viewerpass123",
            role=User.Role.VIEWER,
        )

    def test_login_returns_jwt_tokens(self):
        response = self.client.post(
            reverse("accounts:token_obtain"),
            {"username": "admin_user", "password": "adminpass123"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            reverse("accounts:token_obtain"),
            {"username": "admin_user", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        login = self.client.post(
            reverse("accounts:token_obtain"),
            {"username": "admin_user", "password": "adminpass123"},
        )
        response = self.client.post(
            reverse("accounts:token_refresh"),
            {"refresh": login.data["refresh"]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_logout_blacklists_refresh_token(self):
        login = self.client.post(
            reverse("accounts:token_obtain"),
            {"username": "admin_user", "password": "adminpass123"},
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("accounts:logout"),
            {"refresh": login.data["refresh"]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Refresh token should now be blacklisted
        response = self.client.post(
            reverse("accounts:token_refresh"),
            {"refresh": login.data["refresh"]},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_token_returns_400(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(reverse("accounts:logout"), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MeViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", role=User.Role.EDITOR
        )

    def test_me_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("accounts:me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["role"], "editor")

    def test_me_unauthenticated(self):
        response = self.client.get(reverse("accounts:me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RegisterViewTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_user", password="adminpass123", role=User.Role.ADMIN
        )
        self.viewer = User.objects.create_user(
            username="viewer_user", password="viewerpass123", role=User.Role.VIEWER
        )

    def test_admin_can_register_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "password": "newpass1234",
                "email": "new@example.com",
                "role": "editor",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_viewer_cannot_register_user(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser2",
                "password": "newpass1234",
                "email": "new2@example.com",
                "role": "viewer",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_register(self):
        response = self.client.post(
            reverse("accounts:register"),
            {"username": "anon", "password": "anonpass123"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", password="oldpass1234", role=User.Role.EDITOR
        )

    def test_change_password_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("accounts:change_password"),
            {"old_password": "oldpass1234", "new_password": "newpass5678"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass5678"))

    def test_change_password_wrong_old(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("accounts:change_password"),
            {"old_password": "wrongpass", "new_password": "newpass5678"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
