
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import *

# Register your models here.
User = get_user_model()

class UserAdmin(admin.ModelAdmin):
    list_display = ('email','is_active','is_staff','is_superuser','date_joined',)
    search_fields = ('email',)
    fields = ('email','first_name','last_name','is_superuser','is_staff',
              'is_active','password','date_joined','last_login',
              'groups','user_permissions')
    readonly_fields = ('last_login', 'date_joined', 'password')
    ordering = ('email',)

admin.site.register(User, UserAdmin)
admin.site.register(Movie)
admin.site.register(Collection)
admin.site.register(MoviesCollection)
