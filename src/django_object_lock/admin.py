from django.contrib import admin
from django.db import models
from django.db.models import QuerySet
from django.http.request import HttpRequest
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext_lazy as _


class LockableAdminMixin(admin.ModelAdmin):
    """Mixin to allow model instances to be locked from the admin.

    Implement ``is_instance_locked`` and ``get_locked_queryset`` to define what condition must be
    satisfied for an instance to be locked. For example, check whether a Boolean field is set to
    true (to let the user lock and unlock the instance manually) or depend on the "locked" status
    of a related instance.

    Add the ``locked_icon`` field to ``list_display`` to display a "locked" icon in the changelist.

    To customize the appearance of the "locked" icon, set ``locked_icon_static_url`` to a static
    resource URL.

    To allow manual object locking and/or unlocking, add the ``lock`` and/or ``unlock`` actions.
    """
    locked_icon_static_url = 'django_object_lock/images/locked.svg'


    def locked_icon(self, obj: models.Model) -> SafeString:
        return format_html(
            format_string='<img src="{src}" alt="{alt}" />',
            src=static(self.locked_icon_static_url), alt=_('Locked')
        ) if self.is_instance_locked(obj) else mark_safe('')
    
    locked_icon.short_description = ''

    def is_instance_locked(self, obj: models.Model) -> bool:
        """Implement this method returning ``True`` if the instance should be considered locked,
        and ``False`` otherwise.
        """
        raise NotImplementedError('This method must be implemented.')

    def get_locked_queryset(self, queryset: QuerySet, lock: bool) -> QuerySet:
        """Implement this method returning a ``QuerySet`` that returns only locked objects
        when ``lock`` is ``True`` or only unlocked objects when ``lock`` is ``False``.
        """
        raise NotImplementedError('This method must be implemented.')
    
    def set_locked_status(self, queryset: QuerySet, lock: bool):
        """Implement to lock or unlock a ``QuerySet`` of objects when the ``lock`` or ``unlock``
        actions are used.
        """
        raise NotImplementedError('This method must be implemented.')
    
    def has_change_permission(self, request: HttpRequest, obj: models.Model = None) -> bool:
        is_locked = obj is not None and self.is_instance_locked(obj)
        return not is_locked and super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request: HttpRequest, obj: models.Model = None) -> bool:
        is_locked = obj is not None and self.is_instance_locked(obj)
        return not is_locked and super().has_delete_permission(request, obj)

    @admin.action(description=_('Lock selected %(verbose_name_plural)s'))
    def lock(self, request: HttpRequest, queryset: QuerySet):
        self.set_locked_status(queryset, True)

    @admin.action(description=_('Unlock selected %(verbose_name_plural)s'))
    def unlock(self, request: HttpRequest, queryset: QuerySet):
        self.set_locked_status(queryset, False)