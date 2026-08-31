ZODIAC_CHOICES = [
    ('Ari', 'Aries ♈'),
    ('Tau', 'Taurus ♉'),
    ('Gem', 'Gemini ♊'),
    ('Can', 'Cancer ♋'),
    ('Leo', 'Leo ♌'),
    ('Vir', 'Virgo ♍'),
    ('Lib', 'Libra ♎'),
    ('Sco', 'Scorpio ♏'),
    ('Sag', 'Sagittarius ♐'),
    ('Cap', 'Capricorn ♑'),
    ('Aqu', 'Aquarius ♒'),
    ('Pis', 'Pisces ♓'),
    ('unknown', 'Not defined yet')
]

ZODIAC_CHOICES_VALUES = [value for value, _ in ZODIAC_CHOICES]

CATEGORIES = [
    ('general', 'General'),
    ('career', 'Career'),
    ('relationships', 'Relationships'),
    ('finance', 'Finance')
]

CATEGORIES_VALUES = [value for value, _ in CATEGORIES]

FORECAST_TYPE = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly')
]

FORECAST_TYPE_VALUES = [value for value, _ in FORECAST_TYPE]
