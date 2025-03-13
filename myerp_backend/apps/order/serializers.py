from rest_framework import serializers
from apps.inventory.models import Inventory
from apps.brand.serializers import BrandSerializer
from apps.client.serializers import ClientListSerializer
from apps.staff.serializers import StaffSerializer
from decimal import Decimal

from .models import Order, OrderDetail, BalancePayment, OperationLog, Installer


class OrderCreateSerializer(serializers.Serializer):
    """订单创建序列化器"""
    order_number = serializers.CharField(required=True, max_length=30)
    brand_id = serializers.IntegerField(required=True)
    client_id = serializers.CharField(required=True)
    staff_id = serializers.CharField(required=True)
    total_amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    down_payment = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    total_cost = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    gross_profit = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    address = serializers.CharField(required=True, max_length=200)
    remark = serializers.CharField(required=False, default='', max_length=200)
    details = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
            required=True
        ),
        required=True
    )
    
    def validate(self, data):
        """验证数据"""
        # 验证订单总金额、首付款、成本、毛利润之间的关系
        if data['total_amount'] < data['down_payment']:
            raise serializers.ValidationError("首付定金不能大于订单总额")
        
        # 验证毛利润计算是否正确
        calculated_gross_profit = data['total_amount'] - data['total_cost']
        if abs(calculated_gross_profit - data['gross_profit']) > Decimal('0.01'):
            raise serializers.ValidationError("毛利润计算有误")
        
        # 验证待收尾款计算是否正确(total_amount - down_payment)
        pending_balance = data['total_amount'] - data['down_payment']
        if pending_balance < 0:
            raise serializers.ValidationError("待收尾款不能为负数")
        
        # 验证详情列表不能为空
        if not data['details']:
            raise serializers.ValidationError("订单详情不能为空")
        
        # 验证每个详情项的inventory_id和quantity
        for item in data['details']:
            if 'inventory_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError("订单详情项必须包含inventory_id和quantity")
            
            if item['inventory_id'] <= 0:
                raise serializers.ValidationError("商品ID必须大于0")
            
            if item['quantity'] <= 0:
                raise serializers.ValidationError("商品数量必须大于0")
            
            # 验证库存商品是否存在
            try:
                inventory = Inventory.objects.get(id=item['inventory_id'])
                # 验证商品是否属于指定品牌
                if inventory.brand_id != data['brand_id']:
                    raise serializers.ValidationError(f"商品 {inventory.full_name} 不属于所选品牌")
            except Inventory.DoesNotExist:
                raise serializers.ValidationError(f"商品ID {item['inventory_id']} 不存在")
        
        return data


class InstallerSerializer(serializers.ModelSerializer):
    """安装人员序列化器"""
    
    class Meta:
        model = Installer
        fields = ['id', 'name', 'telephone']


class OrderDetailSerializer(serializers.ModelSerializer):
    """订单详情序列化器"""
    inventory_data = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = OrderDetail
        fields = ['id', 'inventory_id', 'quantity', 'inventory_data']
    
    def get_inventory_data(self, obj):
        """获取商品详细信息"""
        inventory = obj.inventory
        if inventory:
            return {
                'id': inventory.id,
                'name': inventory.name,
                'full_name': inventory.full_name() if hasattr(inventory, 'full_name') else f"{inventory.name}",
                'category': inventory.category.name if inventory.category else '',
                'cost': float(inventory.cost)
            }
        return None


class BalancePaymentSerializer(serializers.ModelSerializer):
    """尾款收取序列化器"""
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    
    class Meta:
        model = BalancePayment
        fields = ['id', 'order', 'amount', 'payment_time', 'operator', 'operator_name']
        read_only_fields = ['operator', 'payment_time']
    
    def validate_amount(self, value):
        """验证金额必须大于0"""
        if value <= 0:
            raise serializers.ValidationError("支付金额必须大于0")
        return value
    
    def validate(self, data):
        """验证整体数据，确保支付金额不超过订单的待收尾款"""
        order = data.get('order')
        amount = data.get('amount')
        
        if order and amount and amount > order.pending_balance:
            raise serializers.ValidationError({
                'amount': f"支付金额(¥{amount})不能超过待收尾款(¥{order.pending_balance})"
            })
        
        return data


class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器"""
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    
    class Meta:
        model = OperationLog
        fields = ['id', 'description', 'created_at', 'operator', 'operator_name']
        read_only_fields = ['created_at']


class OrderListSerializer(serializers.ModelSerializer):
    """订单列表序列化器"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    staff_name = serializers.CharField(source='staff.name', read_only=True)
    delivery_status_display = serializers.CharField(source='get_delivery_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'brand_name', 'client_name', 'staff_name',
            'sign_time', 'total_amount', 'down_payment', 'pending_balance',
            'total_cost', 'gross_profit', 'delivery_status', 'delivery_status_display',
            'payment_status', 'payment_status_display', 'address'
        ]


class OrderSerializer(serializers.ModelSerializer):
    """订单详细序列化器"""
    brand = BrandSerializer(read_only=True)
    client = ClientListSerializer(read_only=True)
    staff = StaffSerializer(read_only=True)
    installer = InstallerSerializer(read_only=True)
    details = OrderDetailSerializer(many=True, read_only=True)
    delivery_status_display = serializers.CharField(source='get_delivery_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    operation_logs = OperationLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'brand', 'client', 'staff',
            'sign_time', 'last_operation_time', 'total_amount', 'down_payment',
            'received_balance', 'pending_balance', 'delivery_status', 'delivery_status_display',
            'payment_status', 'payment_status_display', 'total_cost', 'installation_time',
            'installer', 'installation_fee', 'transportation_fee', 'gross_profit',
            'details', 'operation_logs', 'address', 'remark'
        ]

class OrderInstallSerializer(serializers.Serializer):
    """订单安装序列化器"""
    installer_id = serializers.IntegerField(required=True)
    installation_fee = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    transportation_fee = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    
    def validate_installer_id(self, value):
        """验证安装人员ID是否有效"""
        try:
            installer = Installer.objects.get(id=value)
            return installer  # 返回安装人员实例而不是ID
        except Installer.DoesNotExist:
            raise serializers.ValidationError(f"找不到ID为{value}的安装人员")
    
    def validate(self, attrs):
        """验证费用是否为负数"""
        if attrs.get('installation_fee', 0) < 0:
            raise serializers.ValidationError({"installation_fee": "安装费用不能为负数"})
        
        if attrs.get('transportation_fee', 0) < 0:
            raise serializers.ValidationError({"transportation_fee": "运输费用不能为负数"})
        
        return attrs


