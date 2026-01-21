from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', _('Пользователь')),
        ('moderator', _('Модератор')),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name=_('Роль')
    )

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Название'))

    class Meta:
        verbose_name = _('Марка')
        verbose_name_plural = _('Марки')

    def __str__(self):
        return self.name


class Model(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name=_('Марка'))

    class Meta:
        verbose_name = _('Модель')
        verbose_name_plural = _('Модели')

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class Car(models.Model):
    STATUS_CHOICES = [
        ('active', _('Активно')),
        ('sold', _('Продано')),
        ('deleted', _('Удалено')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Владелец'))
    model = models.ForeignKey(Model, on_delete=models.PROTECT, verbose_name=_('Модель'))
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Цена'))
    year = models.PositiveSmallIntegerField(verbose_name=_('Год выпуска'))
    mileage = models.PositiveIntegerField(verbose_name=_('Пробег, км'))
    description = models.TextField(blank=True, verbose_name=_('Описание'))
    vin = models.CharField(max_length=17, blank=True, verbose_name=_('VIN'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_('Статус'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))

    class Meta:
        verbose_name = _('Объявление')
        verbose_name_plural = _('Объявления')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.model} ({self.year}) — {self.price} ₽"


class CarImage(models.Model):
    car = models.ForeignKey(Car, related_name='images', on_delete=models.CASCADE, verbose_name=_('Объявление'))
    image_path = models.ImageField(upload_to='cars/', verbose_name=_('Изображение'))
    is_main = models.BooleanField(default=False, verbose_name=_('Главное фото'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Загружено'))

    class Meta:
        verbose_name = _('Фотография автомобиля')
        verbose_name_plural = _('Фотографии автомобилей')

    def __str__(self):
        return f"Фото для {self.car} ({'главное' if self.is_main else 'доп.'})"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name=_('Объявление'))
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Добавлено в избранное'))

    class Meta:
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранное')
        unique_together = ('user', 'car')

    def __str__(self):
        return f"{self.user} → {self.car}"


class News(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Заголовок'))
    content = models.TextField(verbose_name=_('Текст'))
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('Автор'))
    cover_image = models.ImageField(upload_to='news/', blank=True, verbose_name=_('Обложка'))
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Опубликовано'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))

    class Meta:
        verbose_name = _('Новость')
        verbose_name_plural = _('Новости')
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    news = models.ForeignKey(News, related_name='comments', on_delete=models.CASCADE, verbose_name=_('Новость'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Автор'))
    text = models.TextField(verbose_name=_('Текст комментария'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создан'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлён'))

    class Meta:
        verbose_name = _('Комментарий')
        verbose_name_plural = _('Комментарии')
        ordering = ['created_at']

    def __str__(self):
        return f"Комментарий от {self.user} к «{self.news.title}»"