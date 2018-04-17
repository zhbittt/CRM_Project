from stark.service import v1
from rbac import models
class MenuStarkConfig(v1.StarkConfig):
    list_display = ['id','title']
    edit_link = ['title']
v1.site.registry(models.Menu,MenuStarkConfig)

class GroupStarkConfig(v1.StarkConfig):
    list_display = ['id','caption','menu']
    edit_link = ['caption']
v1.site.registry(models.Group,GroupStarkConfig)

class PermissionStarkConfig(v1.StarkConfig):
    list_display = ['id','title','url','menu_gp','code','group']
    edit_link = ['title']
v1.site.registry(models.Permission,PermissionStarkConfig)

class UserStarkConfig(v1.StarkConfig):
    list_display = ['id','username','password','email']
    edit_link = ['username']
v1.site.registry(models.User,UserStarkConfig)

class RoleStarkConfig(v1.StarkConfig):
    list_display = ['id','title','permissions']
    edit_link = ['title']
v1.site.registry(models.Role,RoleStarkConfig)