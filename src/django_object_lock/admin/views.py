from django.contrib.admin import ModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse


def parse_pks(pk_string: str) -> list[int] | list[str]:
    pk_strings = pk_string.strip().split(',')
    try:
        return [int(x) for x in pk_strings]
    except ValueError:
        return [x.strip() for x in pk_strings if x]


def lock_or_unlock_by_pk(
    modeladmin: ModelAdmin, request: HttpRequest, pk: int | str, lock: bool
) -> None:
    queryset = modeladmin.get_queryset(request)
    try:
        obj = queryset.get(pk=pk)
        if modeladmin.is_instance_locked(obj) != lock:
            modeladmin.set_locked_status(obj, True)
            obj.save()
    except (modeladmin.model.DoesNotExist, ValidationError, ValueError):
        pass


def default_lock_or_unlock_view(
    modeladmin: ModelAdmin, request: HttpRequest, lock: bool
) -> TemplateResponse | HttpResponseRedirect:
    pk_list = parse_pks(request.GET.get('ids', ''))
    if request.method == 'POST' and request.POST.get('post', False) == 'yes':
        # POST method with confirmation, so we lock/unlock.
        for pk in pk_list:
            lock_or_unlock_by_pk(modeladmin, request, pk, lock)
    else:
        # Show a confirmation message.
        action = 'lock' if lock else 'unlock'
        model = modeladmin.model
        context = {
            **modeladmin.admin_site.each_context(request),
            'objects': model.objects.filter(pk__in=pk_list),
            'lock': lock,
            'opts': model._meta  # noqa
        }
        return TemplateResponse(request, 'django_object_lock/admin_%s.html' % action, context)


def default_lock_view(modeladmin: ModelAdmin, request: HttpRequest):
    """Default lock confirmation view for the Django admin.
    """
    return default_lock_or_unlock_view(modeladmin, request, True)


def default_unlock_view(modeladmin: ModelAdmin, request: HttpRequest):
    """Default unlock confirmation view for the Django admin.
    """
    return default_lock_or_unlock_view(modeladmin, request, False)
