from rest_framework import serializers

from apps.brand.serializers import BrandSerializer
from apps.category.serializers import CategorySerializer
from apps.staff.serializers import StaffSerializer
from . import models


class InventorySerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    brand_id = serializers.IntegerField(write_only=True)
    category_id = serializers.IntegerField(write_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    current_inventory = serializers.SerializerMethodField(read_only=True)
    can_be_sold = serializers.SerializerMethodField(read_only=True)
    total_cost = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Inventory
        fields = "__all__"

    def get_full_name(self, obj):
        return obj.full_name()

    def get_current_inventory(self, obj):
        return obj.current_inventory()

    def get_can_be_sold(self, obj):
        return obj.can_be_sold()

    def get_total_cost(self, obj):
        return "{:.2f}".format(obj.total_cost())

class PurchaseSerializer(serializers.Serializer):
    brand_id = serializers.IntegerField(required=True)
    total_cost = serializers.DecimalField(required=True, max_digits=20, decimal_places=2)
    details = serializers.ListField(required=True)

class ReceiveSerializer(serializers.Serializer):
    brand_id = serializers.IntegerField(required=True)
    details = serializers.ListField(required=True)


class PurchaseListSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    user = StaffSerializer(read_only=True)
    class Meta:
        model = models.Purchase
        fields = "__all__"

class PurchaseDetailSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(read_only=True)

    class Meta:
        model = models.PurchaseDetail
        fields = '__all__'

class ReceiveListSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = models.Receive
        fields = ['id', 'brand_name', 'user_name', 'create_time']


class ReceiveDetailSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(read_only=True)
    
    class Meta:
        model = models.ReceiveDetail
        fields = '__all__'

class ReceiveLogSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    
    class Meta:
        model = models.ReceiveLog
        fields = ['id', 'content', 'operator_name', 'create_time']

class ReceiveDetailFullSerializer(serializers.ModelSerializer):
    details = ReceiveDetailSerializer(source='details.all', many=True, read_only=True)
    logs = ReceiveLogSerializer(source='ordered_logs', many=True, read_only=True)
    brand = BrandSerializer(read_only=True)
    user = StaffSerializer(read_only=True)
    
    class Meta:
        model = models.Receive
        fields = ['id', 'brand', 'user', 'create_time', 'details', 'logs']

class PurchaseLogSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    
    class Meta:
        model = models.PurchaseLog
        fields = ['id', 'content', 'operator_name', 'create_time']

class PurchaseDetailFullSerializer(serializers.ModelSerializer):
    details = PurchaseDetailSerializer(source='details.all', many=True, read_only=True)
    logs = PurchaseLogSerializer(source='ordered_logs', many=True, read_only=True)
    brand = BrandSerializer(read_only=True)
    user = StaffSerializer(read_only=True)
    
    class Meta:
        model = models.Purchase
        fields = ['id', 'brand', 'total_cost', 'user', 'create_time', 'details', 'logs']

class InventoryLogSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    
    class Meta:
        model = models.InventoryLog
        fields = ['id', 'content', 'operator_name', 'create_time']

