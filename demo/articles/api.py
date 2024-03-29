from typing import Union

from django_object_lock.api import mixins as dol_mixins
from django_object_lock.mixins import LockableMixin
from rest_framework import viewsets, serializers, mixins
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from articles.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['url', 'title', 'is_locked_flag']
        read_only_fields = ['is_locked_flag']


class ArticleViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    dol_mixins.LockableUpdateModelMixin,
    dol_mixins.LockableDestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    @action(methods=['PUT', 'PATCH'], detail=True)
    def lock(self: LockableMixin, request: Request, pk: Union[int, str, None] = None) -> Response:
        return dol_mixins.lock_action(self, request, pk)

    @action(methods=['PUT', 'PATCH'], detail=True)
    def unlock(self: LockableMixin, request: Request, pk: Union[int, str, None] = None) -> Response:
        return dol_mixins.unlock_action(self, request, pk)


router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
