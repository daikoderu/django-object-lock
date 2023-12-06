from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArticlesNonlockableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'articles_nonlockable'
    verbose_name = _('Articles Demo (models not lockable)')
