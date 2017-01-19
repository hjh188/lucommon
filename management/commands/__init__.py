import os
import sys
import importlib
import shutil
import inspect
import glob
from optparse import make_option, OptionParser
from termcolor import cprint

import django
from django.template import Template, Context
from django.core.management.base import BaseCommand
from django.db.models import Model

import lucommon
from lucommon.utils import (
    query_yes_no,
    find_installed_app,
    find_project,
)

from lucommon.exception import LuCommandError


class LuBaseCommand(BaseCommand):
    """
    LU Base Command wrapper
    """
    help = 'Generate CRUD method according to app models automatically'

    app_template = None
    app = None

    def add_arguments(self, parser):
        """
        Before Django 1.8, `options` not work.
        """
        pass

    def validate_project(self, args, options):
        """
        Validate project
        """
        project_name = options.get('project_name', None)

        if project_name is None:
            raise LuCommandError('Please use option `--project-name` to set project name!')

        if not os.path.isdir(project_name):
            guess_project = find_project()
            raise LuCommandError('Invalid project: `%s`!\nAvailable project: %s' % (project_name, guess_project))

        return project_name

    def validate_app(self, args, options):
        """
        Validate app
        """
        app_name = options.get('app_name', None)

        if app_name is None:
            raise LuCommandError('Please use option `--app-name` to set app name!')

        try:
            self.app = importlib.import_module(app_name)
        except (ImportError, ValueError), err:
            guess_app = find_installed_app(options.get('project_name'))
            raise LuCommandError('Invalid app `%s`: %s!\nAvailable app: %s' % (app_name, str(err), str(guess_app)))

        return app_name

    def validate_model(self, args, options, app_name):
        """
        Validate model
        """
        model_name = options.get('model_name', None)

        if model_name is None:
            raise LuCommandError('Please use option `--model-name` to set model name!')

        model_name = [name.strip() for name in model_name.split(',')]

        try:
            model = app_name + '.models'
            self.model = importlib.import_module(model)

            all_model = self.get_models('.models', app_name)[0]

            # Check for the given model
            for m in model_name:
                if not hasattr(self.model, m):
                    raise LuCommandError('No model `%s` found for app `%s`!\nAvailable model: %s' % (m, app_name, str(all_model)))

            # Check if need to generate code
            view = importlib.import_module(app_name + '.views')
            for m in model_name:
                if hasattr(view, '%sViewSet' % m):
                    all_model.remove(m)
                    raise LuCommandError('Code for model `%s` exists!\nGuess you are looking for %s' % (m,str(all_model)))

        except (ImportError, ValueError), err:
            raise LuCommandError('No model found for app `%s`!' % app_name)

        return model_name

    def get_path(self, template_type, app_name):
        return (os.path.join(lucommon.__path__[0], 'template', template_type),
                os.path.join(self.app.__path__[0]))


    def print_project_hints(self, context_dict):
        """
        Print project and app access hints according to the template reander
        """
        print '\n'
        print(('-' * 78))
        cprint('Lucommon Update App `%(app_name)s` For Project `%(project_name)s` Completed!' % context_dict, 'blue',
               attrs=['bold'])
        cprint('  App `%(app_name)s` CRUD interfaces are ready and have fun!' % context_dict, 'blue')
        cprint('  Note: `%(app_name)s` connect `default` db, change in `confs.py` accordingly!' % context_dict, 'blue')
        print(('-' * 78))

        cprint('->API Documentation access url: /%(project_name)s/docs/' % context_dict, 'green')
        for model_name in context_dict.get('model_names'):
            cprint('->Model `%s` access url(CREATE, LIST): /%s/%s/%ss/' % \
                   (model_name, context_dict.get('project_name'), context_dict.get('app_name'), model_name.lower()), 'green')
            cprint('->Model `%s` access url(UPDATE, GET, DELETE, PATCH): /%s/%s/%ss/<id>\n' % \
                   (model_name, context_dict.get('project_name'), context_dict.get('app_name'), model_name.lower()), 'green')


    def make_writeable(self, filename):
        """
        Make sure that the file is writeable.
        Useful if our source is read-only.
        """
        if sys.platform.startswith('java'):
            # On Jython there is no os.access()
            return
        if not os.access(filename, os.W_OK):
            st = os.stat(filename)
            new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
            os.chmod(filename, new_permissions)

    def get_models(self, model, app_name):
        """
        Get all models from models.py
        """
        model_names = []
        model_objs = {}
        try:
            models = importlib.import_module(model, app_name)
        except ImportError:
            return model_names, model_objs

        for name, obj in inspect.getmembers(models):
            if inspect.isclass(obj) and issubclass(obj, Model):
                if name in ('AbstractUser','LuModel'):
                    continue
                model_names.append(name)
                model_objs[name] = obj._meta.local_fields

        return model_names, model_objs

    def get_model_field_context(self, model_objs):
        """
        Get model fields name list
        """
        model_field_context = {}
        for model_name in model_objs:
            model_field_context[model_name] = []
            for item in model_objs[model_name]:
                item_name = str(item).split('.')[-1]
                model_field_context[model_name].append(item_name)

        return model_field_context

    def get_filter_field_context(self, model_objs, filter_context):
        """
        Get fields context
        """
        filter_field_context = {}
        for model_name in model_objs:
            filter_field_context[model_name] = []
            for item in model_objs[model_name]:
                item_name = str(item).split('.')[-1]
                filter_field_context[model_name].append(item_name)
                if ('max_' + item_name) in filter_context[model_name]:
                    filter_field_context[model_name].extend(['max_' + item_name, 'min_' + item_name])

        return filter_field_context

    def get_filter_context(self, model_objs):
        """
        Get filter context
        """
        filter_context = {}
        for model_name in model_objs:
            filter_context[model_name] = {}
            for item in model_objs[model_name]:
                if isinstance(item, django.db.models.fields.IntegerField):
                    item_name = str(item).split('.')[-1]
                    filter_context[model_name]['min_' + item_name] = \
                        "django_filters.NumberFilter(name='%s', lookup_type='gte')" % item_name
                    filter_context[model_name]['max_' + item_name] = \
                        "django_filters.NumberFilter(name='%s', lookup_type='lte')" % item_name

                if isinstance(item, django.db.models.fields.DateTimeField) or \
                   isinstance(item, django.db.models.fields.DateField):
                    item_name = str(item).split('.')[-1]
                    filter_context[model_name]['min_' + item_name] = \
                        "django_filters.DateTimeFilter(name='%s', lookup_type='gte')" % item_name
                    filter_context[model_name]['max_' + item_name] = \
                        "django_filters.DateTimeFilter(name='%s', lookup_type='lte')" % item_name

        return filter_context


