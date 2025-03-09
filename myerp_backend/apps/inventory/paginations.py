from rest_framework.pagination import PageNumberPagination

class InventoryPagination(PageNumberPagination):
    page_size = 10

class PurchasePagination(PageNumberPagination):
    page_size = 20