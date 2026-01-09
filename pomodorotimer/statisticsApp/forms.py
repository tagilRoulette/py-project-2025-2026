from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from enum import StrEnum, auto


class DateAggInterval(StrEnum):
    Daily = auto()
    Weekly = auto()
    Monthly = auto()


class ChangeTimeSpanForm(forms.Form):
    preset_date_agg_interval = [
        (DateAggInterval.Daily, 'Daily'),
        (DateAggInterval.Weekly, 'Weekly'),
        (DateAggInterval.Monthly, 'Monthly'),
    ]
    date_agg_interval = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=preset_date_agg_interval,
        label='Date aggregation interval'
    )

    input_time_formats = [
        r'%d/%m/%Y',
        r'%d.%m.%Y',
        r'%d-%m-%Y'
    ]
    start_date = forms.DateField(
        input_formats=input_time_formats, required=False)
    end_date = forms.DateField(
        input_formats=input_time_formats, required=False)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = date.today()
        if end_date < start_date:
            raise ValidationError({
                'end_date': 'End date can\'t be earlier than start date.'
            })

        return cleaned_data
