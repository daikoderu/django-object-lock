from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django_object_lock.admin import LockableAdminMixin

from articles_nonlockable.models import NonLockableArticle


@admin.register(NonLockableArticle)
class ArticleAdmin(LockableAdminMixin, ModelAdmin):
    list_display = ('locked_icon', 'title',)
    list_display_links = ('title',)
    fields = ('title',)
    actions = ('lock', 'unlock')

    def is_instance_locked(self, obj: NonLockableArticle) -> bool:
        return obj.is_locked_flag

    def set_locked_status(self, obj: NonLockableArticle, lock: bool) -> None:
        obj.is_locked_flag = lock
