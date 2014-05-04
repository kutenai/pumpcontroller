# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'LevelLog.timestamp'
        db.alter_column('level_log', 'timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

    def backwards(self, orm):

        # Changing field 'LevelLog.timestamp'
        db.alter_column('level_log', 'timestamp', self.gf('django.db.models.fields.DateTimeField')())

    models = {
        u'ditchmon.levellog': {
            'Meta': {'object_name': 'LevelLog', 'db_table': "'level_log'"},
            'ditch_inches': ('django.db.models.fields.FloatField', [], {}),
            'ditchlvl': ('django.db.models.fields.SmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'north_on': ('django.db.models.fields.BooleanField', [], {}),
            'pump_on': ('django.db.models.fields.BooleanField', [], {}),
            'south_on': ('django.db.models.fields.BooleanField', [], {}),
            'sump_inches': ('django.db.models.fields.FloatField', [], {}),
            'sumplvl': ('django.db.models.fields.SmallIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ditchmon']