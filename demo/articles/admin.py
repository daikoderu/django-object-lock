from django.contrib import admin
from django.utils.safestring import SafeString
from django_object_lock.admin import LockableAdminMixin

from articles.models import Article, ArticleSection


@admin.register(Article)
class ArticleAdmin(LockableAdminMixin):
    list_display = ('locked_icon', 'title',)
    fields = ('title', 'rendered_content')
    readonly_fields = ('rendered_content',)

    def rendered_content(self, obj: Article) -> SafeString:
        return obj.rendered_content


@admin.register(ArticleSection)
class ArticleSectionAdmin(LockableAdminMixin):
    list_display = ('locked_icon', 'heading', 'parent', 'order')
    fields = ('parent', 'heading', 'content', 'order')
    list_select_related = ('parent',)
