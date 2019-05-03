from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.auth.models import User

class Comment(models.Model):
    # 评论的对象是不确定的，用contenttype坐中间关联
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,related_name="comment",on_delete=models.CASCADE)
    root = models.ForeignKey('self',related_name='root_comment',null=True,on_delete=models.CASCADE)
    parent = models.ForeignKey('self',related_name='parent_comment',null = True,on_delete=models.CASCADE)
    reply_to = models.ForeignKey(User,related_name="reply",null = True, on_delete=models.CASCADE)

    def __str__(self):
        return self.text
    class Meta:
        ordering = ['-comment_time']

'''class Reply(models.Model):
    # 回复数据库表 与之相关的包括 userA 回复 commentB 
    comment = models.ForeignKey(Comment,on_delete=models.CASCADE)'''