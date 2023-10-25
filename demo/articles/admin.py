from django.contrib import admin

from articles.models import Article, Section


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('heading', 'parent', 'order')
    list_select_related = ('parent',)
