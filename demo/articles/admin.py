from django.contrib import admin
from django.db.models import QuerySet
from django.utils.safestring import SafeString
from django_object_lock.admin import LockableAdminMixin

from articles.models import Article, ArticleSection


@admin.register(Article)
class ArticleAdmin(LockableAdminMixin):
    list_display = ('locked_icon', 'title',)
    list_display_links = ('title',)
    fields = ('title', 'rendered_content')
    readonly_fields = ('rendered_content',)

    def rendered_content(self, obj: Article) -> SafeString:
        return obj.rendered_content
    
    def is_instance_locked(self, obj: Article) -> bool:
        return obj.is_locked

    def get_locked_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(is_locked=True)


@admin.register(ArticleSection)
class ArticleSectionAdmin(LockableAdminMixin):
    list_display = ('locked_icon', 'heading', 'parent', 'order')
    list_display_links = ('heading',)
    fields = ('parent', 'heading', 'content', 'order')
    list_select_related = ('parent',)

    def is_instance_locked(self, obj: Article) -> bool:
        return obj.parent.is_locked

    def get_locked_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(parent__is_locked=True)
