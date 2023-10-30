from typing import Iterable, Optional, Self

from django.core.checks import Error
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class LockableManager(models.Manager):
    """Manager that adds ``locked`` and ``unlocked`` methods to filter locked instances according
    to a lock condition.

    The lock condition is specified in the constructor as keyword arguments.
    """

    def __init__(self, lock_condition: Q, *args, **kwargs):
        """Initialize the ``LockableManager``, specifying the condition that defines a locked
        instance as a ``Q`` object.
        """
        super().__init__(*args, **kwargs)
        self.lock_condition = lock_condition

    def is_instance_locked(self, instance: models.Model) -> bool:
        """Return whether a specific instance would be locked according to this manager.
        """
        return isinstance(instance, LockableModel) and instance in self.locked()

    def locked(self) -> Self:
        """Return locked instances.
        """
        return self.filter(self.lock_condition)
    
    def unlocked(self) -> Self:
        """Return unlocked instances.
        """
        return self.exclude(self.lock_condition)
    

class LockableModel(models.Model):
    """Abstract model to inherit from to create a model whose instances can be locked or unlocked.

    Any model managers used by this class must inherit from ``LockableManager`` to specify the
    condition that defines a locked instance.
    """

    class Meta:
        abstract = True

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        if not isinstance(cls._default_manager, LockableManager):
            errors.append(Error(
                '%s\'s default manager does not inherit from LockableManager.' % cls.__name__,
                hint='Please set a default manager that inherits from LockableManager.'
            ))
        return errors

    def get_locked_status(self) -> bool:
        """Get whether this instance is locked or not.
        """
        return self.__class__._default_manager.is_instance_locked(self)


class FlagLockableModel(LockableModel):
    """Abstract model to inherit from to create a model whose instances can be locked or unlocked
    using a Boolean field called ``is_locked``.

    This model adds an ``objects`` manager.
    """

    objects = LockableManager(Q(is_locked=True))

    is_locked = models.BooleanField(
        _('is locked'), default=False,
        help_text=_('Whether this object is locked or not. Locked objects cannot be edited.')
    )

    class Meta:
        abstract = True
