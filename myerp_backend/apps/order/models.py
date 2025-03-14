from django.db import models
from apps.client.models import Client
from apps.staff.models import ERPUser
from apps.inventory.models import Inventory
from apps.brand.models import Brand

# Create your models here.

class Installer(models.Model):
    """安装人员模型"""
    name = models.CharField(max_length=30, verbose_name='姓名')
    telephone = models.CharField(max_length=20, verbose_name='联系电话')
    
    class Meta:
        verbose_name = '安装人员'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.name


class Order(models.Model):
    """订单模型"""
    DELIVERY_STATUS_CHOICES = (
        (1, '新订单'),
        (2, '已送货'),
        (3, '已作废')
    )
    
    PAYMENT_STATUS_CHOICES = (
        (1, '未结清'),
        (2, '已结清'),
        (3, '已作废')
    )
    
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='orders', verbose_name='品牌')
    order_number = models.CharField(max_length=30, unique=True, verbose_name='订单编号')
    sign_time = models.DateTimeField(auto_now_add=True, verbose_name='签单时间')
    last_operation_time = models.DateTimeField(auto_now=True, verbose_name='最后一次操作时间')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders', verbose_name='客户信息')
    staff = models.ForeignKey(ERPUser, on_delete=models.CASCADE, related_name='orders', verbose_name='签单人员')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单总额')
    down_payment = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='首付定金')
    received_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='已收尾款')
    pending_balance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='待收尾款')
    delivery_status = models.IntegerField(choices=DELIVERY_STATUS_CHOICES, default=1, verbose_name='订单送货状态')
    payment_status = models.IntegerField(choices=PAYMENT_STATUS_CHOICES, default=1, verbose_name='订单结清状态')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='成本总价')
    installation_time = models.DateTimeField(null=True, blank=True, verbose_name='安装时间')
    installer = models.ForeignKey(Installer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name='安装人员')
    installation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='安装费用')
    transportation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='运输费用')
    gross_profit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='毛利润')
    address = models.CharField(max_length=200, verbose_name='安装地址')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = verbose_name
        ordering = ['-sign_time']
    
    def __str__(self):
        return f"订单 {self.order_number}"
    
    def save(self, *args, **kwargs):
        # 计算待收尾款 = 订单总额 - 首付定金 - 已收尾款
        self.pending_balance = self.total_amount - self.down_payment - self.received_balance
        
        # 计算毛利润 = 订单总额 - 成本总价 - 安装费用 - 运输费用
        self.gross_profit = self.total_amount - self.total_cost - self.installation_fee - self.transportation_fee
        
        # 更新订单结清状态，但如果订单已作废，则保持作废状态
        if self.delivery_status == 3:  # 如果订单已作废
            self.payment_status = 3  # 保持付款状态为已作废
        else:
            # 正常订单的付款状态逻辑
            if self.pending_balance <= 0:
                self.payment_status = 2  # 已结清
            else:
                self.payment_status = 1  # 未结清
            
        super().save(*args, **kwargs)


class OrderDetail(models.Model):
    """订单详情模型"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='details', verbose_name='所属订单')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='order_details', verbose_name='订购商品')
    quantity = models.IntegerField(verbose_name='订购数量')
    
    class Meta:
        verbose_name = '订单详情'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return f"{self.order} - {self.inventory.name} x {self.quantity}"


class BalancePayment(models.Model):
    """尾款收取模型"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='balance_payments', verbose_name='所属订单')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='本次收款')
    payment_time = models.DateTimeField(auto_now_add=True, verbose_name='收款时间')
    operator = models.ForeignKey(ERPUser, on_delete=models.CASCADE, related_name='balance_payments', verbose_name='操作人员')
    
    class Meta:
        verbose_name = '尾款收取'
        verbose_name_plural = verbose_name
        ordering = ['-payment_time']
    
    def __str__(self):
        return f"{self.order} - 收款 {self.amount}"
    
    def save(self, *args, **kwargs):
        # 保存尾款收取记录
        super().save(*args, **kwargs)
        
        # 更新订单的已收尾款
        order = self.order
        total_balance_payment = BalancePayment.objects.filter(order=order).aggregate(models.Sum('amount'))
        order.received_balance = total_balance_payment['amount__sum'] or 0
        order.save()


class OperationLog(models.Model):
    """操作日志模型"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='operation_logs', verbose_name='所属订单')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    description = models.TextField(verbose_name='操作说明')
    operator = models.ForeignKey(ERPUser, on_delete=models.CASCADE, related_name='operation_logs', verbose_name='操作人员')
    
    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order} - {self.created_at}"
