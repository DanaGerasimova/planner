from django.core.management import CommandError
from django.core.management.base import BaseCommand
from forecasts.models import ForecastPreference
from django.contrib.auth import get_user_model
from accounts.models import AstroUserProfile
from common.choices import CATEGORIES_VALUES, FORECAST_TYPE_VALUES

LIST = 'list'
CREATE = 'create'
DELETE = 'delete'

ALLOWED_COMMANDS = [
    LIST, CREATE, DELETE
]

User = get_user_model()


class Command(BaseCommand):
    help = f'Manage forecasts with subcommands {', '.join(ALLOWED_COMMANDS)}'

    def add_arguments(self, parser):
        subparser = parser.add_subparsers(dest='subcommand', required=True)

        list_parser = subparser.add_parser(LIST, help='Get list of forecasts')
        list_parser.add_argument(
            '--user-id',
            type=int,
            dest='user_id',
            help='User ID'
        )
        list_parser.add_argument(
            '--category',
            type=str,
            choices=CATEGORIES_VALUES,
            help='Category'
        )
        list_parser.add_argument(
            '--type',
            type=str,
            choices=FORECAST_TYPE_VALUES,
            help='Forecast type'
        )

        create_parser = subparser.add_parser(CREATE, help='Create forecast')
        create_parser.add_argument(
            'user_id',
            type=int,
            help='Owner'
        )
        create_parser.add_argument(
            'category',
            type=str,
            choices=CATEGORIES_VALUES,
            help='Category of forecast'
        )
        create_parser.add_argument(
            'forecast_type',
            type=str,
            choices=FORECAST_TYPE_VALUES,
            help='Type of forecast'
        )

        delete_parser = subparser.add_parser(
            DELETE, help='Delete forecast by IDs'
        )
        delete_parser.add_argument(
            'forecast_ids',
            type=int,
            nargs='+',
            help='Forecast IDs for deletion'
        )

    def handle(self, *args, **options):
        subcommand = options.get('subcommand')

        if subcommand not in ALLOWED_COMMANDS:
            raise CommandError(f'Allowed only {', '.join(ALLOWED_COMMANDS)} \
            commands')
        
        if subcommand == LIST:
            self._handle_list(**options)
        if subcommand == CREATE:
            self._handle_create(**options)
        if subcommand == DELETE:
            self._handle_delete(**options)

    def _handle_list(self, *args, **options):
        forecasts = ForecastPreference.objects.all()

        user_id = options.get('user_id')
        category = options.get('category')
        forecast_type = options.get('type')

        if user_id:
            forecasts = forecasts.filter(user_id=user_id)

        if category:
            forecasts = forecasts.filter(category=category)

        if forecast_type:
            forecasts = forecasts.filter(forecast_type=forecast_type)

        if not forecasts:
            self.stdout.write(self.style.WARNING('No forecasts found'))
            return

        for forecast in forecasts:
            self.stdout.write(self.style.SUCCESS(f'Forecast: {forecast}'))

    def _handle_create(self, *args, **options):
        user_id = options.get('user_id')
        category = options.get('category')
        forecast_type = options.get('forecast_type')

        try:
            user = User.objects.get(id=user_id)
            profile = AstroUserProfile.objects.get(user=user)
        except (User.DoesNotExist, AstroUserProfile.DoesNotExist) as e:
            raise CommandError(f'The following error caused {e}')

        profile_signs = (
                profile.sun_sign, profile.moon_sign, profile.asc_sign
            )
        valid_profile_signs = {sign for sign in profile_signs if sign != 'unknown'}
        if not valid_profile_signs:
            self.stdout.write(self.style.WARNING('Signs are not defined yet'))
            return

        for profile_sign in valid_profile_signs:
            forecast, created = ForecastPreference.objects.get_or_create(
                user=user,
                sign=profile_sign,
                category=category,
                forecast_type=forecast_type
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Forecast {forecast} is created')
                )
            else:
                self.stdout.write(self.style.WARNING(
                    f'Forecast {forecast} already exists')
                )

    def _handle_delete(self, *args, **options):
        forecast_ids = options.get('forecast_ids')

        forecasts = ForecastPreference.objects.filter(id__in=forecast_ids)

        if not forecasts:
            self.stdout.write(self.style.WARNING('No forecasts to delete'))
            return

        self.stdout.write(self.style.SUCCESS('Deleted'))
        for forecast in forecasts:
            self.stdout.write(self.style.SUCCESS(f'Forecast {forecast}'))

        forecasts.delete()
