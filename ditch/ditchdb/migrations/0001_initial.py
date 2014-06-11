# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DitchCal'
        db.create_table(u'ditchdb_ditchcal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ditch_slope', self.gf('django.db.models.fields.FloatField')()),
            ('ditch_scale', self.gf('django.db.models.fields.FloatField')()),
            ('sump_slope', self.gf('django.db.models.fields.FloatField')()),
            ('sump_scale', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'ditchdb', ['DitchCal'])

        # Adding model 'DitchLog'
        db.create_table(u'ditchdb_ditchlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('ditchlvl', self.gf('django.db.models.fields.IntegerField')()),
            ('sumplvl', self.gf('django.db.models.fields.IntegerField')()),
            ('pump_call', self.gf('django.db.models.fields.BooleanField')()),
            ('pump_on', self.gf('django.db.models.fields.BooleanField')()),
            ('north_call', self.gf('django.db.models.fields.BooleanField')()),
            ('north_on', self.gf('django.db.models.fields.BooleanField')()),
            ('south_call', self.gf('django.db.models.fields.BooleanField')()),
            ('south_on', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'ditchdb', ['DitchLog'])


    def backwards(self, orm):
        # Deleting model 'DitchCal'
        db.delete_table(u'ditchdb_ditchcal')

        # Deleting model 'DitchLog'
        db.delete_table(u'ditchdb_ditchlog')


    models = {
        u'ditchdb.ditchcal': {
            'Meta': {'object_name': 'DitchCal'},
            'ditch_scale': ('django.db.models.fields.FloatField', [], {}),
            'ditch_slope': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sump_scale': ('django.db.models.fields.FloatField', [], {}),
            'sump_slope': ('django.db.models.fields.FloatField', [], {})
        },
        u'ditchdb.ditchlog': {
            'Meta': {'object_name': 'DitchLog'},
            'ditchlvl': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'north_call': ('django.db.models.fields.BooleanField', [], {}),
            'north_on': ('django.db.models.fields.BooleanField', [], {}),
            'pump_call': ('django.db.models.fields.BooleanField', [], {}),
            'pump_on': ('django.db.models.fields.BooleanField', [], {}),
            'south_call': ('django.db.models.fields.BooleanField', [], {}),
            'south_on': ('django.db.models.fields.BooleanField', [], {}),
            'sumplvl': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['ditchdb']