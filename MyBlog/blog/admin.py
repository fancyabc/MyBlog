import imp
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Post, Category, Tag
from .adminform import PostAdminForm
from MyBlog.custom_site import custom_site
from MyBlog.base_admin import BaseOwnerAdmin
# Register your models here.


class PostInline(admin.TabularInline):  # StackedInline样式不同
    #fields = ('title', 'desc','owner','content') # 这样可以直接在目录下编辑文章，但是不合适
    fields = ('title', 'desc')
    extra = 1 # 控制额外多几个
    model = Post


@admin.register(Category, site=custom_site)
class CategoryAdmin(BaseOwnerAdmin):
    inlines = [PostInline, ]

    list_display = ('name', 'status', 'is_nav', 'created_time')
    fields = ('name', 'status', 'is_nav')   # 控制页面上要展示的字段

    def post_count(self, obj):
        return obj.post_set.count()
    
    post_count.short_description = "文章数量"


@admin.register(Tag, site=custom_site)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'created_time')
    fields = ('name', 'status')


class CategoryOwnerFilter(admin.SimpleListFilter):
    """自定义过滤器只展示单前用户分类"""

    title = '分类过滤器'    # 由 SimpleListFilter 类提供
    parameter_name = 'owner_category'   # 由 SimpleListFilter 类提供

    # 由 SimpleListFilter 类提供，返回要展示的内容和查询用的id
    def lookups(self,request, model_admin):
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    # 由 SimpleListFilter 类提供，根据URL Query的内容返回列表页数据
    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=self.value())
        return queryset


@admin.register(Post, site=custom_site)
class PostAdmin(BaseOwnerAdmin):
    # 使用自定义Form
    form = PostAdminForm

    list_display = [
        'title','category','status',
        'created_time', 'owner','operator'
    ]
    list_display_links = []     # 配置哪些字段可以作为链接，点击它们就可以进入编辑页面

#    list_filter = ['category',] # 配置页面过滤器，需要哪些字段来过滤表页
    list_filter = [CategoryOwnerFilter] # 使用上面那个过滤器

    search_fields = ['title','category__name']  # 配置搜索字段

    action_on_top = True
    actions_on_bottom = True

    # 编辑页面
    save_on_top = True

    exclude = ('owner',)

    '''
    # fields配置有两个作用：1限定展示要显示的字段，2配置显示字段的顺序
    fields = (
        ('category','title'),    
        'tag',
        'status',
        'content',
    )
    '''
    # filedsets用来控制页面布局,格式是由两个元素的tuple的list
    fieldsets = (
        ('基础配置',{
            'fields':(
                ('title','category'),
                'status',
                'tag',
            ),
        }),
        ('内容信息',{
            'fields':(
                'desc',
                'content',
            ),
        }),       
    )
    filter_vertical = ('tag',)

    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('cus_admin:blog_post_change', args=(obj.id,))
        )

    operator.short_description = "操作"

    '''引入自定义静态资源'''

    class Media:
        css = {
            'all':("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css",),
        }
        js = ("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js",)
