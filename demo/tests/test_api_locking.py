from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from articles.models import Article
from django_object_lock.api.exceptions import APIObjectLocked, APIObjectAlreadyLocked, APIObjectAlreadyUnlocked


class APILockingTestCase(TestCase):
    client = APIClient()
    articles = [
        Article(title='Article 1', is_locked_flag=False),
        Article(title='Article 2', is_locked_flag=True),
        Article(title='Article 3', is_locked_flag=False),
        Article(title='Article 4', is_locked_flag=True),
        Article(title='Article 5', is_locked_flag=True),
        Article(title='Article 6', is_locked_flag=False),
        Article(title='Article 7', is_locked_flag=False),
        Article(title='Article 8', is_locked_flag=True),
    ]

    @classmethod
    def setUpTestData(cls) -> None:
        Article.objects.bulk_create(cls.articles)

    def test_can_update_unlocked_resource(self) -> None:
        response = self.client.patch('/articles/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_update_locked_resource(self) -> None:
        response = self.client.patch('/articles/2/')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['detail'], APIObjectLocked.default_detail)

    def test_can_lock_unlocked_resource(self) -> None:
        response = self.client.patch('/articles/3/lock/')
        self.assertTrue(Article.objects.get(id=3).is_locked())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_lock_locked_resource(self) -> None:
        response = self.client.patch('/articles/4/lock/')
        self.assertTrue(Article.objects.get(id=4).is_locked())
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['detail'], APIObjectAlreadyLocked.default_detail)

    def test_can_unlock_locked_resource(self) -> None:
        response = self.client.patch('/articles/5/unlock/')
        self.assertFalse(Article.objects.get(id=5).is_locked())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_unlock_unlocked_resource(self) -> None:
        response = self.client.patch('/articles/6/unlock/')
        self.assertFalse(Article.objects.get(id=6).is_locked())
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['detail'], APIObjectAlreadyUnlocked.default_detail)

    def test_can_destroy_unlocked_resource(self) -> None:
        response = self.client.delete('/articles/7/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_destroy_locked_resource(self) -> None:
        response = self.client.delete('/articles/8/')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['detail'], APIObjectLocked.default_detail)
