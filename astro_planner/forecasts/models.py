from django.db import models
from accounts.models import AstroUser
from common.choices import ZODIAC_CHOICES

CATEGORIES = [
    ('general', 'General'),
    ('career', 'Career'),
    ('relationships', 'Relationships'),
    ('finance', 'Finance')
]
FORECAST_TYPE = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly')
]


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

    def __str__(self) -> str:
        return f'{self.forecast_type} forecast for {self.user}'

    class Meta:
        verbose_name = 'Forecast Preference'
        verbose_name_plural = 'Forecast Preferences'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'sign', 'category', 'forecast_type'],
                name='unique_user_sign_category_forecast_type'
            )
        ]
