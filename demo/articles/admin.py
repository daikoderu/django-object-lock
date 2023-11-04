from django.contrib import admin
from django.utils.safestring import SafeString

from articles.models import Article, ArticleSection


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title',)
    fields = ('title', 'rendered_content')
    readonly_fields = ('rendered_content',)

    def rendered_content(self, obj: Article) -> SafeString:
        return obj.rendered_content


@admin.register(ArticleSection)
class ArticleSectionAdmin(admin.ModelAdmin):
    list_display = ('heading', 'parent', 'order')
    fields = ('parent', 'heading', 'content', 'order')
    list_select_related = ('parent',)
