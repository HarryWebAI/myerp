from django.core.management.base import BaseCommand

from apps.brand.models import Brand


class Command(BaseCommand):
    def handle(self, *args, **options):

        Brand.objects.create(name='梦百合',intro='品牌介绍等待填充...')
        Brand.objects.create(name='绅图',intro='品牌介绍等待填充...')

        self.stdout.write('品牌初始化成功!')
