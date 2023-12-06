from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.safestring import SafeString
from django_object_lock.admin import LockableAdminMixin

from articles.models import Article, ArticleSection


@admin.register(Article)
class ArticleAdmin(LockableAdminMixin, ModelAdmin):
    list_display = ('locked_icon', 'title',)
    list_display_links = ('title',)
    fields = ('title', 'rendered_content')
    readonly_fields = ('rendered_content',)
    actions = ('lock', 'unlock')

    def rendered_content(self, obj: Article) -> SafeString:
        return obj.rendered_content


@admin.register(ArticleSection)
class ArticleSectionAdmin(LockableAdminMixin, ModelAdmin):
    list_display = ('locked_icon', 'heading', 'parent', 'order')
    list_display_links = ('heading',)
    fields = ('parent', 'heading', 'content', 'order')
    list_select_related = ('parent',)
