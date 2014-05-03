from django.db import models
from ditchlib.UnitTimestamp import UnixTimestampField

# Create your models here.

class LevelLog(models.Model):
    timestamp       = models.DateTimeField()
    ditchlvl        = models.SmallIntegerField()
    sumplvl         = models.SmallIntegerField()
    ditch_inches    = models.FloatField()
    sump_inches     = models.FloatField()
    pump_on         = models.BooleanField()
    north_on        = models.BooleanField()
    south_on        = models.BooleanField()

    class Meta:
        db_table = 'level_log'






