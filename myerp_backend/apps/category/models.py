from django.db import models


class Category(models.Model):
    """
    商品种类模型
    """
    name = models.CharField(max_length=10, unique=True)
    create_time = models.DateTimeField(auto_now_add=True)
