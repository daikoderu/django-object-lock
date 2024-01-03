# API locking

If you use Django REST Framework's generic views or viewsets, ``django-object-lock`` provides mixins that enforce
model object locking in the ``django_object_lock.api.mixins`` module.

*   Make your generic view or viewset inherit from ``LockableUpdateModelMixin`` to check whether the instance is
    locked before updating it and raise the ``APIObjectLocked`` exception if it is.
*   Make your generic view or viewset inherit from ``LockableDestroyModelMixin`` to check whether the instance is
    locked before deleting it and raise the ``APIObjectLocked`` exception if it is.
    
``APIObjectLocked`` generates an HTTP 409 "Conflict" error.

Define the following methods to implement API-level locking:

*   `is_instance_locked(obj) -> bool` must return whether the `obj` instance is considered locked (`True`) or not
    (`False`).
*   `set_locked_status(obj, lock) -> None` must lock the `obj` if `lock` is `True` and unlock it otherwise. 
    You need not call `save()` in your implementation.

If the model is lockable on its own and these methods are not defined, `is_locked()` and `set_locked(value)` methods
are used instead, respectively. This allows you to use different locking logic in the API and the rest of your
Django project.

```{important}
You will get a `NotImplementedError` if neither `is_instance_locked` nor `is_locked()` are defined, or if neither
`set_locked_status` nor `set_locked` are defined.
```

For example, if you have defined `is_locked()` and `set_locked(value)`, this would be enough:

```python
from django_object_lock.api import mixins as dlo_mixins
from rest_framework import viewsets, serializers, mixins

from articles.models import Article

class ArticleSerializer(serializers.ModelSerializer):
    ...

class ArticleViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    dlo_mixins.LockableUpdateModelMixin,
    dlo_mixins.LockableDestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
```


## Locking and unlocking instances from the API

There are also methods to lock and unlock instances from the API. However, they are not provided as mixins, in order
to give flexibility to set any action name or methods. Instead, add them as actions like so:

```python
from typing import Optional

from django_object_lock.api import mixins as dlo_mixins
from django_object_lock.mixins import LockableMixin
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

class ArticleViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    dlo_mixins.LockableUpdateModelMixin,
    dlo_mixins.LockableDestroyModelMixin,
    viewsets.GenericViewSet,
):
    ...

    @action(methods=['PUT', 'PATCH'], detail=True)
    def lock(self: LockableMixin, request: Request, pk: Optional[int | str] = None) -> Response:
        return dlo_mixins.lock_action(self, request, pk)

    @action(methods=['PUT', 'PATCH'], detail=True)
    def unlock(self: LockableMixin, request: Request, pk: Optional[int | str] = None) -> Response:
        return dlo_mixins.unlock_action(self, request, pk)
```

```{important}
Make sure ``detail`` is set to ``True`` in the ``@action`` decorator.
```

The ``lock_action`` raises ``APIObjectAlreadyLocked`` if the object to be locked is already locked.
Conversely,  ``unlock_action`` raises ``APIObjectAlreadyUnlocked`` if the object to be locked is already locked.
