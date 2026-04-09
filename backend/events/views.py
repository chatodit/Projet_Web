from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminOrEditor
from .filters import EventFilter
from .models import Event, Participant, Registration
from .serializers import (
    EventDetailSerializer,
    EventListSerializer,
    ParticipantSerializer,
    RegistrationSerializer,

)


# ──────────────────────────────────────────────
# Event views
# ──────────────────────────────────────────────

class EventListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/events/         → list all events (with filtering)
    POST /api/events/         → create a new event (admin/editor only)
    """

    queryset = (
        Event.objects.annotate(participant_count=Count("registrations"))
        .order_by("-date")
    )
    permission_classes = [IsAdminOrEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ["title", "location"]
    ordering_fields = ["date", "title", "created_at"]
    ordering = ["-date"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return EventDetailSerializer
        return EventListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/events/<id>/  → event detail with registered participants
    PUT    /api/events/<id>/  → update event (admin/editor only)
    DELETE /api/events/<id>/  → delete event (admin/editor only)
    """

    queryset = Event.objects.annotate(participant_count=Count("registrations"))
    serializer_class = EventDetailSerializer
    permission_classes = [IsAdminOrEditor]


# ──────────────────────────────────────────────
# Participant views
# ──────────────────────────────────────────────

class ParticipantListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/participants/       → list all participants
    POST /api/participants/       → create a participant (admin/editor only)
    """

    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    permission_classes = [IsAdminOrEditor]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["last_name", "created_at"]


class ParticipantDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/participants/<id>/  → participant detail with registered events
    PUT    /api/participants/<id>/  → update participant (admin/editor only)
    DELETE /api/participants/<id>/  → delete participant (admin/editor only)
    """

    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    permission_classes = [IsAdminOrEditor]


# ──────────────────────────────────────────────
# Registration views
# ──────────────────────────────────────────────

class RegistrationListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/registrations/       → list all registrations
    POST /api/registrations/       → register a participant to an event
    """

    queryset = Registration.objects.select_related("event", "participant")
    serializer_class = RegistrationSerializer
    permission_classes = [IsAdminOrEditor]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["event", "participant"]


class RegistrationDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/registrations/<id>/  → registration detail
    DELETE /api/registrations/<id>/  → unregister (admin/editor only)
    """

    queryset = Registration.objects.select_related("event", "participant")
    serializer_class = RegistrationSerializer
    permission_classes = [IsAdminOrEditor]


# ──────────────────────────────────────────────
# Self-registration (viewer)
# ──────────────────────────────────────────────

class EventRegisterView(APIView):
    """
    POST /api/events/<id>/register/
    Inscrit l'utilisateur connecté à l'événement en utilisant les données de son compte.
    Crée le Participant si l'email n'existe pas encore.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if event.status == Event.Status.CANCELLED:
            return Response(
                {"detail": "Impossible de s'inscrire à un événement annulé."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        participant, _ = Participant.objects.get_or_create(
            email=user.email,
            defaults={
                "first_name": user.first_name or user.username,
                "last_name":  user.last_name,
                "phone":      "",
            },
        )

        if Registration.objects.filter(event=event, participant=participant).exists():
            return Response(
                {"detail": "Vous êtes déjà inscrit à cet événement."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reg = Registration.objects.create(event=event, participant=participant)
        return Response(
            {"registration_id": reg.id, "message": "Inscription confirmée."},
            status=status.HTTP_201_CREATED,
        )


class EventUnregisterView(APIView):
    """
    DELETE /api/events/<id>/unregister/
    Permet à un utilisateur authentifié de se désinscrire d'un événement.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        registration_id = request.data.get("registration_id")
        if not registration_id:
            return Response(
                {"detail": "registration_id requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reg = get_object_or_404(Registration, pk=registration_id, event=event)
        reg.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ──────────────────────────────────────────────
# Dashboard view
# ──────────────────────────────────────────────

class DashboardView(generics.GenericAPIView):
    """Summary statistics for the dashboard."""

    permission_classes = [IsAdminOrEditor]

    def get(self, request):
        from rest_framework.response import Response

        return Response(
            {
                "total_events": Event.objects.count(),
                "total_participants": Participant.objects.count(),
                "total_registrations": Registration.objects.count(),
                "events_by_status": {
                    status: Event.objects.filter(status=status).count()
                    for status, _ in Event.Status.choices
                },
                "upcoming_events": EventListSerializer(
                    Event.objects.filter(status=Event.Status.PLANNED)
                    .annotate(participant_count=Count("registrations"))[:5],
                    many=True,
                ).data,
            }
        )
