from django_object_lock.api import mixins as dlo_mixins
from rest_framework import viewsets, serializers, mixins
from rest_framework.routers import DefaultRouter

from articles.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['url', 'title', 'is_locked_flag']
        read_only_fields = ['is_locked_flag']


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    dlo_mixins.LockableUpdateModelMixin,
    dlo_mixins.LockableDestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


router = DefaultRouter()
router.register(r'users', UserViewSet)
