from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class LockableModel(models.Model):
    """Abstract model to inherit from to create a model whose instances can be locked.

    This adds the ``is_locked`` boolean field, which may be set from the admin.
    """

    is_locked = models.BooleanField(
        _('is locked'), default=False,
        help_text=_('Whether this object is locked or not. Locked objects cannot be edited.')
    )

    class Meta:
        abstract = True


class AutoLockableModel(models.Model):
    """Abstract model to inherit from to create a model that will be automatically locked or
    unlocked depending on a condition.

    This adds the ``get_locked_condition`` class method, which must be implemented to set the
    condition (as a Q object) that must be met for an instance to be locked. This Q object may
    be passed to a ``QuerySet`` to filter locked or unlocked objects.
    """

    class Meta:
        abstract = True

    @classmethod
    def get_locked_condition(cls) -> Q:
        """Implement this method to return a Q object specifying which model instances are
        considered to be locked.
        """
        raise NotImplementedError('This method must be implemented.')
