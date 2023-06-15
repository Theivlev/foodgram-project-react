from django.contrib import admin

# Register your models here.
from .models import UserFoodGram


class UserFoodGramAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')


admin.site.register(UserFoodGram, UserFoodGramAdmin)
