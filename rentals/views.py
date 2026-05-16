from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import Car, Rental
from .serializers import CarSerializer, RentalSerializer, RentalCreateSerializer
from . import database


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
    data = serializer.validated_data
    car_id = data['car_id']
    days = data['days']

    # 3. Busca do carro informado e validação de existência + disponibilidade
    car = database.get_car_by_id(car_id)

    if car is None:
        return Response({"error": "Car not found"}, status=status.HTTP_404_NOT_FOUND)

    if not car.available:
        return Response({"error": "Car is not available"}, status=status.HTTP_400_BAD_REQUEST)

    # 4. Cálculo do custo total da locação e aplicação dos descontos
    total_cost = car.daily_rate * days

    if days > 7:
        total_cost -= total_cost * Decimal("0.1")
    elif days > 3:
        total_cost -= total_cost * Decimal("0.05")

    # 5. Definição do período da locação
    start_date = timezone.now()
    end_date = start_date + timedelta(days=days)

    # 6. Criação do registro de locação
    rental = database.create_rental(
        car_id=car_id,
        customer_name=data['customer_name'],
        customer_email=data['customer_email'],
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
    
    if rental.returned == True:
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
    
    serializer = RentalSerializer(rental)
    return Response({
        "message": "Car returned successfully",
        "rental": serializer.data
    })


@api_view(['GET'])
def get_rentals(request):
    rentals = database.get_all_rentals()
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

