# Create your views here.
from django.http import HttpResponse
from datetime import timedelta, tzinfo, datetime
from django.shortcuts import render_to_response

from models import LevelLog
from Ditch.DBConnection import DBConnection
from Ditch.DBDitch import DBDitch

def index(request,hours=2):
    start = datetime.now() - timedelta(hours=hours)
    entries = LevelLog.objects.filter(timestamp__gte=start)

    return render_to_response('ditchmon.html', {'entries' : entries})

def query(request,hours):

    start = datetime.now() - timedelta(hours=hours)
    entries = LevelLog.objects.filter(timestamp_gte=start)

    return render_to_response('ditchmon.html', {'entries' : entries})


def levels(request):
    start = datetime.now() - timedelta(days=21)
    entries = LevelLog.objects.filter(timestamp__minute=0)

    #conn = DBConnection()
    #dbTable = DBDitch(conn)

    #readings = dbTable.queryLastNReadings(1000)

    #print("Done. Retrieved %d records" % len(readings))

    x = [r.timestamp.strftime("%Y %m %d %H:%M") for r in entries]
    y = [r.ditch_inches for r in entries]

    return render_to_response('ditchlevels.html', {'readings' : {'x' : x, 'y': y}})
