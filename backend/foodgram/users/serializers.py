from api.serializers import RecipeShowSerializer
from django.contrib.auth import get_user_model
from djoser.serializers import (SetPasswordSerializer, UserCreateSerializer,
                                UserSerializer)
from rest_framework import serializers

from .models import Subscription
from .validators import validate_email

User = get_user_model()


class UserShowSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_anonymous:
            return False
        return current_user.subscriber.filter(author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        max_length=254, allow_blank=False, validators=[validate_email]
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def to_representation(self, instance):
        return UserShowSerializer(instance).data


class CustomSetPasswordSerializer(SetPasswordSerializer):
    class Meta:
        model = User
        fields = ('new_password', 'current_password')


class ShowSubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    # recipes = RecipeShowSerializer(many=True, read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'id', 'username',
                            'first_name', 'last_name')

    def get_is_subscribed(self, obj):
        return True  # Подписка осуществлена, поэтому всегда True

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = RecipeShowSerializer(recipes, many=True, read_only=True)
        return serializer.data


class SubscribeSerializer(serializers.ModelSerializer):
    author = ShowSubscriptionsSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ('author',)

    def to_representation(self, instance):
        return ShowSubscriptionsSerializer(instance.author).data
