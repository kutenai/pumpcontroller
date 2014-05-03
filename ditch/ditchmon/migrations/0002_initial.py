# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LevelLog'
        db.create_table('level_log', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('ditchlvl', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('sumplvl', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('ditch_inches', self.gf('django.db.models.fields.FloatField')()),
            ('sump_inches', self.gf('django.db.models.fields.FloatField')()),
            ('pump_on', self.gf('django.db.models.fields.BooleanField')()),
            ('north_on', self.gf('django.db.models.fields.BooleanField')()),
            ('south_on', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'ditchmon', ['LevelLog'])


    def backwards(self, orm):
        # Deleting model 'LevelLog'
        db.delete_table('level_log')


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
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['ditchmon']