import cProfile
from cStringIO import StringIO
import marshal
import pstats

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed

class ProfileMiddleware(object):
    def __init__(self):
        if not settings.DEBUG:
            raise MiddlewareNotUsed()
        self.profiler = None

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.DEBUG and ('profile' in request.GET):
            self.profiler = cProfile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)

    def process_response(self, request, response):
        if settings.DEBUG:
            if 'profile' in request.GET:
                self.profiler.create_stats()
                out = StringIO()
                stats = pstats.Stats(self.profiler, stream=out)
                stats.sort_stats('time').print_stats(.2)
                response.content = out.getvalue()
                response['Content-type'] = 'text/plain'
        return response

