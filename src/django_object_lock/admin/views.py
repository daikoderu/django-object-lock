from typing import TYPE_CHECKING, Union, Type

from django.contrib import messages
from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import ngettext_lazy as n_

if TYPE_CHECKING:  # pragma: no cover
    from django_object_lock.admin import LockableAdminMixin


def get_lockable_objects(model: Type[Model], pk_string: str) -> QuerySet:
    try:
        return model.objects.filter(pk__in=pk_string.strip().split(','))
    except ValueError:
        return model.objects.none()


def default_lock_or_unlock_view(
    modeladmin: 'LockableAdminMixin', request: HttpRequest, lock: bool
) -> Union[TemplateResponse, HttpResponseRedirect]:
    model = modeladmin.model
    ids_string = request.POST.get('ids', request.GET.get('ids', ''))
    objects = [
        obj for obj in get_lockable_objects(model, ids_string)
        if modeladmin.is_instance_locked(obj) != lock
    ]
    count = len(objects)
    if request.method == 'POST':
        # POST method, so we lock/unlock.
        for obj in objects:
            modeladmin.set_locked_status(obj, lock)
            obj.save()
        info = modeladmin.admin_site.name, modeladmin.opts.app_label, modeladmin.opts.model_name

        # Show a success message.
        if lock:
            success_message = n_(
                '%(count)d %(name)s object has been successfully locked.',
                '%(count)d %(name)s objects have been successfully locked.',
                count
            )
        else:
            success_message = n_(
                '%(count)d %(name)s object has been successfully unlocked.',
                '%(count)d %(name)s objects have been successfully unlocked.',
                count
            )
        messages.success(request, success_message % {
            'count': count,
            'name': model._meta.verbose_name,
        })

        # Redirect to the changelist.
        return HttpResponseRedirect(reverse('%s:%s_%s_changelist' % info))
    else:
        # Show a confirmation message.
        action = 'lock' if lock else 'unlock'
        context = {
            **modeladmin.admin_site.each_context(request),
            'objects': objects,
            'count': count,
            'lock': lock,
            'ids': ','.join(str(obj.pk) for obj in objects),
            'opts': model._meta  # noqa
        }
        return TemplateResponse(request, 'django_object_lock/admin_%s.html' % action, context)


def default_lock_view(modeladmin: 'LockableAdminMixin', request: HttpRequest):
    """Default lock confirmation view for the Django admin.
    """
    return default_lock_or_unlock_view(modeladmin, request, True)


def default_unlock_view(modeladmin: 'LockableAdminMixin', request: HttpRequest):
    """Default unlock confirmation view for the Django admin.
    """
    return default_lock_or_unlock_view(modeladmin, request, False)
