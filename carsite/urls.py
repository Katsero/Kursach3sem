# carsite/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from . import views

app_name = 'carsite'

# API Router
router = DefaultRouter()
router.register(r'cars', views.CarViewSet)  # Убран префикс 'api/'
router.register(r'news', views.NewsViewSet) # Убран префикс 'api/'

urlpatterns = [
    # Главная страница
    path('', views.HomeView.as_view(), name='home'),
    
    # Объявления
    path('cars/', views.CarListView.as_view(), name='car_list'),
    path('cars/<int:pk>/', views.CarDetailView.as_view(), name='car_detail'),
    path('cars/create/', views.CarCreateView.as_view(), name='car_create'),
    path('cars/<int:pk>/edit/', views.CarUpdateView.as_view(), name='car_edit'),
    path('cars/<int:pk>/delete/', views.CarDeleteView.as_view(), name='car_delete'),

    # Новости
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('news/create/', views.NewsCreateView.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', views.NewsUpdateView.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', views.NewsDeleteView.as_view(), name='news_delete'),
    path('news/<int:pk>/comment/', views.AddCommentView.as_view(), name='news_comment'),
    path('news/<int:news_pk>/comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),

    # Регистрация
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
]

# === Явные URL-адреса для аутентификации (Django 6.0+) ===
urlpatterns += [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

# === API URLs ===
urlpatterns += [
    path('api/', include(router.urls)), # Префикс 'api/' здесь
]