from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import APIException
from rest_framework import status


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('Cannot perform this action.')
    default_code = 'conflict'


class APIObjectLocked(Conflict):
    default_detail = _('This object is locked and cannot be edited.')
    default_code = 'object_locked'


class APIObjectAlreadyLocked(Conflict):
    default_detail = _('This object has already been locked.')
    default_code = 'object_already_locked'


class APIObjectAlreadyUnlocked(Conflict):
    default_detail = _('This object is not locked.')
    default_code = 'object_not_locked'
