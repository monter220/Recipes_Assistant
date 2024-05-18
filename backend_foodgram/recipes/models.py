from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.conf import settings
from django.db import models

from core.validators import validate_field_text


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.TAG_MAX_LENGTH_FIELD,
        unique=True,
        validators=[validate_field_text, ],
    )
    color = ColorField(
        verbose_name='Цвет',
        max_length=settings.COLOR_MAX_LENGTH_FIELD,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=settings.TAG_MAX_LENGTH_FIELD,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.INGREDIENT_MAX_LENGTH_FIELD,
        unique=False,
        validators=[validate_field_text, ],
    )
    measurement_unit = models.CharField(
        verbose_name='Еденицы измерения',
        max_length=settings.INGREDIENT_MAX_LENGTH_FIELD,
        unique=False,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['measurement_unit', 'name', ],
                name='unique ingredients',
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.RECIPE_MAX_LENGTH_FIELD,
        unique=False,
        validators=[validate_field_text, ],
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='images/',
        null=True,
        default=None,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                settings.MIN_VALIDATE_TIME,
                ('Время приготовления не может быть меньше '
                 f'{settings.MIN_VALIDATE_TIME} минуты'),
            ),
        ],
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список тегов',
        related_name='tags',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='author'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Amount(models.Model):
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                settings.MIN_VALIDATE_AMOUNT,
                'Нельзя использовать так мало',
            ),
        ],
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='+',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'

        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique amount',
            )
        ]

    def __str__(self):
        return (f'В {self.recipe} требуется '
                f'{self.ingredient} ({self.amount} шт)')


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='+',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='В корзине',
        related_name='shoppingcart',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique cart',
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='+',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='В избранном',
        related_name='favorite',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique favorite',
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'
