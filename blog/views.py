from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from .models import Blog,BlogType
from comment.models import Comment
from comment.forms import CommentForm
from read_record.models import ReadNum
from read_record.utils import read_record_once_read
from django.conf import settings
from datetime import datetime
from user.forms import LoginForm

def get_blog_list_common_data(request,blogs_all_list):
    paginator = Paginator(blogs_all_list,settings.BLOG_NUM_EACH_PAGE) # 每5篇一页
    page_num = request.GET.get('page',1) #获取页码参数（GET请求）1是默认
    page_of_blogs = paginator.get_page(page_num)
    blog_types = BlogType.objects.all()
    current_page_num = page_of_blogs.number # 获取当前页码
    # 去除页码 -1 和 0 以及超范围的页码
    page_range =list(range(max(current_page_num -2 ,1),current_page_num)) + \
                list(range(current_page_num,min(current_page_num + 3,paginator.num_pages + 1)))
    # 加上首页和尾叶
    if page_range[0] - 1 >= 2 :
        page_range.insert(0,1)
        page_range.insert(1,'…')
    if paginator.num_pages - page_range[-1] >=2:
        page_range.append('…')
        page_range.append(paginator.num_pages)

    # 还可以用anonatate的功能
    # BlogType.objects.annotate()
    # 获取博客分类对应数量  
    blog_types_list = []
    for blog_type in blog_types:
        blog_type.num = Blog.objects.filter(blog_type = blog_type).count()
        blog_types_list.append(blog_type)
    # 获取博客的评论数 
    for blog in  page_of_blogs:
        blog_content_type = ContentType.objects.get_for_model(blog)
        blog.comments_num = Comment.objects.filter(content_type = blog_content_type, object_id=blog.pk,parent = None).count()

    blog_dates = Blog.objects.dates('created_time','month',order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_date_num = Blog.objects.filter(created_time__year = blog_date.year,
                                            created_time__month = blog_date.month).count()
        blog_dates_dict[blog_date] = blog_date_num

    context = {}
    context['blogs'] = blogs_all_list
    context['page_of_blogs'] = page_of_blogs
    context['blog_types'] = blog_types_list
    context['page_range'] = page_range
    context['blog_dates'] = blog_dates_dict
    return context

def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request,blogs_all_list)
    return render(request,'blog/blog_list.html',context)
    

def blogs_with_type(request,blog_type_pk):
    blog_type = get_object_or_404(BlogType,pk=blog_type_pk)
    blogs_type_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_data(request,blogs_type_list)
    context['blogs_type'] = blog_type
    return render(request,'blog/blogs_with_type.html',context)

def blogs_with_date(request,year,month):
    #和前面不一样的取数据
    blogs_type_list = Blog.objects.filter(created_time__year=year,created_time__month=month)
    context = get_blog_list_common_data(request,blogs_type_list)
    blog_dates = Blog.objects.dates('created_time','month',order='DESC')
    context['blogs_with_date'] = '%s年%s月' % (year,month)
    return render(request,'blog/blogs_with_date.html',context)

def blog_detail(request,blog_pk):
    context ={}
    blog = get_object_or_404(Blog,pk=blog_pk)
    # 判断 COOKIE   
    read_cookie_key = read_record_once_read(request,blog)
    # 通过content type去找博客相对应的评论,1:传入实例blog 2：通过ID
    blog_content_type = ContentType.objects.get_for_model(blog)
    comments = Comment.objects.filter(content_type = blog_content_type, object_id=blog.pk,parent = None)

    context['comments'] = comments
    context['comment_form'] = CommentForm(initial={'content_type':blog_content_type.model,'object_id':blog.pk,'reply_comment_id':0})
    context['user'] = request.user
    context['next_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['previous_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    context['login_form'] = LoginForm()
    response = render(request,'blog/blog_detail.html',context)
    # 给browser 设置 阅读标记 COOKIE
    #response.set_cookie('blog_%s_read' % blog_pk,'true',max_age = 60,expires = datetime)
    response.set_cookie(read_cookie_key,'true',max_age = 60,expires = datetime)
    return response
