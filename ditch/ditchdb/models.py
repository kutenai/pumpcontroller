from django.db import models

# Create your models here.

class DitchCal(models.Model):
    """
    Calibration factors to use for converting sump and ditch
    measured values to actual values.
    """

    ditch_slope     = models.FloatField()
    ditch_scale     = models.FloatField()

    sump_slope      = models.FloatField()
    sump_scale      = models.FloatField()

class DitchLog(models.Model):
    timestamp       = models.DateTimeField()
    ditchlvl        = models.IntegerField()
    sumplvl         = models.IntegerField()
    pump_call       = models.BooleanField()
    pump_on         = models.BooleanField()

    north_call      = models.BooleanField()
    north_on        = models.BooleanField()

    south_call      = models.BooleanField()
    south_on        = models.BooleanField()



