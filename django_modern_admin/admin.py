from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.db import models

from .models import (AdminNavLogo, AdminLoginLogo, AdminProfile, AdminTasks)
from .widgets import ModernTextInputWidget, ModernSelectMultiple, ModernSplitDateTime

admin.site.unregister(Group)


@admin.register(Group)
class AdminGroup(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': ModernTextInputWidget},
        models.ManyToManyField: {'widget': ModernSelectMultiple},
    }


admin.site.unregister(User)


@admin.register(User)
class AdminUser(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': ModernTextInputWidget},
        models.ManyToManyField: {'widget': ModernSelectMultiple},
        models.DateTimeField: {'widget': ModernSplitDateTime}
    }


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user'
    ]


@admin.register(AdminNavLogo)
class AdminNavLogoAdmin(admin.ModelAdmin):
    list_display = ['logo_img']

    def has_add_permission(self, request):
        count = AdminNavLogo.objects.all().count()
        return True if count < 1 else False


@admin.register(AdminLoginLogo)
class AdminLoginLogoAdmin(admin.ModelAdmin):
    list_display = ['logo_img']

    def has_add_permission(self, request):
        count = AdminLoginLogo.objects.all().count()
        return True if count < 1 else False


@admin.register(AdminTasks)
class AdminTasksAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'date', 'isDone']
    readonly_fields = ['isDone']