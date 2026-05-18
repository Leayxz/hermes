from unittest.mock import MagicMock, patch
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient
from rentals.models import Car, Rental

from rentals.rewards import RewardsService


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


class TestRewardsService:
    """Testes para serviço de recompensas."""

    def test_get_customer_rewards_should_return_bronze_tier(self):

        # Arrange
        database = MagicMock()
        mock_rewards = MagicMock()

        mock_rewards.total_points = 300
        mock_rewards.lifetime_points_earned = 500
        mock_rewards.lifetime_points_redeemed = 200

        # Act
        database.get_customer_rewards.return_value = mock_rewards
        result = RewardsService(database).get_customer_rewards("teste@hotmail.com")

        # Assert
        database.get_customer_rewards.assert_called_once_with("teste@hotmail.com")
        assert result.customer_email == "teste@hotmail.com"
        assert result.total_points == 300
        assert result.tier == "Bronze"
        assert result.points_to_next_tier == 200
        assert result.lifetime_points_earned == 500
        assert result.lifetime_points_redeemed == 200


    def test_get_customer_rewards_should_return_silver_tier(self):
        
        # Arrange
        database = MagicMock()
        mock_rewards = MagicMock()

        mock_rewards.total_points = 700
        mock_rewards.lifetime_points_earned = 1000
        mock_rewards.lifetime_points_redeemed = 300

        # Act
        database.get_customer_rewards.return_value = mock_rewards
        result = RewardsService(database).get_customer_rewards("teste@email.com")

        # Assert
        assert result.tier == "Prata"
        assert result.points_to_next_tier == 300


    def test_get_customer_rewards_should_return_gold_tier(self):

        # Arrange
        database = MagicMock()
        mock_rewards = MagicMock()

        mock_rewards.total_points = 1500
        mock_rewards.lifetime_points_earned = 3000
        mock_rewards.lifetime_points_redeemed = 500

        # Act
        database.get_customer_rewards.return_value = mock_rewards
        result = RewardsService(database).get_customer_rewards("gold@email.com")

        # Assert
        assert result.tier == "Ouro"
        assert result.points_to_next_tier == 0


    def test_get_transaction_history_should_return_transactions(self):

        # Arrange
        database = MagicMock()
        transaction_1 = MagicMock()
        transaction_2 = MagicMock()

        transaction_1.id = 1
        transaction_1.type = "earned"
        transaction_1.points = 150
        transaction_1.reason = "Rental completed"
        transaction_1.rental_id = 10

        transaction_2.id = 2
        transaction_2.type = "redeemed"
        transaction_2.points = 100
        transaction_2.reason = "Discount applied"
        transaction_2.rental_id = 11

        # Act
        database.get_transaction_history.return_value = [ transaction_1, transaction_2 ]
        result = RewardsService(database).get_transaction_history("test@email.com")

        # Assert
        database.get_transaction_history.assert_called_once_with("test@email.com")
        assert result.customer_email == "test@email.com"
        assert len(result.transactions) == 2
        assert result.transactions[0]["id"] == 1
        assert result.transactions[0]["type"] == "earned"
        assert result.transactions[0]["points"] == 150

        assert result.transactions[1]["id"] == 2
        assert result.transactions[1]["type"] == "redeemed"
        assert result.transactions[1]["points"] == 100


    def test_get_transaction_history_should_return_empty_list(self):

        # Arrange
        database = MagicMock()

        # Act
        database.get_transaction_history.return_value = []
        result = RewardsService(database).get_transaction_history("empty@email.com")

        # Assert
        database.get_transaction_history.assert_called_once_with("empty@email.com")
        assert result.customer_email == "empty@email.com"
        assert result.transactions == []


    def test_add_points_should_update_customer_rewards(self):

        # Arrange
        database = MagicMock()
        reward = MagicMock()
        rental = MagicMock()

        reward.total_points = 300
        reward.lifetime_points_earned = 500

        rental.id = 1
        rental.customer_email = "test@email.com"

        # Act
        database.get_customer_rewards.return_value = reward
        service = RewardsService(database=database)

        with (
            patch.object(service, "_calculate_points", return_value=100),
            patch.object(service, "_calculate_multiplier_points", return_value=125),
            patch.object(service, "_calculate_tier", return_value="Prata"),
            patch.object(service, "_calculate_next_tier", return_value=375),
            patch.object(service, "_build_context_for_transaction", return_value="Rental completed")
        ):
            service.add_points(rental)

        # Assert
        assert reward.total_points == 425
        assert reward.lifetime_points_earned == 625
        database.register_history_transaction.assert_called_once()
        database.update_customer_rewards.assert_called_once_with(reward)


    def test_apply_points_should_return_error_when_user_has_less_than_100_points(self):

        # Arrange
        database = MagicMock()
        rewards = MagicMock()
        data = MagicMock()

        rewards.total_points = 50
        data.customer_email = "test@email.com"
        data.points_to_redeem = 100

        # Act
        database.get_customer_rewards.return_value = rewards
        result = RewardsService(database).apply_points(data)

        # Assert
        assert result.success is False
        assert result.message == "Usuário não possui pontos suficientes."

        database.get_rental_by_id.assert_not_called()
        database.update_customer_rewards.assert_not_called()


    def test_apply_points_should_return_error_when_user_tries_to_redeem_more_points_than_available(self):

        # Arrange
        database = MagicMock()
        rewards = MagicMock()
        data = MagicMock()



        rewards.total_points = 200
        data.customer_email = "test@email.com"
        data.points_to_redeem = 300

        # Act
        database.get_customer_rewards.return_value = rewards
        result = RewardsService(database).apply_points(data)

        # Assert
        assert result.success is False
        assert result.message == "Usuário possui menos pontos do que deseja resgatar."

        database.get_rental_by_id.assert_not_called()


    def test_apply_points_should_return_error_when_rental_not_found(self):

        # Arrange
        database = MagicMock()
        rewards = MagicMock()
        data = MagicMock()

        rewards.total_points = 500
        data.customer_email = "test@email.com"
        data.points_to_redeem = 100
        data.rental_id = 1

        # Act
        database.get_customer_rewards.return_value = rewards
        database.get_rental_by_id.return_value = None
        result = RewardsService(database).apply_points(data)

        # Assert
        assert result.success is False
        assert result.message == "Locação não encontrada."


    def test_apply_points_should_return_error_when_user_tries_to_apply_discount_to_other_user_rental(self):

        # Arrange
        database = MagicMock()
        rewards = MagicMock()
        rental = MagicMock()
        data = MagicMock()
        
        rewards.total_points = 500
        rental.customer_email = "other@email.com"
        
        data.customer_email = "test@email.com"
        data.points_to_redeem = 100
        data.rental_id = 1

        # Act
        database.get_customer_rewards.return_value = rewards
        database.get_rental_by_id.return_value = rental
        result = RewardsService(database).apply_points(data)

        # Assert
        assert result.success is False
        assert result.message == "Usuário só deve aplicar descontos em suas próprias locações."


    def test_apply_points_should_apply_discount_successfully(self):

        # Arrange
        database = MagicMock()
        rewards = MagicMock()
        rental = MagicMock()
        data = MagicMock()

        rewards.total_points = 500
        rewards.lifetime_points_redeemed = 100

        rental.id = 1
        rental.customer_email = "test@email.com"
        rental.total_cost = Decimal("300")
        
        data.customer_email = "test@email.com"
        data.points_to_redeem = 200
        data.rental_id = 1

        service = RewardsService(database)

        with (
            patch.object(service, "_calculate_discount", return_value=(100, 200)),
            patch.object(service, "_calculate_tier", return_value="Bronze"),
            patch.object(service, "_calculate_next_tier", return_value=400)
        ):

            # Act
            database.get_customer_rewards.return_value = rewards
            database.get_rental_by_id.return_value = rental
            result = service.apply_points(data)

        # Assert
        assert result.success is True
        assert result.message == "Desconto aplicado com sucesso."

        assert rental.total_cost == Decimal("200")

        assert rewards.total_points == 300
        assert rewards.lifetime_points_redeemed == 300

        database.register_history_transaction.assert_called_once()
        database.update_customer_rewards.assert_called_once_with(rewards)
        database.update_rental.assert_called_once_with(rental)


    def test_apply_points_should_never_allow_negative_rental_total(self):

        # Arrange
        database = MagicMock()
        rewards = MagicMock()
        rental = MagicMock()
        data = MagicMock()

        rewards.total_points = 500
        rewards.lifetime_points_redeemed = 0

        rental.id = 1
        rental.customer_email = "test@email.com"
        rental.total_cost = Decimal("50")

        data.customer_email = "test@email.com"
        data.points_to_redeem = 200
        data.rental_id = 1

        service = RewardsService(database)

        with (
            patch.object(service, "_calculate_discount", return_value=(100, 200)),
            patch.object(service, "_calculate_tier", return_value="Bronze"),
            patch.object(service, "_calculate_next_tier", return_value=500)
        ):

            # Act
            database.get_customer_rewards.return_value = rewards
            database.get_rental_by_id.return_value = rental
            result = service.apply_points(data)

        # Assert
        assert result.success is True
        assert rental.total_cost == Decimal("0")

        database.update_rental.assert_called_once_with(rental)
