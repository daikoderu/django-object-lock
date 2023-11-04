from django.contrib import admin
from django.db import models
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _


class LockableAdminMixin(admin.ModelAdmin):
    """Mixin to allow model instances to be locked from the admin.

    Add the ``locked_icon`` field to ``list_display`` to display a "locked" icon in the changelist.

    To customize the appearance of the "locked" icon, set ``locked_icon_static_url`` to a static
    resource URL.
    """
    locked_icon_static_url = 'django_object_lock/images/locked.svg'


    def locked_icon(self, obj: models.Model) -> SafeString:
        return format_html(
            format_string='<img src="{src}" alt="{alt}" />',
            src=static(self.locked_icon_static_url), alt=_('Locked')
        )
    
    locked_icon.short_description = ''
