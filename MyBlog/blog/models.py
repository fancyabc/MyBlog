from django.db import models

from django.contrib.auth.models import User
from django.utils.functional import cached_property

# Create your models here.
import mistune

# 每个Moddel相当于数据库中的一个数据表，Field相当于数据库中的一个字段

class Category(models.Model):   # 继承Django的Model
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )

    name = models.CharField(max_length=50, verbose_name="名称")
    status = models.PositiveIntegerField(default=STATUS_NORMAL,choices=STATUS_ITEMS, verbose_name="状态")
    is_nav = models.BooleanField(default=False, verbose_name="是否为导航")
    owner = models.ForeignKey(User, verbose_name="作者", on_delete=models.DO_NOTHING)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间") # auto_now_add 为True会默认填充当前事件

    class Meta:
        verbose_name = verbose_name_plural = "分类"

    def __str__(self):
        return self.name
    
    @classmethod
    def get_navs(cls):
        categories = cls.objects.filter(status=cls.STATUS_NORMAL)
        '''
        # QuerySet惰性特征，下面两个对象在使用时会分别产生自己的查询语句，对系统来说是两次I/O操作
        nav_categories = categories.filter(is_nav=True)
        normal_categories = categories.filter(is_nav=False)
        '''
        # 改进，只需要一次I/O操作
        nav_categories = []
        normal_categories = []

        for cate in categories:
            if cate.is_nav:
                nav_categories.append(cate)
            else:
                normal_categories.append(cate)

        return {
            'navs': nav_categories,
            'categories': normal_categories,
        }


class Tag(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )

    name = models.CharField(max_length=10, verbose_name="名称")
    status = models.PositiveIntegerField(default=STATUS_NORMAL,
                                        choices=STATUS_ITEMS, verbose_name="状态")
    owner = models.ForeignKey(User, verbose_name="作者", on_delete=models.DO_NOTHING)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = verbose_name_plural = "标签"

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_DRAFT = 2
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
        (STATUS_DRAFT, '草稿'),
    )

    title = models.CharField(max_length=255, verbose_name="标题")
    desc = models.CharField(max_length=1024, blank=True, verbose_name="摘要")
    content = models.TextField(verbose_name="正文", help_text="正文必须为Markdown格式")
    status = models.PositiveIntegerField(default=STATUS_NORMAL,
        choices=STATUS_ITEMS, verbose_name="状态")
    category = models.ForeignKey(Category, verbose_name="分类", on_delete=models.DO_NOTHING)
    tag = models.ManyToManyField(Tag, verbose_name="标签")
    owner = models.ForeignKey(User, verbose_name="作者", on_delete=models.DO_NOTHING)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    content_html = models.TextField(verbose_name="正文html代码", blank=True, editable=False)

    pv = models.PositiveIntegerField(default=1)
    uv = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = verbose_name_plural = "文章"
        ordering = ['-id'] # id进行降序排列

    def __str__(self):
        return self.title

    @staticmethod
    def get_by_tag(tag_id):
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            tag = None
            post_list = []
        else:
            post_list = tag.post_set.filter(status=Post.STATUS_NORMAL)\
                .select_related('owner', 'category')
        return post_list, tag

    @staticmethod
    def get_by_category(category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            category = None
            post_list = []
        else:
            post_list = category.post_set.filter(status=Post.STATUS_NORMAL)\
                .select_related('owner', 'category')
        
        return post_list, category

    @classmethod
    def latest_posts(cls, with_related=True):
        queryset = cls.objects.filter(status=cls.STATUS_NORMAL)
        if with_related:
            queryset = queryset.select_related('owner','category')
        return queryset

    def save(self, *args, **kwargs):
        self.content_html = mistune.markdown(self.content)
        super().save(*args, **kwargs)

    @classmethod
    def hot_posts(cls):
        return cls.objects.filter(status=cls.STATUS_NORMAL).order_by('-pv')

    @cached_property
    def tags(self):
        return ','.join(self.tag.values_list('name', flat=True))