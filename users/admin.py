from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Role, Source


class RoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'protocol', 'role')
    search_fields = (
        'user__username',
        'project__name',
        'protocol__name'
    )
    list_filter = ('role',)


class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'isbn', 'url')


class ExtendedUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email',
                                         'scientific_degree')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'scientific_degree')


admin.site.register(User, ExtendedUserAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Source, SourceAdmin)
