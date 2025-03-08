from django.db import models

from apps.brand.models import Brand
from apps.category.models import Category


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
