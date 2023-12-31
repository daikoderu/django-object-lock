from typing import Type

from django.contrib.admin import site
from django.contrib.auth.models import User
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.db import models
from django.http import HttpResponseRedirect
from django.templatetags.static import static
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.html import format_html

from articles.admin import ArticleAdmin, ArticleSectionAdmin
from articles.models import Article, ArticleSection, NotLockedModel


class AdminLockingTestCase(TestCase):
    client = Client()
    admin_site_name = 'admin'
    article_admin = ArticleAdmin(Article, site)
    article_section_admin = ArticleSectionAdmin(ArticleSection, site)
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
    not_lockeds = [
        NotLockedModel(name='foo'),
    ]

    @classmethod
    def setUpTestData(cls) -> None:
        for article in cls.articles:
            article.save()
        ArticleSection.objects.bulk_create(cls.article_sections)
        NotLockedModel.objects.bulk_create(cls.not_lockeds)
        cls.user = User.objects.create_superuser('foo', 'foo@example.com', '123')

    def setUp(self):
        self.client.force_login(self.user)

    def get_admin_url(self, model_class: Type[models.Model], admin_view: str, *args, **kwargs) -> str:
        info = self.admin_site_name, model_class._meta.app_label, model_class._meta.model_name, admin_view
        return reverse('%s:%s_%s_%s' % info, *args, **kwargs)

    def test_lock_icons_appear_in_changelist_for_locked_objects(self) -> None:
        response = self.client.get(self.get_admin_url(Article, 'changelist'))
        self.assertIn(self.article_admin.locked_icon_html(self.articles[1]).encode(), response.content)

    def test_lock_icons_do_not_appear_in_changelist_for_unlocked_objects(self) -> None:
        response = self.client.get(self.get_admin_url(Article, 'changelist'))
        self.assertNotIn(self.article_admin.locked_icon_html(self.articles[0]).encode(), response.content)

    def test_change_page_is_readonly_for_locked_objects(self) -> None:
        response = self.client.get(self.get_admin_url(Article, 'change', args=(2,)))
        self.assertNotIn(b'Save', response.content)

    def test_change_page_is_editable_for_unlocked_objects(self) -> None:
        response = self.client.get(self.get_admin_url(Article, 'change', args=(1,)))
        self.assertIn(b'Save', response.content)

    def test_add_page_is_always_editable(self) -> None:
        response = self.client.get(self.get_admin_url(Article, 'add'))
        self.assertIn(b'Save', response.content)

    def test_default_lock_icon_is_used_in_changelist(self) -> None:
        self.assertIn(
            format_html('src="{src}"', src=static(self.article_admin.locked_icon_url)),
            self.article_admin.locked_icon_html(self.articles[1])
        )

    def test_custom_lock_icon_is_used_in_changelist(self) -> None:
        self.assertIn(
            format_html('src="{src}"', src=static(self.article_section_admin.locked_icon_url)),
            self.article_section_admin.locked_icon_html(self.article_sections[1])
        )

    def test_lock_action_redirects(self) -> None:
        response = self.client.post(self.get_admin_url(Article, 'changelist'), data={
            'action': 'lock',
            ACTION_CHECKBOX_NAME: '1',
        })
        self.assertIsInstance(response, HttpResponseRedirect)

    def test_unlock_action_redirects(self) -> None:
        response = self.client.post(self.get_admin_url(Article, 'changelist'), data={
            'action': 'unlock',
            ACTION_CHECKBOX_NAME: '1',
        })
        self.assertIsInstance(response, HttpResponseRedirect)

    def test_lock_action_shows_affected_instances(self) -> None:
        response = self.client.get(self.get_admin_url(Article, 'lock'), data={'ids': '1'})
        self.assertIn(b'Articles: 1', response.content)
        self.assertIn(b'Article 1', response.content)

    def test_unlock_action_shows_affected_instances(self) -> None:
        response = self.client.get(self.get_admin_url(Article, 'unlock'), data={'ids': '2,5'})
        self.assertIn(b'Articles: 2', response.content)
        self.assertIn(b'Article 2', response.content)
        self.assertIn(b'Article 5', response.content)

    def test_lock_action_with_invalid_parameters_shows_no_instances(self) -> None:
        response = self.client.get(self.get_admin_url(Article, 'lock'), data={'ids': 'a'})
        self.assertIn(b'No objects have been selected', response.content)

    def test_unlock_action_with_invalid_parameters_shows_no_instances(self) -> None:
        response = self.client.get(self.get_admin_url(Article, 'unlock'), data={'ids': 'a'})
        self.assertIn(b'No objects have been selected', response.content)

    def test_lock_action_locks_on_confirmation(self) -> None:
        self.client.post(self.get_admin_url(Article, 'lock'), data={'ids': '4'})
        self.assertTrue(Article.objects.get(id=4).is_locked())

    def test_unlock_action_unlocks_on_confirmation(self) -> None:
        self.client.post(self.get_admin_url(Article, 'unlock'), data={'ids': '3'})
        self.assertFalse(Article.objects.get(id=3).is_locked())

    def test_is_locked_not_defined_in_model_nor_admin_raises_not_implemented(self) -> None:
        with self.assertRaises(NotImplementedError):
            self.client.get(self.get_admin_url(NotLockedModel, 'changelist'))

    def test_set_locked_not_defined_in_model_nor_admin_raises_not_implemented(self) -> None:
        with self.assertRaises(NotImplementedError):
            self.client.post(self.get_admin_url(NotLockedModel, 'lock'), data={'ids': '1'})
