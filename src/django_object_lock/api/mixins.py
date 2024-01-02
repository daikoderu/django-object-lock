from typing import Optional

from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.request import Request
from rest_framework.response import Response

from django_object_lock.api.exceptions import APIObjectAlreadyUnlocked, APIObjectAlreadyLocked, APIObjectLocked
from django_object_lock.mixins import LockableMixin


class LockableUpdateModelMixin(UpdateModelMixin, LockableMixin):
    """Mixin to enforce object locking when updating a resource via API.
    """

    def update(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()  # noqa
        if self.is_instance_locked(instance):
            raise APIObjectLocked()
        return super().update(request, *args, **kwargs)


class LockableDestroyModelMixin(DestroyModelMixin, LockableMixin):
    """Mixin to enforce object locking when destroying a resource via API.
    """

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()  # noqa
        if self.is_instance_locked(instance):
            raise APIObjectLocked()
        return super().destroy(request, *args, **kwargs)


def lock_action(viewset: LockableMixin, request: Request, pk: Optional[int | str] = None) -> Response:
    instance = viewset.get_object()  # noqa
    if viewset.is_instance_locked(instance):
        raise APIObjectAlreadyLocked()
    viewset.set_locked_status(instance, True)
    instance.save()
    serializer = viewset.get_serializer(instance)  # noqa
    return Response(serializer.data)


def unlock_action(viewset: LockableMixin, request: Request, pk: Optional[int | str] = None) -> Response:
    instance = viewset.get_object()  # noqa
    if not viewset.is_instance_locked(instance):
        raise APIObjectAlreadyUnlocked()
    viewset.set_locked_status(instance, False)
    instance.save()
    serializer = viewset.get_serializer(instance)  # noqa
    return Response(serializer.data)
