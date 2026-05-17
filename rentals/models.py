from django.db import models
from django.core.validators import MinValueValidator, EmailValidator


class Car(models.Model):
    """
    Modelo de Carro representando veículos disponíveis para locação
    """
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField(validators=[MinValueValidator(1900)])
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cars'
        ordering = ['brand', 'model']

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"


class Rental(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='rentals')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(validators=[EmailValidator()])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    returned = models.BooleanField(default=False)
    actual_return_date = models.DateTimeField(null=True, blank=True)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rentals'
        ordering = ['-created_at']

    def __str__(self):
        return f"Rental {self.id} - {self.customer_name}"


class Reward(models.Model):
    """Tabela responsável por armazenar o estado atual dos pontos de recompensa do usuário."""

    customer_email = models.EmailField(validators=[EmailValidator()])
    total_points = models.IntegerField(default=0)
    tier = models.TextField(default="Bronze")
    points_to_next_tier = models.IntegerField(default=0)
    lifetime_points_earned = models.IntegerField(default=0)
    lifetime_points_redeemed = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)


class RewardTransaction(models.Model):
    """Tabela responsável por registrar todas as transações de recompensas do usuário."""

    customer_email = models.EmailField(validators=[EmailValidator()])
    type = models.TextField()
    points = models.IntegerField()
    reason = models.TextField()
    rental_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
