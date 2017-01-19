#!/usr/bin/env python

import sys
import os
import errno
from collections import OrderedDict
import importlib

"""
Utils for lucommon module
"""

def mkdir(path):
    """
    Make directory if not exists
    """
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


class ReturnDict(OrderedDict):
    """
    Return object from `serialier.data` for the `Serializer` class.
    """

    def __init__(self, *args, **kwargs):
        self.serializer = kwargs.pop('serializer') if 'serializer' in kwargs else None
        super(ReturnDict, self).__init__(*args, **kwargs)

    def copy(self):
        return ReturnDict(self, serializer=self.serializer)

    def __repr__(self):
        return dict.__repr__(self)

    def __reduce__(self):
        # Pickling these objects will drop the .serializer backlink,
        # but preserve the raw data.
        return (dict, (dict(self),))


class ReturnList(list):
    """
    Return object from `serialier.data` for the `SerializerList` class.
    """

    def __init__(self, *args, **kwargs):
        self.serializer = kwargs.pop('serializer') if 'serializer' in kwargs else None
        super(ReturnList, self).__init__(*args, **kwargs)

    def __repr__(self):
        return list.__repr__(self)

    def __reduce__(self):
        # Pickling these objects will drop the .serializer backlink,
        # but preserve the raw data.
        return (dict, (dict(self),))


def find_installed_app(project_name, user_app=True):
    """
    Find project installed app
    """
    installed_app = [app for app in importlib.import_module(project_name + '.settings').INSTALLED_APPS]
    installed_app.remove('lucommon')

    return list(set(installed_app) & set(os.listdir('.'))) if user_app else installed_app

def find_project():
    """
    Find project name
    """
    _dir = [d for d in os.listdir('.') if os.path.isdir(d)]
    project_files = ['settings.py', 'urls.py', '__init__.py', 'wsgi.py']

    for d in _dir:
        if set(project_files) == set(project_files) & set(os.listdir(d)):
            return d

    return None


