# Exemplos de Requisições à API

## Usando curl

### Obter Carros Disponíveis
```bash
curl http://localhost:8000/api/cars/
```

### Obter Carro Específico
```bash
curl http://localhost:8000/api/cars/1/
```

### Criar uma Locação
```bash
curl -X POST http://localhost:8000/api/rentals/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "car_id": 1,
    "customer_name": "João Silva",
    "customer_email": "joao@example.com",
    "days": 5
  }'
```

### Devolver um Carro
```bash
curl -X POST http://localhost:8000/api/rentals/1/return/
```

### Obter Locações do Cliente
```bash
curl http://localhost:8000/api/rentals/customer/joao@example.com/
```

### Obter Todas as Locações
```bash
curl http://localhost:8000/api/rentals/
```

### Obter Estatísticas
```bash
curl http://localhost:8000/api/stats/
```

## Usando Python requests

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Obter carros disponíveis
response = requests.get(f"{BASE_URL}/cars/")
print(response.json())

# Criar locação
rental_data = {
    "car_id": 1,
    "customer_name": "João Silva",
    "customer_email": "joao@example.com",
    "days": 5
}
response = requests.post(f"{BASE_URL}/rentals/create/", json=rental_data)
rental = response.json()
print(f"Locação criada: {rental['id']}")

# Devolver carro
rental_id = rental['id']
response = requests.post(f"{BASE_URL}/rentals/{rental_id}/return/")
print(response.json())

# Obter estatísticas
response = requests.get(f"{BASE_URL}/stats/")
print(response.json())
```

## Usando Django Shell

```python
python manage.py shell

from rentals.models import Car, Rental
from decimal import Decimal
from django.utils import timezone

# Criar um carro
car = Car.objects.create(
    brand="Toyota",
    model="Camry",
    year=2022,
    daily_rate=Decimal("300.00"),
    available=True
)

# Criar uma locação
rental = Rental.objects.create(
    car=car,
    customer_name="Maria Santos",
    customer_email="maria@example.com",
    start_date=timezone.now(),
    end_date=timezone.now() + timezone.timedelta(days=3),
    total_cost=Decimal("900.00")
)

# Consultar locações
rentals = Rental.objects.filter(customer_email="maria@example.com")
for rental in rentals:
    print(f"Locação {rental.id}: {rental.car} - R${rental.total_cost}")
```
