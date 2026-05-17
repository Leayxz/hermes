from rest_framework import serializers
from .models import Car, Rental


class CarSerializer(serializers.ModelSerializer):
    """Serializer para modelo Carro"""
    class Meta:
        model = Car
        fields = ['id', 'brand', 'model', 'year', 'daily_rate', 'available', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = [
            'id', 'car', 'customer_name', 'customer_email',
            'start_date', 'end_date', 'total_cost', 'returned',
            'actual_return_date', 'late_fee', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RentalCreateSerializer(serializers.Serializer):
    car_id = serializers.IntegerField()
    customer_name = serializers.CharField(max_length=200)
    customer_email = serializers.EmailField()
    days = serializers.IntegerField(min_value=1)


class EmailSerializer(serializers.Serializer):
    """Serializer para validação de inputs que requerem apenas o email do cliente."""
    customer_email = serializers.EmailField()


class ApplyRewardSerializer(serializers.Serializer):
    """Serializer para validação de inputs para o endpoint de aplicação de pontos de recompensa."""

    rental_id = serializers.IntegerField()
    customer_email = serializers.EmailField()
    points_to_redeem = serializers.IntegerField(min_value=100)
