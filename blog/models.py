from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from ckeditor_uploader.fields import RichTextUploadingField
from read_record.models import ReadNumExpandMethod,ReadDetail
from comment.models import Comment
# Create your models here.
# 博文 + 博客分类 

# 博客分类
# 一篇博客对应一种类别/多种类别
class BlogType(models.Model):
    type_name = models.CharField(max_length=15)
    def __str__(self):
        return self.type_name
# 博客数据
class Blog(models.Model,ReadNumExpandMethod):
    title = models.CharField(max_length=50)
    blog_type = models.ForeignKey(BlogType,on_delete=models.CASCADE)
    content = RichTextUploadingField()
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    read_details = GenericRelation(ReadDetail)
    #read_comment = GenericRelation(Comment)
    created_time = models.DateTimeField(auto_now_add=True)
    last_updated_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "<blog: %s>" % self.title
    class Meta:
        ordering = ['-created_time']

'''
class ReadNum(models.Model):
    views_num = models.IntegerField(default=0)
    blog = models.OneToOneField(Blog,on_delete=models.CASCADE)
'''