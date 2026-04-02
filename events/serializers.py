from django.utils import timezone
from rest_framework import serializers

from .models import Event, Participant, Registration


# ──────────────────────────────────────────────
# Event
# ──────────────────────────────────────────────

class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for event lists."""

    participant_count = serializers.IntegerField(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "date",
            "location",
            "status",
            "participant_count",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "created_by")


class EventDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer including registered participants."""

    participant_count = serializers.IntegerField(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    registered_participants = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "date",
            "location",
            "status",
            "participant_count",
            "created_by",
            "registered_participants",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "created_by")

    def get_registered_participants(self, obj):
        registrations = obj.registrations.select_related("participant")
        return [
            {
                "registration_id": reg.id,
                "participant_id": reg.participant.id,
                "first_name": reg.participant.first_name,
                "last_name": reg.participant.last_name,
                "email": reg.participant.email,
                "registered_at": reg.registered_at,
            }
            for reg in registrations
        ]

    def validate_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "Event date cannot be in the past."
            )
        return value


# ──────────────────────────────────────────────
# Participant
# ──────────────────────────────────────────────

class ParticipantSerializer(serializers.ModelSerializer):
    registered_events = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "registered_events",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_registered_events(self, obj):
        registrations = obj.registrations.select_related("event")
        return [
            {
                "registration_id": reg.id,
                "event_id": reg.event.id,
                "title": reg.event.title,
                "date": reg.event.date,
                "status": reg.event.status,
                "registered_at": reg.registered_at,
            }
            for reg in registrations
        ]


# ──────────────────────────────────────────────
# Registration
# ──────────────────────────────────────────────

class RegistrationSerializer(serializers.ModelSerializer):
    participant_name = serializers.CharField(
        source="participant.__str__", read_only=True
    )
    event_title = serializers.CharField(source="event.title", read_only=True)

    class Meta:
        model = Registration
        fields = (
            "id",
            "event",
            "participant",
            "event_title",
            "participant_name",
            "registered_at",
        )
        read_only_fields = ("id", "registered_at")

    def validate(self, attrs):
        event = attrs["event"]
        participant = attrs["participant"]

        # Prevent registration to cancelled events
        if event.status == Event.Status.CANCELLED:
            raise serializers.ValidationError(
                "Cannot register for a cancelled event."
            )

        # Prevent duplicate registration (also enforced at DB level)
        if Registration.objects.filter(event=event, participant=participant).exists():
            raise serializers.ValidationError(
                "This participant is already registered for this event."
            )

        return attrs
