from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Event, Participant, Registration

User = get_user_model()


class EventCRUDTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="admin12345", role=User.Role.ADMIN
        )
        self.viewer = User.objects.create_user(
            username="viewer", password="viewer12345", role=User.Role.VIEWER
        )
        self.event_data = {
            "title": "Django Conference",
            "description": "A conference about Django.",
            "date": (timezone.now() + timezone.timedelta(days=30)).isoformat(),
            "location": "Paris",
            "status": "planned",
        }

    def test_create_event_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(reverse("events:event_list"), self.event_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().created_by, self.admin)

    def test_viewer_cannot_create_event(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.post(reverse("events:event_list"), self.event_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_can_list_events(self):
        Event.objects.create(
            title="Test", date=timezone.now(), location="Paris", created_by=self.admin
        )
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(reverse("events:event_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_update_event(self):
        self.client.force_authenticate(user=self.admin)
        event = Event.objects.create(
            title="Old Title",
            date=timezone.now() + timezone.timedelta(days=10),
            location="Paris",
            created_by=self.admin,
        )
        response = self.client.patch(
            reverse("events:event_detail", args=[event.pk]),
            {"title": "New Title"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        self.assertEqual(event.title, "New Title")

    def test_delete_event(self):
        self.client.force_authenticate(user=self.admin)
        event = Event.objects.create(
            title="To Delete",
            date=timezone.now(),
            location="Lyon",
            created_by=self.admin,
        )
        response = self.client.delete(reverse("events:event_detail", args=[event.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), 0)

    def test_filter_events_by_status(self):
        self.client.force_authenticate(user=self.admin)
        Event.objects.create(
            title="Planned", date=timezone.now(), location="A", status="planned"
        )
        Event.objects.create(
            title="Completed", date=timezone.now(), location="B", status="completed"
        )
        response = self.client.get(reverse("events:event_list"), {"status": "planned"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Planned")

    def test_update_event_with_past_date_rejected(self):
        self.client.force_authenticate(user=self.admin)
        event = Event.objects.create(
            title="Future Event",
            date=timezone.now() + timezone.timedelta(days=10),
            location="Paris",
            created_by=self.admin,
        )
        past_date = (timezone.now() - timezone.timedelta(days=5)).isoformat()
        response = self.client.patch(
            reverse("events:event_detail", args=[event.pk]),
            {"date": past_date},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_response_has_uniform_format(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(reverse("events:event_list"), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data["error"])
        self.assertEqual(response.data["status_code"], 400)
        self.assertIn("message", response.data)

    def test_unauthenticated_cannot_access(self):
        response = self.client.get(reverse("events:event_list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ParticipantCRUDTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="admin12345", role=User.Role.ADMIN
        )
        self.viewer = User.objects.create_user(
            username="viewer", password="viewer12345", role=User.Role.VIEWER
        )

    def test_create_participant(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("events:participant_list"),
            {
                "first_name": "Alice",
                "last_name": "Dupont",
                "email": "alice@example.com",
                "phone": "+33612345678",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Participant.objects.count(), 1)

    def test_viewer_can_list_participants(self):
        Participant.objects.create(
            first_name="Bob", last_name="Martin", email="bob@example.com"
        )
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(reverse("events:participant_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_viewer_cannot_create_participant(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.post(
            reverse("events:participant_list"),
            {"first_name": "X", "last_name": "Y", "email": "x@y.com"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_email_rejected(self):
        self.client.force_authenticate(user=self.admin)
        Participant.objects.create(
            first_name="A", last_name="B", email="dup@example.com"
        )
        response = self.client.post(
            reverse("events:participant_list"),
            {"first_name": "C", "last_name": "D", "email": "dup@example.com"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_participant(self):
        self.client.force_authenticate(user=self.admin)
        p = Participant.objects.create(
            first_name="Old", last_name="Name", email="old@example.com"
        )
        response = self.client.patch(
            reverse("events:participant_detail", args=[p.pk]),
            {"first_name": "New"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        p.refresh_from_db()
        self.assertEqual(p.first_name, "New")

    def test_delete_participant(self):
        self.client.force_authenticate(user=self.admin)
        p = Participant.objects.create(
            first_name="Del", last_name="Me", email="del@example.com"
        )
        response = self.client.delete(
            reverse("events:participant_detail", args=[p.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class RegistrationTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="admin12345", role=User.Role.ADMIN
        )
        self.viewer = User.objects.create_user(
            username="viewer", password="viewer12345", role=User.Role.VIEWER
        )
        self.event = Event.objects.create(
            title="Test Event",
            date=timezone.now() + timezone.timedelta(days=5),
            location="Paris",
            status="planned",
        )
        self.participant = Participant.objects.create(
            first_name="Alice", last_name="Dupont", email="alice@example.com"
        )

    def test_register_participant_to_event(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("events:registration_list"),
            {"event": self.event.pk, "participant": self.participant.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Registration.objects.count(), 1)

    def test_duplicate_registration_rejected(self):
        self.client.force_authenticate(user=self.admin)
        Registration.objects.create(event=self.event, participant=self.participant)
        response = self.client.post(
            reverse("events:registration_list"),
            {"event": self.event.pk, "participant": self.participant.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_to_cancelled_event_rejected(self):
        self.client.force_authenticate(user=self.admin)
        self.event.status = "cancelled"
        self.event.save()
        response = self.client.post(
            reverse("events:registration_list"),
            {"event": self.event.pk, "participant": self.participant.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_viewer_cannot_create_registration(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.post(
            reverse("events:registration_list"),
            {"event": self.event.pk, "participant": self.participant.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_can_list_registrations(self):
        Registration.objects.create(event=self.event, participant=self.participant)
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(reverse("events:registration_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_unregister_participant(self):
        self.client.force_authenticate(user=self.admin)
        reg = Registration.objects.create(
            event=self.event, participant=self.participant
        )
        response = self.client.delete(
            reverse("events:registration_detail", args=[reg.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Registration.objects.count(), 0)

    def test_event_detail_shows_registered_participants(self):
        self.client.force_authenticate(user=self.admin)
        Registration.objects.create(event=self.event, participant=self.participant)
        response = self.client.get(
            reverse("events:event_detail", args=[self.event.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["registered_participants"]), 1)
        self.assertEqual(
            response.data["registered_participants"][0]["email"],
            "alice@example.com",
        )


class DashboardTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="admin12345", role=User.Role.ADMIN
        )

    def test_dashboard_returns_stats(self):
        self.client.force_authenticate(user=self.admin)
        Event.objects.create(
            title="E1", date=timezone.now(), location="A", status="planned"
        )
        Participant.objects.create(
            first_name="P", last_name="1", email="p1@test.com"
        )
        response = self.client.get(reverse("events:dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_events"], 1)
        self.assertEqual(response.data["total_participants"], 1)
        self.assertIn("events_by_status", response.data)
        self.assertIn("upcoming_events", response.data)
