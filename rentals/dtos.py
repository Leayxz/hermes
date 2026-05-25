from dataclasses import dataclass
from datetime import datetime
from rewards import RewardError


# --------------- DTOs para tipagem dos dados em views --------------- #

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


# --------------- DTOs para o serviço de Recompensas --------------- #

@dataclass
class RewardsResult:
    customer_email: str
    total_points: int
    tier: str
    points_to_next_tier: int
    lifetime_points_earned: int
    lifetime_points_redeemed: int
    updated_at: datetime


@dataclass
class RewardTransactionResult:
    customer_email: str
    type: str
    points: float
    reason: str
    rental_id: int


@dataclass
class RewardHistoryResult:
    customer_email: str
    transactions: list[dict]


@dataclass
class ApplyRewardPointsResult:
    message: str | None = None
    error: RewardError | None = None
