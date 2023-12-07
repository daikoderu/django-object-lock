from typing import Optional

from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.request import Request
from rest_framework.response import Response

from django_object_lock.api.exceptions import APIObjectNotLocked, APIObjectAlreadyLocked, APIObjectLocked
from django_object_lock.mixins import LockableMixin


class LockableUpdateModelMixin(UpdateModelMixin, LockableMixin):
    """Mixin to enforce object locking when updating a resource via API.
    """

    def update(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        if self.is_instance_locked(instance):
            raise APIObjectLocked()
        return super().update(request, *args, **kwargs)


class LockableDestroyModelMixin(DestroyModelMixin, LockableMixin):
    """Mixin to enforce object locking when destroying a resource via API.
    """

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        if self.is_instance_locked(instance):
            raise APIObjectLocked()
        return super().destroy(request, *args, **kwargs)


class LockActionMixin(LockableMixin):

    @action(detail=True, description=_('Lock'))
    def lock(self, request: Request, pk: Optional[int | str] = None) -> Response:
        instance = self.get_object()
        if self.is_instance_locked(instance):
            raise APIObjectAlreadyLocked()
        self.set_locked_status(instance, True)
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UnlockActionMixin(LockableMixin):

    @action(detail=True, description=_('Unlock'))
    def unlock(self, request: Request, pk: Optional[int | str] = None) -> Response:
        instance = self.get_object()
        if not self.is_instance_locked(instance):
            raise APIObjectNotLocked()
        self.set_locked_status(instance, False)
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
