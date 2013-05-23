# Create your views here.
from django.http import HttpResponse
from datetime import timedelta, tzinfo, datetime
from django.shortcuts import render_to_response

def home(request):
    return render_to_response('home.html', {})


