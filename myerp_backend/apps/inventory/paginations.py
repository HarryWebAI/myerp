from rest_framework.pagination import PageNumberPagination

class InventoryPagination(PageNumberPagination):
    page_size = 10