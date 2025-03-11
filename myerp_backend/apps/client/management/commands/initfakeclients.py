import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from faker import Faker

from apps.staff.models import ERPUser
from apps.client.models import Client, FollowUpRecord


class Command(BaseCommand):
    help = '创建测试用的假客户数据，包含今天(2025-03-11)需要跟进的客户'

    def handle(self, *args, **options):
        # 初始化faker
        fake = Faker('zh_CN')
        
        # 获取所有员工
        staffs = ERPUser.objects.filter(is_staff=True, is_boss=False)
        if not staffs.exists():
            self.stdout.write(self.style.ERROR('没有找到员工数据，请先运行initfakeusers命令创建员工数据'))
            return
        
        self.stdout.write('开始创建客户测试数据...')
        
        # 设置"今天"为2025-03-11
        test_date = datetime(2025, 3, 11)
        
        # 清除现有客户数据(可选)
        Client.objects.all().delete()
        FollowUpRecord.objects.all().delete()
        self.stdout.write('已清除现有客户数据...')
        
        # 创建一级客户（持续跟进）- 昨天跟进，今天需要再次跟进
        self.stdout.write('创建持续跟进客户(昨天跟进)...')
        for i in range(10):
            staff = random.choice(staffs)
            last_follow_date = test_date - timedelta(days=1)  # 昨天跟进
            
            client = Client.objects.create(
                name=f"持续跟进客户{i+1}",
                telephone=fake.phone_number(),
                address=fake.address(),
                remark="一级客户，昨天跟进，今天需要再次跟进",
                level=1,  # 一级客户
                staff=staff,
                last_follow_time=last_follow_date
            )
            
            # 创建跟进记录
            FollowUpRecord.objects.create(
                client=client,
                staff=staff,
                content=f"昨天的跟进内容：{fake.sentence()}",
                created_at=last_follow_date
            )
        
        # 创建二级客户（潜在客户）- 7天前跟进，今天需要再次跟进
        self.stdout.write('创建潜在客户(7天前跟进)...')
        for i in range(10):
            staff = random.choice(staffs)
            last_follow_date = test_date - timedelta(days=7)  # 7天前跟进
            
            client = Client.objects.create(
                name=f"潜在客户{i+1}",
                telephone=fake.phone_number(),
                address=fake.address(),
                remark="二级客户，7天前跟进，今天需要再次跟进",
                level=2,  # 二级客户
                staff=staff,
                last_follow_time=last_follow_date
            )
            
            # 创建跟进记录
            FollowUpRecord.objects.create(
                client=client,
                staff=staff,
                content=f"7天前跟进内容：{fake.sentence()}",
                created_at=last_follow_date
            )
        
        # 创建三级客户（暂时观望）- 30天前跟进，今天需要再次跟进
        self.stdout.write('创建暂时观望客户(30天前跟进)...')
        for i in range(10):
            staff = random.choice(staffs)
            last_follow_date = test_date - timedelta(days=30)  # 30天前跟进
            
            client = Client.objects.create(
                name=f"暂时观望客户{i+1}",
                telephone=fake.phone_number(),
                address=fake.address(),
                remark="三级客户，30天前跟进，今天需要再次跟进",
                level=3,  # 三级客户
                staff=staff,
                last_follow_time=last_follow_date
            )
            
            # 创建跟进记录
            FollowUpRecord.objects.create(
                client=client,
                staff=staff,
                content=f"30天前跟进内容：{fake.sentence()}",
                created_at=last_follow_date
            )
        
        # 创建不需要跟进的客户组 - 跟进时间未到
        self.stdout.write('创建不需要跟进的客户(跟进时间未到)...')
        
        # 一级客户今天已跟进
        for i in range(5):
            staff = random.choice(staffs)
            client = Client.objects.create(
                name=f"今日已跟进客户{i+1}",
                telephone=fake.phone_number(),
                address=fake.address(),
                remark="一级客户，今天已经跟进过了",
                level=1,
                staff=staff,
                last_follow_time=test_date  # 今天已跟进
            )
            
            FollowUpRecord.objects.create(
                client=client,
                staff=staff,
                content="今天的跟进内容，不应出现在需要跟进列表中",
                created_at=test_date
            )
            
        # 二级客户6天前跟进（未到7天）
        for i in range(5):
            staff = random.choice(staffs)
            last_follow_date = test_date - timedelta(days=6)  # 6天前跟进
            
            client = Client.objects.create(
                name=f"未到期潜在客户{i+1}",
                telephone=fake.phone_number(),
                address=fake.address(),
                remark="二级客户，6天前跟进，还未到再次跟进时间",
                level=2,
                staff=staff,
                last_follow_time=last_follow_date
            )
            
            FollowUpRecord.objects.create(
                client=client,
                staff=staff,
                content="6天前的跟进内容，不应出现在需要跟进列表中",
                created_at=last_follow_date
            )
            
        # 三级客户29天前跟进（未到30天）
        for i in range(5):
            staff = random.choice(staffs)
            last_follow_date = test_date - timedelta(days=29)  # 29天前跟进
            
            client = Client.objects.create(
                name=f"未到期观望客户{i+1}",
                telephone=fake.phone_number(),
                address=fake.address(),
                remark="三级客户，29天前跟进，还未到再次跟进时间",
                level=3,
                staff=staff,
                last_follow_time=last_follow_date
            )
            
            FollowUpRecord.objects.create(
                client=client,
                staff=staff,
                content="29天前的跟进内容，不应出现在需要跟进列表中",
                created_at=last_follow_date
            )
            
        # 创建其他类型客户 - 已成交/希望渺茫/已流失
        self.stdout.write('创建其他类型客户(已成交/希望渺茫/已流失)...')
        for level, level_name in [(0, "已成交"), (4, "希望渺茫"), (5, "已流失")]:
            for i in range(5):
                staff = random.choice(staffs)
                last_follow_date = test_date - timedelta(days=random.randint(1, 10))
                
                client = Client.objects.create(
                    name=f"{level_name}客户{i+1}",
                    telephone=fake.phone_number(),
                    address=fake.address(),
                    remark=f"{level_name}客户，无需定期跟进",
                    level=level,
                    staff=staff,
                    last_follow_time=last_follow_date
                )
                
                FollowUpRecord.objects.create(
                    client=client,
                    staff=staff,
                    content=f"{level_name}客户跟进内容，无需出现在需要跟进列表中",
                    created_at=last_follow_date
                )
        
        # 统计需要跟进的客户数量
        total_count = Client.objects.count()
        self.stdout.write(self.style.SUCCESS(f'成功创建 {total_count} 个客户测试数据！'))
        
        # 计算应该在2025-03-11需要跟进的客户数量
        from django.db.models import Q
        
        # 为了计算需要跟进的客户，临时修改系统时间
        original_now = timezone.now
        timezone.now = lambda: test_date
        
        try:
            need_follow_count = 0
            need_follow_clients = []
            
            for client in Client.objects.filter(~Q(level=0) & ~Q(level=4) & ~Q(level=5)):
                if client.is_overdue:
                    need_follow_count += 1
                    need_follow_clients.append(client.name)
            
            self.stdout.write(self.style.SUCCESS(f'其中在2025-03-11需要跟进的客户有 {need_follow_count} 个'))
            self.stdout.write(f'需要跟进的客户: {", ".join(need_follow_clients[:10])}' + ('...' if len(need_follow_clients) > 10 else ''))
        finally:
            # 恢复系统时间函数
            timezone.now = original_now 