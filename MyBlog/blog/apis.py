from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from .models import Post, Category
from .serializers import(
    PostSerializer, PostDetailSerializer,
    CategorySerializer,CategoryDetailSerializer
) 


class PostViewSet(viewsets.ModelViewSet):
    """提供文章接口"""
    serializer_class = PostSerializer # serializer_class 所有的数据都会通过这个配置进行序列化，通过重写详情数据的接口，然后指定 serializer_class
    queryset = Post.objects.filter(status=Post.STATUS_NORMAL)
    # permission_classes = [IsAdminUser]    # 写入时的权限校验

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = PostDetailSerializer # 在此重新设置serializer_class的值， 达到了不同接口使用不同 Serializer的目的
        return super().retrieve(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(status=Category.STATUS_NORMAL)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = CategoryDetailSerializer
        return super().retrieve(request, *args, **kwargs)