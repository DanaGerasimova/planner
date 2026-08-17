from django.urls import path
from accounts.views import (
    AstroUserListView,
    AstroUserView,
    AstroUserPermissionsUpdateView,
)

urlpatterns = [
    path('all/', AstroUserListView.as_view(), name='users_list'),
    path(
        'permissions/<int:user_id>',
        AstroUserView.as_view(),
        name='user_permissions_list'
    ),
    path(
        'permissions/<int:user_id>/update/',
        AstroUserPermissionsUpdateView.as_view(),
        name='update_permissions'
    ),
]
