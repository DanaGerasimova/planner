from django.contrib import admin
from accounts.models import AstroUser, AstroUserProfile
from accounts.forms import AstroUserForm
from django.contrib.auth.models import Permission


class AstroUserProfileInline(admin.StackedInline):
    model = AstroUserProfile
    fields = [
        'gender', 'sun_sign', 'moon_sign', 'asc_sign', 'notifications_enabled'
    ]


class AstroUserAdmin(admin.ModelAdmin):
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
            'date_of_birth'
        ]
        if obj is None:
            return fields_1 + ['password_repeated'] + fields_2 + fields_3
        else:
            return fields_1 + fields_2 + ['date_joined'] + fields_3 + ['last_login', 'user_permissions']

    filter_horizontal = ('user_permissions',)

    def get_readonly_fields(self, request, obj):
        return ['date_joined', 'last_login', 'password'] if obj is not None else []

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        if not change:
            if not hasattr(form.instance, 'astrouserprofile'):
                AstroUserProfile.objects.create(user=form.instance)


admin.site.register(AstroUser, AstroUserAdmin)
admin.site.register(Permission)
