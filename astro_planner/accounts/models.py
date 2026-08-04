from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone

AVAILABLE_LANGS = [
    ('uk', 'Ukrainian'),
    ('en', 'English')
]


class CustomUserManager(BaseUserManager):
    def create_user(
        self, cell_phone, email, first_name, password=None, **extra_fields
    ):
        if not cell_phone:
            raise ValueError('Cell phone is required')
        if not email:
            raise ValueError('Email is required')
        if not first_name:
            raise ValueError('First name is required')
        email = self.normalize_email(email)
        user = self.model(
            cell_phone=cell_phone,
            email=email,
            first_name=first_name,
            **extra_fields,
        )
        user.set_password(password)
        user.save()
        AstroUserProfile.objects.create(user=user)
        return user

    def create_superuser(
        self, cell_phone, email, first_name, password=None, **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(
            cell_phone,
            email,
            first_name,
            password,
            **extra_fields
        )


class AstroUser(AbstractBaseUser, PermissionsMixin):
    cell_phone = models.CharField('Cell phone', max_length=10, unique=True)
    email = models.EmailField('Email', unique=True)
    date_of_birth = models.DateField('Date of birth', null=True, blank=True)
    first_name = models.CharField('First name', max_length=30, blank=True)
    last_name = models.CharField('Last name', max_length=50, blank=True)
    is_staff = models.BooleanField('Is staff', default=False)
    is_active = models.BooleanField('Is active', default=True)
    date_joined = models.DateTimeField(
        'Date of account creation',
        default=timezone.now,
    )
    preffered_lang = models.CharField(
        'Language',
        max_length=5,
        choices=AVAILABLE_LANGS,
        default='uk',
    )

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'cell_phone'
    REQUIRED_FIELDS = ['email', 'first_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return self.email


GENDER_TYPES = [
    ('N', 'Prefer not to say'),
    ('M', 'Male'),
    ('F', 'Female'),
]
ZODIAC_CHOICES = [
    ('aries', 'Aries ♈'),
    ('taurus', 'Taurus ♉'),
    ('gemini', 'Gemini ♊'),
    ('cancer', 'Cancer ♋'),
    ('leo', 'Leo ♌'),
    ('virgo', 'Virgo ♍'),
    ('libra', 'Libra ♎'),
    ('scorpio', 'Scorpio ♏'),
    ('sagittarius', 'Sagittarius ♐'),
    ('capricorn', 'Capricorn ♑'),
    ('aquarius', 'Aquarius ♒'),
    ('pisces', 'Pisces ♓'),
    ('unknown', 'Not defined yet')
]


class AstroUserProfile(models.Model):
    user = models.OneToOneField(
        AstroUser,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    notifications_enabled = models.BooleanField(
        'Are notifications enabled',
        default=True,
    )
    gender = models.CharField('Gender', choices=GENDER_TYPES, default='N')
    sun_sign = models.CharField(
        'Sun Sign', max_length=15, choices=ZODIAC_CHOICES, default='unknown'
    )
    moon_sign = models.CharField(
        'Moon Sign', max_length=15, choices=ZODIAC_CHOICES, default='unknown'
    )
    asc_sign = models.CharField(
        'Ascendant Sign',
        max_length=15,
        choices=ZODIAC_CHOICES,
        default='unknown'
    )

    class Meta:
        verbose_name = 'UserProfile'
        verbose_name_plural = 'UserProfiles'

    def __str__(self) -> str:
        return f'Profile for {self.user.cell_phone} \
            with Sun Sign "{self.sun_sign}"'
