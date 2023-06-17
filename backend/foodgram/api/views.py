from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .permission import IsAuthorOrAdmin
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeListRetrieveSerializer,
                          ShoppingCartSerializer, TagSerializer)
from .utils import download_cart


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrAdmin)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListRetrieveSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        return download_cart(request=request)


class ShoppingCartViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        if ShoppingCart.objects.filter(
            user=self.request.user, recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже есть в списке покупок.'
            )
        serializer.save(user=self.request.user, recipe=recipe)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        shoppingcart = get_object_or_404(
            ShoppingCart, user=request.user, recipe=recipe)
        shoppingcart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        if Favorite.objects.filter(
            user=self.request.user, recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже есть в избранных.'
            )
        serializer.save(user=self.request.user, recipe=recipe)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite = get_object_or_404(
            Favorite, user=request.user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
