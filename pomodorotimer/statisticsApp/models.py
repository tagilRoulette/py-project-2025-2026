from django.db import models
from authUser.models import *


class Activity(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Activities'


class ActivityTime(models.Model):
    owner = models.ForeignKey(CustomUser, models.CASCADE)
    time_span = models.IntegerField()
    activity_type = models.ForeignKey(Activity, models.PROTECT)
    date = models.DateField()

    def __str__(self):
        return self.owner.username + ' ' + self.date.strftime(r'%d/%m/%Y')


class PomodoroTimings(models.Model):
    owner = models.ForeignKey(CustomUser, models.CASCADE)
    work_time = models.IntegerField(default=25)
    break_time = models.IntegerField(default=5)
    long_break_time = models.IntegerField(default=15)

    def __str__(self):
        return self.owner.username + "'s timer"

    class Meta:
        verbose_name = 'Pomodoro Timings'
        verbose_name_plural = 'Pomodoro Timings'
