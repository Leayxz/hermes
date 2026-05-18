# API Documentation

### Obter rewards do cliente

### Request

```http
GET /api/rewards/customer/{customer_email}/
```

### Response

```json
{
  "customer_email": "joao@example.com",
  "total_points": 350,
  "tier": "Bronze",
  "points_to_next_tier": 150,
  "lifetime_points_earned": 450,
  "lifetime_points_redeemed": 100
}
```

---

### Obter histórico de transações do cliente
### Request

```http
GET /api/rewards/customer/{customer_email}/history/
```

### Response

```json
{
  "customer_email": "joao@example.com",
  "transactions": [
    {
      "id": 1,
      "type": "earned",
      "points": 75,
      "reason": "Rental #123 | 5 dias | Status: Devolução no prazo.",
      "rental_id": 123,
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### Aplicar pontos na locação do cliente

### Request

```http
POST /api/rewards/apply/
```

### Payload

```json
{
  "rental_id": 125,
  "customer_email": "joao@example.com",
  "points_to_redeem": 200
}
```

### Response

```json
{
  "success": true,
  "message": "Desconto aplicado com sucesso."
}
```
