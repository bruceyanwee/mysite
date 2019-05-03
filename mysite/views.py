import datetime
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.contenttypes.models import ContentType
from read_record.utils import get_seven_days_readdata,get_today_hot_data,get_yesterday_hot_data,get_seven_days_hotdata
from blog.models import Blog
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from django.urls import reverse

def get_7_days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects \
                .filter(read_details__date__lt=today,read_details__date__gte=date) \
                .values('id','title') \
                .annotate(read_num_sum=Sum('read_details__read_num')) \
                .order_by('-read_num_sum')
    return blogs[:7]

def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates,read_nums = get_seven_days_readdata(blog_content_type)
    today_hot_data = get_today_hot_data(blog_content_type)
    yes_hot_data = get_yesterday_hot_data(blog_content_type)
    # 获取七天热门博客缓存数据
    week_hot_data = cache.get('week_hot_data')
    if week_hot_data is None:
        week_hot_data = get_7_days_hot_blogs()
        cache.set('week_hot_data',week_hot_data,3600)
        print('calc')
    else:
        print('use cache')
    context = {}
    context['read_nums'] = read_nums
    context['dates'] = dates
    context['today_hot_data'] = today_hot_data
    context['yes_hot_data'] = yes_hot_data
    context['week_hot_data'] = week_hot_data 
    return render(request,'home.html',context)

