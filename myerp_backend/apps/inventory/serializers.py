from rest_framework import serializers

from apps.brand.serializers import BrandSerializer
from apps.category.serializers import CategorySerializer
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