"""Settings object definition for ``django_object_lock``.

Based on Django REST Framework's settings file.
https://github.com/encode/django-rest-framework/blob/master/rest_framework/settings.py
"""

from typing import Any

from django.conf import settings
from django.core.signals import setting_changed
from django.utils.module_loading import import_string


# Default values.
DEFAULTS = {
    'DEFAULT_LOCKED_ICON_URL': 'django_object_lock/images/locked.svg'
}


# List of settings that may be in string import notation.
IMPORT_STRINGS = []


# Removed settings.
REMOVED_SETTINGS = []


# Django setting name containing django-object-lock's specific settings.
DJANGO_SETTING_NAME = 'DJANGO_OBJECT_LOCK'


# Documentation URL for settings.
SETTINGS_DOC = 'https://django-object-lock.readthedocs.io/en/latest/'


def perform_import(val: Any, setting_name: str) -> Any:  # pragma: no cover
    """If the given setting is a string import notation, then perform the necessary import(s).
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val: Any, setting_name: str) -> Any:  # pragma: no cover
    """Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = 'Could not import "%s" for setting "%s". %s: %s.' \
            % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class DjangoObjectLockSettings:
    """A settings object that allows ``django-object-lock`` settings to be accessed as
    properties. For example:

    .. code-block:: python

        from django_object_lock.settings import dol_settings
        print(dol_settings.DEFAULT_LOCKED_ICON_URL)
    """

    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, DJANGO_SETTING_NAME, {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid setting: '%s'" % attr)

        try:
            # Check if present in user settings.
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults.
            val = self.defaults[attr]

        # Coerce import strings into classes.
        if attr in self.import_strings:  # pragma: no cover
            val = perform_import(val, attr)

        # Cache the result.
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def __check_user_settings(self, user_settings):  # pragma: no cover
        for setting in REMOVED_SETTINGS:
            if setting in user_settings:
                raise RuntimeError(
                    'The "%s" setting has been removed. '
                    'Please refer to "%s" for available settings.' % (setting, SETTINGS_DOC)
                )
        return user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')


dol_settings = DjangoObjectLockSettings(None, DEFAULTS, IMPORT_STRINGS)


def reload_settings(*args, **kwargs):
    setting = kwargs['setting']
    if setting == DJANGO_SETTING_NAME:
        dol_settings.reload()


setting_changed.connect(reload_settings)
