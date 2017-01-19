import traceback

from django.conf import settings

from rest_framework.views import exception_handler
from rest_framework import viewsets

from django.core.exceptions import (
    ObjectDoesNotExist,
    FieldError,
    ImproperlyConfigured,
    ValidationError,
)

from exceptions import AssertionError

from django.db.utils import IntegrityError

from django.core.management.base import CommandError

from lucommon.response import LuResponse
from lucommon.logger import lu_logger
from lucommon import status

"""
Exception related
"""

class LuCommandError(CommandError):
    """
    Command Exception
    """
    pass

class LuSQLNotAllowError(Exception):
    """
    SQL Not Allow
    """
    pass

class LuSQLSyntaxError(Exception):
    """
    SQL Syntax Error
    """
    pass

class LuExceptionHandler(object):
    """
    Exception handler
    """
    # Post exception handler
    def handle_exception(self, exc):
        try:
            response = super(viewsets.ModelViewSet, self).handle_exception(exc)
        except ObjectDoesNotExist, err:
            msg = traceback.format_exc() if settings.DEBUG else str(err)
            lu_logger.warn(msg)
            response = LuResponse(status=400, code=status.LU_4004_NOT_FOUND, message=msg)
        except (FieldError, ValidationError), err:
            msg = traceback.format_exc() if settings.DEBUG else str(err)
            lu_logger.warn(msg)
            response = LuResponse(status=400, code=status.LU_4007_INVALID_PARAM, message=msg)
        except ImproperlyConfigured, err:
            msg = traceback.format_exc() if settings.DEBUG else str(err)
            lu_logger.warn(msg)
            response = LuResponse(status=500, code=status.LU_5001_SERVER_ERROR_CONFIGURED, message=msg)
        except (ValueError, IntegrityError), err:
            msg = traceback.format_exc() if settings.DEBUG else str(err)
            lu_logger.warn(msg)
            response = LuResponse(status=400, code=status.LU_4009_PARAM_TYPE_ERROR, message=msg)
        except AssertionError, err:
            msg = traceback.format_exc() if settings.DEBUG else str(err)
            lu_logger.error(msg)
            response = LuResponse(status=500, code=status.LU_5000_SERVER_ERROR, message=msg)
        except LuSQLNotAllowError, err:
            msg = traceback.format_exc() if settings.DEBUG else str(err)
            lu_logger.error(msg)
            response = LuResponse(status=400, code=status.LU_4011_SQL_NOT_ALLOW_ERROR, message=msg)
        except (LuSQLSyntaxError), err:
            msg = traceback.format_exc() if settings.DEBUG else str(err)
            lu_logger.error(msg)
            response = LuResponse(status=400, code=status.LU_4012_SQL_SYNTAX_ERROR, message=msg)
        except Exception, err:
            msg = traceback.format_exc() if settings.DEBUG else 'Not catch exception `%s`: %s' % (str(type(err)), str(err))
            lu_logger.error(msg)
            response = LuResponse(status=500, code=status.LU_9999_UNKNOWN_ERROR, message=msg)

        return self.post_exception_process(exc, response)


    def post_exception_process(self, exc, response):
        if response is not None:
            if isinstance(response.data, dict):
                if 'detail' in response.data \
                     and response.data.get('detail'):
                    response.data['code'] = response.status_code
                    response.data['message'] = response.data.get('detail')
                    response.data['data'] = None
                    del response.data['detail']
                else:
                    response.data['message'] = str(response.data)
                    response.data['code'] = response.status_code
                    response.data['data'] = None

        return response


