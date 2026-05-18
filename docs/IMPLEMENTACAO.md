# Como testar
```bash
# Ambiente virtual e ativação
python -m venv venv
venv/scripts/activate

# Instalação das dependências
pip install -r requirements.txt

# Migrações DB
python manage.py makemigrations
python manage.py migrate

# Ingestão dos dados
./setup.cmd

# Rodando o servidor
python manage.py runserver

# Rodando testes
pytest
```


# Decisões de Design
### 1. Esquema do Banco de Dados
- A implementação foi baseada em dois modelos, `Reward` e `RewardTransaction`.

- O modelo `Reward` é responsável por armazenar o estado atual das recompensas do usuário, funcionando como uma visão consolidada dos pontos acumulados.

- Já o modelo `RewardTransaction` foi criado com foco em auditoria e rastreabilidade. Cada operação relevante gera um registro independente.

- Optei por utilizar diretamente o `customer_email` como identificador do usuário para manter compatibilidade com a arquitetura existente do projeto e evitar introduzir um novo modelo.

### 2. Arquitetura
- Implementações foram organizadas pensando em seraração explícita de responsabilidades.

- Minha principal preocupação foi evitar espalhar regras de negócio diretamente nas views. Por esse motivo toda a lógica relacionada a cálculo de pontos, multiplicadores, tiers e aplicação de descontos foi centralizada no `RewardsService`.

- Os cálculos de pontos foram divididos em métodos privados específicos para cada regra de negócio. Essa abordagem permitiu simplificar manutenção, facilitar cobertura de testes, reduzir duplicação de regras, e melhorar legibilidade da lógica de negócio.

### 3. Abordagem de Integração
- A principal integração ocorreu no endpoint de devolução de locações `return_rental`, onde o `RewardsService` passou a ser acionado após a finalização bem-sucedida da rental. Dessa forma, o sistema de pontos funciona como uma extensão do fluxo atual, sem alterar a lógica principal de locação. Essa abordagem permitiu adicionar a nova funcionalidade sem modificar contratos existentes da API.

### 4. Estratégia de Testes
- Os testes existentes do projeto foram corrigidos e padronizados para garantir execução consistente.

- A maior parte da cobertura da nova feature foi concentrada no `TestRewardsService`, isolando a regra de negócio da infraestrutura.

- A principal preocupação foi validar regras de negócio críticas e efeitos colaterais importantes.

### 5. O que poderia ser feito com mais tempo
- Algumas operações não estão sendo atômicas, ou seja, em casos de erro, algumas operações acontecem enquanto outras não.

- Não existe nenhum log no sistema, e também queria retornar alguns outros dados na aplicação do desconto, como quantidade do desconto talvez.

- Implementaria uma tipagem muito mais forte nos dados de entrada e no transporte de dados dentro do sistema.

- Poderia aplicar paginação nos endpoints que retornam todos os dado, ordenação e filtragem, e exportação em PDF.

- Implementar autorização e permissão.

- Implementar `multi-stage` em Dockerfile e padronizar todos os `COPY` individualmente para não precisar acontecer sempre.

# Anotações
### 1. Migrações em Rentals
- Pasta `rentals` não possuí pasta `migrations`, possívelmente foi criada manualmente e não como app django.

- Tabela `Cars` e `Rental` só são criadas corretamente quando feito `python manage.py makemigrations rentals` e depois `python manage.py migrate`.

### 2. View Create Rental
- Endpoint `rentals/create/` está definida na documentação como `rentals/create/` porém o código contém um typo, faltando `/` ao final da url.

- Endpoint para criação de locações utilizava a variável `daily_rate` sem definição prévia, causando `NameError` durante o cálculo do valor total.

- Cálculo de desconto realizando operações entre `Decimal` e `float`, resultando em TypeError.

- Adicionado `dataclass` para representar os dados de entrada da criação de locações, substituindo o acesso aos dados como `data["algo"]` para `data.car_id`, melhorando legibilidade, ergonomia e manutenção.

### 3. Cobertura de Testes Create Rental
- Suíte de testes quebrando o padrão `test_`, tornando impossível a execução pelo pytest.

- Feita a padronização dos testes para o formato correto `test_` e organização do código em `Arrange/Act/Assert`.

- Maior cobertura de testes para `POST create_rental`, cobrindo criação de locação, carro inexistente, indisponível, validação de payload e regras de desconto.

### 4. Implementação da Feature
- Estou presumindo que a multiplicação dos pontos aconteça baseado nos pontos atuais (Tier) do usuário e aplicado nos pontos de fechamento da rental. Ou seja, se o usuário é tier ouro, ele recebe mais pontos ao fechar uma rental.

- Feature de aplicação de pontos vai retornar algo bem simples e gravar alterações em histórico para auditoria.

- Consultas ineficientes foram corrigidas e otimizadas com filtros diretos usando o ORM.

- Regras de negócio foram centralizadas em `RewardsService`, utilizando DTOs para transporte de dados e `Dependency Injection` para isolamento entre serviço e infraestrutura.

- Acúmulo de pontos foi integrado ao fluxo de devolução de locações de maneira limpa, com separação explícita de SRPs entre view e service.

- Testes unitários com cobertura de comportamento e mocks de infraestrutura. Cenários de erro tratados como comportamento esperado e não exceptions, permitindo o `hot path otimization`.

- Tabelas `RewardAdmin` e `RewardTransactionAdmin` foram adicionados para controle em `Admin`.

- Toda a documentação foi padronizada em `docs/`.