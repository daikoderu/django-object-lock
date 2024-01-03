from django.db import models
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext_lazy as _
from django_object_lock.models import LockableModel


class Article(LockableModel):
    """Example of a model that can be locked.
    """
    title = models.CharField(_('title'), max_length=120, help_text=_('The title of this article.'))
    is_locked_flag = models.BooleanField(
        _('is locked'), default=False, help_text=_('Whether this article is locked or not.')
    )

    def __str__(self) -> str:
        return f'Article "{self.title}"'

    def is_locked(self) -> bool:
        return self.is_locked_flag

    def set_locked(self, value: bool) -> None:
        self.is_locked_flag = value

    @property
    def rendered_content(self) -> SafeString:
        return mark_safe('\n\n'.join(
            format_html('<h1>{heading}</h1>{content}', heading=section.heading, content=section.content)
            for section in self.sections.all()
        ))


class ArticleSection(LockableModel):
    """Example of a model that is related to a model that can be locked.

    An ``ArticleSection`` is locked if and only if the related ``Article`` is locked.
    """
    parent = models.ForeignKey(
        Article, verbose_name=_('parent article'), on_delete=models.CASCADE, related_name='sections',
        help_text=_('The article containing this section.')
    )
    heading = models.CharField(_('heading'), max_length=120, help_text=_('The heading for this section.'))
    content = models.TextField(_('content'), help_text=_('The contents of this section.'))
    order = models.IntegerField(
        _('order'),
        help_text=_('The relative position of this field in relation to other sections in the same article.')
    )

    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        return f'ArticleSection "{self.heading}"'

    def is_locked(self) -> bool:
        return self.parent.is_locked_flag


class NotLockedModel(models.Model):
    """Example of a model that cannot be locked.
    """
    name = models.CharField(_('name'), max_length=120, help_text=_('The name of this instance.'))

    def __str__(self) -> str:
        return f'NotLockedModel "{self.name}"'
