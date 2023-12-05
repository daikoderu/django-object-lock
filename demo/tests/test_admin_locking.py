from django.contrib.auth.models import User
from django.db import models
from django.test import Client, TestCase
from django.urls import reverse

from articles.models import Article, ArticleSection


def get_admin_url(model_class: type[models.Model], admin_view: str, *args, **kwargs) -> str:
    info = model_class._meta.app_label, model_class._meta.model_name, admin_view
    return reverse('admin:%s_%s_%s' % info, *args, **kwargs)


class AdminLockingTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        articles = [
            Article(title='Article 1', is_locked_flag=False),
            Article(title='Article 2', is_locked_flag=True),
            Article(title='Article 3', is_locked_flag=True),
            Article(title='Article 4', is_locked_flag=False),
            Article(title='Article 5', is_locked_flag=True),
        ]
        Article.objects.bulk_create(articles)

        article_sections = [
            ArticleSection(parent=articles[0], heading='Section 1.1', content='Lorem', order=1),
            ArticleSection(parent=articles[1], heading='Section 2.1', content='Dolor', order=1),
        ]
        ArticleSection.objects.bulk_create(article_sections)

        cls.user = User.objects.create_superuser('foo', 'foo@example.com', '123')
        cls.client = Client()

    def setUp(self):
        self.client.force_login(self.user)

    def test_lock_icons_appear_in_changelist(self) -> None:
        response = self.client.get(get_admin_url(Article, 'changelist'), follow=True)
        self.assertIn(b'alt="Locked"', response.content)
