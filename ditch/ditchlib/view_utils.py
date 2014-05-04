import os.path
import re

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.renderers import JSONRenderer
from django.shortcuts import redirect
from django.contrib.auth import logout

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders it's content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def parsePhotoFile(images,mdfile):
    """
    Parse the md file that contains image tags and captions

    Example format:
    ![](thumbs/Euphorbia.JPG "Euphorbia")
    ![](thumbs/IMG_0003.JPG "Bright Gaillardia")

    """
    fp = open(mdfile,'r')
    for line in fp:
        m = re.search('!\[(.*)\]\(([A-Za-z0-9_\-./]+)(\s+"(.*)")\)',line)
        if m:
            # Found a line
            alttext = m.group(1)
            imgfile = m.group(2)
            title = m.group(4) # Skips a group
            filename = os.path.basename(imgfile)

            d = images.get(filename)
            if d:
                d['title'] = title
                d['alt'] = alttext

            pass
    fp.close()

def loadImages(imgPath,urlBase):
    """
    Load files from the given season.
    Load files from the height_300 dir, and then
    match with files from the 'thumb' dir.
    """
    imageList = []
    imageFiles = {}

    h300path = os.path.join(imgPath,'height_300')
    if os.path.exists(h300path):
        for root, dirs, files in os.walk(h300path):
            for f in files:
                if re.search('\.(jpg|png)$',f,re.I):
                    t = {
                        'img'   : os.path.join(urlBase,'height_300',f),
                        'title' : ""
                    }
                    imageList.append(t)
                    imageFiles[f] = t

    thumbPath = os.path.join(imgPath,'thumbs')
    if os.path.exists(thumbPath):
        for root, dirs, files in os.walk(thumbPath):
            for f in files:
                if re.search('\.(jpg|png)$',f,re.I):
                    if imageFiles.has_key(f):
                        imageFiles[f]['thumb'] = os.path.join(urlBase,'thumbs',f)

    mdfile = os.path.join(imgPath,'photos.md')
    if os.path.exists(mdfile):
        parsePhotoFile(imageFiles,mdfile)

    return imageList

class DitchMixin(object):
    angular_app = 'gardenbuzz'

    def get_context_data(self, **kwargs):
        context = super(DitchMixin,self).get_context_data(**kwargs)

        context.update({
            "angularapp": self.angular_app
            })
        return context

class LoginReqMixin(object):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginReqMixin, self).dispatch(request, *args, **kwargs)


def get_redirect(r):
    '''This function is used by the SignUp and Login views.'''
    redirect_url = None
    if r.GET.get('next'):
        redirect_url = r.GET.get('next')
        if r.GET.get('fiddle'):
            redirect_url = redirect_url + '&fiddle=1'
    return redirect_url

def logout_user(r):
    logout(r)
    return redirect("home")


