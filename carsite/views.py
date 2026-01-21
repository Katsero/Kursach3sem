# carsite/views.py
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Car

class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'  # ← убрано 'carsite/'
    context_object_name = 'car_list'
    ordering = ['-created_at']

class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'  # ← убрано 'carsite/'

class CarCreateView(LoginRequiredMixin, CreateView):
    model = Car
    fields = ['model', 'price', 'year', 'mileage', 'description', 'vin', 'status']
    template_name = 'car_form.html'  # ← убрано 'carsite/'
    success_url = reverse_lazy('carsite:car_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class CarUpdateView(LoginRequiredMixin, UpdateView):
    model = Car
    fields = ['model', 'price', 'year', 'mileage', 'description', 'vin', 'status']
    template_name = 'car_form.html'  # ← убрано 'carsite/'
    success_url = reverse_lazy('carsite:car_list')

    def get_queryset(self):
        user = self.request.user
        if user.role == 'moderator':
            return Car.objects.all()
        return Car.objects.filter(user=user)

class CarDeleteView(LoginRequiredMixin, DeleteView):
    model = Car
    template_name = 'car_confirm_delete.html'  # ← убрано 'carsite/'
    success_url = reverse_lazy('carsite:car_list')

    def get_queryset(self):
        user = self.request.user
        if user.role == 'moderator':
            return Car.objects.all()
        return Car.objects.filter(user=user)