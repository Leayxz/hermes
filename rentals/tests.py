from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient
from rentals.models import Car, Rental


class TestCarAPITestCase(TestCase):
    """Testes para APIs `GET get_cars` e `GET get_car`"""

    def setUp(self):
        self.client = APIClient()
        self.car = Car.objects.create(brand="Toyota", model="Corolla", year=2020, daily_rate=Decimal("50.00"), available=True)


    def test_obter_carros_disponiveis(self):

        # Act - Pylance não infere o tipo `response.data`
        response = self.client.get('/api/cars/')

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('cars', response.data)
        self.assertEqual(len(response.data['cars']), 1)


    def test_obter_carro_por_id(self):

        # Act
        response = self.client.get(f'/api/cars/{self.car.id}/')

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['brand'], 'Toyota')


class TestCreateRentalView(TestCase):
    """Testes para API `POST create_rental`."""

    def setUp(self):
          self.client = APIClient()
          self.car = Car.objects.create(brand="Honda", model="Civic", year=2021, daily_rate=Decimal("55.00"), available=True)


    def test_sucesso_criacao_locacao(self):

        # Act - Pylance não consegue inferir o tipo `self.car.id`
        data = {"car_id": self.car.id, "customer_name": "John Doe", "customer_email": "john@example.com", "days": 5}
        resposta = self.client.post('/api/rentals/create/', data, format='json')

        # Assert
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(Rental.objects.count(), 1)
        self.car.refresh_from_db()
        self.assertFalse(self.car.available)


    def test_retorna_404_carro_nao_existe(self):

        # Act
        data = {"car_id": 999, "customer_name": "John Doe", "customer_email": "john@example.com", "days": 5}
        resposta = self.client.post('/api/rentals/create/', data, format='json')

        # Assert
        self.assertEqual(resposta.status_code, 404)
        self.assertEqual(resposta.json()["error"], "Car not found")


    def test_retorna_400_carro_nao_disponivel(self):

        # Arrange
        self.car.available = False
        self.car.save()

        # Act
        data = {"car_id": self.car.id, "customer_name": "John Doe", "customer_email": "john@example.com", "days": 5}
        resposta = self.client.post('/api/rentals/create/', data, format='json')

        # Assert
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(resposta.json()["error"], "Car is not available")


    def test_retorna_400_dados_invalidos(self):

        # Act
        data = {"car_id": self.car.id, "customer_name": "John Doe", "customer_email": "john@example.com"}
        resposta = self.client.post('/api/rentals/create/', data, format='json')

        # Assert
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("days", resposta.json())


    def test_aplicacao_cinco_porcento_desconto(self):

        # Act
        data = {"car_id": self.car.id, "customer_name": "John Doe", "customer_email": "john@example.com", "days": 4}
        resposta = self.client.post('/api/rentals/create/', data, format='json')
        rental = Rental.objects.get()

        # Assert       
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(rental.total_cost, Decimal("209.00"))


    def test_aplicacao_dez_porcento_desconto(self):

        # Act
        data = {"car_id": self.car.id, "customer_name": "John Doe", "customer_email": "john@example.com", "days": 8}
        resposta = self.client.post('/api/rentals/create/', data, format='json')
        rental = Rental.objects.get()

        # Assert       
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(rental.total_cost, Decimal("396.00"))
