from django.urls import path
from . import views

app_name = 'carsite'

urlpatterns = [
    path('', views.CarListView.as_view(), name='car_list'),
    path('car/<int:pk>/', views.CarDetailView.as_view(), name='car_detail'),
    path('car/create/', views.CarCreateView.as_view(), name='car_create'),
    path('car/<int:pk>/edit/', views.CarUpdateView.as_view(), name='car_edit'),
    path('car/<int:pk>/delete/', views.CarDeleteView.as_view(), name='car_delete'),
]