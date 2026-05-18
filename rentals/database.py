from .models import Car, Rental, Reward, RewardTransaction
from django.db.models import Sum

from rentals.rewards import RewardTransactionResult


def get_all_cars():
    """Obter todos os carros disponíveis e indisponíveis."""
    return Car.objects.all()


def get_available_cars():
    """Obter todos os carros disponíveis."""
    return Car.objects.filter(available=True)


def get_car_by_id(car_id):
    """Obter um carro específico por ID."""
    return Car.objects.filter(id=car_id).first()


def create_rental(car_id, customer_name, customer_email, start_date, end_date, total_cost):
    """Cria uma nova locação."""
    return Rental.objects.create(
        car_id=car_id,
        customer_name=customer_name,
        customer_email=customer_email,
        start_date=start_date,
        end_date=end_date,
        total_cost=total_cost,
        returned=False
    )


def get_rental_by_id(rental_id):
    """Obter uma locação específica por ID."""
    return Rental.objects.filter(id=rental_id).first()


def get_all_rentals():
    """Get all rentals"""
    return Rental.objects.all()


def get_customer_rentals(customer_email):
    """Obter todas as locações de um cliente específico usando o email."""
    return Rental.objects.filter(customer_email=customer_email)


def update_rental(rental):
    """Atualiza uma locação existente."""
    return rental.save()


def update_car(car):
    """Atualiza um carro existente."""
    return car.save()


def get_rental_stats():
    """Calcular estatísticas básicas de locação para o dashboard."""

    total_rentals = Rental.objects.count()
    active_rentals = Rental.objects.filter(returned=False).count()
    total_revenue = Rental.objects.aggregate(total=Sum("total_cost"))["total"] or 0
    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(available=True).count()

    return {
        'total_rentals': total_rentals,
        'active_rentals': active_rentals,
        'available_cars': available_cars,
        'total_cars': total_cars,
        'total_revenue': total_revenue,
    }


def get_customer_rewards(customer_email: str):
    """Busca rewards ou cria default para o usuário usando email e devolve objeto."""
    reward, _ = Reward.objects.get_or_create(customer_email=customer_email)
    return reward


def get_transaction_history(customer_email):
    """Obter histórico de transações do usuário."""
    return RewardTransaction.objects.filter(customer_email=customer_email).order_by("-timestamp")


def update_customer_rewards(reward):
    """Atualiza os pontos do usuário."""
    return reward.save()


def register_history_transaction(data: RewardTransactionResult):
    """Registra histórico de transação."""
    return RewardTransaction.objects.create(customer_email=data.customer_email, type=data.type, points=data.points, reason=data.reason, rental_id=data.rental_id)
