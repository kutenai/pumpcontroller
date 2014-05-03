# Create your views here.

import os
import sys

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from Ditch.Controller import DitchController

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders it's content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def index(request):
    """
    List all code nurseries, or create a new snippet.
    """
    if request.method == 'GET':
        d = DitchController()
        stat = d.getSystemStatus()
        return JSONResponse(stat, status=201)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        if data.has_key('zone'):
            d = DitchController()
            zone = data['zone']
            if zone == 'north':
                d.runNorth()
            elif zone == 'south':
                d.runSouth()

        return JSONResponse({}, status=201)

    elif request.method == 'DELETE':
        print("Deleting. or stopping it")
        d = DitchController()
        d.allOff()
        return JSONResponse({}, status=201)

@csrf_exempt
def levels(request):
    """
    List all code nurseries, or create a new snippet.
    """
    if request.method == 'GET':
        d = DitchController()
        stat = d.getSystemStatus()
        return JSONResponse(stat, status=201)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        if data.has_key('zone'):
            d = DitchController()
            zone = data['zone']
            if zone == 'north':
                d.runNorth()
            elif zone == 'south':
                d.runSouth()

        return JSONResponse({}, status=201)

    elif request.method == 'DELETE':
        print("Deleting. or stopping it")
        d = DitchController()
        d.allOff()
        return JSONResponse({}, status=201)


