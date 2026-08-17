from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.views.generic import DetailView, FormView, ListView
from accounts.models import AstroUser
from accounts.forms import AstroUserPermissionsForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden


class TargetUserMixin:
    def get_target_user(self):
        return get_object_or_404(AstroUser, id=self.kwargs.get('user_id'))


class PermissionCheckMixin(UserPassesTestMixin):
    required_permission = None

    def test_func(self) -> bool:
        return self.request.user.has_perm(self.required_permission)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return HttpResponseForbidden('You should log in!')
        return HttpResponseForbidden('You have no permissions!')


class AstroUserListView(ListView):
    model = AstroUser
    template_name = 'user_list.html'
    context_object_name = 'users'


class AstroUserView(
    LoginRequiredMixin,
    PermissionCheckMixin,
    TargetUserMixin,
    DetailView
):
    model = AstroUser
    template_name = 'user_permissions_list.html'
    pk_url_kwarg = 'user_id'
    context_object_name = 'user'

    required_permission = 'accounts.view_all_permissions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        permissions_view = AstroUserPermissionsForm(
            user=self.get_target_user(),
            manager=self.request.user
        )
        context['astrouserpermissions'] = permissions_view
        return context


class PermissionsManagementService:
    @staticmethod
    def update_user_permissions(user, permission_ids):
        user.user_permissions.clear()
        selected_permissions = Permission.objects.filter(id__in=permission_ids)
        user.user_permissions.set(selected_permissions)


class AstroUserPermissionsUpdateView(
    LoginRequiredMixin,
    PermissionCheckMixin,
    TargetUserMixin,
    FormView
):
    form_class = AstroUserPermissionsForm
    template_name = 'user_permissions_list.html'

    required_permission = 'accounts.manage_all_permissions'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.get_target_user()
        kwargs['manager'] = self.request.user
        return kwargs

    def form_valid(self, form):
        selected_permission_ids = form.cleaned_data['permissions']
        user = self.get_target_user()
        PermissionsManagementService.update_user_permissions(
            user, selected_permission_ids
        )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'user_permissions_list',
            kwargs={'user_id': self.kwargs['user_id']},
        )
