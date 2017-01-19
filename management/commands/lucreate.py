import os
import sys
import shutil
import glob
from optparse import make_option, OptionParser
from termcolor import cprint

from django.template import Template, Context

from lucommon.utils import (
    query_yes_no,
)

from lucommon.exception import LuCommandError
from lucommon.management.commands import LuBaseCommand

"""
Subcommand: lucreate

>>>python manager.py lucreate --project-name=PROJECT_NAME --app-name=APP_NAME
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
    )

    app_template = 'app_template'

    def handle(self, *args, **options):
        """
        Core process entry
        """
        project_name = self.validate_project(args, options)
        app_name = self.validate_app(args, options)
        (template_dir, target_dir) = self.get_path(self.app_template, app_name)

        self.generate(project_name, app_name, template_dir, target_dir)

    def generate(self, project_name, app_name, template_dir, target_dir):
        """
        Render template
        """
        model_names, model_objs = self.get_models('.models', app_name)
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
        }
        context = Context(context_dict, autoescape=False)

        self.install_packages()

        print(('-' * 78))
        cprint('Lucommon Init App `%(app_name)s` For Project `%(project_name)s` Starting ...' % context_dict, 'blue',
                attrs=['bold'])
        print(('-' * 78))
        self.update_setting(project_name, app_name)
        self.update_url(project_name, app_name)
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
                with open(old_path, 'rb') as template_file:
                    content = template_file.read()
                if filename.endswith('.py'):
                    content = content.decode('utf-8')
                    template = Template(content)
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

    def install_packages(self):
        """
        Install dependencies
        """
        print(('-' * 78))
        cprint('Lucommon dependencies installation ...', 'blue', attrs=['bold'])
        print(('-' * 78))

        os.system('pip install -r lucommon/requirements.txt')
        print '\n'

    def update_setting(self, project_name, app_name):
        """
        Update project settings from third_project
        """
        setting_path = os.path.join(project_name, 'settings.py')

        third_setting_path = None
        third_proj_setting_path = None

        if query_yes_no('Do you really want to replace the file `%s`?' % \
                        setting_path, default='yes'):
            with open(setting_path, 'ab') as new_file:
                if third_setting_path:
                    with open(third_setting_path, 'r') as third_file:
                        new_file.write(third_file.read())
                if third_proj_setting_path:
                    with open(third_proj_setting_path, 'r') as third_file:
                        new_file.write(third_file.read())
                cprint("->Creating `%s` Success!" % setting_path, 'green')

    def update_url(self, project_name, app_name):
        """
        Update project urls
        * add swagger doc path
        * add app urls
        """
        url_path = os.path.join(project_name, 'urls.py')
        content="""
urlpatterns.append(url(r'^%(project_name)s/docs/', include('rest_framework_swagger.urls')))
urlpatterns.append(url(r'^%(project_name)s/%(app_name)s/', include('%(app_name)s.urls')))
""" % {'project_name': project_name, 'app_name': app_name}

        third_url_path = None

        if query_yes_no('Do you really want to replace the file `%s`?' % \
                        url_path, default='yes'):
            with open(url_path, 'ab') as new_file:
                new_file.write(content)
                if third_url_path:
                    with open(third_url_path, 'r') as third_file:
                        new_file.write(third_file.read())
                cprint("->Creating `%s` Success!" % url_path, 'green')


