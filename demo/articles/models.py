from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from django_object_lock.models import LockableModel, AutoLockableModel


class Article(LockableModel, models.Model):
    title = models.CharField(
        _('title'), max_length=120,
        help_text=_('The title of this article.')
    )

    def __str__(self) -> str:
        return self.title


class Section(AutoLockableModel, models.Model):
    parent = models.ForeignKey(
        Article, verbose_name=_('parent article'), on_delete=models.CASCADE,
        help_text=_('The article containing this section.')
    )
    heading = models.CharField(
        _('heading'), max_length=120,
        help_text=_('The heading for this section.')
    )
    content = models.TextField(
        _('content'),
        help_text=_('The contents of this section.')
    )
    order = models.IntegerField(
        _('order'),
        help_text=_(
            'The relative position of this field in relation to other sections in the same '
            'report.'
        )
    )

    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        return self.heading
    
    @classmethod
    def get_locked_condition(cls) -> Q:
        return Q(parent__is_locked=True)
    