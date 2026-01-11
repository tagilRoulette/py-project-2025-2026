from django.forms import *
from enum import StrEnum, auto
from datetime import date


class ActivityType(StrEnum):
    work = auto()
    s_break = auto()
    l_break = auto()


class ManualRecordEntryForm(Form):
    activities_choices = [
        (ActivityType.work, 'Work'),
        (ActivityType.s_break, 'Break'),
        (ActivityType.l_break, 'Long break'),
    ]
    input_time_formats = [
        r'%d/%m/%Y',
        r'%d.%m.%Y',
        r'%d-%m-%Y'
    ]

    activity_type = ChoiceField(
        widget=RadioSelect,
        choices=activities_choices,
        label='Type of activity',
    )

    time_span = IntegerField(
        label='Time spent in minutes',
    )

    date = DateField(
        input_formats=input_time_formats,
        required=False,
        initial=date.today(),
        label='Date of record'
    )


class ChangeTimingsForm(Form):
    work_time = IntegerField(label='Work time in minutes')
    break_time = IntegerField(label='Break time in minutes')
    long_break_time = IntegerField(label='Long break time in minutes')
