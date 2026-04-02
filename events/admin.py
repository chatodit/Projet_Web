from django.contrib import admin

from .models import Event, Participant, Registration


class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = ("registered_at",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "location", "status", "get_participant_count", "created_by")
    list_filter = ("status", "date")
    search_fields = ("title", "location")
    inlines = [RegistrationInline]

    @admin.display(description="Participants")
    def get_participant_count(self, obj):
        return obj.registrations.count()


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone")
    search_fields = ("first_name", "last_name", "email")
    inlines = [RegistrationInline]


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("participant", "event", "registered_at")
    list_filter = ("event",)
    search_fields = ("participant__first_name", "participant__last_name", "event__title")
