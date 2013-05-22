# Create your views here.
from django.http import HttpResponse
from datetime import timedelta, tzinfo, datetime
from django.shortcuts import render_to_response

from models import LevelLog

def index(request,hours=2):
    start = datetime.now() - timedelta(hours=hours)
    entries = LevelLog.objects.filter(timestamp__gte=start)

    return render_to_response('ditchmon.html', {'entries' : entries})

def query(request,hours):

    start = datetime.now() - timedelta(hours=hours)
    entries = LevelLog.objects.filter(timestamp_gte=start)

    return render_to_response('ditchmon.html', {'entries' : entries})

