from django.contrib import admin

from .models import UserFoodGram, Follow


class UserFoodGramAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')
    list_display = ('email', 'username', 'followers_count', 'recipes_count')
    readonly_fields = ('followers_count', 'recipes_count')

    def followers_count(self, obj):
        return Follow.objects.filter(following=obj).count()

    def recipes_count(self, obj):
        return obj.recipes.count()


admin.site.register(UserFoodGram, UserFoodGramAdmin)
