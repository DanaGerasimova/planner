import json
import os
from celery import shared_task
from django.db.models import QuerySet
from forecasts.models import ForecastPreference
from django.conf import settings
from google import genai
from dotenv import load_dotenv
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.utils import timezone
from datetime import timedelta
from django.core.files.base import ContentFile

load_dotenv()


def create_forecast_schedule(forecast_data: ForecastPreference):
    if forecast_data.forecast_type == 'daily':
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='10',
            day_of_week='*',
            day_of_month='*'
        )
    elif forecast_data.forecast_type == 'weekly':
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='10',
            day_of_week='1',
            day_of_month='*'
        )
    elif forecast_data.forecast_type == 'monthly':
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='10',
            day_of_week='*',
            day_of_month='1'
        )
    PeriodicTask.objects.update_or_create(
        name=f'forecast_{forecast_data.pk}',
        defaults={
            'crontab': schedule,
            'task': 'forecasts.tasks.created_forecast_file',
            'args': json.dumps([forecast_data.pk])
        }
    )


def prepare_forecast_context(forecast_data: ForecastPreference) -> str:
    def create_forecast_prompt(forecast_obj) -> str:
        local_date = timezone.localdate()

        if forecast_obj.forecast_type == 'daily':
            forecast_period = local_date.strftime('%d.%m.%Y')
        elif forecast_obj.forecast_type == 'weekly':
            forecast_period = f"from {local_date.strftime('%d.%m.%Y')} to {
                (local_date + timedelta(days=6)).strftime('%d.%m.%Y')
            }"
        elif forecast_obj.forecast_type == 'monthly':
            forecast_period = local_date.strftime('%B %Y')

        return f"""
            Generate an astrological forecast based on the following settings:

            Zodiac sign: {forecast_obj.sign}
            Gender: {forecast_obj.user.astrouserprofile.gender}
            Forecast type: {forecast_obj.forecast_type}
            Category: {forecast_obj.category}

            Requirements:
            - Start the forecast with the exact text:
            "Forecast for the period {forecast_period} {forecast_obj.get_sign_display()}".
            - Write the forecast for the specified zodiac sign and period.
            - Focus specifically on the selected category.
            - Take the gender into account when addressing the reader.
            - Make the forecast practical, clear, and natural.
            - Describe likely tendencies, opportunities, challenges, and
            useful advice.
            - Do not make absolute or guaranteed predictions.
            - Do not mention that you are an AI or language model.
            - Do not explain how the forecast was generated.
            - Do not include introductory phrases such as "Here is your
            forecast".
            - Return only the forecast text.
            - Length: 150-250 words.
            """

    try:
        if isinstance(forecast_data, ForecastPreference):
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            response = client.interactions.create(
                model="gemini-3.6-flash",
                input=create_forecast_prompt(forecast_data)
            )
            context_data = getattr(response, 'output_text', '') or ''
    except Exception:
        context_data = ''

    return context_data


@shared_task
def created_forecast_file(forecast_id: int):
    try:
        forecast = ForecastPreference.objects.get(pk=forecast_id)
    except ForecastPreference.DoesNotExist:
        return

    forecast_context = prepare_forecast_context(forecast)
    file_name = f'forecast_{forecast.id}_{timezone.now().strftime(
            '%Y-%m-%d_%H:%M'
        )}.txt'

    if forecast.forecast_file:
        forecast.forecast_file.delete(save=False)

    forecast.forecast_file.save(file_name, ContentFile(forecast_context))


def prepare_forecast_report_context(forecast_data: QuerySet) -> list:
    def fill_context(forecast_obj) -> dict:
        return {
            'id': forecast_obj.id,
            'user': forecast_obj.user.first_name,
            'sign': forecast_obj.get_sign_display()[
                :forecast_obj.get_sign_display().find(' ')
            ],
            'category': forecast_obj.get_category_display(),
            'forecast_type': forecast_obj.get_forecast_type_display()
        }

    return [
            fill_context(forecast) for forecast in forecast_data
        ]


@shared_task
def generate_forecasts_report():
    forecasts = ForecastPreference.objects.all()
    daily_forecasts = ForecastPreference.objects.filter(forecast_type='daily')
    weekly_forecasts = ForecastPreference.objects.filter(
        forecast_type='weekly'
    )
    monthly_forecasts = ForecastPreference.objects.filter(
        forecast_type='monthly'
    )
    report_context = {
        'total_forecasts': forecasts.count(),
        'daily': {
            'total': daily_forecasts.count(),
            'forecasts': prepare_forecast_report_context(daily_forecasts)
        },
        'weekly': {
            'total': weekly_forecasts.count(),
            'forecasts': prepare_forecast_report_context(weekly_forecasts)
        },
        'monthly': {
            'total': monthly_forecasts.count(),
            'forecasts': prepare_forecast_report_context(monthly_forecasts)
        }
    }
    output_path = os.path.join(
        settings.MEDIA_ROOT,
        'forecasts_report',
        f"forecasts_{timezone.now().strftime('%Y-%m-%d_%H:%M')}.json"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as report:
        json.dump(report_context, report, indent=4, ensure_ascii=True)
