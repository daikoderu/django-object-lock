from django.test import TestCase
from django_object_lock.exceptions import ObjectLocked

from articles.models import Article, ArticleSection


class ModelLockingTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        articles = [
            Article(title='Article 1', is_locked_flag=False),
            Article(title='Article 2', is_locked_flag=True),
            Article(title='Article 3', is_locked_flag=True),
            Article(title='Article 4', is_locked_flag=False),
            Article(title='Article 5', is_locked_flag=True),
        ]
        for article in articles:
            article.save()

        article_sections = [
            ArticleSection(parent=articles[0], heading='Section 1.1', content='Lorem', order=1),
            ArticleSection(parent=articles[1], heading='Section 2.1', content='Dolor', order=1),
        ]
        ArticleSection.objects.bulk_create(article_sections)

    def test_unlocked_instance_can_be_saved(self) -> None:
        article = Article.objects.get(pk=1)
        article.title = 'Article 1 Edited'
        article.save()
        self.assertEqual(Article.objects.get(pk=1).title, 'Article 1 Edited')

    def test_locked_instance_cannot_be_saved(self) -> None:
        article = Article.objects.get(pk=2)
        with self.assertRaises(ObjectLocked):
            article.title = 'Article 2 Edited'
            article.save()
        self.assertEqual(Article.objects.get(pk=2).title, 'Article 2')

    def test_locked_instance_can_be_saved_when_unlocked(self) -> None:
        article = Article.objects.get(pk=3)
        article.set_locked(False)
        article.title = 'Article 3 Edited'
        article.save()
        self.assertEqual(Article.objects.get(pk=3).title, 'Article 3 Edited')

    def test_related_locked_instance_cannot_be_saved(self) -> None:
        article_section = ArticleSection.objects.get(pk=2)
        with self.assertRaises(ObjectLocked):
            article_section.heading = 'Section 2.1 Edited'
            article_section.save()
        self.assertEqual(ArticleSection.objects.get(pk=2).heading, 'Section 2.1')

    def test_related_unlocked_instance_can_be_saved(self) -> None:
        article_section = ArticleSection.objects.get(pk=1)
        article_section.heading = 'Section 1.1 Edited'
        article_section.save()
        self.assertEqual(ArticleSection.objects.get(pk=1).heading, 'Section 1.1 Edited')

    def test_unlocked_instance_can_be_deleted(self) -> None:
        article = Article.objects.get(pk=4)
        article.delete()
        self.assertEqual(article.pk, None)

    def test_locked_instance_cannot_be_deleted(self) -> None:
        article = Article.objects.get(pk=5)
        with self.assertRaises(ObjectLocked):
            article.delete()
        self.assertEqual(article.pk, 5)
