import random
from django.core.management.base import BaseCommand
from apps.staff.models import ERPUser


class Command(BaseCommand):
    help = '创建测试用的假员工数据'

    def handle(self, *args, **options):
        # 创建一个经理
        manager = ERPUser.objects.create_user(
            account='manager01',
            name='张经理',
            telephone='13800001111',
            password='123456',
            is_manager=True
        )
        self.stdout.write(self.style.SUCCESS(f'成功创建经理: {manager.name}'))

        # 创建两个仓库管理员
        for i in range(1, 3):
            storekeeper = ERPUser.objects.create_user(
                account=f'store{i:02d}',
                name=f'王仓管{i}',
                telephone=f'1380000{i+1000}',
                password='123456',
                is_storekeeper=True
            )
            self.stdout.write(self.style.SUCCESS(f'成功创建仓库管理员: {storekeeper.name}'))

        # 创建多个普通员工
        first_names = ["李", "张", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
        last_names = ["小", "大", "明", "华", "强", "勇", "伟", "芳", "娜", "静"]
        
        for i in range(1, 11):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            full_name = f"{first_name}{last_name}"
            
            staff = ERPUser.objects.create_user(
                account=f'staff{i:02d}',
                name=full_name,
                telephone=f'1390000{1000+i}',
                password='123456'
            )
            self.stdout.write(self.style.SUCCESS(f'成功创建普通员工: {staff.name}'))

        self.stdout.write(self.style.SUCCESS('测试员工数据创建完成！')) 