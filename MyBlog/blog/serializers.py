from rest_framework import serializers, pagination
from .models import Post, Category

class PostSerializer(serializers.HyperlinkedModelSerializer):
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    tag = serializers.SlugRelatedField( # SlugRelatedField 如果是外键数据需要通过它来配置，定义外键是否可写 （read_only参数）
        many=True,
        read_only=True,
        slug_field='name' # slug_field 指定要展示的字段是什么
    )
    owner = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    created_time = serializers.DateTimeField(format="%￥-%m-%d %H:%M:%S")
    url = serializers.HyperlinkedIdentityField(view_name='api-post-detail')

    class Meta:
        model = Post
        fields = ['url', 'id', 'title', 'category','tag', 'owner','created_time']


class PostDetailSerializer(PostSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'category', 'tag', 'owner', 'content_html', 'created_time']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'created_time',
        )


"""详情页"""
class CategoryDetailSerializer(CategorySerializer):
    posts = serializers.SerializerMethodField('paginated_posts') # 将posts字段获取到的内容映射到 paginated_posts 方法上（posts对应的数据需要通过paginated_posts来获取）

    def paginated_posts(self, obj): # 实现对某个分类下文章列表的获取和分页
        posts = obj.post_set.filter(status=Post.STATUS_NORMAL)
        paginator = pagination.PageNumberPagination()
        page = paginator.paginate_queryset(posts, self.context['request'])
        serializers = PostSerializer(page, many=True, context={'request': self.context['request']})
        return {
            'count': posts.count(),
            'results': serializers.data,
            'previous': paginator.get_previous_link(),
            'next': paginator.get_next_link(),
        } # 返回的分页信息

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'created', 'posts',
        )