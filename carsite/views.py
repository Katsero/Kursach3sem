# carsite/views.py
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView 
from django.db.models import Q
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Car, News, Comment
from .serializers import CarSerializer, NewsSerializer
from .forms import SignUpForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# === HTML Views ===
class HomeView(TemplateView):
    """Главная страница сайта."""
    template_name = 'home.html'


class RegisterView(CreateView):
    """Страница регистрации нового пользователя."""
    form_class = SignUpForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('carsite:home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)


class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'
    context_object_name = 'car_list'
    ordering = ['-created_at']
    paginate_by = 5 

class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'


class CarCreateView(LoginRequiredMixin, CreateView):
    model = Car
    fields = ['model', 'price', 'year', 'mileage', 'description', 'vin', 'status']
    template_name = 'car_form.html'
    success_url = reverse_lazy('carsite:car_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CarUpdateView(LoginRequiredMixin, UpdateView):
    model = Car
    fields = ['model', 'price', 'year', 'mileage', 'description', 'vin', 'status']
    template_name = 'car_form.html'
    success_url = reverse_lazy('carsite:car_list')

    def get_queryset(self):
        # Модератор может редактировать все объявления
        if self.request.user.role == 'moderator':
            return Car.objects.all()
        # Обычный пользователь — только свои
        return Car.objects.filter(user=self.request.user)


class CarDeleteView(LoginRequiredMixin, DeleteView):
    model = Car
    template_name = 'car_confirm_delete.html'
    success_url = reverse_lazy('carsite:car_list')

    def get_queryset(self):
        if self.request.user.role == 'moderator':
            return Car.objects.all()
        return Car.objects.filter(user=self.request.user)


# === Новости ===

class NewsListView(ListView):
    model = News
    template_name = 'news_list.html'
    context_object_name = 'news_list'
    ordering = ['-published_at', '-created_at']

    def get_queryset(self):
        return News.objects.filter(published_at__isnull=False).order_by('-published_at', '-created_at')


class NewsDetailView(DetailView):
    model = News
    template_name = 'news_detail.html'
    context_object_name = 'news'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all().select_related('user')
        return context


class NewsCreateView(LoginRequiredMixin, CreateView):
    model = News
    fields = ['title', 'content', 'cover_image']
    template_name = 'news_form.html'
    success_url = reverse_lazy('carsite:news_list')

    def form_valid(self, form):
        from django.utils import timezone
        form.instance.author = self.request.user
        form.instance.published_at = form.instance.published_at or timezone.now()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'moderator':
            return redirect('carsite:news_list')
        return super().dispatch(request, *args, **kwargs)


class NewsUpdateView(LoginRequiredMixin, UpdateView):
    model = News
    fields = ['title', 'content', 'cover_image']
    template_name = 'news_form.html'
    success_url = reverse_lazy('carsite:news_list')

    def get_queryset(self):
        if self.request.user.role == 'moderator':
            return News.objects.all()
        return News.objects.filter(author=self.request.user)


class NewsDeleteView(LoginRequiredMixin, DeleteView):
    model = News
    template_name = 'news_confirm_delete.html'
    success_url = reverse_lazy('carsite:news_list')

    def get_queryset(self):
        if self.request.user.role == 'moderator':
            return News.objects.all()
        return News.objects.filter(author=self.request.user)


# === Комментарии ===

class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        news = get_object_or_404(News, pk=pk)
        text = request.POST.get('text', '').strip()
        if text:
            Comment.objects.create(news=news, user=request.user, text=text)
        return HttpResponseRedirect(reverse_lazy('carsite:news_detail', kwargs={'pk': pk}))


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'comment_confirm_delete.html'
    success_url = reverse_lazy('carsite:news_detail') 

    def get_success_url(self):
        return reverse_lazy('carsite:news_detail', kwargs={'pk': self.object.news.pk})

    def get_queryset(self):
        if self.request.user.role == 'moderator':
            return Comment.objects.all()
        return Comment.objects.filter(user=self.request.user)


# === API Views ===

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['year', 'status']
    search_fields = ['model__name', 'model__brand__name']

    def get_queryset(self):
        queryset = super().get_queryset()
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(Q(year=year) | Q(status='active'))
        return queryset

    @action(detail=False, methods=['get'])
    def expensive(self, request):
        cars = self.queryset.filter(price__gt=1000000)
        page = self.paginate_queryset(cars)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(cars, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_sold(self, request, pk=None):
        car = self.get_object()
        car.status = 'sold'
        car.save()
        return Response({'status': 'marked as sold'})


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']