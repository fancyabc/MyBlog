import imp
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Post, Category, Tag
# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'is_nav', 'created_time')
    fields = ('name', 'status', 'is_nav')   # 控制页面上要展示的字段

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(CategoryAdmin, self).save_model(request, obj, form, change)

    def post_count(self, obj):
        return obj.post_set.count()
    
    post_count.short_description = "文章数量"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_time')
    fields = ('name', 'status')

    """ request.user 当前已经登陆的用户，
        obj 当前要保存的对象
        form 页面提交过来的表单之后的对象
        change 标志本次保存的数据是新增的还是更新的
    """
    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(TagAdmin, self).save_model(request, obj, form, change)



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = [
        'title','category','status',
        'created_time', 'operator'
    ]
    list_display_links = []     # 配置哪些字段可以作为链接，点击它们就可以进入编辑页面

    list_filter = ['category',] # 配置页面过滤器，需要哪些字段来过滤表页

    search_fields = ['title','category__name']  # 配置搜索字段

    action_on_top = True
    actions_on_bottom = True

    # 编辑页面
    save_on_top = True

#    exclude = ['owner']

    # fields配置有两个作用：1限定展示要显示的字段，2配置显示字段的顺序
    fields = (
        ('category','title'),    
        'tag',
        'status',
        'content',
    )

    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('admin:blog_post_change', args=(obj.id,))
        )

    operator.short_description = "操作"

    def save_model(self, request, obj, form, change):
        obj.owner = request.user    # 在此设置，文章的拥有者是当前登录用户
        return super(PostAdmin, self).save_model(request, obj, form, change)