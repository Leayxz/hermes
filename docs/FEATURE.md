# 🎁 Solicitação de Funcionalidade: Sistema de Recompensas para Clientes

## Visão Geral

Implemente um **sistema de pontos de recompensa** para a API de Locação de Carros onde os clientes ganham pontos baseados em sua atividade de locação. Esta funcionalidade deve se integrar com o sistema de locação existente e fornecer APIs para gerenciar e consultar pontos de recompensa.

## Requisitos de Negócio

### Regras para Ganho de Pontos

Os clientes devem ganhar pontos baseados nos seguintes critérios:

1. **Pontos Base**: 10 pontos por dia de locação
2. **Bônus por Categoria de Carro**:
   - Carros Econômicos (diária < R$300): Sem bônus
   - Carros Standard (diária R$300-R$499): +5 pontos por dia
   - Carros Premium (diária R$500+): +10 pontos por dia

3. **Bônus por Duração da Locação**:
   - Locações de 7+ dias: +50 pontos de bônus
   - Locações de 14+ dias: +150 pontos de bônus

4. **Bônus por Devolução Pontual**:
   - Devolvido na data ou antes: +25 pontos
   - Devoluções atrasadas: Sem bônus (e sem penalidade nos pontos existentes)

5. **Multiplicadores por Nível** (Opcional - para implementação avançada):
   - Bronze (0-499 pontos): multiplicador 1x
   - Prata (500-999 pontos): multiplicador 1.25x
   - Ouro (1000+ pontos): multiplicador 1.5x

### Resgate de Pontos (Opcional)

Permitir que clientes resgatem pontos para descontos:
- 100 pontos = R$50 de desconto
- Resgate mínimo: 100 pontos
- Pontos são deduzidos após conclusão bem-sucedida da locação

## Requisitos Técnicos

### 1. Esquema do Banco de Dados

Crie modelo(s) apropriado(s) para armazenar:
- Saldo de pontos de recompensa do cliente
- Histórico de transações de pontos (ganhos/resgatados)
- Tipo de transação e motivo
- Timestamp das transações
- Locação relacionada (se aplicável)

**Considerações:**
- Os pontos devem estar vinculados ao email do cliente ou criar um modelo Cliente separado?
- Como lidar com histórico de pontos e auditoria?
- Restrições e validações de banco de dados

### 2. Endpoints da API

Implemente os seguintes endpoints:

#### Obter Recompensas do Cliente
```
GET /api/rewards/customer/{customer_email}/
```
Resposta:
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

#### Obter Histórico de Pontos
```
GET /api/rewards/customer/{customer_email}/history/
```
Resposta:
```json
{
  "customer_email": "joao@example.com",
  "transactions": [
    {
      "id": 1,
      "type": "earned",
      "points": 75,
      "reason": "Locação #123 - locação de 5 dias com devolução pontual",
      "rental_id": 123,
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "type": "redeemed",
      "points": -100,
      "reason": "Desconto na locação #124",
      "rental_id": 124,
      "timestamp": "2024-01-20T14:00:00Z"
    }
  ]
}
```

#### Aplicar Pontos na Locação
```
POST /api/rewards/apply/
```
Requisição:
```json
{
  "rental_id": 125,
  "customer_email": "joao@example.com",
  "points_to_redeem": 200
}
```

## Critérios de Aceitação

### Requisitos Mínimos (Obrigatório)

- [ ] Endpoint GET para recuperar saldo de recompensas do cliente
- [ ] Pontos automaticamente concedidos quando locação é devolvida
- [ ] Cálculo de pontos segue regras base (pontos por dia + bônus)
- [ ] Código funcional e passa em todos os testes

### Recomendado 

- [ ] Endpoint de histórico de pontos implementado
- [ ] Sistema de níveis implementado (Bronze/Prata/Ouro)
- [ ] Funcionalidade de resgate de pontos implementada
- [ ] Painel admin configurado para gerenciamento de recompensas

### Opcional (Bom Ter)

- [ ] Multiplicador de pontos baseado no nível
- [ ] Exportar histórico de pontos como CSV/PDF
- [ ] Paginação para histórico de pontos
- [ ] Opções de filtragem e ordenação da API


## Critérios de Avaliação

Sua submissão será avaliada em:

### 1. Funcionalidade (30%)
- Funcionalidade funciona conforme especificado
- Trata casos extremos
- Sem bugs críticos

### 2. Qualidade de Código (20%)
- Código limpo e legível
- Abstração e organização adequadas
- Segue melhores práticas Django
- Boas convenções de nomenclatura
- Problemas existentes refatorados

### 3. Testes (30%)
- Cobertura abrangente de testes
- Testes significativos e bem estruturados
- Casos extremos cobertos
- Testes existentes ainda passam

### 4. Documentação (10%)
- Docstrings claras
- Documentação da API
- Decisões arquiteturais explicadas
- Instruções de configuração atualizadas

### 5. Design & Arquitetura (10%)
- Modelos bem estruturados
- Consultas de banco de dados eficientes
- Separação adequada de responsabilidades
- Design escalável

### Como Submeter

1. Criar um branch git: `git checkout -b feature/rewards-system`
2. Fazer commit das mudanças com mensagens claras
3. Incluir um resumo das mudanças em IMPLEMENTACAO.md
4. "Pushar" as suas mudanças em um repositório público e enviar o link como resposta ao e-mail de desafio

## Dúvidas?

Se você tiver dúvidas sobre requisitos:
1. Faça suposições razoáveis e documente-as
2. Mostre sua abordagem de resolução de problemas
3. Explique soluções alternativas consideradas

## Exemplo de Cálculo de Pontos

**Cenário**: Cliente aluga um Audi Q3 (R$600/dia) por 8 dias e devolve pontualmente.

**Cálculo**:
- Pontos base: 10 × 8 = 80 pontos
- Bônus carro premium: 10 × 8 = 80 pontos
- Bônus 7+ dias: 50 pontos
- Bônus devolução pontual: 25 pontos
- **Total**: 235 pontos

**Com nível Prata (multiplicador 1.25x)**:
- Total antes do multiplicador: 235 pontos
- Com multiplicador: 235 × 1.25 = 293 pontos (arredondado)

## Resumo

Construa um sistema de pontos de recompensa que:
- ✅ Concede pontos baseados em comportamento de locação
- ✅ Fornece APIs para consultar pontos do cliente
- ✅ Integra com fluxo de locação existente
- ✅ É bem testado e documentado
- ✅ Mostra sua capacidade de melhorar código existente

**Lembre-se**: Esta é uma oportunidade de mostrar não apenas habilidades de codificação, mas também:
- Pensamento de design de sistema
- Práticas de teste
- Hábitos de documentação
- Habilidades de refatoração
- Atenção aos detalhes

Boa sorte! Estamos ansiosos para ver sua solução! 🚀
