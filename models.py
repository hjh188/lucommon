from django.db import models
from reversion import revisions

from crum import get_current_request

# Create your models here.

class LuModel(models.Model):
    """
    Lu Model
    """
    def save(self, *args, **kwargs):
        # Load the request
        request = get_current_request()

        if hasattr(request, 'conf') and getattr(request.conf, 'enable_reversion_%s' % request.method.lower()):
            with revisions.create_revision():
                super(LuModel, self).save(*args, **kwargs)

                revisions.set_user(request.user)
                revisions.set_comment("[%s] Called from Lucommon Framework" % request.method)
        else:
            super(LuModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True

