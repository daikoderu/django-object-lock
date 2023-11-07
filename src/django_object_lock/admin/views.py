from django.contrib.admin import ModelAdmin
from django.db.models import Model, QuerySet
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse


def get_lockable_objects(model: type[Model], pk_string: str) -> QuerySet[Model]:
    try:
        return model.objects.filter(pk__in=pk_string.strip().split(','))
    except ValueError:
        return model.objects.none()


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
    model = modeladmin.model
    objects = [
        obj for obj in get_lockable_objects(model, request.GET.get('ids', ''))
        if obj.is_locked() != lock
    ]
    if request.method == 'POST' and request.POST.get('post', False) == 'yes':
        # POST method with confirmation, so we lock/unlock.
        for obj in objects:
            modeladmin.set_locked_status(obj, True)
            obj.save()
        info = modeladmin.admin_site.name, modeladmin.opts.app_label, modeladmin.opts.model_name
        return HttpResponseRedirect(reverse('%s:%s_%s_changelist' % info))
    else:
        # Show a confirmation message.
        action = 'lock' if lock else 'unlock'
        context = {
            **modeladmin.admin_site.each_context(request),
            'objects': objects,
            'count': len(objects),
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
