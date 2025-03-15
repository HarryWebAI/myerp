from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = '执行系统初始化，包括创建超级用户、初始化品牌和商品分类'

    def handle(self, *args, **options):
        self.stdout.write('开始系统初始化...')
        
        # 执行创建超级用户命令
        self.stdout.write('1. 创建超级用户...')
        call_command('initsuperuser')
        
        # 执行初始化品牌命令
        self.stdout.write('2. 初始化品牌...')
        call_command('initbrands')
        
        # 执行初始化商品分类命令
        self.stdout.write('3. 初始化商品分类...')
        call_command('initcategories')
        
        self.stdout.write(self.style.SUCCESS('系统初始化完成！请使用账号 liuhaoyu 密码 111111 登录系统，并及时修改密码！')) 