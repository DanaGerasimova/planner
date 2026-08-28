from django.contrib import admin
from accounts.models import AstroUser, AstroUserProfile
from accounts.forms import AstroUserForm
from django.contrib.auth.models import Permission
from forecasts.services.kerykeion_service import get_subject

UNKNOWN_SIGN = 'unknown'


class AstroUserProfileInline(admin.StackedInline):
    model = AstroUserProfile
    fields = [
        'gender', 'sun_sign', 'moon_sign', 'asc_sign', 'notifications_enabled'
    ]

    readonly_fields = ['sun_sign', 'moon_sign', 'asc_sign']


class AstroUserAdmin(admin.ModelAdmin):
    birth_data_set_for_recalculation = {
        'date_of_birth',
        'time_of_birth',
        'longitude',
        'latitude',
        'iana_timezone'
    }

    inlines = [AstroUserProfileInline]
    form = AstroUserForm

    def get_fields(self, request, obj):
        fields_1 = ['cell_phone', 'password']
        fields_2 = ['email', 'first_name', 'last_name']
        fields_3 = [
            'is_active',
            'is_staff',
            'is_superuser',
            'preffered_lang',
            'date_of_birth',
            'time_of_birth',
            'longitude',
            'latitude',
            'iana_timezone'
        ]
        if obj is None:
            return fields_1 + ['password_repeated'] + fields_2 + fields_3
        else:
            return fields_1 + fields_2 + ['date_joined'] + fields_3 + ['last_login', 'user_permissions']

    filter_horizontal = ('user_permissions',)

    def get_readonly_fields(self, request, obj):
        return ['date_joined', 'last_login', 'password'] if obj is not None else []

    def get_signs(self, user):
        if not user.date_of_birth:
            return UNKNOWN_SIGN, UNKNOWN_SIGN, UNKNOWN_SIGN

        subject = get_subject(user)
        asc_flag = all([
            user.time_of_birth,
            user.longitude,
            user.latitude,
            user.iana_timezone
        ])
        asc_sign = subject.ascendant.sign if asc_flag else UNKNOWN_SIGN

        return subject.sun.sign, subject.moon.sign, asc_sign

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)

        if not change or self.birth_data_set_for_recalculation.intersection(
            form.changed_data
        ):
            sun_sign, moon_sign, asc_sign = self.get_signs(form.instance)
            AstroUserProfile.objects.update_or_create(
                user=form.instance,
                defaults={
                    'sun_sign': sun_sign,
                    'moon_sign': moon_sign,
                    'asc_sign': asc_sign
                }
            )


admin.site.register(AstroUser, AstroUserAdmin)
admin.site.register(Permission)
