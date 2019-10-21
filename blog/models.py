from django.db import models
from user.models import User
from django.utils import timezone
from django.conf import settings
import time
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=10, verbose_name='分类名')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'category'


class Tag(models.Model):
    name = models.CharField(max_length=10, unique=True, verbose_name='标签名')
    count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'tag'

def upload_to_blog_path(instance, filename):
    return 'blog/cover/%s/%s' % ('article_'+str(instance.pk), filename)

# def default_cover(instance):
#     if instance.is_markdown:
#         return '/static/images/default/markdown.png'
#     else:
#         return '/static/images/default/blog.jpg'

class Article(models.Model):  # 文章

    # id = models.AutoField(primary_key=True)  # 博客id
    # author_id = models.CharField(blank=False, max_length=50)  # 作者id
    author = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(default='untitled', max_length=50)
    summary = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)
    # updated_at = models.FloatField(default=time.time(), null=True)
    # created_at = models.FloatField(default=time.time(), null=True)
    updated_at = models.DateTimeField(default=timezone.now())
    created_at = models.DateTimeField(default=timezone.now())
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    # tags = models.CharField(max_length=200, blank=True, null=True)
    tags = models.ManyToManyField(Tag)
    views = models.IntegerField(default=0)
    is_markdown = models.BooleanField(default=True)
    cover = models.ImageField(upload_to=upload_to_blog_path, null=True, blank=True) # default='/static/images/default/markdown.png'



    class Meta:
        db_table = 'articles'

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        # if self.is_markdown:
        #     self.cover = '/static/images/default/markdown.png'
        # else:
        #     self.cover = '/static/images/default/blog.jpg'
        super(Article, self).save(*args, **kwargs)




class Comment(models.Model):    # 评论

    # id = models.AutoField(primary_key=True)
    # user_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE,  related_name='article_comment')
    # reply_to = models.IntegerField(null=True, blank=True)
    # content = models.CharField(max_length=500, default='')
    content = models.TextField()
    display = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_reply =models.BooleanField(default=True, verbose_name='是否是回复')
    reply_to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='user_to_reply')
    topic = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='主题', related_name='comment_topic', null=True)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='reply')

    class Meta:
        db_table = 'comment'




