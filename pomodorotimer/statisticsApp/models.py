from django.db import models
from authUser.models import *


class Activity(models.Model):
    name = models.CharField(max_length=16)


class ActivityTime(models.Model):
    owner = models.ForeignKey(CustomUser, models.CASCADE)
    time_span = models.IntegerField()
    activity_type = models.ForeignKey(Activity, models.PROTECT)
    date = models.DateField()


class PomodoroTimings(models.Model):
    owner = models.ForeignKey(CustomUser, models.CASCADE)
    work_time = models.IntegerField()
    break_time = models.IntegerField()
    long_break_time = models.IntegerField()


class Sheet(models.Model):
    owner = models.ForeignKey(CustomUser, models.CASCADE, primary_key=True)
    url = models.CharField(max_length=128)
