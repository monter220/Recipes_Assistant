from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Amount,
    Ingredient,
    Recipe,
    Tag,
    Favorite,
    ShoppingCart,
)
from core.validators import validate_amount
from users.models import Subscribe


User = get_user_model()


class UsersSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            subscriber=user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField(
        validators=[validate_amount, ],
    )

    class Meta:
        model = Amount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AmountWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(
        required=True,
        validators=[validate_amount, ],
    )


class RecipeSerializer(serializers.ModelSerializer):
    author = UsersSerializer(read_only=True)
    ingredients = AmountSerializer(many=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=obj, user=request.user).exists()


class ShortenedRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = AmountWriteSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def add_ingredients(self, ingredients_list, recipe):
        Amount.objects.bulk_create([
            Amount(
                recipe=recipe,
                amount=ingredient.get('amount'),
                ingredient_id=ingredient.get('id'),
            ) for ingredient in ingredients_list
        ])

    def create(self, validated_data):
        request = self.context.get('request')
        author = request.user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.add(*tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.add(*tags)
        Amount.objects.filter(recipe_id=instance.pk).delete()
        self.add_ingredients(ingredients, instance)
        super().update(instance, validated_data)
        return instance


class SubscribeListSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user
        if not request or user.is_anonymous:
            return False
        return user.subscriber.filter(author=obj.author).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipe_query = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            if not recipes_limit.isdigit():
                raise serializers.ValidationError(
                    f'{recipes_limit} не похоже на число'
                )
            return ShortenedRecipeSerializer(
                recipe_query[:int(recipes_limit)],
                many=True,
                context={'request': request},
            ).data
        return ShortenedRecipeSerializer(
            recipe_query,
            many=True,
            context={'request': request},
        ).data


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('author', 'subscriber')

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeListSerializer(
            instance.author,
            context={'request': request}
        ).data

    def validate(self, data):
        subscriber = self.context.get('request').user
        author = data.get('author')
        if subscriber == author:
            raise serializers.ValidationError(
                'Подписаться на себя? Серьезно? так нельзя'
            )
        if Subscribe.objects.filter(
                subscriber=subscriber.id,
                author=author.id,
        ):
            raise serializers.ValidationError(
                f'Вы уже подписаны на {author}'
            )
        return data


class FavoriteSerializer(serializers.Serializer):

    def to_representation(self, instance):
        return ShortenedRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')},
        ).data
