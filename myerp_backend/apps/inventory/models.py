from django.db import models

from apps.brand.models import Brand
from apps.category.models import Category
from apps.staff.models import ERPUser


class Inventory(models.Model):
    name = models.CharField(max_length=30)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='inventories',
                              related_query_name='inventories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='inventories',
                                 related_query_name='inventories')
    size = models.CharField(max_length=15, default='原版')
    color = models.CharField(max_length=15, default='原色')
    cost = models.DecimalField(max_digits=20, decimal_places=2)
    on_road = models.IntegerField(default=0)
    in_stock = models.IntegerField(default=0)
    been_order = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)

    def full_name(self):
        return self.name + f'({self.size},{self.color})'

    def current_inventory(self):
        return self.on_road + self.in_stock

    def can_be_sold(self):
        return self.current_inventory() - self.been_order

    def total_cost(self):
        return self.current_inventory() * self.cost

class Purchase(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='purchase', related_query_name='purchase')
    total_cost = models.DecimalField(max_digits=20, decimal_places=2)
    user = models.ForeignKey(ERPUser, on_delete=models.CASCADE, related_name='purchaser', related_query_name='purchaser')
    create_time = models.DateTimeField(auto_now_add=True)

class PurchaseDetail(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='details', related_query_name='details')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='purchase_details', related_query_name='purchase_details')
    quantity = models.IntegerField()

class Receive(models.Model):
    # 关联到品牌
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='receive', related_query_name='receive')
    # 负责入库的人员
    user = models.ForeignKey(ERPUser, on_delete=models.CASCADE, related_name='receiver', related_query_name='receiver')
    # 入库时间
    create_time = models.DateTimeField(auto_now_add=True)

class ReceiveDetail(models.Model):
    # 关联到入库单
    receive = models.ForeignKey(Receive, on_delete=models.CASCADE, related_name='details', related_query_name='details')
    # 关联到库存项
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='receive_details', related_query_name='receive_details')
    # 入库数量
    quantity = models.IntegerField()

class PurchaseLog(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='logs', related_query_name='logs')
    content = models.TextField()
    operator = models.ForeignKey(ERPUser, on_delete=models.CASCADE, related_name='purchase_logs', related_query_name='purchase_logs')
    create_time = models.DateTimeField(auto_now_add=True)

class ReceiveLog(models.Model):
    receive = models.ForeignKey(Receive, on_delete=models.CASCADE, related_name='logs', related_query_name='logs')
    content = models.TextField()
    operator = models.ForeignKey(ERPUser, on_delete=models.CASCADE, related_name='receive_logs', related_query_name='receive_logs')
    create_time = models.DateTimeField(auto_now_add=True)
    
