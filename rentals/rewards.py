from enum import Enum
from decimal import Decimal
from dtos import RewardsResult, RewardHistoryResult, ApplyRewardPointsResult, RewardTransactionResult

# debt: se os erros forem movidos, todos os imports precisam ser atualizados, idealmente deveria ser errors.py
class RewardError(Enum): 
    INSUFFICIENT_POINTS = "Usuário não possui pontos suficientes."
    RENTAL_NOT_FOUND = "Locação não encontrada."
    USER_NOT_AUTORIZED = "Usuário só deve aplicar descontos em suas próprias locações."

class RewardsService:
    """Serviço responsável pelo sistema de recompensas do usuário."""

    def __init__(self, database) -> None:
        self._database = database


    def get_customer_rewards(self, customer_email: str) -> RewardsResult:
        """Busca pontos de recompensas do cliente baseado no email."""

        # 1. Busca os atuais pontos de rewards do usuário em DB
        rewards = self._database.get_customer_rewards(customer_email)

        # 2. Cálculo para o tier e próximo Tier
        tier = self._calculate_tier(total_points=rewards.total_points)
        points_to_next_tier = self._calculate_next_tier(total_points=rewards.total_points)

        return RewardsResult(
            customer_email=customer_email,
            total_points=rewards.total_points,
            tier=tier,
            points_to_next_tier=points_to_next_tier,
            lifetime_points_earned=rewards.lifetime_points_earned,
            lifetime_points_redeemed=rewards.lifetime_points_redeemed,
            updated_at=rewards.updated_at
        )


    def get_transaction_history(self, customer_email: str) -> RewardHistoryResult:
        """Busca todo o histórico de pontos de rewards do usuário."""

        # 1. Busca histórico no DB
        transactions = self._database.get_transaction_history(customer_email)

        # 2. List comprehension para colocar todos os dados em lista
        transactions_list = [
            {
                "id": transaction.id,
                "type": transaction.type,
                "points": transaction.points,
                "reason": transaction.reason,
                "rental_id": transaction.rental_id,
                "timestamp": transaction.timestamp,
            }

            for transaction in transactions

        ]

        return RewardHistoryResult(customer_email=customer_email, transactions=transactions_list)


    def add_points(self, rental) -> None:
        """Método público responsável por persistir atualização dos pontos de reward do usuário."""

        # 1. Cálculo dos pontos pós rental fechada e dados atuais de reward do usuário
        points_for_rental = self._calculate_points(days=(rental.end_date - rental.start_date).days, daily_rate=rental.car.daily_rate, returned_at=rental.actual_return_date, expected_return=rental.end_date)
        reward = self._database.get_customer_rewards(rental.customer_email)

        # 2. Multiplicação, Tier e Next Tier para substituição em DB
        final_points = self._calculate_multiplier_points(reward.total_points, points_for_rental)
        reward.total_points += final_points
        reward.lifetime_points_earned += final_points
        reward.tier = self._calculate_tier(total_points=reward.total_points)
        reward.points_to_next_tier = self._calculate_next_tier(reward.total_points)

        # 3. Registra histórico da transação e salva novo estado
        context = self._build_context_for_transaction(rental)
        history_transaction = RewardTransactionResult(customer_email=rental.customer_email, type="earned", points=final_points, reason=context, rental_id=rental.id)
        self._database.register_history_transaction(history_transaction)
        self._database.update_customer_rewards(reward)


    def apply_points(self, data) -> ApplyRewardPointsResult:
        """Aplica pontos de recompensa do usuário para desconto em locação."""

        # 1. Rewards atuais do usuário
        rewards = self._database.get_customer_rewards(data.customer_email)

        # 2. Usuário deve possuir no mínimo 100 pontos para aplicar desconto
        if rewards.total_points < 100:
            return ApplyRewardPointsResult(error=RewardError.INSUFFICIENT_POINTS)

        # 3. Usuário deve possuir pontos suficientes para aplicar o desconto desejado
        if rewards.total_points < data.points_to_redeem:
            return ApplyRewardPointsResult(error=RewardError.INSUFFICIENT_POINTS)

        # 4. Dados da rental em que será aplicado o desconto
        rental = self._database.get_rental_by_id(data.rental_id)

        if not rental:
            return ApplyRewardPointsResult(error=RewardError.RENTAL_NOT_FOUND)

        # 5. Usuário só deve aplicar descontos na sua própria locação
        if rental.customer_email != data.customer_email:
            return ApplyRewardPointsResult(error=RewardError.USER_NOT_AUTORIZED)

        # 6. Calculo do desconto baseado nos pontos do usuário
        discount, used_points = self._calculate_discount(data.points_to_redeem)

        # 7. Aplicação do desconto e garantia de que o custo total não seja negativo
        rental.total_cost -= Decimal(discount) # debt
        rental.total_cost = max(rental.total_cost, Decimal("0"))

        # 8. Atualização dos pontos do usuário, Tier e Next Tier
        rewards.total_points -= used_points
        rewards.lifetime_points_redeemed += used_points
        rewards.tier = self._calculate_tier(total_points=rewards.total_points)
        rewards.points_to_next_tier = self._calculate_next_tier(rewards.total_points)

        # 9. Registra histórico da transação e salva novo estado
        context = f"Aplicação de {used_points} pontos para desconto em Rental #{rental.id}"
        history_transaction = RewardTransactionResult(customer_email=data.customer_email, type="redeemed", points=used_points, reason=context, rental_id=rental.id)
        self._database.register_history_transaction(history_transaction)
        self._database.update_customer_rewards(rewards)
        self._database.update_rental(rental)

        return ApplyRewardPointsResult(message="Desconto aplicado com sucesso.")


    def _calculate_discount(self, points_to_redeem: int) -> tuple[Decimal, int]:
        """Cálculo para definir desconto do usuário baseado nos pontos acumulados: 100PTS == R$50 Desconto."""

        blocks = points_to_redeem // 100
        discount = blocks * 50
        used_points = blocks * 100

        return Decimal(discount), used_points


    def _calculate_points(self, days, daily_rate, returned_at, expected_return) -> int:
        """Toda rental fechada deve resultar em pontos para o usuário."""

        # Idealmente todas as regras de negócio deveriam estar isoladas em domínio
        base_points = self._base_points(days)
        category_points = self._category_bonus_points(daily_rate=daily_rate, days=days)
        duration_points = self._duration_bonus_points(days=days)
        punctuality_points = self._punctuality_bonus_points(returned_at=returned_at, expected_return=expected_return)

        total_points = base_points + category_points + duration_points + punctuality_points
        return total_points


    def _base_points(self, days) -> int:
        """Pontos base, multiplicados por dia."""
        return days * 10


    def _category_bonus_points(self, daily_rate, days) -> int:
        """Carros Premium acumulam +10 PTS, Standard +5 PTS, Econômicos não acumulam."""

        if daily_rate > 500:
            return days * 10

        elif daily_rate > 300:
            return days * 5

        return 0


    def _duration_bonus_points(self, days) -> int:
        """Locações +14 dias acumulam +150 PTS, +7 dias acumulam +50 PTS, locações abaixo não acumulam."""

        if days >= 14:
            return 150

        elif days >= 7:
            return 50

        return 0


    def _punctuality_bonus_points(self, returned_at, expected_return) -> int:
        """Locações devolvidas na data ou antes acumulam +25 PTS, atrasadas não acumulam."""

        if returned_at <= expected_return:
            return 25

        return 0


    def _calculate_multiplier_points(self, total_points: int, points_for_rental: int) -> float:
        """Multiplicação dos pontos do usuário baseado no atual Tier: Ouro/Prata/Bronze."""

        if total_points >= 1000:
            return 1.5 * points_for_rental

        elif total_points >= 500:
            return 1.25 * points_for_rental

        return 1.0 * points_for_rental


    def _calculate_tier(self, total_points) -> str:
        """Cálculo para definir Tier do usuário: Ouro/Prata/Bronze"""

        if total_points >= 1000:
            return "Ouro"

        elif total_points >= 500:
            return "Prata"

        return "Bronze"


    def _calculate_next_tier(self, total_points) -> int:
        """Cálculo de quanto falta para o usuário alcançar um novo Tier."""

        if total_points >= 1000:
            return 0

        elif total_points >= 500:
            return 1000 - total_points

        return 500 - total_points


    def _build_context_for_transaction(self, rental) -> str:
        """Constrói contexto para registro de transação de rewards do usuário."""

        rental_days = (rental.end_date - rental.start_date).days

        if rental.actual_return_date < rental.end_date:
            status = "Devolução antecipada."

        elif rental.actual_return_date == rental.end_date:
            status = "Devolução no prazo."

        else:
            status = "Devolução com atraso."

        return f"Rental #{rental.id} | {rental_days} dias | Status: {status}"
