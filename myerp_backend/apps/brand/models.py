from django.db import models


class Brand(models.Model):
    """
    品牌模型
    """
    name = models.CharField(max_length=10, unique=True)
    intro = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)
