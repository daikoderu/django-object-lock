from unittest.mock import patch

from django.contrib.admin import site
from django.contrib.auth.models import User
from django.db import models
from django.test import Client, TestCase
from django.urls import reverse

from articles_nonlockable.admin import NonLockableArticleAdmin
from articles_nonlockable.models import NonLockableArticle, NotImplementedModel


class NonModelLockableAdminLockingTestCase(TestCase):
    client = Client()
    admin_site_name = 'admin'
    article_admin = NonLockableArticleAdmin(NonLockableArticle, site)
    articles = [
        NonLockableArticle(title='Article 1', is_locked_flag=False),
        NonLockableArticle(title='Article 2', is_locked_flag=True),
    ]

    @classmethod
    def setUpTestData(cls) -> None:
        NonLockableArticle.objects.bulk_create(cls.articles)
        NotImplementedModel.objects.create()
        cls.user = User.objects.create_superuser('foo', 'foo@example.com', '123')

    def setUp(self):
        self.client.force_login(self.user)

    def get_admin_url(self, model_class: type[models.Model], admin_view: str, *args, **kwargs) -> str:
        info = self.admin_site_name, model_class._meta.app_label, model_class._meta.model_name, admin_view
        return reverse('%s:%s_%s_%s' % info, *args, **kwargs)

    @patch('articles_nonlockable.admin.NonLockableArticleAdmin.is_instance_locked')
    def test_admin_lock_is_called_when_no_model_locking(self, is_instance_locked) -> None:
        self.client.get(self.get_admin_url(NonLockableArticle, 'changelist'))
        is_instance_locked.assert_called()

    def test_not_implemented_error_raised_when_no_admin_lock_methods_and_no_model_locking(self) -> None:
        with self.assertRaises(NotImplementedError):
            self.client.get(self.get_admin_url(NotImplementedModel, 'changelist'))
