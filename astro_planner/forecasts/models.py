from django.db import models
from accounts.models import AstroUser
from common.choices import (
    ZODIAC_CHOICES,
    CATEGORIES,
    FORECAST_TYPE,
    ZODIAC_CHOICES_VALUES,
    CATEGORIES_VALUES,
    FORECAST_TYPE_VALUES
)
from django.core.files.storage import storages


class ForecastPreference(models.Model):
    user = models.ForeignKey(
        AstroUser, on_delete=models.CASCADE, verbose_name='CustomUser'
    )
    sign = models.CharField(
        'Sign', max_length=15, choices=ZODIAC_CHOICES, default='unknown'
    )
    category = models.CharField(
        'Category', max_length=13, choices=CATEGORIES, default='general'
    )
    forecast_type = models.CharField(
        'Forecast Type', max_length=7, choices=FORECAST_TYPE, default='daily'
    )
    forecast_file = models.FileField(
        upload_to='forecasts/',
        storage=storages['default'],
        blank=True
    )

    def __str__(self) -> str:
        return f'{self.forecast_type} forecast for {self.user}: {self.get_sign_display()} about {self.category}'

    class Meta:
        verbose_name = 'Forecast Preference'
        verbose_name_plural = 'Forecast Preferences'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'sign', 'category', 'forecast_type'],
                name='unique_user_sign_category_forecast_type'
            ),
            models.CheckConstraint(
                condition=models.Q(
                    sign__in=ZODIAC_CHOICES_VALUES
                ),
                name='valid_zodiac_signs'
            ),
            models.CheckConstraint(
                condition=models.Q(
                    category__in=CATEGORIES_VALUES
                ),
                name='valid_categories'
            ),
            models.CheckConstraint(
                condition=models.Q(
                    forecast_type__in=FORECAST_TYPE_VALUES
                ),
                name='valid_forecast_type'
            )
        ]
