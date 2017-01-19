import os
import sys
import shutil
from optparse import make_option, OptionParser
from termcolor import cprint

from django.template import Template, Context

from lucommon.utils import (
    query_yes_no,
)

from lucommon.exception import LuCommandError
from lucommon.management.commands import LuBaseCommand

"""
Subcommand: luadd

>>>python manager.py luadd --project-name=PROJECT_NAME --app-name=APP_NAME --model-name=MODEL_NAME

Multiple model join by comma(,)
"""

class Command(LuBaseCommand):

    help = __doc__

    # Before Django 1.8, `options` not work,
    # we use this kind of method to add option
    option_list = LuBaseCommand.option_list
    option_list += (
        make_option('--project-name', '-p',
            help='project name. e.g. "qc"'),
        make_option('--app-name', '-a',
            help='app name. e.g. "qcJira"'),
        make_option('--model-name', '-m',
            help='model name. e.g. "Bug,Issue"'),
    )

    app_template = 'app_template_luadd'

    def handle(self, *args, **options):
        """
        Core process entry
        """
        project_name = self.validate_project(args, options)
        app_name = self.validate_app(args, options)
        model_name = self.validate_model(args, options, app_name)
        (template_dir, target_dir) = self.get_path(self.app_template, app_name)

        self.generate(project_name, app_name, model_name, template_dir, target_dir)

    def generate(self, project_name, app_name, model_name, template_dir, target_dir):
        """
        Render template
        """
        model_names, _model_objs = self.get_models('.models', app_name)

        # Filter model and model obj
        model_names = model_name
        model_objs = {}
        for m in model_names:
            model_objs[m] = _model_objs[m]

        filter_context = self.get_filter_context(model_objs)
        filter_field_context = self.get_filter_field_context(model_objs, filter_context)
        admin_field_context = self.get_model_field_context(model_objs)

        context_dict = {
            'project_name': project_name,
            'app_name': app_name,
            'model_names': model_names,
            'filter_context': filter_context,
            'filter_field_context': filter_field_context,
            'admin_field_context': admin_field_context,
            'old_content': '',
        }

        print(('-' * 78))
        cprint('Lucommon Update App `%(app_name)s` For Project `%(project_name)s` Starting ...' % context_dict, 'blue',
                attrs=['bold'])
        print(('-' * 78))

        for root, dirs, files in os.walk(template_dir):

            for dirname in dirs[:]:
                if dirname.startswith('.') or dirname == '__pycache__':
                    dirs.remove(dirname)

            for filename in files:
                if filename.endswith(('.pyo', '.pyc', '.py.class')):
                    # Ignore some files as they cause various breakages.
                    continue

                old_path = os.path.join(root, filename)
                new_path = os.path.join(target_dir, filename)
                bak_path = os.path.join(target_dir, '.%s' % filename)

                # Only render the Python files, as we don't want to
                # accidentally render Django templates files
                with open(new_path,'rb') as old_file:
                    old_content = old_file.read().strip()
                    context_dict.update({'old_content':old_content})
                with open(old_path, 'rb') as template_file:
                    content = template_file.read()
                if filename.endswith('.py'):
                    content = content.decode('utf-8')
                    template = Template(content)

                    context = Context(context_dict, autoescape=False)

                    content = template.render(context)
                    content = content.encode('utf-8')
                if query_yes_no('Do you really want to replace the file `%s`?' % \
                                new_path, default='yes'):
                    with open(new_path, 'wb') as new_file:
                        new_file.write(content)
                        cprint("->Creating `%s` Success!" % new_path, 'green')
                    try:
                        shutil.copymode(old_path, new_path)
                        self.make_writeable(new_path)
                    except OSError:
                        self.stderr.write(
                            "Notice: Couldn't set permission bits on %s. You're "
                            "probably using an uncommon filesystem setup. No "
                            "problem." % new_path)

        self.print_project_hints(context_dict)


