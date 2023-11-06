from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.http import HttpResponse


if TYPE_CHECKING:
    from django_object_lock.admin import LockableAdminMixin


def parse_pks(pk_string: str) -> list[int] | list[str]:
    pk_strings = pk_string.strip().split(',')
    try:
        return [int(x) for x in pk_strings]
    except ValueError:
        return [x.strip() for x in pk_strings if x]


def lock_or_unlock_by_pk(
    model_admin: 'LockableAdminMixin', model_class: type[Model], pk: int | str, lock: bool
) -> None:
    try:
        obj = model_class._default_manager.get(pk=pk)
        if model_admin.is_instance_locked(obj) != lock:
            model_admin.set_locked_status(obj, True)
            obj.save()
    except model_class.DoesNotExist:
        pass


def default_lock_view(model_admin, request, *args, **kwargs):
    # TODO Query parameter 'ct' could not be defined, and the ContentType could not exist
    # TODO Account for other HTTP methods
    ct = ContentType.objects.get(pk=request.GET.get('ct', None))
    pk_list = parse_pks(request.GET.get('ids', ''))
    if request.method == 'POST':
        for pk in pk_list:
            lock_or_unlock_by_pk(model_admin, ct, pk, True)
    else:
        return HttpResponse('Locking objects.')


def default_unlock_view(model_admin, request, *args, **kwargs):
    # TODO Query parameter 'ct' could not be defined, and the ContentType could not exist
    # TODO Account for other HTTP methods
    ct = ContentType.objects.get(pk=request.GET.get('ct', None))
    pk_list = parse_pks(request.GET.get('ids', ''))
    if request.method == 'POST':
        for pk in pk_list:
            lock_or_unlock_by_pk(model_admin, ct, pk, False)
    else:
        return HttpResponse('Unlocking objects.')
