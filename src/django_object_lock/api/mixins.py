from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.request import Request
from rest_framework.response import Response

from django_object_lock.exceptions import ObjectLocked
from django_object_lock.mixins import LockableMixin


class LockableUpdateModelMixin(UpdateModelMixin, LockableMixin):
    """Mixin to enforce object locking when updating a resource via API.
    """

    def update(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        if self.is_instance_locked(instance):
            raise ObjectLocked()
        return super().update(request, *args, **kwargs)


class LockableDestroyModelMixin(DestroyModelMixin, LockableMixin):
    """Mixin to enforce object locking when destroying a resource via API.
    """

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        if self.is_instance_locked(instance):
            raise ObjectLocked()
        return super().destroy(request, *args, **kwargs)
