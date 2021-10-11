from datetime import date, datetime

from django.forms.widgets import DateTimeInput
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import RSVP, Event


class IndexView(generic.ListView):
    template_name = "events/index.html"
    context_object_name = "events"

    def get_queryset(self):
        """Return the 10 upcoming events."""
        return Event.objects.filter(start_time__gte=date.today()).order_by("start_time")[:10]


class DetailView(generic.DetailView):
    model = Event
    template_name = "events/detail.html"


class CreateRSVPView(generic.CreateView):
    model = RSVP
    fields = ["name"]

    def form_valid(self, form):
        form.instance.event_id = self.kwargs["event_id"]
        return super().form_valid(form)

    def get_success_url(self):
        event_id = self.kwargs["event_id"]
        rsvp_id = self.object.id
        # Store the rsvp_id in the session with the event_id as the key so we know we've RSVP'd
        self.request.session[str(event_id)] = str(rsvp_id)
        # Redirect back to the event detail page
        return reverse("events:detail", kwargs={"pk": event_id})


class CreateEventView(generic.CreateView):
    model = Event
    fields = "__all__"

    def get_form(self):
        form = super(CreateEventView, self).get_form()
        form.fields["start_time"].widget = DateTimeInput(attrs={"type": "datetime-local"})
        form.fields["end_time"].widget = DateTimeInput(attrs={"type": "datetime-local"})
        return form

    def get_success_url(self):
        return reverse("events:detail", kwargs={"pk": self.object.id})