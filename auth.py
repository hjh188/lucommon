from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from simple_sso.sso_client.client import Client

from lucommon import settings as lusettings

"""
Authentication and Permissions
"""

class LuAuthPerm(object):
    """
    Process auth and perm related
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication) if lusettings.AUTH else ()
    permission_classes = (IsAuthenticated,) if lusettings.PERM else ()


sso_client = Client(settings.SSO_SERVER, settings.SSO_PUBLIC_KEY, settings.SSO_PRIVATE_KEY) if hasattr(settings, 'SSO_SERVER') else None
