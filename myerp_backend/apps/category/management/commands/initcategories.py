from django.core.management.base import BaseCommand

from apps.category.models import Category


class Command(BaseCommand):
    def handle(self, *args, **options):

        Category.objects.create(name='沙发')
        Category.objects.create(name='茶几')
        Category.objects.create(name='床垫')
        Category.objects.create(name='软床')
        Category.objects.create(name='餐桌')
        Category.objects.create(name='餐椅')
        Category.objects.create(name='梳妆台')

        self.stdout.write('种类初始化成功!')
