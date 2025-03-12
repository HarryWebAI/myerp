from django.core.management.base import BaseCommand

from apps.order.models import Installer


class Command(BaseCommand):
    def handle(self, *args, **options):
        # 创建安装师傅
        Installer.objects.create(
            name='张师傅',
            telephone='12345678899'
        )
        
        Installer.objects.create(
            name='唐师傅',
            telephone='12345678890'
        )

        self.stdout.write('安装师傅初始化成功!') 