from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from articles.models import Article, ArticleSection


class APILockingTestCase(TestCase):
    factory = APIRequestFactory()
    articles = [
        Article(title='Article 1', is_locked_flag=False),
        Article(title='Article 2', is_locked_flag=True),
        Article(title='Article 3', is_locked_flag=True),
        Article(title='Article 4', is_locked_flag=False),
        Article(title='Article 5', is_locked_flag=True),
    ]
    article_sections = [
        ArticleSection(parent=articles[0], heading='Section 1.1', content='Lorem', order=1),
        ArticleSection(parent=articles[1], heading='Section 2.1', content='Dolor', order=1),
    ]

    @classmethod
    def setUpTestData(cls) -> None:
        Article.objects.bulk_create(cls.articles)
        ArticleSection.objects.bulk_create(cls.article_sections)
        cls.user = User.objects.create_superuser('foo', 'foo@example.com', '123')
