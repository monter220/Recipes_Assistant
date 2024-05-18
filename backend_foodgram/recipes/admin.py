from django.contrib.auth import get_user_model
from django.contrib import admin

from .models import (
    Amount,
    Ingredient,
    Recipe,
    Tag,
    Favorite,
    ShoppingCart,
)
from users.models import Subscribe


User = get_user_model()


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    empty_value_display = 'null'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)
    empty_value_display = 'null'


class AmountInLine(admin.TabularInline):
    model = Amount
    min_num = 1
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'text', 'in_favorite', )
    search_fields = ('name',)
    empty_value_display = 'null'
    inlines = [AmountInLine, ]

    def in_favorite(self, obj):
        return obj.favorite.all().count()

    in_favorite.short_description = 'Добавлен в избранное'


admin.site.register(User)
admin.site.register(Favorite)
admin.site.register(Subscribe)
admin.site.register(ShoppingCart)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
