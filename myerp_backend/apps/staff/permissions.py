from rest_framework import permissions

class IsBoss(permissions.BasePermission):
    """
    老板权限
    """
    def has_permission(self, request, view):
        return request.user.is_boss

class IsManager(permissions.BasePermission):
    """
    经理权限
    """
    def has_permission(self, request, view):
        return request.user.is_manager  
    
class IsStorekeeper(permissions.BasePermission):
    """
    仓库管理员权限
    """
    def has_permission(self, request, view):
        return request.user.is_storekeeper

