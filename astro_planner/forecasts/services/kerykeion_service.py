from kerykeion import (
    AstrologicalSubjectFactory, AspectsFactory, KerykeionException
)
from kerykeion.settings.config_constants import (
    ALL_ACTIVE_ASPECTS, ALL_ACTIVE_POINTS
)

MAJOR_ASPECTS_DICT = {
    'conjunction': {'rank': 1, 'temperament': 'choleric'},
    'trine': {'rank': 2, 'temperament': 'phlegmatic'},
    'opposition': {'rank': 3, 'temperament': 'melancholic'},
    'square': {'rank': 4, 'temperament': 'sanguine'}
}

# format: https://kerykeion.net/python-library/docs/v5/aspects
ACTIVE_ASPECTS = [
    {'name': 'conjunction', 'orb': 5},
    {'name': 'opposition', 'orb': 5},
    {'name': 'trine', 'orb': 2.3},
    {'name': 'square', 'orb': 1.54},
]

ACTIVE_POINTS = [
    'Sun',
    'Moon',
    'Mercury',
    'Uranus',
    'Venus',
    'Neptune',
    'Mars',
    'Pluto',
    'Jupiter',
    'Saturn'
]

PLANET_RANKING_DICT = {
    'sun': 1,
    'moon': 2,
    'mercury': 3,
    'uranus': 4,
    'venus': 5,
    'neptune': 6,
    'mars': 7,
    'pluto': 8,
    'jupiter': 9,
    'saturn': 10,
}


def get_subject(user):
    time_of_birth = user.time_of_birth
    hour = time_of_birth.hour if time_of_birth else 12
    minute = time_of_birth.minute if time_of_birth else 0
    longitude = user.longitude or -84.38798
    latitude = user.latitude or 33.7490
    iana_timezone = user.iana_timezone or 'America/New_York'

    try:
        subject = AstrologicalSubjectFactory.from_birth_data(
            name=user.first_name,
            year=user.date_of_birth.year,
            month=user.date_of_birth.month,
            day=user.date_of_birth.day,
            hour=hour,
            minute=minute,
            lng=float(longitude),
            lat=float(latitude),
            tz_str=iana_timezone,
            online=False
        )
        return subject
    except KerykeionException as e:
        print(f"Error calculating chart: {e}")
    # print(subject.sun.model_dump_json())
    # print(subject.first_house.model_dump_json())
    return None


def get_aspects(
    subject,
    active_points=ALL_ACTIVE_POINTS,
    active_aspects=ALL_ACTIVE_ASPECTS
):
    single_chart_result = AspectsFactory.single_chart_aspects(
        subject, active_points=active_points, active_aspects=active_aspects
    )
    return single_chart_result.aspects


def get_temperament(subject) -> tuple[str, list[str]]:
    """
    Calculate human temperament based on major aspects.

    Returns:
        Tuple:
            - Basic temperament.
            - A ranked list of temperaments for a multi-temperament. If only
            one temperament is present, it is considered a mono-temperament.
    """
    major_aspects = get_aspects(
        subject=subject,
        active_points=ACTIVE_POINTS,
        active_aspects=ACTIVE_ASPECTS
    )
    aspects_list = list(
        {major_aspect.aspect for major_aspect in major_aspects}
    )
    aspects_list.sort(
        key=lambda key: MAJOR_ASPECTS_DICT[key]['rank'], reverse=True
    )

    return (
        MAJOR_ASPECTS_DICT[aspects_list[0]]['temperament'],
        [
            MAJOR_ASPECTS_DICT[asp]['temperament']
            for asp in aspects_list
        ]
    )
