from rest_framework.pagination import PageNumberPagination

class OrderPagination(PageNumberPagination):
    """订单列表分页器"""
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 50

class OrderDetailPagination(PageNumberPagination):
    """订单详情分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class OperationLogPagination(PageNumberPagination):
    """操作日志分页器"""
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100

class BalancePaymentPagination(PageNumberPagination):
    """尾款支付分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50 