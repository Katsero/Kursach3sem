from django.contrib import admin
from django.utils.html import format_html
from .models import User, Brand, Model, Car, CarImage, Favorite, News, Comment


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1
    readonly_fields = ['uploaded_at']
    fields = ['image_path', 'is_main', 'uploaded_at']


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['id', 'model', 'price_rub', 'year', 'status_badge', 'owner_link', 'created_at']
    list_display_links = ['id', 'model']
    list_filter = ['status', 'year', 'created_at', 'model__brand']
    search_fields = ['model__name', 'model__brand__name', 'vin']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user', 'model']
    inlines = [CarImageInline]
    readonly_fields = ['created_at', 'updated_at']

    @admin.display(description='Цена')
    def price_rub(self, obj):
        return f"{obj.price:,} ₽".replace(',', ' ')

    @admin.display(description='Статус')
    def status_badge(self, obj):
        colors = {'active': 'green', 'sold': 'gray', 'deleted': 'red'}
        return format_html(
            '<span style="color: {}"><b>{}</b></span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )

    @admin.display(description='Владелец')
    def owner_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:carsite_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'models_count']
    search_fields = ['name']
    list_display_links = ['id', 'name']

    @admin.display(description='Моделей')
    def models_count(self, obj):
        return obj.model_set.count()


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'brand', 'cars_count']
    list_filter = ['brand']
    search_fields = ['name', 'brand__name']
    raw_id_fields = ['brand']

    @admin.display(description='Объявлений')
    def cars_count(self, obj):
        return obj.car_set.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'car', 'added_at']
    list_filter = ['added_at']
    date_hierarchy = 'added_at'
    raw_id_fields = ['user', 'car']
    readonly_fields = ['added_at']


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published_at', 'comments_count']
    list_filter = ['published_at', 'author']
    search_fields = ['title', 'content']
    date_hierarchy = 'published_at'
    raw_id_fields = ['author']
    inlines = [CommentInline]
    readonly_fields = ['created_at', 'updated_at']

    @admin.display(description='Комментариев')
    def comments_count(self, obj):
        return obj.comments.count()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['short_text', 'news', 'user', 'created_at']
    list_filter = ['created_at', 'news']
    search_fields = ['text', 'user__username']
    raw_id_fields = ['user', 'news']
    readonly_fields = ['created_at', 'updated_at']

    @admin.display(description='Текст')
    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'date_joined', 'cars_count', 'favorites_count']
    list_filter = ['role', 'date_joined']
    search_fields = ['username', 'email']
    readonly_fields = ['date_joined', 'last_login']
    filter_horizontal = ['groups', 'user_permissions']

    @admin.display(description='Объявлений')
    def cars_count(self, obj):
        return obj.car_set.count()

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        return obj.favorite_set.count()