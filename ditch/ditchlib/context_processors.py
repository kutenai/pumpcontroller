from __future__ import absolute_import

from django.conf import settings

def gardenbuzz_ctx(request):

    return {
        'use_less':settings.USE_LESS,
        'less_poll': settings.LESS_POLL,
        'allow_signup' : False,
        'allow_social' : False,
        }


