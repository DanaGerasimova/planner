from django import forms
from forecasts.models import ForecastPreference
from common.choices import ZODIAC_CHOICES


class ForecastPreferenceForm(forms.ModelForm):
    class Meta:
        model = ForecastPreference
        exclude = ['user', 'forecast_file']

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def get_profile_sign_values(self):
        if self.user:
            profile = self.user.astrouserprofile
            return [
                profile.sun_sign,
                profile.moon_sign,
                profile.asc_sign
            ]
        return []

    def get_profile_sign_choices(self):
        profile_signs = self.get_profile_sign_values()
        return [
            sign for sign in ZODIAC_CHOICES if sign[0] in profile_signs
            and sign[0] != 'unknown'
        ]

    def clean(self):
        cleaned_data = super().clean()

        sign = cleaned_data.get('sign')
        category = cleaned_data.get('category')
        forecast_type = cleaned_data.get('forecast_type')

        if self.user and sign and category and forecast_type:
            exists = ForecastPreference.objects.filter(
                user=self.user,
                sign=sign,
                category=category,
                forecast_type=forecast_type
            ).exclude(pk=self.instance.pk).exists()
            if exists:
                raise forms.ValidationError('This forecast already exists')
        return cleaned_data


class ForecastPreferenceCreateForm(ForecastPreferenceForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        profile_sign_choices = self.get_profile_sign_choices()

        if profile_sign_choices:
            self.fields['sign'].choices = profile_sign_choices
        else:
            self.fields['sign'].choices = [(
                '',
                'No zodiac signs selected in profile'
            )]
            self.fields['sign'].error_messages['required'] = (
                'Select a zodiac sign in your profile'
            )


class ForecastPreferenceUpdateForm(ForecastPreferenceForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        profile_sign_choices = self.get_profile_sign_choices()
        profile_sign_values = self.get_profile_sign_values()

        if self.instance.pk and self.instance.sign not in profile_sign_values:
            current_choice = (
                self.instance.sign,
                dict(ZODIAC_CHOICES)[self.instance.sign]
            )
            profile_sign_choices.append(current_choice)
        self.fields['sign'].choices = profile_sign_choices

    def clean(self):
        cleaned_data = super().clean()
        if (
            self.instance.pk
            and self.instance.sign not in self.get_profile_sign_values()
        ):
            raise forms.ValidationError(
                'Can not update forecast with deleted sign'
            )
        return cleaned_data
