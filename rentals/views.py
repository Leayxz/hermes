from dataclasses import dataclass, asdict
from typing import cast, Any
from datetime import timedelta
from decimal import Decimal

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone

from .serializers import CarSerializer, RentalSerializer, RentalCreateSerializer, EmailSerializer, ApplyRewardSerializer
from . import database
from .rewards import RewardsService


@dataclass
class RentalDataInput:
    car_id: int
    customer_name: str
    customer_email: str
    days: int


@dataclass
class ApplyRewardInput:
    rental_id: int
    customer_email: str
    points_to_redeem: int


@api_view(['GET'])
def index(request):
    """Endpoint de boas-vindas"""
    return Response({"message": "Welcome to Car Rental API"})


@api_view(['GET'])
def get_cars(request):
    cars = database.get_available_cars()
    serializer = CarSerializer(cars, many=True)
    return Response({"cars": serializer.data})


@api_view(['GET'])
def get_car(request, car_id):
    car = database.get_car_by_id(car_id)
    if car is None:
        return Response({"error": "Car not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CarSerializer(car)
    return Response(serializer.data)


@api_view(['POST'])
def create_rental(request):
    """Criar uma nova locação para um carro disponível."""

    # 1. Validação dos dados recebidos da REQ
    serializer = RentalCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 2. Extração dos dados já validados
    validated_data = cast(dict[str, Any], serializer.validated_data)
    data = RentalDataInput(**validated_data)

    # 3. Busca do carro informado e validação de existência + disponibilidade
    car = database.get_car_by_id(data.car_id)

    if car is None:
        return Response({"error": "Car not found"}, status=status.HTTP_404_NOT_FOUND)

    if not car.available:
        return Response({"error": "Car is not available"}, status=status.HTTP_400_BAD_REQUEST)

    # 4. Cálculo do custo total da locação e aplicação dos descontos
    total_cost = car.daily_rate * data.days

    if data.days > 7:
        total_cost -= total_cost * Decimal("0.1")
    elif data.days > 3:
        total_cost -= total_cost * Decimal("0.05")

    # 5. Definição do período da locação
    start_date = timezone.now()
    end_date = start_date + timedelta(days=data.days)

    # 6. Criação do registro de locação
    rental = database.create_rental(
        car_id=data.car_id,
        customer_name=data.customer_name,
        customer_email=data.customer_email,
        start_date=start_date,
        end_date=end_date,
        total_cost=total_cost
    )

    # 7. Atualização da disponibilidade do carro
    car.available = False
    database.update_car(car)

    rental_serializer = RentalSerializer(rental)
    return Response(rental_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def return_rental(request, rental_id):
    rental = database.get_rental_by_id(rental_id)

    if rental is None:
        return Response({"error": "Rental not found"}, status=status.HTTP_404_NOT_FOUND)

    if rental.returned:
        return Response({"error": "Car already returned"}, status=status.HTTP_400_BAD_REQUEST)

    # Marcar como retornado
    rental.returned = True
    rental.actual_return_date = timezone.now()

    # Calcular multas de atraso
    if rental.actual_return_date > rental.end_date:
        late_days = (rental.actual_return_date - rental.end_date).days
        car = rental.car
        late_fee = float(car.daily_rate) * late_days * 1.5
        rental.late_fee = Decimal(str(late_fee))
        rental.total_cost = rental.total_cost + rental.late_fee

    database.update_rental(rental)

    # Marcar carro como disponível
    car = rental.car
    car.available = True
    database.update_car(car)

    # Serviço para acumulação dos pontos de recompensa do usuário
    RewardsService(database=database).add_points(rental)

    serializer = RentalSerializer(rental)
    return Response({"message": "Car returned successfully", "rental": serializer.data})


@api_view(['GET'])
def get_rentals(request):
    rentals = database.get_all_rentals() # debt: limitar dados
    serializer = RentalSerializer(rentals, many=True)
    return Response({"rentals": serializer.data})


@api_view(['GET'])
def get_customer_rentals(request, customer_email):
    """Obter locações para um cliente específico"""
    rentals = database.get_customer_rentals(customer_email)
    serializer = RentalSerializer(rentals, many=True)
    return Response({"rentals": serializer.data})


@api_view(['GET'])
def get_stats(request):
    stats = database.get_rental_stats()
    return Response(stats)


@api_view(["GET"])
def get_client_rewards(request, customer_email: str):
    """Endpoint para obter recompensas do cliente baseado no email."""

    # 1. Validação de entrada garantindo consistência do email
    serializer = EmailSerializer(data={"customer_email": customer_email})
    
    if not serializer.is_valid():
        return Response({"error": "Email not found or invalid."}, status=status.HTTP_400_BAD_REQUEST)

    # 2. Busca recompensas para o usuário e valida sucesso
    reward = RewardsService(database=database).get_customer_rewards(customer_email)
    return Response(data=asdict(reward), status=status.HTTP_200_OK)


@api_view(["GET"])
def get_reward_transaction_history(request, customer_email):
    """Endpoint para obter todo o histórico de pontos de recompensa do cliente."""

    # 1. Validação de entrada garantindo consistência do email
    serializer = EmailSerializer(data={"customer_email": customer_email})

    if not serializer.is_valid():
        return Response({"error": "Email not found or invalid."}, status=status.HTTP_400_BAD_REQUEST)

    # 2. Busca registro de transações
    transaction_history = RewardsService(database=database).get_transaction_history(customer_email)    
    return Response(data=asdict(transaction_history), status=status.HTTP_200_OK)


@api_view(["POST"])
def apply_rewards_points(request):
    """Endpoint para aplicação dos pontos do usuário na locação."""

    # 1. Validação de entrada garantindo consistência dos dados
    serializer = ApplyRewardSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 2. Extração dos dados já validados e tipagem
    validated_data = cast(dict[str, Any], serializer.validated_data)
    data = ApplyRewardInput(**validated_data)

    # 3. Aplicação dos pontos de recompensa do usuário
    result = RewardsService(database=database).apply_points(data)

    if not result.success:
        return Response(data={"error": result.message}, status=status.HTTP_400_BAD_REQUEST)

    return Response(data=asdict(result), status=status.HTTP_200_OK)
