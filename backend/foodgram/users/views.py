from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription
from .serializers import ShowSubscriptionsSerializer, SubscribeSerializer

User = get_user_model()


class ListSubscriptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ShowSubscriptionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(subscriptions__user=user)


class SubscribeViewSet(mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        author = get_object_or_404(User, id=self.kwargs['user_id'])
        user = self.request.user
        if Subscription.objects.filter(
            user=user, author=author
        ).exists():
            raise serializers.ValidationError(
                'Подписка на пользователя уже есть.'
            )
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        serializer.save(user=self.request.user, author=author)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        subscription = get_object_or_404(
            Subscription, user=request.user, author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
