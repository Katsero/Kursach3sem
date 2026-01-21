from rest_framework import serializers
from .models import Car, News


class CarSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='model.brand.name', read_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True)

    class Meta:
        model = Car
        fields = '__all__'

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть положительной")
        return value


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'