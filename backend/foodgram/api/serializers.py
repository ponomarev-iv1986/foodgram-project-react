import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import F
from django.shortcuts import get_object_or_404
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            file_format, imgstr = data.split(';base64,')
            ext = file_format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr),
                               name='img.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class AuthorShowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')
        read_only_fields = ('email', 'id', 'username',
                            'first_name', 'last_name')

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_anonymous:
            return False
        return current_user.subscriber.filter(author=obj).exists()


class RecipeListRetrieveSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorShowSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        return (
            obj.ingredients.values(
                'id', 'name', 'measurement_unit',
                amount=F('ingredientrecipes__amount')
            )
        )

    def get_is_favorited(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_anonymous:
            return False
        return Favorite.objects.filter(user=current_user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=current_user, recipe=obj
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = IngredientCreateSerializer(
        many=True, source='ingredientrecipes')
    author = author = AuthorShowSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredientrecipes')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data.pop('id')
            amount = ingredient_data.pop('amount')
            current_ingredient = get_object_or_404(Ingredient, pk=ingredient)
            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=current_ingredient, amount=amount
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        print(validated_data)
        ingredients_data = validated_data.pop('ingredientrecipes')
        tags = validated_data.pop('tags')
        IngredientRecipe.objects.filter(recipe=instance).delete()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data.pop('id')
            amount = ingredient_data.pop('amount')
            current_ingredient = get_object_or_404(Ingredient, pk=ingredient)
            IngredientRecipe.objects.create(
                recipe=instance, ingredient=current_ingredient, amount=amount
            )
        instance.tags.set(tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        context = {
            'request': self.context.get('request')
        }
        return RecipeListRetrieveSerializer(
            instance=instance,
            context=context
        ).data


class RecipeShowSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = RecipeShowSerializer(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('recipe',)

    def to_representation(self, instance):
        return RecipeShowSerializer(instance.recipe).data


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = RecipeShowSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('recipe',)

    def to_representation(self, instance):
        return RecipeShowSerializer(instance.recipe).data
