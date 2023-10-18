ACTIVITY_COLORS_DICT = {
            "Unplanned/illegal hunting": "#FF5252",
            "Planned euthanasia": "rgb(83 83 84)",
            "Unplanned/natural deaths": "#75B37A",
            "Planned hunt/cull": "#282829",
            "Planned translocation": "#F9A95D",
            "Base population": "rgb(212 212 212)"
        }

YEAR_DATA_LIMIT = 10

REGIONAL_DATA_CONSUMER = 'Regional data consumer'
NATIONAL_DATA_CONSUMER = 'National data consumer'

REGIONAL_DATA_SCIENTIST = 'Regional data scientist'
NATIONAL_DATA_SCIENTIST = 'National data scientist'

ORGANISATION_MEMBER = 'Organisation member'
ORGANISATION_MANAGER = 'Organisation manager'

SUPER_USER = 'Super user'


DATA_CONTRIBUTORS = [
    ORGANISATION_MEMBER,
    ORGANISATION_MANAGER,
]

DATA_CONSUMERS = [
    NATIONAL_DATA_CONSUMER,
    REGIONAL_DATA_CONSUMER
]

DATA_SCIENTISTS = [
    NATIONAL_DATA_SCIENTIST,
    REGIONAL_DATA_SCIENTIST,
    SUPER_USER
]
