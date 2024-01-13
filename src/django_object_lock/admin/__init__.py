from functools import update_wrapper
from typing import Optional, List

from django.db import models
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.http.request import HttpRequest
from django.templatetags.static import static
from django.urls import path, reverse
from django.urls.resolvers import URLPattern
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext_lazy as _

from django_object_lock.admin.views import default_lock_view, default_unlock_view
from django_object_lock.mixins import LockableMixin
from django_object_lock.settings import dol_settings


class LockableAdminMixin(LockableMixin):
    """Mixin to allow model instances to be locked from the admin.

    Add the ``locked_icon`` field to ``list_display`` to display a "locked" icon in the changelist.

    To customize the appearance of the "locked" icon, set ``locked_icon_static_url`` to a static
    resource URL.

    To allow manual object locking and/or unlocking, add the ``lock`` and/or ``unlock`` actions.
    """
    locked_icon_url: str = dol_settings.DEFAULT_LOCKED_ICON_URL
    lock_view = default_lock_view
    unlock_view = default_unlock_view

    class Media:
        css = {
            'all': ['django_object_lock/css/admin.css'],
        }

    def locked_icon(self, obj: models.Model) -> SafeString:
        return self.locked_icon_html(obj) if self.is_instance_locked(obj) else mark_safe('')

    locked_icon.short_description = ''

    def locked_icon_html(self, obj: models.Model) -> SafeString:
        alt = _('%(obj_str)s is locked') % {'obj_str': str(obj)}
        return format_html(
            format_string='<img src="{src}" alt="{alt}" title="{alt}" />', src=static(self.locked_icon_url), alt=alt
        )

    def has_change_permission(self, request: HttpRequest, obj: Optional[models.Model] = None) -> bool:
        return not (obj is not None and self.is_instance_locked(obj)) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj: Optional[models.Model] = None) -> bool:
        return not (obj is not None and self.is_instance_locked(obj)) and super().has_delete_permission(request, obj)

    def get_urls(self) -> List[URLPattern]:
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        extra_urls = []
        info = self.opts.app_label, self.opts.model_name

        if 'lock' in self.actions:
            extra_urls.append(path('lock/', wrap(self.lock_view), name='%s_%s_lock' % info))
        if 'unlock' in self.actions:
            extra_urls.append(path('unlock/', wrap(self.unlock_view), name='%s_%s_unlock' % info))

        return [*extra_urls, *super().get_urls()]

    def lock(self, request: HttpRequest, queryset: QuerySet) -> HttpResponseRedirect:
        info = self.admin_site.name, self.opts.app_label, self.opts.model_name
        path = reverse('%s:%s_%s_lock' % info)
        pks = ','.join(str(pk) for pk in queryset.values_list('pk', flat=True))
        return HttpResponseRedirect('%s?ids=%s' % (path, pks))

    lock.short_description = _('Lock selected %(verbose_name_plural)s')

    def unlock(self, request: HttpRequest, queryset: QuerySet) -> HttpResponseRedirect:
        info = self.admin_site.name, self.opts.app_label, self.opts.model_name
        path = reverse('%s:%s_%s_unlock' % info)
        pks = ','.join(str(pk) for pk in queryset.values_list('pk', flat=True))
        return HttpResponseRedirect('%s?ids=%s' % (path, pks))

    unlock.short_description = _('Unlock selected %(verbose_name_plural)s')
