from typing import Any, Collection, Optional

from django.db import models

from django_object_lock.exceptions import ObjectLocked


class LockableModel(models.Model):

    class Meta:
        abstract = True

    @classmethod
    def from_db(
        cls, db: Optional[str], field_names: Collection[str], values: Collection[Any]
    ) -> models.Model:
        instance = super().from_db(db, field_names, values)
        instance._was_locked_on_load = instance.is_locked()
        return instance

    def is_locked(self) -> bool:
        """Implement to determine when a model instance is locked (return ``True``) or not
        (return ``False``).
        """
        raise NotImplementedError('This method must be implemented.')

    def set_locked(self, value: bool) -> None:
        """Implement to set the locked status of this model instance to allow manual locking
        and unlocking.
        """
        raise NotImplementedError('This method must be implemented.')

    def save(self, *args, **kwargs):
        if self.is_locked() and getattr(self, '_was_locked_on_load', False):
            raise ObjectLocked()
        super().save(*args, **kwargs)
        self._was_locked_on_load = self.is_locked()

    def delete(self, *args, **kwargs):
        if self.is_locked():
            raise ObjectLocked()
        super().delete(*args, **kwargs)
