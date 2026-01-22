# carsite/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User  # Импортируем нашу кастомную модель

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Обязательное поле.')

    class Meta:
        model = User  # Указываем, что форма работает с нашей моделью
        fields = ('username', 'email', 'password1', 'password2')