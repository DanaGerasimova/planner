from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView
)
from forecasts.forms import (
    ForecastPreferenceCreateForm, ForecastPreferenceUpdateForm
)
from forecasts.models import ForecastPreference
from django.http import FileResponse, Http404, HttpResponseForbidden
from forecasts.tasks import created_forecast_file, create_forecast_schedule
from django_celery_beat.models import PeriodicTask


class PermissionCheckMixin(PermissionRequiredMixin):
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return HttpResponseForbidden('You should log in!')
        return HttpResponseForbidden('You have no permissions!')


class OwnForecastQuerysetMixin:
    def get_queryset(self):
        return ForecastPreference.objects.filter(user=self.request.user)


class ForcastPreferenceListView(
    PermissionCheckMixin,
    OwnForecastQuerysetMixin,
    ListView
):
    model = ForecastPreference
    template_name = 'forecast_preference_list.html'
    context_object_name = 'forecasts'

    permission_required = 'forecasts.view_forecastpreference'


class ForcastPreferenceDetailView(
    PermissionCheckMixin,
    OwnForecastQuerysetMixin,
    DetailView
):
    model = ForecastPreference
    template_name = 'forecast_preference_form_update.html'
    context_object_name = 'forecast'
    pk_url_kwarg = 'forecast_preference_id'

    permission_required = 'forecasts.view_forecastpreference'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ForecastPreferenceUpdateForm(
            user=self.request.user,
            instance=self.object
        )
        return context


class ForcastPreferenceDownloadDetailView(
    PermissionCheckMixin,
    OwnForecastQuerysetMixin,
    DetailView
):
    model = ForecastPreference
    pk_url_kwarg = 'forecast_preference_id'

    permission_required = 'forecasts.view_forecastpreference'

    def get(self, request, *args, **kwargs):
        forecast = self.get_object()

        if not forecast.forecast_file:
            raise Http404('Forecast file does not exist')

        return FileResponse(
            forecast.forecast_file.open('rb'),
            as_attachment=True,
            filename=f'forecast_{forecast.id}.txt'
        )


class ForcastPreferenceCreateView(PermissionCheckMixin, CreateView):
    form_class = ForecastPreferenceCreateForm
    model = ForecastPreference
    template_name = 'forecast_preference_form_create.html'
    success_url = reverse_lazy('all_forecast_preferences')

    permission_required = 'forecasts.add_forecastpreference'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        created_forecast_file.delay(self.object.pk)
        create_forecast_schedule(self.object)
        return response


class ForcastPreferenceUpdateView(
    PermissionCheckMixin,
    OwnForecastQuerysetMixin,
    UpdateView
):
    model = ForecastPreference
    template_name = 'forecast_preference_form_update.html'
    form_class = ForecastPreferenceUpdateForm
    pk_url_kwarg = 'forecast_preference_id'
    success_url = reverse_lazy('all_forecast_preferences')
    context_object_name = 'forecast'

    permission_required = 'forecasts.change_forecastpreference'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        created_forecast_file.delay(self.object.pk)
        create_forecast_schedule(self.object)
        return response


class ForcastPreferenceDeleteView(
    PermissionCheckMixin,
    OwnForecastQuerysetMixin,
    DeleteView
):
    model = ForecastPreference
    success_url = reverse_lazy('all_forecast_preferences')
    pk_url_kwarg = 'forecast_preference_id'
    context_object_name = 'forecast'

    permission_required = 'forecasts.delete_forecastpreference'

    def form_valid(self, form):
        PeriodicTask.objects.filter(name=f'forecast_{self.object.pk}').delete()
        return super().form_valid(form)
