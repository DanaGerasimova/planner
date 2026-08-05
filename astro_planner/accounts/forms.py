
from django import forms
from accounts.models import AstroUser


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
