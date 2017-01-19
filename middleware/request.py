import re

from django.conf import settings

from lucommon.decorator import login_required


class LuRequireLoginMiddleware(object):
    """
    Example:
    ------
    LOGIN_REQUIRED_URLS = (
        r'/lts/qc/(.*)$',
    )
    LOGIN_REQUIRED_URLS_EXCEPTIONS = (
        r'/lts/qc/login(.*)$',
        r'/lta/qc/logout(.*)$',
    )
    ------
    """
    def __init__(self):
        self.required = tuple(re.compile(url) for url in settings.LOGIN_REQUIRED_URLS)
        self.exceptions = tuple(re.compile(url) for url in settings.LOGIN_REQUIRED_URLS_EXCEPTIONS)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # No need to process URLs if user already logged in
        if request.user.is_authenticated():
            return None

        # An exception match should immediately return None
        for url in self.exceptions:
            if url.match(request.path):
                return None

        # if LOGIN_REQUIRED_URLS is [], we will set everything to login_required
        # otherwise, we will filter the login_required for the specified url
        if not self.required:
            return login_required(view_func)(request, *view_args, **view_kwargs)
        else:
            for url in self.required:
                if url.match(request.path):
                    return login_required(view_func)(request, *view_args, **view_kwargs)


class LuDisableCSRF(object):
    """
    Disable CSRF check
    """
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)


