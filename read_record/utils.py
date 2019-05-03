import datetime
from django.contrib.contenttypes.models import ContentType
from .models import ReadNum,ReadDetail
from django.db.models import Sum
from django.utils import timezone

def read_record_once_read(request,obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model,obj.pk)
    if not request.COOKIES.get(key):
        # 如果该博客存在阅读计数的记录，加1 
        readnum,created = ReadNum.objects.get_or_create(content_type=ct,object_id=obj.pk)
        # 统一加1
        readnum.read_num += 1
        readnum.save()
        date = timezone.now().date()
        '''if ReadDetail.objects.filter(content_type=ct,object_id=obj.pk,date =date).count():
            read_detail = ReadDetail.objects.get(content_type=ct,object_id=obj.pk,date =date)
        else:
            read_detail = ReadDetail(content_type=ct,object_id=obj.pk,date =date)'''
        read_detail,created = ReadDetail.objects.get_or_create(content_type=ct,object_id=obj.pk,date = date)
        read_detail.read_num += 1
        read_detail.save()
    return key
def get_seven_days_readdata(content_type):
    today = timezone.now().date()
    read_nums = []
    dates = []
    for i in range(7,0,-1):
        date = today - datetime.timedelta(days=i)
        read_details = ReadDetail.objects.filter(content_type=content_type,date=date)
        result = read_details.aggregate(read_num_sum = Sum('read_num'))
        read_nums.append(result['read_num_sum'] or 0)
        dates.append(date.strftime("%m/%d"))
    return dates,read_nums

def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type = content_type,date = today).order_by('-read_num')
    return read_details[:7]
    
def get_yesterday_hot_data(content_type):
    today = timezone.now().date()
    yes = today - datetime.timedelta(days=1)
    read_details = ReadDetail.objects.filter(content_type = content_type,date = yes).order_by('-read_num')
    return read_details[:7]

# 分组统计
def get_seven_days_hotdata(content_type):
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    read_details = ReadDetail.objects \
                             .filter(content_type = content_type,date__lt=today,date__gte=date) \
                             .values('content_type','object_id') \
                             .annotate(read_num_sum = Sum('read_num')) \
                             .order_by('-read_num_sum')
    return read_details[:7]