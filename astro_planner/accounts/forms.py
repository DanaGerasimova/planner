from django import forms
from django.contrib.auth.models import Permission
from django.forms.widgets import CheckboxSelectMultiple
from accounts.models import AstroUser


class AstroUserPermissionsForm(forms.Form):
    permissions = forms.MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, user=None, manager=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.manager = manager
        all_permissions = Permission.objects.all()
        self.fields['permissions'].choices = [
            (permission.id, f'{permission.content_type} | {permission.codename} | {permission.name}')
            for permission in all_permissions
        ]
        if self.user:
            permission_ids = list(
                user.user_permissions.values_list('id', flat=True)
            )
            self.fields['permissions'].initial = permission_ids
        if not self.manager.has_perm('accounts.manage_all_permissions'):
            self.fields['permissions'].disabled = True


class AstroUserForm(forms.ModelForm):
    password_repeated = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput(),
        required=False
    )

    class Meta:
        model = AstroUser
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput()
        }

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if first_name and len(first_name) < 3:
            raise forms.ValidationError('Should be at least 3 chars long')
        return first_name

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_repeated = cleaned_data.get('password_repeated')

        if self.instance.pk is None:
            if not password or not password_repeated:
                raise forms.ValidationError('Both password fields are required')
            if password and password_repeated and password != password_repeated:
                raise forms.ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.pk is None:
            user.set_password(self.cleaned_data['password_repeated'])
        if commit:
            user.save()
        return user
