from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    # Events
    path("events/", views.EventListCreateView.as_view(), name="event_list"),
    path("events/<int:pk>/", views.EventDetailView.as_view(), name="event_detail"),
    # Participants
    path("participants/", views.ParticipantListCreateView.as_view(), name="participant_list"),
    path("participants/<int:pk>/", views.ParticipantDetailView.as_view(), name="participant_detail"),
    # Registrations
    path("registrations/", views.RegistrationListCreateView.as_view(), name="registration_list"),
    path("registrations/<int:pk>/", views.RegistrationDetailView.as_view(), name="registration_detail"),
    # Dashboard
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
]
