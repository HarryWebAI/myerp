from django.core.management.base import BaseCommand

from apps.staff.models import ERPUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        ERPUser.objects.create_superuser(account='liuhaoyu', name='刘浩宇', telephone='13006462272',
                                                   password='111111')

        self.stdout.write('超级用户创建成功! 初始密码[6个1]! 请迅速登录并修改密码以确保系统安全!')
