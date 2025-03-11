from rest_framework.pagination import PageNumberPagination

class ClientPagination(PageNumberPagination):
    """客户列表分页类"""
    page_size = 15  # 每页显示15条记录
    page_size_query_param = 'page_size'  # 允许客户端通过page_size参数覆盖页面大小
    max_page_size = 100  # 最大页面大小 