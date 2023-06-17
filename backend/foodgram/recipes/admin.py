from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe, Tag,
                     TagRecipe)


class TagInLine(admin.TabularInline):
    model = TagRecipe
    extra = 3


class IngredientInLine(admin.TabularInline):
    model = IngredientRecipe
    extra = 3


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'favorites']
    list_filter = ['name', 'author', 'tags']
    inlines = (TagInLine, IngredientInLine)

    def favorites(self, obj):
        if Favorite.objects.filter(recipe=obj).exists():
            return Favorite.objects.filter(recipe=obj).count()
        return 0


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    list_editable = ['measurement_unit']
    list_filter = ['name']
