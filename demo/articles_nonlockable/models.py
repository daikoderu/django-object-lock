from django.db import models
from django.utils.translation import gettext_lazy as _


class NonLockableArticle(models.Model):
    """Example of a model that cannot be locked.
    """
    title = models.CharField(_('title'), max_length=120, help_text=_('The title of this article.'))
    is_locked_flag = models.BooleanField(
        _('is locked'), default=False, help_text=_('Whether this article is locked or not.')
    )
