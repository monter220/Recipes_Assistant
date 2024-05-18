from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ReadOnlyModelViewSet,
    ModelViewSet,
    GenericViewSet,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_204_NO_CONTENT,
    HTTP_201_CREATED,
)

from core.permissions import IsOwnerOrReadOnly
from core.utils import download_shopcart
from .filters import RecipeFilter, IngredientFilter
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeWriteSerializer,
    TagSerializer,
    FavoriteSerializer,
    SubscribeListSerializer,
    SubscribeSerializer,
    UsersSerializer,
)
from users.models import Subscribe
from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    Favorite,
    ShoppingCart,
)


User = get_user_model()


class UsersViewSet(GenericViewSet):
    serializer_class = UsersSerializer
    queryset = User.objects.all()
    permissions = (AllowAny, )

    @action(
        detail=False,
        methods=['get', ],
        permission_classes=[IsAuthenticated, ]
    )
    def subscriptions(self, request):
        queryset = Subscribe.objects.filter(subscriber=request.user)
        if queryset:
            serializer = SubscribeListSerializer(
                self.paginate_queryset(queryset),
                many=True,
                context={'request': request},
            )
            return self.get_paginated_response(serializer.data)
        return Response(
            'Нет подписок',
            status=HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post', 'delete', ],
        permission_classes=[IsAuthenticated, ]
    )
    def subscribe(self, request, *args, **kwargs):
        subscriber = request.user
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data={'author': author.id, 'subscriber': subscriber.id, },
                context={'request': request, },
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'author': author.id, 'subscriber': subscriber.id, },
                status=HTTP_201_CREATED,
            )
        subscribe = get_object_or_404(
            Subscribe,
            subscriber=subscriber.id,
            author=author.id,
        )
        subscribe.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientFilter, ]
    search_fields = ['name', ]
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return RecipeWriteSerializer

    def add_or_remove(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            model.objects.filter(user=user, recipe__id=pk).delete()
            return Response(status=HTTP_204_NO_CONTENT)
        instance = model.objects.create(
            user=user, recipe=get_object_or_404(Recipe, pk=pk))
        serializer = FavoriteSerializer(instance)
        return Response(data=serializer.data, status=HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self.add_or_remove(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.add_or_remove(ShoppingCart, request.user, pk)


class DownloadCart(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return download_shopcart(
            list_ing=ShoppingCart.objects.filter(user=request.user).values(
                'recipe__ingredients__ingredient__name',
                'recipe__ingredients__ingredient__measurement_unit',
            ).order_by(
                'recipe__ingredients__ingredient__name'
            ).annotate(summ_amount=Sum('recipe__ingredients__amount'))
        )
