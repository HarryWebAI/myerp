from django.db import models
from django.utils import timezone
from datetime import timedelta
from shortuuidfield import ShortUUIDField
from apps.staff.models import ERPUser

# Create your models here.

class Client(models.Model):
    """客户信息模型"""
    LEVEL_CHOICES = (
        (0, '已成交'),
        (1, '一级客户'),
        (2, '二级客户'),
        (3, '三级客户'),
        (4, '四级客户'),
        (5, '已流失'),
    )
    
    uid = ShortUUIDField(primary_key=True)
    name = models.CharField(max_length=30, verbose_name='客户姓名')
    telephone = models.CharField(max_length=20, verbose_name='联系电话', null=True, blank=True, unique=True)
    address = models.CharField(max_length=200, verbose_name='详细住址')
    remark = models.TextField(blank=True, null=True, verbose_name='备注信息')
    level = models.IntegerField(choices=LEVEL_CHOICES, default=1, verbose_name='客户级别')
    last_follow_time = models.DateTimeField(default=timezone.now, verbose_name='最近一次跟进时间')
    staff = models.ForeignKey(ERPUser, on_delete=models.CASCADE, related_name='clients', verbose_name='所属员工')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '客户'
        verbose_name_plural = verbose_name
        ordering = ['level', 'last_follow_time']
    
    def __str__(self):
        return self.name
    
    @property
    def latest_follow_time(self):
        """计算最晚跟进时间"""
        if self.level == 0 or self.level == 5:
            return None
        
        if self.level == 1:
            # 一级客户需要次日跟进
            return self.last_follow_time + timedelta(days=1)
        elif self.level == 2:
            # 二级客户需要一周内跟进
            return self.last_follow_time + timedelta(days=7)
        elif self.level == 3:
            # 三级客户需要一月内跟进
            return self.last_follow_time + timedelta(days=30)
        elif self.level == 4:
            # 四级客户不需要跟进
            return None
    
    @property
    def is_overdue(self):
        """判断是否需要跟进（包括一天内需要跟进的客户）"""
        latest_time = self.latest_follow_time
        if latest_time is None:
            return False
        
        # 当前时间（只取日期部分）
        now = timezone.now()
        today = now.date()
        
        # 最后跟进时间（只取日期部分）
        last_follow_date = self.last_follow_time.date()
        
        # 如果今天已经跟进了，不需要再次跟进
        if last_follow_date == today:
            return False
        
        # 一天后的时间
        one_day_later = now + timedelta(days=1)
        
        # 最晚跟进时间（转为日期比较）
        latest_date = latest_time.date()
        one_day_later_date = one_day_later.date()
        
        # 如果已经过期，或者最晚跟进时间在一天内，都视为需要跟进
        # 注意：这里用日期进行比较，而不是时间戳
        return today > latest_date or latest_date <= one_day_later_date


class FollowUpRecord(models.Model):
    """跟进记录模型"""
    uid = ShortUUIDField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='follow_records', verbose_name='跟进客户')
    staff = models.ForeignKey(ERPUser, on_delete=models.CASCADE, related_name='follow_records', verbose_name='跟进员工')
    content = models.TextField(verbose_name='跟进信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '跟进记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.client.name}的跟进记录-{self.created_at.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        """重写save方法，更新客户的最近一次跟进时间"""
        super().save(*args, **kwargs)
        # 更新客户的最近一次跟进时间
        self.client.last_follow_time = self.created_at
        self.client.save(update_fields=['last_follow_time'])
