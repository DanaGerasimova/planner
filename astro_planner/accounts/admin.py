from django.contrib import admin
from accounts.models import AstroUser, AstroUserProfile


class AstroUserProfileInline(admin.StackedInline):
    model = AstroUserProfile
    fields = [
        'gender', 'sun_sign', 'moon_sign', 'asc_sign', 'notifications_enabled'
    ]


class AstroUserAdmin(admin.ModelAdmin):
    inlines = [AstroUserProfileInline]
    fields = ['cell_phone', 'password', 'email', 'first_name', 'last_name',
    'date_joined', 'is_active', 'is_staff', 'is_superuser', 'preffered_lang',
    'date_of_birth']
    readonly_fields = ['date_joined', 'last_login']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(obj.password)
     
        super().save_model(request, obj, form, change)

        if not change:
            AstroUserProfile.objects.create(user=obj)


admin.site.register(AstroUser, AstroUserAdmin)
