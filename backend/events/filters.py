import django_filters

from .models import Event


class EventFilter(django_filters.FilterSet):
    """Filter events by date range and/or status."""

    date_from = django_filters.DateTimeFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateTimeFilter(field_name="date", lookup_expr="lte")
    status = django_filters.ChoiceFilter(choices=Event.Status.choices)

    class Meta:
        model = Event
        fields = ["status", "date_from", "date_to"]
