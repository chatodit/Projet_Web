from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters

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
