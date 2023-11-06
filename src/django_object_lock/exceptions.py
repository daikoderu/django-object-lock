from django.utils.translation import gettext_lazy as _


class ObjectLocked(Exception):
    def __init__(self, msg: str = _('This object is locked and cannot be edited.'), *args):
        super().__init__(msg, *args)
