# 🐳 Configuração Docker para API de Locação de Carros

## Início Rápido com Docker

### Opção 1: Usando Docker Compose (Recomendado)

```bash
# Construir e iniciar o container
docker-compose up --build

# A API estará disponível em http://localhost:8000/api/
```

É só isso! O container automaticamente irá:
- Instalar dependências
- Executar migrações do banco de dados
- Carregar dados de exemplo de carros
- Iniciar o servidor de desenvolvimento

### Opção 2: Usando Docker diretamente

```bash
# Construir a imagem
docker build -t car-rental-api .

# Executar o container
docker run -p 8000:8000 car-rental-api
```

## 🛠️ Comandos Docker

### Iniciar a aplicação
```bash
docker-compose up
```

### Iniciar em modo detached (segundo plano)
```bash
docker-compose up -d
```

### Visualizar logs
```bash
docker-compose logs -f
```

### Parar a aplicação
```bash
docker-compose down
```

### Reconstruir após alterações no código
```bash
docker-compose up --build
```

### Acessar shell Django no container
```bash
docker-compose exec web python manage.py shell
```

### Executar testes no container
```bash
docker-compose exec web python manage.py test rentals
# ou
docker-compose exec web pytest
```

### Criar superusuário
```bash
docker-compose exec web python manage.py createsuperuser
```

## 📊 Persistência do Banco de Dados

O banco de dados SQLite é armazenado em um volume Docker chamado `sqlite_data`, o que significa:
- ✅ Dados persistem entre reinicializações do container
- ✅ Dados sobrevivem ao `docker-compose down`
- ⚠️ Dados são perdidos se você remover o volume

### Para resetar o banco de dados:
```bash
docker-compose down -v  # -v remove volumes
docker-compose up --build
```


## 🐛 Solução de Problemas

### Porta 8000 já em uso
```bash
# Altere a porta no docker-compose.yml
ports:
  - "8001:8000"  # Use a porta 8001
```

### Container não inicia
```bash
# Verificar logs
docker-compose logs

# Reconstruir do zero
docker-compose down -v
docker-compose up --build
```

### Problemas de permissão com SQLite
```bash
# O script entrypoint deve lidar com isso, mas se necessário:
docker-compose exec web chmod 666 db.sqlite3
```

## 📁 Estrutura de Arquivos para Docker

```
recrutamento/
├── Dockerfile              # Definição da imagem Docker
├── docker-compose.yml      # Configuração Docker Compose
├── docker-entrypoint.sh    # Script de inicialização
├── .dockerignore          # Arquivos a excluir da imagem
└── ...
```

## 🚀 Endpoints da API

Uma vez em execução, acesse:
- Raiz da API: http://localhost:8000/api/
- Carros Disponíveis: http://localhost:8000/api/cars/
- Painel Admin: http://localhost:8000/admin/
- Documentação da API: Veja example_requests.md

## 📝 Observações

- O servidor de desenvolvimento executa em `0.0.0.0:8000` dentro do container
- Alterações no código são refletidas imediatamente (montagem de volume)
- Banco de dados SQLite persiste em um volume nomeado
- Dados de exemplo iniciais (5 carros) são carregados automaticamente
- Container executa como root (para simplicidade no ambiente de avaliação)
