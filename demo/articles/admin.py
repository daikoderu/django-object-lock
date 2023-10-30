from django.contrib import admin

from articles.models import Article, ArticleSection


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title',)

@admin.register(ArticleSection)
class ArticleSectionAdmin(admin.ModelAdmin):
    list_display = ('heading', 'parent', 'order')
    list_select_related = ('parent',)
