from django.urls import path
from forecasts.views import (
    ForcastPreferenceCreateView,
    ForcastPreferenceListView,
    ForcastPreferenceDetailView,
    ForcastPreferenceUpdateView,
    ForcastPreferenceDeleteView,
    ForcastPreferenceDownloadDetailView
)


urlpatterns = [
    path(
        'create/',
        ForcastPreferenceCreateView.as_view(),
        name='create_forecast_preference'
    ),
    path(
        'all/',
        ForcastPreferenceListView.as_view(),
        name='all_forecast_preferences'
    ),
    path(
        '<int:forecast_preference_id>/',
        ForcastPreferenceDetailView.as_view(),
        name='forecast_preference_detail'
    ),
    path(
        '<int:forecast_preference_id>/update/',
        ForcastPreferenceUpdateView.as_view(),
        name='forecast_preference_update'
    ),
    path(
        '<int:forecast_preference_id>/delete/',
        ForcastPreferenceDeleteView.as_view(),
        name='forecast_preference_delete'
    ),
    path(
        '<int:forecast_preference_id>/download/',
        ForcastPreferenceDownloadDetailView.as_view(),
        name='forecast_preference_download'
    ),
]
