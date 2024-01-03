from django.db import models

from django_object_lock.models import LockableModel


class LockableMixin:
    """Mixin to add object locking logic for models that do not inherit from ``LockableModel`` or to override
    locking logic.
    """

    def is_instance_locked(self, obj: models.Model) -> bool:
        """Implement this method returning ``True`` if the instance should be considered locked,
        and ``False`` otherwise.

        If your model inherits from ``LockableModel``, you need not implement this method. In that
        case, the ``LockableModel``'s ``is_locked`` method is used.
        """
        if isinstance(obj, LockableModel):
            return obj.is_locked()
        else:
            raise NotImplementedError('This method must be implemented.')

    def set_locked_status(self, obj: models.Model, lock: bool) -> None:
        """Implement to lock or unlock an object when the ``lock`` or ``unlock``
        actions are used.

        If your model inherits from ``LockableModel``, you need not implement this method. In that
        case, the ``LockableModel``'s ``set_locked`` method is used.
        """
        if isinstance(obj, LockableModel):
            obj.set_locked(lock)
        else:
            raise NotImplementedError('This method must be implemented.')
